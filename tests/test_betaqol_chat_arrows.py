"""Chat edit-box modes, new windows, and autocomplete restoration."""
import unittest

from test_forever_quick_accept import HOST, SOURCE, LuaRuntime
from settings_ui import UI_ENGINE

ENGINE = r'''
CHAT_FRAMES = {}
AutoCompleteBox = {}
function hooksecurefunc(name, hook)
    local original = assert(_G[name])
    _G[name] = function(...) local result = original(...); hook(...); return result end
end
function makeChat(name, mode)
    local box = {mode = mode}
    function box:GetAltArrowKeyMode() return self.mode end
    function box:SetAltArrowKeyMode(value) self.mode = value end
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
        assert(checkboxes[10].Text.text == 'Arrow Keys Chat Control')
        assert(not normal.mode and not alreadyFree.mode and unrelated.mode)
        clickSetting(10, false)
        assert(normal.mode and not alreadyFree.mode)
        clickSetting(10, true); assert(not normal.mode)
        ''')

    def test_saved_disabled_setting_and_new_windows(self):
        self.lua.execute('''
        BetaQoLDB = {chatArrowKeys = false}
        emit('ADDON_LOADED', 'BetaQoL'); SlashCmdList.QOL()
        assert(normal.mode and not checkboxes[10]:GetChecked())
        local whisper = FCF_OpenTemporaryWindow(); assert(whisper.mode)
        clickSetting(10, true); assert(not whisper.mode)
        local regular = FCF_OpenNewWindow(); assert(not regular.mode)
        clickSetting(10, false); assert(regular.mode and whisper.mode)
        ''')

    def test_autocomplete_open_before_enable_does_not_restore_stale_mode(self):
        self.lua.execute('''
        startComplete(normal)
        emit('ADDON_LOADED', 'BetaQoL'); SlashCmdList.QOL()
        endComplete(normal); assert(not normal.mode)
        clickSetting(10, false); assert(normal.mode)
        ''')

    def test_disabling_preserves_autocomplete_navigation_then_restores_alt(self):
        self.lua.execute('''
        emit('ADDON_LOADED', 'BetaQoL'); SlashCmdList.QOL()
        startComplete(normal); clickSetting(10, false)
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
