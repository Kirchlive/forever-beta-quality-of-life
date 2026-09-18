-- Target: WoW Forever Beta 1.60.1 (Interface 16001).
-- One offer per event: the server supplies QUEST_DETAIL after selection.
local enabled = true
local frame = CreateFrame("Frame")
local interactionPaused = false
local interactionNPC
local interactionRevision = 0
local gossipContinuing = false
local interactionTypes = Enum.PlayerInteractionType

local function ResetInteraction()
    interactionPaused = false
    interactionNPC = nil
    gossipContinuing = false
    interactionRevision = interactionRevision + 1
end

local function CheckInteractionEnded()
    if not interactionPaused then
        return
    end
    local revision = interactionRevision
    -- Quest/gossip pages can close while another page opens in the same update.
    C_Timer.After(0, function()
        if revision ~= interactionRevision or gossipContinuing then
            return
        end
        if not C_PlayerInteractionManager.IsInteractingWithNpcOfType(interactionTypes.Gossip)
            and not C_PlayerInteractionManager.IsInteractingWithNpcOfType(interactionTypes.QuestGiver) then
            ResetInteraction()
        end
    end)
end

frame:RegisterEvent("GOSSIP_SHOW")
frame:RegisterEvent("QUEST_GREETING")
frame:RegisterEvent("QUEST_DETAIL")
frame:RegisterEvent("QUEST_PROGRESS")
frame:RegisterEvent("QUEST_COMPLETE")
frame:RegisterEvent("GOSSIP_CLOSED")
frame:RegisterEvent("QUEST_FINISHED")
frame:RegisterEvent("PLAYER_INTERACTION_MANAGER_FRAME_HIDE")
frame:RegisterEvent("PLAYER_ENTERING_WORLD")

frame:SetScript("OnEvent", function(_, event, arg)
    if event == "PLAYER_ENTERING_WORLD" then
        ResetInteraction()
        return
    elseif event == "GOSSIP_CLOSED" then
        gossipContinuing = arg == true
        if not gossipContinuing then
            CheckInteractionEnded()
        end
        return
    elseif event == "QUEST_FINISHED" then
        CheckInteractionEnded()
        return
    elseif event == "PLAYER_INTERACTION_MANAGER_FRAME_HIDE" then
        if arg == interactionTypes.Gossip or arg == interactionTypes.QuestGiver then
            CheckInteractionEnded()
        end
        return
    end

    -- Item and adventure-map offers use a separate Blizzard UI flow.
    if event == "QUEST_DETAIL" and ((arg and arg ~= 0) or QuestIsFromAdventureMap()) then
        return
    end

    local npc = UnitGUID("npc") or UnitGUID("questnpc")
    if npc and interactionNPC and npc ~= interactionNPC then
        ResetInteraction()
    end
    interactionNPC = npc or interactionNPC
    interactionRevision = interactionRevision + 1
    gossipContinuing = false
    -- Once requested, manual control lasts until this conversation ends.
    if IsShiftKeyDown() then
        interactionPaused = true
    end
    if not enabled or interactionPaused then
        return
    end

    if event == "GOSSIP_SHOW" then
        local quests = C_GossipInfo.GetAvailableQuests()
        for _, quest in ipairs(quests or {}) do
            if not quest.isIgnored then
                C_GossipInfo.SelectAvailableQuest(quest.questID)
                return
            end
        end
    elseif event == "QUEST_GREETING" then
        -- The older greeting API expects an index, not a quest ID.
        if GetNumAvailableQuests() > 0 then
            SelectAvailableQuest(1)
        end
    elseif event == "QUEST_DETAIL" then
        if QuestGetAutoAccept() then
            CloseQuest()
        elseif not QuestFlagsPVP() then
            -- Leave the default PvP confirmation available for manual use.
            AcceptQuest()
        end
    end
end)

SLASH_BETAQOL1 = "/betaqol"
SLASH_BETAQOL2 = "/fqa"
SlashCmdList.BETAQOL = function()
    enabled = not enabled
    print("Beta Quality of Life: Quest Auto Accept " .. (enabled and "on" or "off") .. ". Hold Shift to keep a conversation manual.")
end

-- Loot state is independent of the Shift latch used for quest conversations.
local lootFrame = CreateFrame("Frame")
local lootSession
local nativeLootFrame
local lootMask
local RETRY_INTERVAL = 0.1
local RETRY_LIMIT = 1
local TryLoot

local function DisableLootMouse(widget)
    if not lootMask.mouse[widget] then
        lootMask.mouse[widget] = { widget:IsMouseClickEnabled(), widget:IsMouseMotionEnabled() }
    end
    widget:SetMouseClickEnabled(false)
    widget:SetMouseMotionEnabled(false)
    for _, child in ipairs({ widget:GetChildren() }) do
        DisableLootMouse(child)
    end
end

local function RestoreLootWindow()
    if not lootMask then
        return
    end
    local previous = lootMask
    lootMask = nil
    nativeLootFrame:StopAllAnimations()
    for animation, values in pairs(previous.alpha) do
        animation:SetFromAlpha(values[1])
        animation:SetToAlpha(values[2])
    end
    for widget, values in pairs(previous.mouse) do
        widget:SetMouseClickEnabled(values[1])
        widget:SetMouseMotionEnabled(values[2])
    end
    -- Native show animations run 0 -> 1; the pre-show alpha can still be 0.
    nativeLootFrame:SetAlpha(1)
end

local function MaskLootWindow()
    if not lootMask then
        local alpha = {}
        for _, animation in ipairs({ nativeLootFrame.HideAnim:GetAnimations() }) do
            if animation:GetObjectType() == "Alpha" then
                alpha[animation] = { animation:GetFromAlpha(), animation:GetToAlpha() }
            end
        end
        if not next(alpha) then
            return false
        end
        lootMask = { alpha = alpha, mouse = {} }
        nativeLootFrame.HideAnim:Stop()
        for animation in pairs(alpha) do
            animation:SetFromAlpha(0)
            animation:SetToAlpha(0)
        end
    end
    nativeLootFrame.ShowAnim:Stop()
    nativeLootFrame:SetAlpha(0)
    DisableLootMouse(nativeLootFrame)
    return true
end

local function BeginLoot(autoLoot)
    if not lootSession then
        -- Preserve an explicit native false. Sample preferences only if the
        -- client did not supply its documented boolean, then latch the result.
        if type(autoLoot) ~= "boolean" then
            autoLoot = (GetCVarBool("autoLootDefault") == true)
                ~= (IsModifiedClick("AUTOLOOTTOGGLE") == true)
        end
        lootSession = { autoLoot = autoLoot, started = GetTime() }
    end
    return lootSession
end

local function ShowManualLoot(session)
    session.manual = true
    RestoreLootWindow()
end

local function HasLoot()
    for slot = 1, GetNumLootItems() do
        if GetLootSlotType(slot) ~= Enum.LootSlotType.None then
            return true
        end
    end
    return false
end

local function QueueLootRetry(session)
    if session.pending or session.manual or lootSession ~= session then
        return
    end
    session.pending = true
    C_Timer.After(RETRY_INTERVAL, function()
        session.pending = false
        -- Object identity makes callbacks from an earlier corpse harmless.
        if lootSession == session then
            TryLoot(session)
        end
    end)
end

TryLoot = function(session)
    if lootSession ~= session or not session.autoLoot or session.manual or session.busy then
        return
    end

    local now = GetTime()
    if now - session.started >= RETRY_LIMIT then
        if HasLoot() then
            ShowManualLoot(session)
        end
        return
    end
    if session.nextAttempt and now + 0.0001 < session.nextAttempt then
        QueueLootRetry(session)
        return
    end

    session.busy = true
    local ok, failure = pcall(function()
        for slot = GetNumLootItems(), 1, -1 do
            -- LootSlot can synchronously close loot or request confirmation.
            if lootSession ~= session or session.manual then
                break
            end
            -- Cleared indices can remain in the list with type None.
            if GetLootSlotType(slot) ~= Enum.LootSlotType.None then
                local _, _, _, _, _, locked = GetLootSlotInfo(slot)
                if not locked then
                    session.nextAttempt = now + RETRY_INTERVAL
                    LootSlot(slot)
                end
            end
        end
    end)
    session.busy = false
    if not ok then
        if lootSession == session then
            ShowManualLoot(session)
        end
        geterrorhandler()(failure)
        return
    end
    QueueLootRetry(session)
end

local function LootOpened(autoLoot)
    local session = BeginLoot(autoLoot)
    -- The opening event can refine the early readiness decision.
    if type(autoLoot) == "boolean" then
        session.autoLoot = autoLoot
    end
    if not session.autoLoot or session.manual or (nativeLootFrame and nativeLootFrame.isInEditMode) then
        ShowManualLoot(session)
        return
    end
    if lootMask then
        -- Open starts ShowAnim and can populate more scroll-box children after
        -- OnShow. Stop that animation and include those children before render.
        MaskLootWindow()
    end
    -- Do not synchronously close loot from inside the native Open call stack.
    C_Timer.After(0, function()
        if lootSession == session then
            TryLoot(session)
        end
    end)
end

local function HookNativeLoot()
    if nativeLootFrame or not LootFrame then
        return
    end
    if not LootFrame.ShowAnim or not LootFrame.HideAnim or type(LootFrame.Open) ~= "function" then
        return
    end
    nativeLootFrame = LootFrame
    -- Preserve the native event script and its secure execution path, including
    -- ShowUIPanel in combat. These post-hooks only adjust rendering/input.
    nativeLootFrame:HookScript("OnShow", function(self)
        local session = BeginLoot(self.isAutoLoot)
        if type(self.isAutoLoot) == "boolean" then
            session.autoLoot = self.isAutoLoot
        end
        if session.autoLoot and not session.manual and not self.isInEditMode then
            MaskLootWindow()
        end
    end)
    hooksecurefunc(nativeLootFrame, "Open", function(self)
        LootOpened(self.isAutoLoot)
    end)
    nativeLootFrame:HookScript("OnHide", function()
        -- The native close animation remains active (alpha 0 -> 0), including
        -- its secure HideUIPanel cleanup. Restore only after the frame is hidden.
        RestoreLootWindow()
    end)
    -- The native Open post-hook handles OPENED, independent of listener order.
    lootFrame:UnregisterEvent("LOOT_OPENED")
    lootFrame:UnregisterEvent("ADDON_LOADED")
    lootFrame:UnregisterEvent("PLAYER_LOGIN")
end

lootFrame:RegisterEvent("LOOT_READY")
lootFrame:RegisterEvent("LOOT_OPENED")
lootFrame:RegisterEvent("LOOT_CLOSED")
lootFrame:RegisterEvent("LOOT_BIND_CONFIRM")
lootFrame:RegisterEvent("UI_ERROR_MESSAGE")
lootFrame:RegisterEvent("PLAYER_ENTERING_WORLD")
lootFrame:RegisterEvent("ADDON_LOADED")
lootFrame:RegisterEvent("PLAYER_LOGIN")
lootFrame:SetScript("OnEvent", function(_, event, arg, detail)
    if event == "LOOT_READY" then
        TryLoot(BeginLoot(arg))
    elseif event == "LOOT_OPENED" then
        LootOpened(arg, detail)
    elseif event == "LOOT_CLOSED" then
        lootSession = nil
    elseif event == "PLAYER_ENTERING_WORLD" then
        lootSession = nil
        -- Keep an in-flight native close alive until OnHide restores the mask.
        if not nativeLootFrame or not nativeLootFrame.HideAnim:IsPlaying() then
            RestoreLootWindow()
        end
    elseif event == "ADDON_LOADED" or event == "PLAYER_LOGIN" then
        HookNativeLoot()
    elseif lootSession and lootSession.autoLoot then
        if event == "LOOT_BIND_CONFIRM"
            or (event == "UI_ERROR_MESSAGE" and type(detail) == "string"
                and (detail == ERR_INV_FULL or detail == ERR_ITEM_MAX_COUNT)) then
            ShowManualLoot(lootSession)
        end
    end
end)
HookNativeLoot()

-- Enter confirms the main button of standard Blizzard confirmation popups.
-- Keep changes on the visible instance, never on shared dialog definitions.
local popupFrame = CreateFrame("Frame")
local popupScripts = {}
local popupsHooked = false

local function IsForegroundPopup(dialog)
    if not dialog:IsVisible() then
        return false
    end
    local foreground = true
    -- The native popup list is sorted by frame ID, not by keyboard focus.
    -- All these frames use DIALOG strata; Raise determines their frame level.
    StaticPopup_ForEachShownDialog(function(other)
        if other ~= dialog and other:IsVisible()
            and other:GetFrameLevel() > dialog:GetFrameLevel() then
            foreground = false
        end
    end)
    return foreground
end

local function ConfirmPopup(dialog)
    local info = StaticPopupDialogs[dialog.which]
    if not info or info.ignoreKeys or not IsForegroundPopup(dialog) then
        return
    end
    local button = dialog:GetButton1()
    -- Never fall through to Cancel if the main button is temporarily disabled.
    if button and button:IsShown() and button:IsEnabled() then
        StaticPopup_OnClick(dialog, 1)
    end
end

local function RestorePopupScripts(_, dialog)
    local scripts = popupScripts[dialog]
    popupScripts[dialog] = nil
    for _, entry in ipairs(scripts or {}) do
        if entry.widget:GetScript(entry.event) == entry.handler then
            entry.widget:SetScript(entry.event, entry.previous)
        end
    end
end

local function EnablePopupEnter(_, dialog)
    RestorePopupScripts(nil, dialog)
    local info = StaticPopupDialogs[dialog.which]
    if not info or info.ignoreKeys or not dialog.GetButton1 then
        return
    end

    local scripts = {}
    popupScripts[dialog] = scripts
    local function SetTemporaryScript(widget, event, handler)
        scripts[#scripts + 1] = {
            widget = widget, event = event,
            previous = widget:GetScript(event), handler = handler,
        }
        widget:SetScript(event, handler)
    end

    local previousKeyDown = dialog:GetScript("OnKeyDown")
    SetTemporaryScript(dialog, "OnKeyDown", function(self, key)
        if key == "ENTER" or key == "NUMPADENTER" then
            -- Editboxes dispatch OnEnterPressed themselves, including native
            -- text validation. Do not also accept from their parent frame.
            if GetCurrentKeyBoardFocus and GetCurrentKeyBoardFocus() then
                return
            end
            ConfirmPopup(self)
        elseif previousKeyDown then
            previousKeyDown(self, key)
        elseif GetBindingFromClick(key) == "TOGGLEGAMEMENU" and self.hideOnEscape then
            -- Most game dialogs use the UIParent escape cascade, rather than
            -- the separate escapeHides flag in the native keyboard handler.
            StaticPopup_EscapePressed()
        else
            StaticPopup_OnKeyDown(self, key)
        end
    end)

    if not info.EditBoxOnEnterPressed then
        local function EnableEditBoxEnter(editBox)
            if not editBox then
                return
            end
            local previous = editBox:GetScript("OnEnterPressed")
            local standard = StaticPopupEditBoxMixin and StaticPopupEditBoxMixin.OnEnterPressed
            if previous and previous ~= standard then
                return
            end
            SetTemporaryScript(editBox, "OnEnterPressed", function(self)
                if self.hasAutoComplete and AutoCompleteEditBox_OnEnterPressed(self) then
                    return
                end
                ConfirmPopup(dialog)
            end)
        end
        if info.hasEditBox then
            EnableEditBoxEnter(dialog:GetEditBox())
        end
        if info.hasMoneyInputFrame and dialog.MoneyInputFrame then
            EnableEditBoxEnter(dialog.MoneyInputFrame.gold)
            EnableEditBoxEnter(dialog.MoneyInputFrame.silver)
            EnableEditBoxEnter(dialog.MoneyInputFrame.copper)
        end
    end
end

local function HookPopupEnter()
    if popupsHooked or not PopupEventManager or not StaticPopupDialogs then
        return
    end
    popupsHooked = true
    PopupEventManager:RegisterCallback("PopupOpened", EnablePopupEnter, popupFrame)
    PopupEventManager:RegisterCallback("PopupClosed", RestorePopupScripts, popupFrame)
    popupFrame:UnregisterEvent("ADDON_LOADED")
    popupFrame:UnregisterEvent("PLAYER_LOGIN")
end

popupFrame:RegisterEvent("ADDON_LOADED")
popupFrame:RegisterEvent("PLAYER_LOGIN")
popupFrame:SetScript("OnEvent", HookPopupEnter)
HookPopupEnter()
