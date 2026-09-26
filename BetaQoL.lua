-- SPDX-License-Identifier: MIT
-- Copyright (c) 2026 Kirchlive and contributors
-- Target: WoW Forever Beta 1.60.1 (Interface 16001).
local addonName = ... or "BetaQoL"
local settings = {
    autoAccept = true, autoTurnIn = true, fastLoot = true,
    enterConfirm = true, rangeColor = true, whisperDoubleClick = true,
    backspaceDestroy = true,
    backspaceQuestDetails = true,
    squareMinimap = true,
    questNameplateBag = true,
    chatArrowKeys = true,
    shiftEscapeReload = true,
    questLogXP = true,
    questDropRate = true,
    flightMasterInstantMap = true,
    professionArrowKeys = true,
    fasterChatScroll = true,
    lowSpellReminder = true,
    missingSpellCheck = false,
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
    -- Preserve the old reload toggle when moving away from the Windows shortcut.
    if type(BetaQoLDB.shiftEscapeReload) ~= "boolean" and type(BetaQoLDB.ctrlEscapeReload) == "boolean" then
        BetaQoLDB.shiftEscapeReload = BetaQoLDB.ctrlEscapeReload
    end
    BetaQoLDB.ctrlEscapeReload = nil
    -- Removed until a taint-safe damage-meter shortcut is available.
    BetaQoLDB.damageMeterDoubleClick = nil
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
    -- Shared visual templates only: the real Professions/LFG windows stay untouched.
    local window = CreateFrame("Frame", "BetaQoLSettingsFrame", UIParent, "PortraitFrameTemplate")
    settingsWindow = window
    window:SetSize(458, 582)
    window:SetPoint("CENTER")
    window:SetFrameStrata("DIALOG")
    window:SetTitle("Forever Beta Quality of Life")
    window:SetPortraitToAsset("Interface\\AddOns\\BetaQoL\\Media\\Icon")
    local portrait = window:GetPortrait()
    portrait:SetSize(50, 50)
    portrait:ClearAllPoints()
    -- 50x50, one pixel left and two pixels above the native portrait center.
    portrait:SetPoint("TOPLEFT", window.PortraitContainer, "TOPLEFT", 0, 3)
    window:SetClampedToScreen(true)
    window:SetMovable(true)
    window:EnableMouse(true)
    window:RegisterForDrag("LeftButton")
    window:SetScript("OnDragStart", window.StartMoving)
    window:SetScript("OnDragStop", window.StopMovingOrSizing)
    tinsert(UISpecialFrames, "BetaQoLSettingsFrame")
    if type(settings.settingsUI) ~= "table" then settings.settingsUI = {} end
    local ui = settings.settingsUI
    if type(ui.bottomExpanded) ~= "boolean" then ui.bottomExpanded = true end
    if type(ui.showCategories) ~= "boolean" then ui.showCategories = true end

    local features = {
        { "autoAccept", "Quest Auto Accept (shift disable)" },
        { "autoTurnIn", "Quest Auto Turn-in (shift disable)" },
        { "questDropRate", "Quest Item Drop Rate" },
        { "questNameplateBag", "Quest Icon Target Nameplate" },
        { "questLogXP", "Questlog XP (+ item rewards)" },
        { "fastLoot", "Fast Autoloot" },
        { "squareMinimap", "Square Minimap (forever look)" },
        { "rangeColor", "Spellicon Range Color" },
        { "backspaceQuestDetails", "Backspace Leave Quest Details Window" },
        { "backspaceDestroy", "Backspace Destroy Item Dialog" },
        { "enterConfirm", "Enter Confirm Dialog Box" },
        { "chatArrowKeys", "Chatbox Arrow Keys" },
        { "shiftEscapeReload", "Left Shift Escape Reload" },
        { "flightMasterInstantMap", "Flight Master Auto Map (shift disable)" },
        { "whisperDoubleClick", "Whisper Tab Doubleclick Close" },
        { "professionArrowKeys", "Panel Arrow Keys (guild and professions)" },
        { "fasterChatScroll", "Multiline Scroll (chatframe and guild)" },
        { "lowSpellReminder", "Low Spell Rank Check (at launch)" },
        { "missingSpellCheck", "Missing Spell Check (at launch)" },
    }
    -- Descriptions are intentionally separate from labels and saved setting keys.
    local descriptions = {
        autoAccept = { "INV_Misc_Note_01", "Accepts ordinary quests automatically when you speak to an NPC.", "Hold Shift before speaking to keep the conversation manual." },
        autoTurnIn = { "INV_Misc_Note_05", "Turns in completed NPC quests automatically.", "Hold Shift before speaking to keep the conversation manual. Choosing between multiple item rewards and quests requiring gold remain manual." },
        questDropRate = { "INV_Misc_Bag_10", "Shows each quest item's drop rate directly after its name in a creature's tooltip.", "Includes completed item objectives while the quest remains in your quest log. Each item has its own rate; completed objectives appear gray. Unknown drops are omitted." },
        questNameplateBag = { "INV_Misc_Bag_08", "Adds a small bag beside a creature's nameplate when it contributes to one of your unfinished quest objectives.", "Includes item, kill and interaction objectives. The marker disappears when the relevant objectives are complete." },
        questLogXP = { "INV_Misc_Book_11", "Shows the quest's XP reward between its level and title in your quest log.", "Example: [15] (1,350+) Chen's Empty Keg\n\nA + means the quest also offers guaranteed or selectable item rewards." },
        fastLoot = { "INV_Misc_Coin_02", "Speeds up automatic looting and hides the loot window during successful auto-looting.", "Uses your normal auto-loot setting and modifier. Items that need manual handling can still be collected through the normal loot window." },
        squareMinimap = { "INV_Misc_Map_01", "Changes the minimap to a square with rounded corners and a bronze border in the Forever style.", "The day/night icon moves to the top-right and the group-finder eye to the bottom-left. Disabling restores the round minimap and native icon positions." },
        rangeColor = { "Spell_Fire_FlameBolt", "Colors a spell's action-bar icon red when its target is out of range.", "The normal icon color returns when the target is in range again." },
        backspaceQuestDetails = { "INV_Misc_Book_09", "Press Backspace in the quest log's details view to return to the quest list.", "Works outside combat. Typing, modifier keys and picked-up items keep their normal behavior." },
        backspaceDestroy = { "INV_Misc_Bag_07", "Press Backspace while holding an item from your bags to open its normal delete confirmation.", "Works outside combat with whole items or whole stacks. Split stacks are excluded. The item still requires confirmation before deletion." },
        enterConfirm = { "INV_Misc_Note_06", "Press Enter to confirm supported standard popup dialogs.", "The normal confirmation button is used. Any required typed confirmation must still be completed." },
        chatArrowKeys = { "INV_Misc_Note_03", "Use Left and Right to move the cursor in the chat edit box without holding Alt.", "Up and Down recall your recent sent messages. The native Alt shortcuts remain available." },
        shiftEscapeReload = { "Spell_Arcane_PortalOrgrimmar", "Press Left Shift + Escape to reload the user interface.", "Plain Escape keeps its usual behavior. A reload also runs any enabled spell checks again." },
        flightMasterInstantMap = { "Ability_Mount_Wyvern_01", "Opens the flight map automatically when a flight master offers a ride.", "Hold Shift before speaking to keep the entire conversation manual. This opens the map; you still choose your destination." },
        whisperDoubleClick = { "INV_Misc_Note_04", "Double-click a separate whisper tab to close that conversation's chat window.", "Uses the normal whisper-tab close action." },
        professionArrowKeys = { "Trade_BlackSmithing", "Use Up and Down to select recipes in the Professions window or scroll the Guild/Communities chat by three lines.", "Hold a key to repeat after a short initial delay. Text input and modifier keys keep their usual behavior. Works outside combat." },
        fasterChatScroll = { "INV_Misc_ScrollUnrolled01", "Scroll chat by three lines per mousewheel step.", "Applies to normal chat windows. Guild/Communities chat already uses three lines and keeps its native scrolling." },
        lowSpellReminder = { "INV_Misc_Book_07", "At login and reload, compares the highest rank of each spell on your action bars with the highest rank you have learned.", "Only spells already on your action bars are checked. Lower ranks do not trigger a reminder if the highest learned rank is also present. Uses a red BetaQoL prefix. Macros are not inspected." },
        missingSpellCheck = { "INV_Misc_Book_06", "At login and reload, checks for learned spells missing from your action bars, regardless of rank.", "Excludes General and passive spells. Uses a yellow BetaQoL prefix. Only direct spell buttons are checked; spells used solely through macros may still be reported." },
    }
    local categories = {
        { "Quests", { 1, 2, 3, 4, 5 } },
        { "Chat", { 12, 15, 17 } },
        { "Controls", { 16, 9, 10, 11, 13 } },
        { "World & Interface", { 6, 7, 14 } },
        { "Spells", { 8, 18, 19 } },
    }
    local function Label(parent, style, width, text)
        local label = parent:CreateFontString(nil, "OVERLAY", style)
        label:SetWidth(width)
        label:SetJustifyH("LEFT")
        label:SetJustifyV("TOP")
        label:SetWordWrap(true)
        label:SetText(text or "")
        return label
    end
    -- Preserve the portrait/title/border art; recolor only the interior.
    if window.Bg then window.Bg:SetColorTexture(0.055, 0.055, 0.055, 1) end
    if window.TopTileStreaks then window.TopTileStreaks:Hide() end
    local toolbar = window:CreateTexture(nil, "BACKGROUND", nil, 1)
    toolbar:SetPoint("TOPLEFT", 3, -25)
    toolbar:SetPoint("BOTTOMRIGHT", window, "TOPRIGHT", -3, -58)
    toolbar:SetTexture("Interface\\FrameGeneral\\UI-Background-Rock")
    toolbar:SetHorizTile(true)
    toolbar:SetVertTile(true)
    toolbar:SetDesaturated(true)
    toolbar:SetVertexColor(0.5, 0.5, 0.5)

    local search = CreateFrame("EditBox", "BetaQoLSettingsSearchBox", window, "SearchBoxTemplate")
    window.SearchBox = search
    search:SetSize(200, 22)
    search:SetPoint("TOPRIGHT", -16, -32)
    search:SetAutoFocus(false)
    search:SetMaxLetters(100)

    local listPanel = CreateFrame("Frame", nil, window, "InsetFrameTemplate")
    listPanel:SetPoint("TOPLEFT", 4, -58)
    listPanel:SetSize(450, 404)
    local listBackground = listPanel:CreateTexture(nil, "BACKGROUND", nil, 1)
    listBackground:SetPoint("TOPLEFT", 3, -3)
    listBackground:SetPoint("BOTTOMRIGHT", -3, 3)
    listBackground:SetTexture("Interface\\FrameGeneral\\UI-Background-Rock")
    listBackground:SetHorizTile(true)
    listBackground:SetVertTile(true)
    listBackground:SetDesaturated(true)
    listBackground:SetVertexColor(0.3, 0.3, 0.3)

    local scroll = CreateFrame("ScrollFrame", "BetaQoLSettingsListScrollFrame", listPanel, "ScrollFrameTemplate")
    window.ListScroll = scroll
    scroll:SetPoint("TOPLEFT", 12, -10)
    scroll:SetSize(414, 384)
    scroll.ScrollBar:ClearAllPoints()
    scroll.ScrollBar:SetPoint("TOPLEFT", scroll, "TOPRIGHT", 6, 0)
    scroll.ScrollBar:SetPoint("BOTTOMLEFT", scroll, "BOTTOMRIGHT", 6, 0)
    scroll.ScrollBar:SetHideIfUnscrollable(true)
    local content = CreateFrame("Frame", nil, scroll)
    window.ListContent = content
    content:SetSize(414, 384)
    scroll:SetScrollChild(content)
    local empty = Label(content, "GameFontDisable", 390, "No matching features. Try another search.")
    window.EmptyText = empty
    empty:SetPoint("TOPLEFT", 8, -12)

    local rows, headers = {}, {}
    window.FeatureRows, window.CategoryHeaders = rows, headers
    local tooltipOwner
    local function HideFeatureTooltip()
        if tooltipOwner and GameTooltip:IsOwned(tooltipOwner) then GameTooltip:Hide() end
        tooltipOwner = nil
    end
    for _, feature in ipairs(features) do
        local key, title = feature[1], feature[2]
        local info = descriptions[key]
        local row = CreateFrame("Button", nil, content)
        rows[key] = row
        row:SetWidth(396)
        row:SetHighlightAtlas("Professions_Recipe_Hover")
        local function ShowFeatureTooltip(owner)
            tooltipOwner = owner
            GameTooltip:SetOwner(owner, "ANCHOR_RIGHT")
            GameTooltip:SetText(title:gsub("%s*%b()", ""), 1, 0.82, 0)
            GameTooltip:AddLine(info[2], 1, 1, 1, true)
            GameTooltip:AddLine(" ")
            GameTooltip:AddLine(info[3], 0.8, 0.8, 0.8, true)
            GameTooltip:Show()
        end
        row:SetScript("OnEnter", ShowFeatureTooltip)
        row:SetScript("OnLeave", HideFeatureTooltip)
        row:SetScript("OnClick", function() SetFeatureEnabled(key, not settings[key]) end)
        local checkbox = CreateFrame("CheckButton", nil, row, "UICheckButtonTemplate")
        checkbox:SetSize(26, 26)
        checkbox:SetHitRectInsets(0, 0, 2, 2)
        checkbox:SetPoint("LEFT", 0, 0)
        checkbox.Text:ClearAllPoints()
        checkbox.Text:SetPoint("LEFT", checkbox, "RIGHT", 2, 0)
        checkbox.Text:SetWidth(362)
        checkbox.Text:SetFontObject("GameFontNormal")
        checkbox.Text:SetWordWrap(true)
        checkbox.Text:SetJustifyH("LEFT")
        checkbox.Text:SetText((title:gsub("(%b())", "|cff999999%1|r")))
        row:SetHeight(math.max(22, checkbox.Text:GetStringHeight() + 6))
        checkbox:SetScript("OnEnter", ShowFeatureTooltip)
        checkbox:SetScript("OnLeave", HideFeatureTooltip)
        checkbox:SetScript("OnClick", function(self) SetFeatureEnabled(key, self:GetChecked()) end)
        settingsChecks[key] = checkbox
    end
    local collapsed = {}
    local function LayoutList()
        HideFeatureTooltip()
        local query = search:GetText():lower():match("^%s*(.-)%s*$")
        local y, count = 4, 0
        for _, category in ipairs(categories) do
            local name, matches = category[1], {}
            for _, index in ipairs(category[2]) do
                local feature = features[index]
                local key = feature[1]
                if query == "" or (name .. " " .. feature[2]):lower():find(query, 1, true) then
                    matches[#matches + 1] = key
                end
                rows[key]:Hide()
            end
            local header = headers[name]
            header:SetShown(ui.showCategories and #matches > 0)
            if #matches > 0 then
                if ui.showCategories then
                    header:ClearAllPoints()
                    header:SetPoint("TOPLEFT", 0, -y)
                    y = y + 22
                end
                local isCollapsed = ui.showCategories and query == "" and collapsed[name] == true
                if not isCollapsed then
                    for _, key in ipairs(matches) do
                        local row = rows[key]
                        row:ClearAllPoints()
                        row:SetPoint("TOPLEFT", 18, -y)
                        row:Show()
                        y = y + row:GetHeight()
                    end
                end
                if ui.showCategories then y = y + 8 end
                count = count + #matches
            end
        end
        empty:SetShown(count == 0)
        content:SetHeight(math.max(scroll:GetHeight(), y))
        scroll:SetVerticalScroll(math.min(scroll:GetVerticalScroll(), math.max(0, y - scroll:GetHeight())))
    end
    for _, category in ipairs(categories) do
        local name = category[1]
        local header = CreateFrame("Button", nil, content)
        headers[name] = header
        header:SetSize(414, 22)
        header.Title = Label(header, "GameFontHighlight", 400, name)
        header.Title:SetPoint("LEFT", 4, 0)
        header.Title:SetTextColor(0.65, 0.65, 0.65)
        header:SetScript("OnClick", function()
            -- Search expands matches without changing the saved collapse choice.
            if search:GetText():match("%S") then return end
            collapsed[name] = not collapsed[name]
            LayoutList()
        end)
        header:SetScript("OnEnter", function() header.Title:SetTextColor(1, 1, 1) end)
        header:SetScript("OnLeave", function() header.Title:SetTextColor(0.65, 0.65, 0.65) end)
    end
    scroll:HookScript("OnVerticalScroll", HideFeatureTooltip)
    search:HookScript("OnTextChanged", function() scroll:SetVerticalScroll(0); LayoutList() end)
    window:SetScript("OnHide", function() search:ClearFocus(); HideFeatureTooltip() end)
    local function FitWindow()
        window:SetScale(math.min(1, (UIParent:GetWidth() - 32) / 458, (UIParent:GetHeight() - 32) / 582))
    end
    window:SetScript("OnShow", function() FitWindow(); RefreshSettings() end)
    window:RegisterEvent("DISPLAY_SIZE_CHANGED")
    window:RegisterEvent("UI_SCALE_CHANGED")
    window:SetScript("OnEvent", function() if window:IsShown() then FitWindow() end end)

    -- One continuous footer texture reaches the bottom border, including the version.
    -- Keep existing layout preferences, but hide the retired layout controls.
    local footer = CreateFrame("Frame", nil, window)
    window.FooterPanel = footer
    footer:SetPoint("BOTTOMLEFT", 4, 4)
    footer:SetSize(450, 116)
    local footerBackground = window:CreateTexture(nil, "BACKGROUND", nil, 1)
    footerBackground:SetAllPoints(footer)
    footerBackground:SetTexture("Interface\\FrameGeneral\\UI-Background-Rock")
    footerBackground:SetHorizTile(true)
    footerBackground:SetVertTile(true)
    footerBackground:SetDesaturated(true)
    footerBackground:SetVertexColor(0.18, 0.18, 0.18)
    local divider = footer:CreateTexture(nil, "OVERLAY")
    divider:SetPoint("TOPLEFT")
    divider:SetPoint("TOPRIGHT")
    divider:SetHeight(8)
    divider:SetAtlas("shop-list-rule")
    local hint = Label(footer, "GameFontDisableSmall", 414, "Changes are saved automatically.")
    hint:SetPoint("TOPLEFT", 12, -22)
    local help = Label(footer, "GameFontDisableSmall", 414, "Hover a feature for details.")
    help:SetPoint("TOPLEFT", 12, -42)

    local function FooterButton(x, text, tooltipText)
        local button = CreateFrame("Button", nil, window, "UIPanelButtonTemplate")
        button:SetSize(24, 22)
        button:SetPoint("BOTTOMLEFT", x, 8)
        button:SetText(text)
        button:SetScript("OnEnter", function(self)
            tooltipOwner = self
            GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
            GameTooltip:SetText(tooltipText(), 1, 0.82, 0)
            GameTooltip:Show()
        end)
        button:SetScript("OnLeave", HideFeatureTooltip)
        return button
    end
    local footerToggle = FooterButton(16, "-", function()
        return ui.bottomExpanded and "Collapse bottom bar" or "Expand bottom bar"
    end)
    local categoryToggle = FooterButton(44, "T", function()
        return ui.showCategories and "Hide category headings" or "Show category headings"
    end)
    window.FooterToggle, window.CategoryToggle = footerToggle, categoryToggle
    local function UpdateLayout()
        local bottomHeight = ui.bottomExpanded and 120 or 37
        footer:SetShown(ui.bottomExpanded)
        footerBackground:SetShown(ui.bottomExpanded)
        listPanel:SetHeight(window:GetHeight() - 58 - bottomHeight)
        scroll:SetHeight(listPanel:GetHeight() - 20)
        footerToggle:SetText(ui.bottomExpanded and "-" or "+")
        categoryToggle:SetNormalFontObject(ui.showCategories and "GameFontNormalSmall" or "GameFontDisableSmall")
        LayoutList()
    end
    footerToggle:SetScript("OnClick", function()
        if not footerToggle:IsEnabled() then return end
        ui.bottomExpanded = not ui.bottomExpanded
        UpdateLayout()
    end)
    categoryToggle:SetScript("OnClick", function()
        if not categoryToggle:IsEnabled() then return end
        ui.showCategories = not ui.showCategories
        UpdateLayout()
    end)
    footerToggle:SetEnabled(false)
    categoryToggle:SetEnabled(false)
    footerToggle:Hide()
    categoryToggle:Hide()
    local version = window:CreateFontString(nil, "OVERLAY", "GameFontDisableSmall")
    version:SetPoint("BOTTOMRIGHT", -16, 17)
    local getMetadata = C_AddOns and C_AddOns.GetAddOnMetadata or GetAddOnMetadata
    version:SetText(getMetadata and getMetadata(addonName, "Version") or "")
    UpdateLayout()
    RefreshSettings()
    FitWindow()
    window:Show()
end

-- Set the actual chat-frame wheel step, regardless of its previous handler.
-- Communities already uses three; no shared ScrollUtil methods are replaced.
do
    local events = CreateFrame("Frame")
    local originals, hooks = {}, {}
    local function ScrollThreeLines(frame, delta)
        if frame:GetInsertMode() == SCROLLING_MESSAGE_FRAME_INSERT_MODE_TOP then delta = -delta end
        frame:ScrollByAmount(delta * 3)
    end
    local function UpdateChatScroll()
        if not settingsLoaded then return end
        if not settings.fasterChatScroll then
            for frame, original in pairs(originals) do
                if frame:GetScript("OnMouseWheel") == ScrollThreeLines then frame:SetScript("OnMouseWheel", original) end
                originals[frame] = nil
            end
            return
        end
        for _, name in pairs(CHAT_FRAMES or {}) do
            local frame = _G[name]
            if frame and frame.ScrollByAmount and frame.GetInsertMode then
                local current = frame:GetScript("OnMouseWheel")
                if current and current ~= ScrollThreeLines and not originals[frame] then
                    originals[frame] = current
                    frame:SetScript("OnMouseWheel", ScrollThreeLines)
                end
            end
        end
    end
    local function HookChatScroll()
        for _, name in ipairs({ "FCF_OpenNewWindow", "FCF_OpenTemporaryWindow" }) do
            if not hooks[name] and type(_G[name]) == "function" then
                hooksecurefunc(name, UpdateChatScroll)
                hooks[name] = true
            end
        end
        UpdateChatScroll()
    end
    featureChanged.fasterChatScroll = HookChatScroll
    for _, event in ipairs({ "ADDON_LOADED", "PLAYER_LOGIN", "UPDATE_CHAT_WINDOWS" }) do events:RegisterEvent(event) end
    events:SetScript("OnEvent", HookChatScroll)
end

-- Read the player's own book and direct spell actions once after login/reload.
-- No combat callbacks, actionbar changes, rank database, or frame hooks.
do
    local events = CreateFrame("Frame")
    local pending, queued = false, false
    local function CheckActionBarSpells()
        queued = false
        if not pending then return end
        if InCombatLockdown and InCombatLockdown() then return end
        pending = false
        if not settingsLoaded or not (settings.lowSpellReminder or settings.missingSpellCheck) then return end
        local book = C_SpellBook
        if not book or not book.GetNumSpellBookSkillLines or not book.GetSpellBookSkillLineInfo
            or not book.GetSpellBookItemInfo or not book.IsSpellBookItemLowRank
            or not C_ActionBar or not C_ActionBar.FindSpellActionButtons
            or not GetActionInfo or not Enum.SpellBookSpellBank or not Enum.SpellBookItemType then return end
        if not Enum.ActionBarSet then return end
        local bank = Enum.SpellBookSpellBank.Player
        local general = Enum.SpellBookSkillLineIndex and Enum.SpellBookSkillLineIndex.General
        local families, ordered, byID, lookupIDs = {}, {}, {}, {}
        for lineIndex = 1, book.GetNumSpellBookSkillLines() do
            local line = book.GetSpellBookSkillLineInfo(lineIndex)
            if line and not line.offSpecID then
                for index = line.itemIndexOffset + 1, line.itemIndexOffset + line.numSpellBookItems do
                    local info = book.GetSpellBookItemInfo(index, bank)
                    if info and info.itemType == Enum.SpellBookItemType.Spell
                        and not info.isPassive and not info.isOffSpec and info.spellID and info.name then
                        local family = families[info.name]
                        if not family then
                            family = {}
                            families[info.name] = family
                            ordered[#ordered + 1] = family
                        end
                        local low = book.IsSpellBookItemLowRank(index, bank)
                        if general and lineIndex ~= general then family.outsideGeneral = true end
                        byID[info.spellID] = { family = family, low = low }
                        lookupIDs[info.actionID or info.spellID] = true
                        if not low then family.highest = info end
                    end
                end
            end
        end
        -- FindSpellActionButtons supplies candidates, not proof of an exact rank.
        -- Exclude separate gamepad storage, which may retain starter spell ranks.
        local checked = {}
        for id in pairs(lookupIDs) do
            local slots = C_ActionBar.FindSpellActionButtons(id, Enum.ActionBarSet.Mkb)
            for _, slot in ipairs(slots or {}) do
                if not checked[slot] then
                    checked[slot] = true
                    local kind, actionID = GetActionInfo(slot)
                    local rank = kind == "spell" and byID[actionID]
                    if rank then
                        rank.family.present = true
                        if not rank.low then rank.family.highestPresent = true end
                    end
                end
            end
        end
        -- A family needs an upgrade only if it is on a bar and every placed
        -- rank is below its highest learned rank. Intentional lower copies are fine.
        for _, family in ipairs(ordered) do
            if settings.lowSpellReminder and family.present and family.highest and not family.highestPresent then
                local info = family.highest
                local rank = info.subName and info.subName ~= "" and (" " .. info.subName) or ""
                print("|cffff0000BetaQoL:|r " .. info.name .. rank
                    .. " available. Check your spellbook.")
            end
            if settings.missingSpellCheck and family.outsideGeneral and family.highest and not family.present then
                print("|cffffd100BetaQoL:|r " .. family.highest.name .. " not in actionbar.")
            end
        end
    end
    events:RegisterEvent("PLAYER_ENTERING_WORLD")
    events:RegisterEvent("PLAYER_REGEN_ENABLED")
    events:SetScript("OnEvent", function(_, event, initialLogin, reloadingUI)
        if event == "PLAYER_ENTERING_WORLD" and (initialLogin or reloadingUI) then pending = true end
        if pending and not queued then
            queued = true
            C_Timer.After(1, CheckActionBarSpells)
        end
    end)
end

-- Observe physical modifier events: the live client returned false from the left-Shift query.
do
    local events = CreateFrame("Frame")
    local keys
    local escapeDown = false
    local leftShiftDown = false
    local function UpdateReloadKeys()
        if not settingsLoaded or type(ReloadUI) ~= "function" then return end
        if not settings.shiftEscapeReload then
            if keys then keys:Hide() end
            escapeDown = false
            return
        end
        if not keys then
            -- Keyboard propagation is protected; initialize it outside combat.
            if InCombatLockdown() then return end
            keys = CreateFrame("Frame", nil, UIParent)
            keys:SetSize(1, 1)
            keys:SetPoint("CENTER")
            keys:SetFrameStrata("FULLSCREEN_DIALOG")
            keys:EnableKeyboard(true)
            -- Observation only: ordinary Escape and all other keys retain their routing.
            keys:SetPropagateKeyboardInput(true)
            keys:SetScript("OnKeyDown", function(_, key)
                if key == "LSHIFT" then leftShiftDown = true; return end
                if key ~= "ESCAPE" then return end
                if not escapeDown and settings.shiftEscapeReload and leftShiftDown
                    and not IsControlKeyDown() and not IsAltKeyDown() then
                    -- Native Escape can redirect key-up to another panel. Only
                    -- latch a reload attempt, never an ordinary Escape press.
                    escapeDown = true
                    ReloadUI()
                end
            end)
            keys:SetScript("OnKeyUp", function(_, key)
                if key == "LSHIFT" then leftShiftDown = false end
                if key == "ESCAPE" then escapeDown = false end
            end)
            keys:SetScript("OnHide", function() escapeDown = false end)
        end
        keys:Show()
    end
    featureChanged.shiftEscapeReload = UpdateReloadKeys
    events:RegisterEvent("PLAYER_LOGIN")
    events:RegisterEvent("PLAYER_REGEN_ENABLED")
    events:RegisterEvent("MODIFIER_STATE_CHANGED")
    events:SetScript("OnEvent", function(_, event, key, state)
        if event == "MODIFIER_STATE_CHANGED" then
            if key == "LSHIFT" then leftShiftDown = state == 1 end
        else
            UpdateReloadKeys()
        end
    end)
end

-- Extend the native prefix before WoW measures and lays out each quest row.
local questXPFrame = CreateFrame("Frame")
local questXPHooked = false
local questXPRefreshPending = false

local function HasQuestRewardItems(countFunction, questID)
    if type(countFunction) ~= "function" then return false end
    -- Choice counts omit currencies by default, as in the native item tooltip.
    local ok, count = pcall(countFunction, questID)
    return ok and not (issecretvalue and issecretvalue(count))
        and type(count) == "number" and count > 0
end

local function RefreshQuestXP()
    if questXPRefreshPending or not QuestScrollFrame or not QuestScrollFrame:IsVisible()
        or type(QuestLogQuests_Update) ~= "function" then
        return
    end
    questXPRefreshPending = true
    C_Timer.After(0, function()
        questXPRefreshPending = false
        if QuestScrollFrame and QuestScrollFrame:IsVisible() then
            QuestLogQuests_Update()
        end
    end)
end

local function HookQuestXP()
    if not settingsLoaded or questXPHooked or not QuestMapFrameOverrides
        or type(QuestMapFrameOverrides.GetQuestTitlePrefix) ~= "function" then
        return
    end
    local nativePrefix = QuestMapFrameOverrides.GetQuestTitlePrefix
    QuestMapFrameOverrides.GetQuestTitlePrefix = function(info)
        local prefix = nativePrefix(info)
        if not settings.questLogXP or info.isHeader or not info.questID
            or type(GetQuestLogRewardXP) ~= "function" then
            return prefix
        end
        if C_QuestLog.ShouldShowQuestRewards and not C_QuestLog.ShouldShowQuestRewards(info.questID) then
            return prefix
        end
        if HaveQuestRewardData and not HaveQuestRewardData(info.questID) then
            return prefix
        end
        -- The explicit quest ID keeps the selected quest and details unchanged.
        local ok, xp = pcall(GetQuestLogRewardXP, info.questID)
        if not ok or (issecretvalue and issecretvalue(xp)) or type(xp) ~= "number"
            or xp < 0 or xp ~= xp or xp == math.huge then
            return prefix
        end
        local hasItems = HasQuestRewardItems(GetNumQuestLogRewards, info.questID)
            or HasQuestRewardItems(GetNumQuestLogChoices, info.questID)
        return (prefix or "") .. "(" .. BreakUpLargeNumbers(xp) .. (hasItems and "+" or "") .. ") "
    end
    questXPHooked = true
    questXPFrame:UnregisterEvent("ADDON_LOADED")
    RefreshQuestXP()
end

featureChanged.questLogXP = function()
    HookQuestXP()
    RefreshQuestXP()
end
questXPFrame:RegisterEvent("ADDON_LOADED")
questXPFrame:RegisterEvent("QUEST_DATA_LOAD_RESULT")
questXPFrame:RegisterEvent("PLAYER_LEVEL_UP")
questXPFrame:SetScript("OnEvent", function(_, event)
    if event == "ADDON_LOADED" then
        HookQuestXP()
    elseif settingsLoaded and settings.questLogXP then
        RefreshQuestXP()
    end
end)

-- Native edit-box arrow handling only consumes keys while the box has focus.
local chatArrowModes = {}
local chatArrowHooks = {}
local chatArrowFrame = CreateFrame("Frame")
local chatHistories = {}
local chatDraftAttributes = { "chatType", "tellTarget", "channelTarget" }

local function AttachChatHistory(box)
    if chatHistories[box] or not box.AddHistoryLine or not box.HookScript then
        return
    end
    local history = { lines = {} }
    chatHistories[box] = history
    local function ResetSelection()
        history.index, history.draft, history.context = nil, nil, nil
    end
    hooksecurefunc(box, "AddHistoryLine", function(_, text)
        ResetSelection()
        if (issecretvalue and issecretvalue(text)) or type(text) ~= "string" then
            return
        end
        text = text:match("^%s*(.-)%s*$")
        if text == "" then return end
        local command = text:match("^(/%S+)")
        -- Re-inserting protected commands through addon code can taint execution.
        if command and (not IsSecureCmd or IsSecureCmd(command:upper())) then
            return
        end
        local lines = history.lines
        if lines[#lines] ~= text then
            lines[#lines + 1] = text
        end
        local limit = math.min(32, box:GetHistoryLines())
        while #lines > limit do table.remove(lines, 1) end
    end)
    if box.ClearHistory then
        hooksecurefunc(box, "ClearHistory", function()
            history.lines = {}
            ResetSelection()
        end)
    end
    box:HookScript("OnEditFocusGained", ResetSelection)
    box:HookScript("OnEditFocusLost", ResetSelection)
    box:HookScript("OnTextChanged", function(_, userInput)
        if userInput then ResetSelection() end
    end)
    box:HookScript("OnArrowPressed", function(self, key)
        if not settings.chatArrowKeys or not self:HasFocus()
            or (key ~= "UP" and key ~= "DOWN")
            or (IsAltKeyDown and IsAltKeyDown())
            or (IsControlKeyDown and IsControlKeyDown()) or IsShiftKeyDown()
            or (AutoCompleteBox and AutoCompleteBox.parent == self and AutoCompleteBox:IsShown()) then
            return
        end
        local count = #history.lines
        if count == 0 then return end
        if not history.index then
            if key == "DOWN" then return end
            local draft = self:GetText()
            if issecretvalue and issecretvalue(draft) then return end
            local command = draft:match("^%s*(/%S+)")
            if command and (not IsSecureCmd or IsSecureCmd(command:upper())) then return end
            history.draft, history.index = draft, count + 1
            history.context = {
                source = self.autoCompleteSource,
                params = self.autoCompleteParams,
            }
            for _, attribute in ipairs(chatDraftAttributes) do
                history.context[attribute] = self:GetAttribute(attribute)
            end
        end
        history.index = math.max(1, math.min(count + 1, history.index + (key == "UP" and -1 or 1)))
        local restoringDraft = history.index == count + 1
        if restoringDraft then
            -- Recalled slash prefixes change the destination in native SetText.
            -- Restore it too, so a whisper draft cannot become a public message.
            for _, attribute in ipairs(chatDraftAttributes) do
                self:SetAttribute(attribute, history.context[attribute])
            end
            self.autoCompleteSource = history.context.source
            self.autoCompleteParams = history.context.params
        end
        local text = history.lines[history.index] or history.draft
        self:SetText(text)
        self:SetCursorPosition(#self:GetText())
        if restoringDraft then
            self:UpdateHeader()
            ResetSelection()
        end
    end)
end

local function ApplyChatArrowKeys()
    if not settingsLoaded then
        return
    end
    for _, name in pairs(CHAT_FRAMES or {}) do
        local chat = _G[name]
        local box = chat and chat.editBox
        if box and box.GetAltArrowKeyMode and box.SetAltArrowKeyMode then
            AttachChatHistory(box)
            local completing = AutoCompleteBox and AutoCompleteBox.parent == box
            if settings.chatArrowKeys and chatArrowModes[box] == nil then
                local original = box:GetAltArrowKeyMode()
                if completing and type(AutoCompleteBox.parentArrows) == "boolean" then
                    original = AutoCompleteBox.parentArrows
                end
                chatArrowModes[box] = original
            end
            local original = chatArrowModes[box]
            if original ~= nil then
                local mode = not settings.chatArrowKeys and original
                -- Autocomplete temporarily owns the arrows. Update its saved
                -- mode so closing the suggestions restores the current choice.
                if completing then
                    AutoCompleteBox.parentArrows = mode
                    box:SetAltArrowKeyMode(false)
                else
                    box:SetAltArrowKeyMode(mode)
                end
                if not settings.chatArrowKeys then
                    chatArrowModes[box] = nil
                    local history = chatHistories[box]
                    if history then history.index, history.draft, history.context = nil, nil, nil end
                end
            end
        end
    end
end

local function HookChatArrowKeys()
    for _, name in ipairs({ "FCF_OpenNewWindow", "FCF_OpenTemporaryWindow" }) do
        if not chatArrowHooks[name] and type(_G[name]) == "function" then
            hooksecurefunc(name, ApplyChatArrowKeys)
            chatArrowHooks[name] = true
        end
    end
    ApplyChatArrowKeys()
end

featureChanged.chatArrowKeys = HookChatArrowKeys
chatArrowFrame:RegisterEvent("ADDON_LOADED")
chatArrowFrame:RegisterEvent("PLAYER_LOGIN")
chatArrowFrame:SetScript("OnEvent", HookChatArrowKeys)

-- One offer per event: the server supplies QUEST_DETAIL after selection.
local frame = CreateFrame("Frame")
local interactionPaused = false
local interactionNPC
local interactionRevision = 0
local gossipContinuing = false
local interactionTypes = Enum.PlayerInteractionType
local progressRequested
local rewardRequested
local flightMapRequested = false

local function ResetInteraction()
    interactionPaused = false
    interactionNPC = nil
    gossipContinuing = false
    progressRequested = nil
    rewardRequested = nil
    flightMapRequested = false
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
        flightMapRequested = false
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
        if settings.flightMasterInstantMap and not flightMapRequested and npc
            and C_GossipInfo.GetOptions and C_GossipInfo.SelectOptionByIndex
            and Enum.GossipOptionStatus then
            for _, option in ipairs(C_GossipInfo.GetOptions() or {}) do
                -- TaxiGossipIcon: identify the service independently of locale.
                -- Use the server's orderIndex, just like the native gossip button.
                if option.icon == 132057 and option.status == Enum.GossipOptionStatus.Available
                    and type(option.orderIndex) == "number" and option.orderIndex >= 0 then
                    flightMapRequested = true
                    C_GossipInfo.SelectOptionByIndex(option.orderIndex)
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

-- Damage-meter switching is suspended after reproducible persistent taint.
-- Do not attach scripts/hooks to native meter windows, even for saved enabled settings.

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

-- A child of the native Back button only receives input while details are visible.
do
    local events = CreateFrame("Frame")
    local keys, attachedButton
    local function UpdateQuestBackKeys()
        if InCombatLockdown and InCombatLockdown() then
            if keys then keys:Hide() end
            return
        end
        local details = QuestMapFrame and QuestMapFrame.DetailsFrame
        local button = details and details.BackFrame and details.BackFrame.BackButton
        if not settings.backspaceQuestDetails or not button then
            if keys then keys:Hide() end
            return
        end
        if not keys or attachedButton ~= button then
            if keys then keys:Hide() end
            attachedButton = button
            keys = CreateFrame("Frame", nil, button)
            keys:SetSize(1, 1)
            keys:SetPoint("CENTER")
            keys:EnableKeyboard(true)
            keys:SetScript("OnKeyDown", function(self, key)
                if InCombatLockdown() then
                    self:Hide()
                    return
                end
                local handled = settings.backspaceQuestDetails and key == "BACKSPACE"
                    and button:IsVisible() and button:IsEnabled()
                    and not GetCurrentKeyBoardFocus() and not CursorHasItem()
                    and not IsShiftKeyDown() and not IsControlKeyDown() and not IsAltKeyDown()
                -- Consume before the native click hides the details and this child.
                self:SetPropagateKeyboardInput(not handled)
                if handled then button:Click() end
            end)
            keys:SetScript("OnKeyUp", function(self)
                if not InCombatLockdown() then self:SetPropagateKeyboardInput(true) end
            end)
        end
        keys:SetPropagateKeyboardInput(true)
        keys:Show()
    end
    featureChanged.backspaceQuestDetails = UpdateQuestBackKeys
    for _, event in ipairs({ "ADDON_LOADED", "PLAYER_LOGIN", "PLAYER_REGEN_DISABLED", "PLAYER_REGEN_ENABLED" }) do
        events:RegisterEvent(event)
    end
    events:SetScript("OnEvent", UpdateQuestBackKeys)
end

-- Shared arrow repeat for native recipe selection and guild chat scrolling.
do
    local events = CreateFrame("Frame")
    local controllers = {}
    local function GetTargets()
        local page = ProfessionsFrame and ProfessionsFrame.CraftingPage
        local chat = CommunitiesFrame and CommunitiesFrame.Chat
        return page and page.RecipeList, chat and chat.MessageFrame
    end
    local function GetActiveTarget()
        local recipes, guild = GetTargets()
        local recipesVisible = recipes and recipes:IsVisible()
        local guildVisible = guild and guild:IsVisible()
        if recipesVisible and guildVisible then
            local recipeLevel = ProfessionsFrame.GetFrameLevel and ProfessionsFrame:GetFrameLevel() or 0
            local guildLevel = CommunitiesFrame.GetFrameLevel and CommunitiesFrame:GetFrameLevel() or 0
            return guildLevel > recipeLevel and guild or recipes
        end
        return recipesVisible and recipes or guildVisible and guild or nil
    end
    local function CanNavigate(target)
        return settings.professionArrowKeys and not InCombatLockdown()
            and target == GetActiveTarget() and not GetCurrentKeyBoardFocus()
            and not IsShiftKeyDown() and not IsControlKeyDown() and not IsAltKeyDown()
    end
    local function FindAdjacentRecipe(list, direction)
        local scroll, selection = list.ScrollBox, list.selectionBehavior
        if not scroll or not selection or not scroll:HasDataProvider() then return end
        local recipes, selectedIndex = {}, nil
        -- EntireRange includes collapsed branches; ordinary enumeration does not.
        for _, node in scroll:EnumerateDataProvider() do
            local data = node:GetData()
            if data.recipeInfo and not data.isDivider then
                recipes[#recipes + 1] = data.recipeInfo
                if selection:IsElementDataSelected(node) then selectedIndex = #recipes end
            end
        end
        if #recipes == 0 then return end
        if not selectedIndex then return recipes[1] end
        local nextIndex = selectedIndex + direction
        if nextIndex < 1 or nextIndex > #recipes then return nil, true end
        return recipes[nextIndex], true
    end
    local function CreateArrowController(target, kind)
        -- Recipes keep native stepper timings; guild navigation repeats twice as fast.
        local initialDelay = kind == "guild" and 0.25 or 0.5
        local repeatInterval = kind == "guild" and 0.05 or 0.1
        local keys = CreateFrame("Frame", nil, target)
        local heldKey, remaining
        keys:SetSize(1, 1)
        keys:SetPoint("CENTER")
        keys:EnableKeyboard(true)
        local function StopRepeat()
            heldKey, remaining = nil, nil
            keys:SetScript("OnUpdate", nil)
            if not InCombatLockdown() then keys:SetPropagateKeyboardInput(true) end
        end
        local function GetStep(key)
            if kind == "guild" then
                if not target.ScrollByAmount then return end
                return key == "UP" and 3 or -3, true
            end
            return FindAdjacentRecipe(target, key == "UP" and -1 or 1)
        end
        local function ApplyStep(step)
            if kind == "guild" then target:ScrollByAmount(step)
            else target:SelectRecipe(step, true) end
        end
        local function RepeatStep(self, elapsed)
            if not heldKey or not CanNavigate(target)
                or (IsKeyDown and IsKeyDown(heldKey) == false) then
                StopRepeat()
                return
            end
            remaining = remaining - elapsed
            if remaining > 0 then return end
            -- At most one step per frame; never catch up with a burst after a stall.
            remaining = repeatInterval
            local step, atBoundary = GetStep(heldKey)
            if step then ApplyStep(step)
            elseif not atBoundary then StopRepeat() end
        end
        keys:SetScript("OnKeyDown", function(self, key)
            if (key ~= "UP" and key ~= "DOWN") or not CanNavigate(target) then
                StopRepeat()
                return
            end
            -- Ignore OS key-repeat events; our timer owns repeat speed and delay.
            if heldKey == key then self:SetPropagateKeyboardInput(false); return end
            local step, atBoundary = GetStep(key)
            if not step and not atBoundary then StopRepeat(); return end
            heldKey, remaining = key, initialDelay
            self:SetPropagateKeyboardInput(false)
            self:SetScript("OnUpdate", RepeatStep)
            if step then ApplyStep(step) end
        end)
        keys:SetScript("OnKeyUp", function(_, key)
            if heldKey == key then StopRepeat() end
        end)
        keys:SetScript("OnHide", StopRepeat)
        keys:SetPropagateKeyboardInput(true)
        return { target = target, keys = keys, stop = StopRepeat }
    end
    local function UpdateInterfaceKeys()
        if not settingsLoaded or not settings.professionArrowKeys
            or (InCombatLockdown and InCombatLockdown()) then
            for _, controller in pairs(controllers) do
                controller.stop()
                controller.keys:Hide()
            end
            return
        end
        local recipes, guild = GetTargets()
        for _, kind in ipairs({ "recipes", "guild" }) do
            local target
            if kind == "recipes" then target = recipes else target = guild end
            local controller = controllers[kind]
            if controller and controller.target ~= target then
                controller.stop()
                controller.keys:Hide()
                controllers[kind] = nil
                controller = nil
            end
            if target then
                if not controller then
                    controller = CreateArrowController(target, kind)
                    controllers[kind] = controller
                end
                controller.keys:Show()
            end
        end
    end
    featureChanged.professionArrowKeys = UpdateInterfaceKeys
    for _, event in ipairs({ "ADDON_LOADED", "PLAYER_LOGIN", "PLAYER_REGEN_DISABLED", "PLAYER_REGEN_ENABLED" }) do
        events:RegisterEvent(event)
    end
    events:SetScript("OnEvent", UpdateInterfaceKeys)
end

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

-- A plain addon-owned button opens the same settings window as /qol.
-- Native minimap frames and their click handlers remain untouched.
local addonMinimapButton
local function UpdateAddonMinimapButton()
    if InCombatLockdown() then return end
    if not addonMinimapButton then
        local button = CreateFrame("Button", "BetaQoLMinimapButton", Minimap)
        addonMinimapButton = button
        button:SetSize(32, 32)
        button:SetFrameLevel(Minimap:GetFrameLevel() + 5)
        button:RegisterForClicks("LeftButtonUp")
        local background = button:CreateTexture(nil, "BACKGROUND")
        background:SetSize(25, 25)
        background:SetPoint("TOPLEFT", 3, -4)
        background:SetTexture("Interface\\Minimap\\UI-Minimap-Background")
        local icon = button:CreateTexture(nil, "ARTWORK")
        button.Icon = icon
        icon:SetSize(20, 20)
        icon:SetPoint("TOPLEFT", 7, -6)
        icon:SetTexture(132849) -- INV_Elemental_Primal_Mana, already supplied by the client.
        icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
        local border = button:CreateTexture(nil, "OVERLAY")
        border:SetSize(54, 54)
        border:SetPoint("TOPLEFT")
        border:SetTexture("Interface\\Minimap\\MiniMap-TrackingBorder")
        button:SetHighlightTexture("Interface\\Minimap\\UI-Minimap-ZoomButton-Highlight", "ADD")
        local function HideTooltip(self)
            if GameTooltip and GameTooltip:IsOwned(self) then GameTooltip:Hide() end
        end
        button:SetScript("OnClick", function(self, mouseButton)
            if mouseButton ~= "LeftButton" then return end
            HideTooltip(self)
            SlashCmdList.QOL()
        end)
        button:SetScript("OnEnter", function(self)
            GameTooltip:SetOwner(self, "ANCHOR_LEFT")
            GameTooltip:SetText("Forever Beta Quality of Life", 1, 0.82, 0)
            GameTooltip:AddLine("Click to open or close settings.", 1, 1, 1)
            GameTooltip:Show()
        end)
        button:SetScript("OnLeave", HideTooltip)
        button:SetScript("OnHide", HideTooltip)
    end
    -- Leave the native bottom-right zoom controls accessible.
    local inset = settings.squareMinimap and 8 or 14
    addonMinimapButton:ClearAllPoints()
    addonMinimapButton:SetPoint("CENTER", Minimap, "RIGHT", -inset, -32)
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
    UpdateAddonMinimapButton()
end

featureChanged.squareMinimap = UpdateSquareMinimap
minimapEvents:RegisterEvent("ADDON_LOADED")
minimapEvents:RegisterEvent("PLAYER_LOGIN")
minimapEvents:RegisterEvent("PLAYER_ENTERING_WORLD")
minimapEvents:RegisterEvent("PLAYER_REGEN_ENABLED")
minimapEvents:SetScript("OnEvent", UpdateSquareMinimap)

-- Read typed quest objectives without opening or changing the visible tooltip.
-- Each objective belongs to this NPC; whole-quest completion is not sufficient.
local questPlateEvents = CreateFrame("Frame")
local questPlateIcons = {}
local questPlateUnits = {}
local questPlateRefreshPending = false
local questPlateElapsed = 0

local function IsReadableQuestValue(value)
    return not issecretvalue or not issecretvalue(value)
end

local function IsOwnQuestPlayer(text)
    if not IsReadableQuestValue(text) or type(text) ~= "string" then
        return false
    end
    text = text:gsub("|c%x%x%x%x%x%x%x%x", ""):gsub("|r", ""):match("^%s*(.-)%s*$")
    -- Forever's UnitName and UnitNameUnmodified can both include a surname,
    -- while QuestPlayer lines show the first name. Use its native name parser.
    local firstName = NameUtil and NameUtil.GetUnitFirstName and NameUtil.GetUnitFirstName("player")
    if IsReadableQuestValue(firstName) and type(firstName) == "string" and text == firstName then
        return true
    end
    local name, realm = UnitName("player")
    if not IsReadableQuestValue(name) or type(name) ~= "string" then
        return false
    end
    realm = realm or (GetRealmName and GetRealmName())
    return text == name or (IsReadableQuestValue(realm) and type(realm) == "string"
        and text == name .. "-" .. realm:gsub("%s", ""))
end

local function IsQuestObjectiveIncomplete(line)
    if not IsReadableQuestValue(line.completed) or not IsReadableQuestValue(line.numFulfilled)
        or not IsReadableQuestValue(line.numRequired) or line.completed == true then
        return false
    end
    if type(line.numFulfilled) == "number" and type(line.numRequired) == "number"
        and line.numRequired > 0 then
        return line.numFulfilled < line.numRequired
    end
    -- Interactions and other objectives need not have a numeric target.
    return line.completed == false
end

local function UnitNeedsQuestBag(unit)
    local isPlayer = UnitIsPlayer(unit)
    if not IsReadableQuestValue(isPlayer) or isPlayer then
        return false
    end
    local ok, data = pcall(C_TooltipInfo.GetUnit, unit)
    if not ok or not data or type(data.lines) ~= "table" then
        return false
    end
    local types = Enum.TooltipDataLineType
    local ownQuest, ownPlayer = false, true
    for _, line in ipairs(data.lines) do
        if not IsReadableQuestValue(line.type) then
            return false
        end
        if line.type == types.QuestTitle then
            ownQuest = false
            ownPlayer = true
            if IsReadableQuestValue(line.id) and type(line.id) == "number" and line.id > 0 then
                local active = C_QuestLog.IsOnQuest(line.id)
                ownQuest = IsReadableQuestValue(active) and active == true
            end
        elseif line.type == types.QuestPlayer then
            ownPlayer = IsOwnQuestPlayer(line.leftText)
        elseif line.type == types.QuestObjective and ownQuest and ownPlayer
            and IsQuestObjectiveIncomplete(line) then
            return true
        end
    end
    return false
end

local function HideQuestPlateIcons(unit)
    for bar, icon in pairs(questPlateIcons) do
        if not unit or questPlateUnits[bar] == unit then
            if icon:IsShown() then
                icon:Hide()
            end
            questPlateUnits[bar] = nil
        end
    end
end

local RefreshQuestPlateIcons
local function PollQuestPlateIcons(_, elapsed)
    questPlateElapsed = questPlateElapsed + elapsed
    if questPlateElapsed >= 0.5 then
        questPlateElapsed = 0
        RefreshQuestPlateIcons()
    end
end

RefreshQuestPlateIcons = function()
    questPlateEvents:SetScript("OnUpdate", nil)
    if not settingsLoaded or not settings.questNameplateBag
        or not C_NamePlate or not C_NamePlate.GetNamePlates
        or not C_TooltipInfo or not C_TooltipInfo.GetUnit
        or not C_QuestLog or not C_QuestLog.IsOnQuest
        or not Enum.TooltipDataLineType then
        HideQuestPlateIcons()
        return
    end
    local plates = C_NamePlate.GetNamePlates()
    local visibleUnits = {}
    for _, plate in ipairs(plates) do
        if not (plate.IsForbidden and plate:IsForbidden()) then
            local unitFrame = plate.UnitFrame
            local unit = plate.GetUnit and plate:GetUnit()
            if IsReadableQuestValue(unit) and type(unit) == "string" and unitFrame
                and not (unitFrame.IsForbidden and unitFrame:IsForbidden()) then
                local bar = unitFrame.healthBar
                if bar and bar:IsShown() and UnitNeedsQuestBag(unit) then
                    local icon = questPlateIcons[bar]
                    if not icon then
                        icon = bar:CreateTexture(nil, "OVERLAY")
                        icon:SetTexture("Interface\\Minimap\\Tracking\\Banker")
                        icon:SetSize(20, 20)
                        icon:SetPoint("RIGHT", bar, "LEFT", -6, 0)
                        questPlateIcons[bar] = icon
                    end
                    visibleUnits[bar] = unit
                    if not icon:IsShown() then
                        icon:Show()
                    end
                end
            end
        end
    end
    -- Reconcile once after scanning. Unchanged icons stay shown while their
    -- nameplates move; removing another unit must not blank every marker.
    for bar, icon in pairs(questPlateIcons) do
        if not visibleUnits[bar] and icon:IsShown() then
            icon:Hide()
        end
    end
    questPlateUnits = visibleUnits
    -- Retry delayed server data only while nameplates exist. Reuse textures with
    -- the native health-bar pool; never keep quest eligibility on pooled frames.
    if #plates > 0 then
        questPlateEvents:SetScript("OnUpdate", PollQuestPlateIcons)
    end
end

local function QueueQuestPlateRefresh()
    if questPlateRefreshPending or not settingsLoaded or not settings.questNameplateBag then
        return
    end
    questPlateRefreshPending = true
    C_Timer.After(0, function()
        questPlateRefreshPending = false
        RefreshQuestPlateIcons()
    end)
end

featureChanged.questNameplateBag = function()
    questPlateElapsed = 0
    RefreshQuestPlateIcons()
end
for _, event in ipairs({ "NAME_PLATE_UNIT_ADDED", "NAME_PLATE_UNIT_REMOVED",
    "QUEST_LOG_UPDATE", "QUEST_ACCEPTED", "QUEST_REMOVED", "QUEST_WATCH_UPDATE",
    "PLAYER_ENTERING_WORLD", "GROUP_ROSTER_UPDATE", "LOOT_CLOSED" }) do
    questPlateEvents:RegisterEvent(event)
end
questPlateEvents:SetScript("OnEvent", function(_, event, unit)
    if event == "NAME_PLATE_UNIT_REMOVED" then
        -- Clear only the departing unit before Blizzard reuses its frame.
        -- The deferred refresh runs after all native handlers finish.
        HideQuestPlateIcons(unit)
    end
    QueueQuestPlateRefresh()
end)


-- Questie-style NPC/item lookup for the player's quests still in the quest log.
-- Classic estimates and Forever observations; provenance is documented in README.
local function QuestItemObjectiveName(text)
    if not IsReadableQuestValue(text) or type(text) ~= "string" then return nil end
    text = text:gsub("|c%x%x%x%x%x%x%x%x", ""):gsub("|r", ""):match("^%s*(.-)%s*$")
    return text:match("^%d+%s*/%s*%d+%s+(.+)$")
        or text:match("^(.+):%s*%d+%s*/%s*%d+$") or text
end

local function QuestItemObjectives(questID)
    if not IsReadableQuestValue(questID) or type(questID) ~= "number" then return nil end
    local active = C_QuestLog.IsOnQuest(questID)
    if not IsReadableQuestValue(active) or not active then return nil end
    local ok, objectives = pcall(C_QuestLog.GetQuestObjectives, questID)
    if not ok or type(objectives) ~= "table" then return nil end
    local names = {}
    for _, objective in ipairs(objectives) do
        if IsReadableQuestValue(objective.type) and objective.type == "item" then
            local name = QuestItemObjectiveName(objective.text)
            if name then names[name] = true end
        end
    end
    return names
end

local requestedDropItems = {}
local function QuestDropItemName(itemID, database)
    local name = C_Item and C_Item.GetItemNameByID and C_Item.GetItemNameByID(itemID)
    if not IsReadableQuestValue(name) then return nil end
    if type(name) == "string" then return name end
    local locale = GetLocale()
    if locale == "enUS" or locale == "enGB" then return database.names[itemID] end
    -- Request missing localized names once; a later native tooltip build picks them up.
    if C_Item and C_Item.RequestLoadItemDataByID and not requestedDropItems[itemID] then
        requestedDropItems[itemID] = true
        C_Item.RequestLoadItemDataByID(itemID)
    end
end

local function QuestDropTitleColor(line)
    local fallback = "|cffffd100"
    if not IsReadableQuestValue(line.lineIndex) or type(line.lineIndex) ~= "number" then return fallback end
    local row = _G["GameTooltipTextLeft" .. line.lineIndex]
    if not row or not row.GetTextColor then return fallback end
    local r, g, b = row:GetTextColor()
    for _, value in ipairs({r, g, b}) do
        if not IsReadableQuestValue(value) or type(value) ~= "number"
            or value ~= value or value < 0 or value > 1 then return fallback end
    end
    if r == nil or g == nil or b == nil then return fallback end
    return string.format("|cff%02x%02x%02x", math.floor(r * 255 + 0.5),
        math.floor(g * 255 + 0.5), math.floor(b * 255 + 0.5))
end

local function QuestDropPercent(rate)
    local rounded = math.floor(rate + 0.5)
    if rate >= 19 then
        local nearestFive = math.floor(rate / 5 + 0.5) * 5
        if math.abs(rate - nearestFive) <= 1 then rounded = nearestFive end
    end
    return rounded == 0 and "<1" or tostring(rounded)
end

local function QuestDropObjectiveComplete(line)
    if IsReadableQuestValue(line.completed) and line.completed == true then return true end
    local fulfilled, required = line.numFulfilled, line.numRequired
    return IsReadableQuestValue(fulfilled) and IsReadableQuestValue(required)
        and type(fulfilled) == "number" and type(required) == "number"
        and required > 0 and fulfilled >= required
end

-- Repeated post-calls may change styling without rebuilding the native row first.
local questDropRows = setmetatable({}, {__mode = "k"})
local function AddQuestDropRates(tooltip, data)
    if not settingsLoaded or not settings.questDropRate or tooltip ~= GameTooltip
        or (tooltip.IsForbidden and tooltip:IsForbidden())
        or not data or type(data.lines) ~= "table" or not IsReadableQuestValue(data.guid)
        or type(data.guid) ~= "string" or not BetaQoLQuestDrops
        or not C_QuestLog or not C_QuestLog.IsOnQuest or not C_QuestLog.GetQuestObjectives
        or not Enum.TooltipDataLineType then return end
    local npcID = tonumber(data.guid:match("^Creature%-%d+%-%d+%-%d+%-%d+%-(%d+)%-"))
    local database = BetaQoLQuestDrops
    local drops = npcID and database.npcs[npcID]
    if not drops then return end
    local types = Enum.TooltipDataLineType
    local ownItems, ownPlayer, itemNames = nil, true, {}
    local questColor = "|cffffd100"
    for _, line in ipairs(data.lines) do
        if not IsReadableQuestValue(line.type) then return end
        if line.type == types.QuestTitle then
            ownItems, ownPlayer = QuestItemObjectives(line.id), true
            questColor = QuestDropTitleColor(line)
        elseif line.type == types.QuestPlayer then
            -- GUIDs avoid surname/display-name differences in grouped tooltips.
            if IsReadableQuestValue(line.guid) and type(line.guid) == "string" then
                local playerGUID = UnitGUID("player")
                ownPlayer = IsReadableQuestValue(playerGUID) and line.guid == playerGUID
            else
                ownPlayer = IsOwnQuestPlayer(line.leftText)
            end
        elseif line.type == types.QuestObjective and ownItems and ownPlayer then
            local objectiveName = QuestItemObjectiveName(line.leftText)
            if objectiveName and ownItems[objectiveName] then
                local matchedRate, ambiguous
                for itemID, rate in pairs(drops) do
                    if itemNames[itemID] == nil then
                        itemNames[itemID] = QuestDropItemName(itemID, database) or false
                    end
                    if itemNames[itemID] == objectiveName then
                        if matchedRate then ambiguous = true; break end
                        matchedRate = rate
                    end
                end
                -- Some distinct items share a name (e.g. Windsor's Lost Information).
                -- Native objective text cannot distinguish them: omit, never guess.
                if matchedRate and not ambiguous and IsReadableQuestValue(line.lineIndex)
                    and type(line.lineIndex) == "number" then
                    -- The native handler records the rendered row, including any extra lines.
                    -- Keep its colors, completion icon and shared tooltip data intact.
                    local fontString = _G["GameTooltipTextLeft" .. line.lineIndex]
                    local text = fontString and fontString:GetText()
                    if IsReadableQuestValue(text) and type(text) == "string" then
                        local previous = questDropRows[fontString]
                        local base = previous and text == previous.rendered and previous.base or text
                        local percent = "(" .. QuestDropPercent(matchedRate) .. "%)"
                        -- Completed percentages inherit the native objective's gray.
                        local suffix = QuestDropObjectiveComplete(line) and (" " .. percent)
                            or (" " .. questColor .. percent .. "|r")
                        local rendered = base .. suffix
                        questDropRows[fontString] = {base = base, rendered = rendered}
                        if text ~= rendered then
                            fontString:SetText(rendered)
                        end
                    end
                end
            end
        end
    end
end

local dropTooltipHooked = false
local function HookQuestDropTooltip()
    if not dropTooltipHooked and TooltipDataProcessor and TooltipDataProcessor.AddTooltipPostCall
        and Enum.TooltipDataType and Enum.TooltipDataType.Unit then
        TooltipDataProcessor.AddTooltipPostCall(Enum.TooltipDataType.Unit, AddQuestDropRates)
        dropTooltipHooked = true
    end
end
featureChanged.questDropRate = HookQuestDropTooltip
local dropTooltipEvents = CreateFrame("Frame")
dropTooltipEvents:RegisterEvent("ADDON_LOADED")
dropTooltipEvents:SetScript("OnEvent", function(self)
    HookQuestDropTooltip()
    if dropTooltipHooked then self:UnregisterEvent("ADDON_LOADED") end
end)
HookQuestDropTooltip()
