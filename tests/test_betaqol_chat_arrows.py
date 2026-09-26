"""Chat edit-box modes, new windows, and autocomplete restoration."""
import unittest

from test_forever_quick_accept import HOST, SOURCE, LuaRuntime
from settings_ui import UI_ENGINE

ENGINE = r'''
CHAT_FRAMES = {}
AutoCompleteBox = {}
function AutoCompleteBox:IsShown() return self.parent ~= nil end
function IsAltKeyDown() return alt end
function IsControlKeyDown() return ctrl end
function IsSecureCmd(command) return command:upper() == '/CAST' end
function hooksecurefunc(target, name, hook)
    if type(target) == 'string' then target, name, hook = _G, target, name end
    local original = assert(target[name])
    target[name] = function(...) local result = original(...); hook(...); return result end
end
function makeChat(name, mode)
    local box = {mode = mode, text = '', focused = true, scripts = {}, nativeLines = {}, attributes = {chatType='SAY'}}
    function box:GetAttribute(key) return self.attributes[key] end
    function box:SetAttribute(key, value) self.attributes[key] = value end
    function box:UpdateHeader() self.headerType = self:GetAttribute('chatType') end
    function box:GetAltArrowKeyMode() return self.mode end
    function box:SetAltArrowKeyMode(value) self.mode = value end
    function box:HookScript(event, fn) self.scripts[event] = fn end
    function box:HasFocus() return self.focused end
    function box:GetText() return self.text end
    function box:SetText(text)
        self.text = text
        if self.scripts.OnTextChanged then self.scripts.OnTextChanged(self, false) end
    end
    function box:SetCursorPosition(pos) self.cursor = pos end
    function box:GetHistoryLines() return 32 end
    function box:AddHistoryLine(text) table.insert(self.nativeLines, text) end
    function box:ClearHistory() self.nativeLines = {} end
    function box:arrow(key) if self.scripts.OnArrowPressed then self.scripts.OnArrowPressed(self, key) end end
    _G[name] = {editBox = box}
    table.insert(CHAT_FRAMES, name)
    return box
end
function FCF_OpenNewWindow() return makeChat('ChatFrame4', true) end
function FCF_OpenTemporaryWindow() return makeChat('ChatFrame11', true) end
function startComplete(box)
    AutoCompleteBox.parent = box
    AutoCompleteBox.parentArrows = box:GetAltArrowKeyMode()
    box:SetAltArrowKeyMode(false)
end
function endComplete(box)
    if AutoCompleteBox.parentArrows then
        box:SetAltArrowKeyMode(AutoCompleteBox.parentArrows)
    end
    AutoCompleteBox.parent = nil
    AutoCompleteBox.parentArrows = nil
end
normal = makeChat('ChatFrame1', true)
alreadyFree = makeChat('ChatFrame2', false)
unrelated = {mode = true}
'''


class ChatArrowBehaviour(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST + UI_ENGINE + ENGINE)
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))

    def test_defaults_and_immediate_toggle_restore_previous_modes(self):
        self.lua.execute('''
        emit('ADDON_LOADED', 'BetaQoL'); SlashCmdList.QOL()
        assert(checkboxes[12].Text.text == 'Arrow Keys Chat Control')
        assert(not normal.mode and not alreadyFree.mode and unrelated.mode)
        clickSetting(12, false)
        assert(normal.mode and not alreadyFree.mode)
        clickSetting(12, true); assert(not normal.mode)
        ''')

    def test_saved_disabled_setting_and_new_windows(self):
        self.lua.execute('''
        BetaQoLDB = {chatArrowKeys = false}
        emit('ADDON_LOADED', 'BetaQoL'); SlashCmdList.QOL()
        assert(normal.mode and not checkboxes[12]:GetChecked())
        local whisper = FCF_OpenTemporaryWindow(); assert(whisper.mode)
        clickSetting(12, true); assert(not whisper.mode)
        local regular = FCF_OpenNewWindow(); assert(not regular.mode)
        clickSetting(12, false); assert(regular.mode and whisper.mode)
        ''')

    def test_autocomplete_open_before_enable_does_not_restore_stale_mode(self):
        self.lua.execute('''
        startComplete(normal)
        emit('ADDON_LOADED', 'BetaQoL'); SlashCmdList.QOL()
        endComplete(normal); assert(not normal.mode)
        clickSetting(12, false); assert(normal.mode)
        ''')

    def test_disabling_preserves_autocomplete_navigation_then_restores_alt(self):
        self.lua.execute('''
        emit('ADDON_LOADED', 'BetaQoL'); SlashCmdList.QOL()
        startComplete(normal); clickSetting(12, false)
        assert(not normal.mode)
        endComplete(normal); assert(normal.mode)
        ''')

    def test_chat_loaded_later_is_discovered(self):
        self.lua.execute('''
        local oldFrames = CHAT_FRAMES; CHAT_FRAMES = nil
        emit('ADDON_LOADED', 'BetaQoL'); assert(normal.mode)
        CHAT_FRAMES = oldFrames
        emit('PLAYER_LOGIN'); assert(not normal.mode)
        ''')

    def test_arrows_recall_messages_in_order_and_restore_draft(self):
        self.lua.execute('''
        emit('ADDON_LOADED','BetaQoL')
        normal:AddHistoryLine('/say first'); normal:AddHistoryLine('/say second')
        normal:SetText('unfinished draft')
        normal:arrow('UP'); assert(normal.text == '/say second')
        normal:arrow('UP'); assert(normal.text == '/say first')
        normal:arrow('UP'); assert(normal.text == '/say first')
        normal:arrow('DOWN'); assert(normal.text == '/say second')
        normal:arrow('DOWN'); assert(normal.text == 'unfinished draft')
        assert(normal.cursor == #'unfinished draft' and #normal.nativeLines == 2)
        ''')

    def test_history_respects_focus_modifiers_autocomplete_and_toggle(self):
        self.lua.execute('''
        emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()
        normal:AddHistoryLine('saved'); normal:SetText('draft')
        normal.focused=false; normal:arrow('UP'); assert(normal.text=='draft')
        normal.focused=true; alt=true; normal:arrow('UP'); assert(normal.text=='draft')
        alt=false; ctrl=true; normal:arrow('UP'); assert(normal.text=='draft')
        ctrl=false; shift=true; normal:arrow('UP'); assert(normal.text=='draft')
        shift=false; startComplete(normal); normal:arrow('UP'); assert(normal.text=='draft')
        endComplete(normal); clickSetting(12,false)
        normal:arrow('UP'); assert(normal.text=='draft')
        clickSetting(12,true); normal:arrow('UP'); assert(normal.text=='saved')
        ''')

    def test_native_secure_commands_are_not_recalled_by_addon(self):
        self.lua.execute('''
        emit('ADDON_LOADED','BetaQoL')
        normal:AddHistoryLine('safe message'); normal:AddHistoryLine('/cast Frostbolt')
        normal:SetText(''); normal:arrow('UP'); assert(normal.text=='safe message')
        assert(#normal.nativeLines==2)
        normal.scripts.OnEditFocusGained(normal)
        normal:SetText('/cast Frostbolt'); normal:arrow('UP')
        assert(normal.text=='/cast Frostbolt')
        ''')

    def test_history_is_bounded_and_cleared_with_native_history(self):
        self.lua.execute('''
        emit('ADDON_LOADED','BetaQoL')
        for i=1,40 do normal:AddHistoryLine('message '..i) end
        for i=1,50 do normal:arrow('UP') end
        assert(normal.text=='message 9')
        normal:ClearHistory(); normal:SetText('draft'); normal:arrow('UP')
        assert(normal.text=='draft')
        ''')

    def test_new_whisper_history_is_separate_and_typing_resets_navigation(self):
        self.lua.execute('''
        emit('ADDON_LOADED','BetaQoL')
        normal:AddHistoryLine('general')
        local whisper=FCF_OpenTemporaryWindow()
        whisper:AddHistoryLine('/w Friend hello'); whisper:arrow('UP')
        assert(whisper.text=='/w Friend hello' and normal.text=='')
        whisper.text='new draft'; whisper.scripts.OnTextChanged(whisper,true)
        whisper:arrow('UP'); whisper:arrow('DOWN'); assert(whisper.text=='new draft')
        ''')

    def test_restoring_draft_restores_whisper_recipient_and_channel(self):
        self.lua.execute('''
        emit('ADDON_LOADED','BetaQoL')
        local originalSetText = normal.SetText
        function normal:SetText(text)
            if text:sub(1,5)=='/say ' then
                self:SetAttribute('chatType','SAY')
                text=text:sub(6)
            end
            originalSetText(self,text)
        end
        normal:AddHistoryLine('/say public message')
        normal:SetAttribute('chatType','WHISPER'); normal:SetAttribute('tellTarget','Friend')
        normal:SetAttribute('channelTarget',3)
        normal.autoCompleteSource='whisper source'; normal.autoCompleteParams={1,2}
        normal:SetText('private draft'); normal:arrow('UP')
        assert(normal.text=='public message' and normal:GetAttribute('chatType')=='SAY')
        normal:arrow('DOWN')
        assert(normal.text=='private draft' and normal:GetAttribute('chatType')=='WHISPER')
        assert(normal:GetAttribute('tellTarget')=='Friend' and normal:GetAttribute('channelTarget')==3)
        assert(normal.headerType=='WHISPER' and normal.autoCompleteSource=='whisper source')
        ''')
