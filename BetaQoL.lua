-- Target: WoW Forever Beta 1.60.1 (Interface 16001).
local addonName = ... or "BetaQoL"
local settings = {
    autoAccept = true, autoTurnIn = true, fastLoot = true,
    enterConfirm = true, rangeColor = true, whisperDoubleClick = true,
    backspaceDestroy = true,
    squareMinimap = false,
}
local featureChanged = {}
local settingsLoaded = false
local settingsWindow
local settingsChecks = {}

local function RefreshSettings()
    for key, checkbox in pairs(settingsChecks) do
        checkbox:SetChecked(settings[key])
    end
end

local function LoadSettings()
    if settingsLoaded then
        return
    end
    -- SavedVariables are restored after this file runs, before ADDON_LOADED.
    if type(BetaQoLDB) ~= "table" then
        BetaQoLDB = {}
    end
    for key, default in pairs(settings) do
        if type(BetaQoLDB[key]) ~= "boolean" then
            BetaQoLDB[key] = default
        end
    end
    settings = BetaQoLDB
    settingsLoaded = true
    for key, callback in pairs(featureChanged) do
        callback(settings[key])
    end
    RefreshSettings()
end

local function SetFeatureEnabled(key, value)
    LoadSettings()
    settings[key] = value == true
    if featureChanged[key] then
        featureChanged[key](settings[key])
    end
    RefreshSettings()
end

local settingsFrame = CreateFrame("Frame")
settingsFrame:RegisterEvent("ADDON_LOADED")
settingsFrame:SetScript("OnEvent", function(self, _, name)
    if name == addonName then
        LoadSettings()
        self:UnregisterEvent("ADDON_LOADED")
    end
end)

SLASH_QOL1 = "/qol"
SlashCmdList.QOL = function()
    LoadSettings()
    if settingsWindow then
        if settingsWindow:IsShown() then
            settingsWindow:Hide()
        else
            settingsWindow:Show()
        end
        return
    end
    local window = CreateFrame("Frame", "BetaQoLSettingsFrame", UIParent, "BasicFrameTemplateWithInset")
    settingsWindow = window
    window:SetSize(380, 374)
    window:SetPoint("CENTER")
    window:SetFrameStrata("DIALOG")
    window.TitleText:SetText("Beta Quality of Life")
    window:SetMovable(true)
    window:EnableMouse(true)
    window:RegisterForDrag("LeftButton")
    window:SetScript("OnDragStart", window.StartMoving)
    window:SetScript("OnDragStop", window.StopMovingOrSizing)
    window:SetScript("OnShow", RefreshSettings)
    tinsert(UISpecialFrames, "BetaQoLSettingsFrame")

    local features = {
        { "autoAccept", "Quest Auto Accept (hold Shift to disable)" },
        { "autoTurnIn", "Quest Auto Turn-in (hold Shift to disable)" },
        { "fastLoot", "Fast Autoloot" },
        { "enterConfirm", "Enter Confirm Dialog-Box" },
        { "rangeColor", "Spellicon Range Color" },
        { "whisperDoubleClick", "Whisper Tab Doubleclick Close" },
        { "backspaceDestroy", "Backspace Destroy Select Item" },
        { "squareMinimap", "Square Minimap" },
    }
    for index, feature in ipairs(features) do
        local key = feature[1]
        local checkbox = CreateFrame("CheckButton", nil, window, "UICheckButtonTemplate")
        checkbox:SetPoint("TOPLEFT", 16, -35 - (index - 1) * 36)
        checkbox.Text:SetText(feature[2])
        checkbox:SetScript("OnClick", function(self)
            SetFeatureEnabled(key, self:GetChecked())
        end)
        settingsChecks[key] = checkbox
    end
    local hint = window:CreateFontString(nil, "OVERLAY", "GameFontDisableSmall")
    hint:SetPoint("BOTTOMLEFT", 20, 16)
    hint:SetText("Changes apply immediately and are saved.")
    RefreshSettings()
    window:Show()
end

-- One offer per event: the server supplies QUEST_DETAIL after selection.
local frame = CreateFrame("Frame")
local interactionPaused = false
local interactionNPC
local interactionRevision = 0
local gossipContinuing = false
local interactionTypes = Enum.PlayerInteractionType
local progressRequested
local rewardRequested

local function ResetInteraction()
    interactionPaused = false
    interactionNPC = nil
    gossipContinuing = false
    progressRequested = nil
    rewardRequested = nil
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
        progressRequested = nil
        rewardRequested = nil
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
    if interactionPaused then
        return
    end

    if event == "GOSSIP_SHOW" then
        if settings.autoTurnIn then
            for _, quest in ipairs(C_GossipInfo.GetActiveQuests() or {}) do
                if quest.isComplete and not quest.isIgnored then
                    C_GossipInfo.SelectActiveQuest(quest.questID)
                    return
                end
            end
        end
        if settings.autoAccept then
            for _, quest in ipairs(C_GossipInfo.GetAvailableQuests() or {}) do
                if not quest.isIgnored then
                    C_GossipInfo.SelectAvailableQuest(quest.questID)
                    return
                end
            end
        end
    elseif event == "QUEST_GREETING" then
        -- The older greeting API expects an index, not a quest ID.
        if settings.autoTurnIn then
            for index = 1, GetNumActiveQuests() do
                local _, isComplete = GetActiveTitle(index)
                if isComplete == true or isComplete == 1 then
                    SelectActiveQuest(index)
                    return
                end
            end
        end
        if settings.autoAccept and GetNumAvailableQuests() > 0 then
            SelectAvailableQuest(1)
        end
    elseif event == "QUEST_DETAIL" and settings.autoAccept then
        if QuestGetAutoAccept() then
            CloseQuest()
        elseif not QuestFlagsPVP() then
            -- Leave the default PvP confirmation available for manual use.
            AcceptQuest()
        end
    elseif (event == "QUEST_PROGRESS" or event == "QUEST_COMPLETE") and settings.autoTurnIn and npc then
        local questID = GetQuestID()
        if not questID or questID <= 0 then
            return
        end
        if event == "QUEST_PROGRESS" then
            if IsQuestCompletable() and progressRequested ~= questID then
                progressRequested = questID
                CompleteQuest()
            end
        else
            local numChoices = GetNumQuestChoices()
            local requiredMoney = GetQuestMoneyToGet()
            -- Multiple rewards stay manual; never bypass the native gold
            -- confirmation. Zero/one uses the same index as Blizzard's button.
            if (numChoices == 0 or numChoices == 1) and not (requiredMoney and requiredMoney > 0)
                and rewardRequested ~= questID then
                rewardRequested = questID
                GetQuestReward(numChoices)
            end
        end
    end
end)

SLASH_BETAQOL1 = "/betaqol"
SLASH_BETAQOL2 = "/fqa"
SlashCmdList.BETAQOL = function()
    LoadSettings()
    SetFeatureEnabled("autoAccept", not settings.autoAccept)
    print("Beta Quality of Life: Quest Auto Accept " .. (settings.autoAccept and "on" or "off") .. ". Hold Shift to keep a conversation manual.")
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
    if not settings.fastLoot or lootSession ~= session or not session.autoLoot or session.manual or session.busy then
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
    if not settings.fastLoot then
        return
    end
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
        if not settings.fastLoot then
            return
        end
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
        if settings.fastLoot then
            TryLoot(BeginLoot(arg))
        end
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

featureChanged.fastLoot = function(active)
    if not active then
        lootSession = nil
        -- Let the native close animation finish its secure HideUIPanel cleanup.
        if not nativeLootFrame or not nativeLootFrame.HideAnim:IsPlaying() then
            RestoreLootWindow()
        end
    end
end

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
    if not settings.enterConfirm or not info or info.ignoreKeys or not IsForegroundPopup(dialog) then
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
    if not settings.enterConfirm or not info or info.ignoreKeys or not dialog.GetButton1 then
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

featureChanged.enterConfirm = function(active)
    if active then
        if StaticPopup_ForEachShownDialog then
            StaticPopup_ForEachShownDialog(function(dialog)
                EnablePopupEnter(nil, dialog)
            end)
        end
    else
        for dialog in pairs(popupScripts) do
            RestorePopupScripts(nil, dialog)
        end
    end
end

-- Reuse Blizzard's range updates; no extra polling or action attributes.
local rangeFrame = CreateFrame("Frame")
local rangeButtons = {}
local rangeHooked = false

local function ApplyRangeColor(button, outOfRange)
    local state = rangeButtons[button]
    if not state then
        return
    end
    if settings.rangeColor and outOfRange then
        button.icon:SetVertexColor(1, 0.15, 0.15, state.color[4])
        state.tinted = true
    elseif state.tinted then
        button.icon:SetVertexColor(unpack(state.color))
        state.tinted = false
    end
end

local function RefreshRangeColor(button)
    local inRange
    local action = button.action
    if settings.rangeColor and type(action) == "number"
        and not (issecretvalue and issecretvalue(action)) and action > 0 then
        inRange = C_ActionBar.IsActionInRange(action)
    end
    if issecretvalue and issecretvalue(inRange) then
        ApplyRangeColor(button, false)
    else
        ApplyRangeColor(button, inRange == false)
    end
end

local function HookRangeButton(button)
    if rangeButtons[button] or not button.icon or type(button.UpdateUsable) ~= "function"
        or type(button.Update) ~= "function" then
        return
    end
    local state = { color = { button.icon:GetVertexColor() } }
    rangeButtons[button] = state
    -- Methods are copied from the mixin onto each button, so hook instances.
    hooksecurefunc(button, "UpdateUsable", function(self)
        -- Capture the fresh native color before applying our tint. This keeps
        -- the blue no-mana and gray unusable states when range recovers.
        state.color = { self.icon:GetVertexColor() }
        state.tinted = false
        RefreshRangeColor(self)
    end)
    hooksecurefunc(button, "Update", RefreshRangeColor)
    RefreshRangeColor(button)
end

local function HookActionbarRange()
    if rangeHooked or not ActionBarButtonEventsFrame or not C_ActionBar
        or type(C_ActionBar.IsActionInRange) ~= "function"
        or type(ActionButton_UpdateRangeIndicator) ~= "function" then
        return
    end
    rangeHooked = true
    hooksecurefunc("ActionButton_UpdateRangeIndicator", function(button, checksRange, inRange)
        if (issecretvalue and (issecretvalue(checksRange) or issecretvalue(inRange))) then
            ApplyRangeColor(button, false)
        else
            ApplyRangeColor(button, checksRange == true and inRange == false)
        end
    end)
    hooksecurefunc(ActionBarButtonEventsFrame, "RegisterFrame", function(_, button)
        HookRangeButton(button)
    end)
    ActionBarButtonEventsFrame:ForEachFrame(HookRangeButton)
    rangeFrame:UnregisterEvent("ADDON_LOADED")
    rangeFrame:UnregisterEvent("PLAYER_LOGIN")
end

featureChanged.rangeColor = function()
    for button in pairs(rangeButtons) do
        RefreshRangeColor(button)
    end
end

rangeFrame:RegisterEvent("ADDON_LOADED")
rangeFrame:RegisterEvent("PLAYER_LOGIN")
rangeFrame:SetScript("OnEvent", HookActionbarRange)
HookActionbarRange()

-- Use the client's double-click detection and the context menu's pop-in path.
local whisperFrame = CreateFrame("Frame")
local whisperTabs = {}
local whisperHooked = false

local function AttachWhisperTabs()
    for _, name in pairs(CHAT_FRAMES) do
        local tab = _G[name .. "Tab"]
        if tab and not whisperTabs[tab] then
            local previous = tab:GetScript("OnDoubleClick")
            tab:SetScript("OnDoubleClick", function(self, button, ...)
                local chatFrame = FCF_GetChatFrameByID(self:GetID())
                if settings.whisperDoubleClick and button == "LeftButton" and not MOVING_CHATFRAME
                    and chatFrame and chatFrame.isTemporary and chatFrame.inUse
                    and not IsBuiltinChatWindow(chatFrame)
                    and (chatFrame.chatType == "WHISPER" or chatFrame.chatType == "BN_WHISPER") then
                    -- Restores message routing to the main chat before closing
                    -- and unregistering the temporary conversation window.
                    FCF_PopInWindow(chatFrame)
                    return
                end
                -- Undocked tabs normally minimize on double-click. Keep that
                -- behavior when disabled or when the tab is not a whisper.
                if previous then
                    return previous(self, button, ...)
                end
            end)
            whisperTabs[tab] = true
        end
    end
end

local function HookWhisperTabs()
    if whisperHooked or type(CHAT_FRAMES) ~= "table"
        or type(FCF_OpenTemporaryWindow) ~= "function" or type(FCF_PopInWindow) ~= "function"
        or type(FCF_GetChatFrameByID) ~= "function" or type(IsBuiltinChatWindow) ~= "function" then
        return
    end
    whisperHooked = true
    hooksecurefunc("FCF_OpenTemporaryWindow", AttachWhisperTabs)
    AttachWhisperTabs()
    whisperFrame:UnregisterEvent("ADDON_LOADED")
    whisperFrame:UnregisterEvent("PLAYER_LOGIN")
end

whisperFrame:RegisterEvent("ADDON_LOADED")
whisperFrame:RegisterEvent("PLAYER_LOGIN")
whisperFrame:SetScript("OnEvent", HookWhisperTabs)
HookWhisperTabs()

-- Backspace is intercepted only for a real item picked up from carried bags.
-- Request the native confirmation; never delete directly from this shortcut.
local destroyEvents = CreateFrame("Frame")
local destroyKeys
local backspaceDown = false
local splitCursor = false
local splitHooked = false

local function GetPickedUpBagItemGUID()
    if splitCursor or not CursorHasItem() then
        return
    end
    local location = C_Cursor.GetCursorItem()
    if not location or not location:IsBagAndSlot() then
        return
    end
    local bag = location:GetBagAndSlot()
    local lastBag = NUM_TOTAL_EQUIPPED_BAG_SLOTS or NUM_BAG_SLOTS
    if not lastBag or bag < 0 or bag > lastBag then
        return
    end
    local guid = C_Item.GetItemGUID(location)
    if not (issecretvalue and issecretvalue(guid)) then
        return guid
    end
end

local function UpdateDestroyKeys()
    if not C_Cursor or type(C_Cursor.GetCursorItem) ~= "function" or not C_Item
        or type(C_Item.ConfirmDeleteItem) ~= "function" or type(C_Item.GetItemGUID) ~= "function"
        or not C_Container or type(C_Container.SplitContainerItem) ~= "function" then
        return
    end
    if not splitHooked then
        splitHooked = true
        hooksecurefunc(C_Container, "SplitContainerItem", function()
            -- A location GUID may refer to the original stack. Leave split
            -- quantities to native cursor deletion until the cursor is empty.
            if CursorHasItem() then
                splitCursor = true
                UpdateDestroyKeys()
            end
        end)
    end
    if not CursorHasItem() then
        splitCursor = false
    end
    if not settings.backspaceDestroy or InCombatLockdown() then
        if destroyKeys then
            destroyKeys:Hide()
        end
        backspaceDown = false
        return
    end
    if not destroyKeys then
        destroyKeys = CreateFrame("Frame", nil, UIParent)
        destroyKeys:SetSize(1, 1)
        destroyKeys:SetPoint("CENTER")
        destroyKeys:SetFrameStrata("FULLSCREEN_DIALOG")
        destroyKeys:EnableKeyboard(true)
        destroyKeys:SetScript("OnKeyDown", function(self, key)
            if InCombatLockdown() then
                self:Hide()
                return
            end
            local handled = false
            if settings.backspaceDestroy and key == "BACKSPACE"
                and not GetCurrentKeyBoardFocus()
                and not IsShiftKeyDown() and not IsControlKeyDown() and not IsAltKeyDown() then
                local guid = GetPickedUpBagItemGUID()
                if guid then
                    handled = true
                    if not backspaceDown then
                        backspaceDown = true
                        C_Item.ConfirmDeleteItem(guid)
                    end
                end
            end
            -- ConfirmDeleteItem can synchronously change the cursor. Decide
            -- propagation last so the triggering key stays consumed.
            if not InCombatLockdown() then
                self:SetPropagateKeyboardInput(not handled)
            end
        end)
        destroyKeys:SetScript("OnKeyUp", function(self, key)
            if key == "BACKSPACE" then
                backspaceDown = false
            end
            if not InCombatLockdown() then
                self:SetPropagateKeyboardInput(true)
            end
        end)
    end
    destroyKeys:SetPropagateKeyboardInput(true)
    if GetPickedUpBagItemGUID() then
        destroyKeys:Show()
    else
        destroyKeys:Hide()
        backspaceDown = false
    end
end

featureChanged.backspaceDestroy = UpdateDestroyKeys
for _, event in ipairs({ "CURSOR_CHANGED", "PLAYER_REGEN_DISABLED", "PLAYER_REGEN_ENABLED",
    "PLAYER_ENTERING_WORLD", "PLAYER_LOGIN", "ADDON_LOADED" }) do
    destroyEvents:RegisterEvent(event)
end
destroyEvents:SetScript("OnEvent", UpdateDestroyKeys)
UpdateDestroyKeys()

-- Forever's skin resets the circular mask when rotateMinimap changes.
-- Keep the map geometry and controls intact; hide only the two ring textures.
local minimapEvents = CreateFrame("Frame")
local minimapHooked = false
local minimapActive = false
local changingMinimapMask = false
local normalMinimapMask = "ui-hud-minimap-frame-generic-mask"
local minimapBorderAlpha = {}
local squareMinimapBorder
local minimapMedia = "Interface\\AddOns\\" .. addonName .. "\\Media\\"
local squareMinimapMask = minimapMedia .. "SquareMinimapMask3"
local squareMinimapTexture = minimapMedia .. "SquareMinimapBorder5"
local nativeMinimapRings = { "MinimapCompassTexture", "MinimapCompassTextureUnderlay" }
local previousMinimapShape
local function SquareMinimapShape()
    return "SQUARE"
end

local function SetMinimapMask(mask)
    changingMinimapMask = true
    Minimap:SetMaskTexture(mask)
    changingMinimapMask = false
end

local minimapIcons = {}

local function ReadIconPoints(icon)
    local points = {}
    for index = 1, icon:GetNumPoints() do
        points[index] = { icon:GetPoint(index) }
    end
    return points
end

local function ApplyMinimapIcon(icon, state)
    -- The group-finder button belongs to Edit Mode; defer anchor changes in combat.
    if InCombatLockdown and InCombatLockdown() then
        return
    end
    state.changing = true
    if minimapActive then
        icon:ClearAllPoints()
        icon:SetPoint("CENTER", Minimap, state.corner, state.x, state.y)
        state.applied = true
    elseif state.applied then
        icon:ClearAllPoints()
        for _, point in ipairs(state.points) do
            icon:SetPoint(unpack(point))
        end
        state.applied = false
    end
    state.changing = false
end

local function PositionMinimapIcon(icon, corner, x, y)
    if not icon then
        return
    end
    local state = minimapIcons[icon]
    if not state then
        state = { points = ReadIconPoints(icon), scale = icon:GetScale(), corner = corner, x = x, y = y }
        minimapIcons[icon] = state
        hooksecurefunc(icon, "SetPoint", function()
            if not state.changing then
                local points = ReadIconPoints(icon)
                local scale = icon:GetScale()
                local point = points[1]
                if state.applied and #points == 1 and point[1] == "CENTER"
                    and point[2] == Minimap and point[3] == state.corner then
                    -- Edit Mode reads back our corner anchor while scaling.
                    -- Rescale the saved native offsets, not the square anchor.
                    for _, original in ipairs(state.points) do
                        original[4] = original[4] * state.scale / scale
                        original[5] = original[5] * state.scale / scale
                    end
                else
                    state.points = points
                end
                state.scale = scale
                ApplyMinimapIcon(icon, state)
            end
        end)
    end
    ApplyMinimapIcon(icon, state)
end

local function GetSquareMinimapBorder()
    if not squareMinimapBorder then
        squareMinimapBorder = CreateFrame("Frame", "BetaQoLSquareMinimapBorder", Minimap)
        squareMinimapBorder:SetPoint("TOPLEFT", Minimap, "TOPLEFT", -11, 11)
        squareMinimapBorder:SetPoint("BOTTOMRIGHT", Minimap, "BOTTOMRIGHT", 11, -11)
        squareMinimapBorder:SetFrameLevel(Minimap:GetFrameLevel() + 1)
        squareMinimapBorder:EnableMouse(false)
        local border = squareMinimapBorder:CreateTexture(nil, "OVERLAY")
        border:SetAllPoints()
        border:SetTexture(squareMinimapTexture, "CLAMP", "CLAMP", "LINEAR")
        border:SetSnapToPixelGrid(false)
        border:SetTexelSnappingBias(0)
    end
    return squareMinimapBorder
end

local function HideNativeMinimapRings()
    for _, name in ipairs(nativeMinimapRings) do
        local texture = _G[name]
        if texture then
            if minimapBorderAlpha[texture] == nil then
                minimapBorderAlpha[texture] = texture:GetAlpha()
            end
            -- Alpha survives native Show/Hide calls without changing their state.
            texture:SetAlpha(0)
        end
    end
end

local function RestoreNativeMinimapRings()
    for texture, alpha in pairs(minimapBorderAlpha) do
        texture:SetAlpha(alpha)
    end
    minimapBorderAlpha = {}
end

local function UpdateSquareMinimap()
    if not settingsLoaded or not Minimap or type(Minimap.SetMaskTexture) ~= "function" then
        return
    end
    if not minimapHooked then
        minimapHooked = true
        hooksecurefunc(Minimap, "SetMaskTexture", function(_, mask)
            if changingMinimapMask then
                return
            end
            normalMinimapMask = mask
            if minimapActive then
                SetMinimapMask(squareMinimapMask)
            end
        end)
    end
    if settings.squareMinimap then
        if not minimapActive then
            previousMinimapShape = GetMinimapShape
            GetMinimapShape = SquareMinimapShape
            minimapActive = true
        end
        SetMinimapMask(squareMinimapMask)
        GetSquareMinimapBorder():Show()
        HideNativeMinimapRings()
    elseif minimapActive then
        minimapActive = false
        if squareMinimapBorder then
            squareMinimapBorder:Hide()
        end
        SetMinimapMask(normalMinimapMask)
        RestoreNativeMinimapRings()
        if GetMinimapShape == SquareMinimapShape then
            GetMinimapShape = previousMinimapShape
        end
    end
    PositionMinimapIcon(MinimapCluster and MinimapCluster.DielFrame, "TOPRIGHT", -8, -8)
    PositionMinimapIcon(QueueStatusButton, "BOTTOMLEFT", 11, 11)
end

featureChanged.squareMinimap = UpdateSquareMinimap
minimapEvents:RegisterEvent("ADDON_LOADED")
minimapEvents:RegisterEvent("PLAYER_LOGIN")
minimapEvents:RegisterEvent("PLAYER_ENTERING_WORLD")
minimapEvents:RegisterEvent("PLAYER_REGEN_ENABLED")
minimapEvents:SetScript("OnEvent", UpdateSquareMinimap)
