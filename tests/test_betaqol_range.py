"""Actual Forever UpdateUsable/range-indicator code with simulated actions."""
import unittest

from test_forever_quick_accept import HOST, SOURCE, LuaRuntime
from test_betaqol_popups import native_between
from settings_ui import UI_ENGINE

NATIVE = '\n'.join([
    native_between('Blizzard_ActionBar/Shared/ActionButton.lua',
                   'function ActionBarActionButtonMixin:UpdateUsable(',
                   'function ActionBarActionButtonMixin:EvaluateState()'),
    native_between('Blizzard_ActionBar/Shared/ActionButton.lua',
                   'function ActionButton_UpdateRangeIndicator(',
                   'function ActionBarActionButtonMixin:GetPagedID()'),
    native_between('Blizzard_ActionBar/Shared/ActionButton.lua',
                   'function ActionBarButtonEventsFrameMixin:RegisterFrame(',
                   'ActionBarActionEventsFrameMixin ='),
])

ENGINE = r'''
ActionBarActionButtonMixin, ActionBarButtonEventsFrameMixin = {}, {}
actions = { [1]={usable=true, mana=false, inRange=true}, [2]={usable=false, mana=true, inRange=false} }
C_ActionBar = {}
function C_ActionBar.IsUsableAction(slot)
    local action=actions[slot]; return action.usable, action.mana
end
function C_ActionBar.IsActionInRange(slot)
    assert(type(slot)=='number' and slot>0)
    return actions[slot] and actions[slot].inRange
end
assertsafe=assert
function hooksecurefunc(target,name,hook)
    if type(target)=='string' then target,name,hook=_G,target,name end
    local original=assert(target[name], 'Missing hooked API: '..name)
    target[name]=function(...) local result=original(...); hook(...); return result end
end
RANGE_INDICATOR='*'
ACTIONBAR_HOTKEY_FONT_COLOR={GetRGB=function() return 0.6,0.6,0.6 end}
RED_FONT_COLOR={GetRGB=function() return 1,0.1,0.1 end}
function texture()
    local t={color={1,1,1,1}}
    function t:SetVertexColor(r,g,b,a) self.color={r,g,b,a or 1} end
    function t:GetVertexColor() return unpack(self.color) end
    function t:SetDesaturated(value) self.desaturated=value end
    function t:GetText() return '1' end
    function t:Show() end
    function t:Hide() end
    return t
end
function makeButton(slot)
    local button={action=slot, icon=texture(), HotKey=texture()}
    button.UpdateUsable=ActionBarActionButtonMixin.UpdateUsable
    function button:EvaluateState() end
    function button:Update() if self.action then self:UpdateUsable() end end
    -- Registration precedes the button's initial native UpdateAction/Update.
    ActionBarButtonEventsFrame:RegisterFrame(button)
    button:Update()
    return button
end
function assertColor(button,r,g,b)
    local ar,ag,ab=button.icon:GetVertexColor()
    assert(ar==r and ag==g and ab==b, string.format('Expected %g,%g,%g; got %g,%g,%g',r,g,b,ar,ag,ab))
end
function assertRed(button)
    local r,g,b=button.icon:GetVertexColor()
    assert(r>0.8 and g<0.3 and b<0.3,'Whole icon is not red')
end
'''


class RangeBehaviour(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST + UI_ENGINE + ENGINE + NATIVE)
        self.lua.execute('''
        ActionBarButtonEventsFrame={frames={}, RegisterFrame=ActionBarButtonEventsFrameMixin.RegisterFrame,
            ForEachFrame=ActionBarButtonEventsFrameMixin.ForEachFrame}
        button=makeButton(1); second=makeButton(2)
        ''')

    def load_addon(self):
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))
        self.lua.execute("emit('ADDON_LOADED','BetaQoL')")

    def test_range_event_tints_entire_icon_and_restores_native_color(self):
        self.load_addon()
        self.lua.execute('''
        ActionButton_UpdateRangeIndicator(button,true,false); assertRed(button)
        ActionButton_UpdateRangeIndicator(button,true,true); assertColor(button,1,1,1)
        assertRed(second)
        ActionButton_UpdateRangeIndicator(second,true,true); assertColor(second,0.5,0.5,1)
        ''')

    def test_usability_update_keeps_red_then_restores_correct_gray(self):
        self.load_addon()
        self.lua.execute('''
        actions[1].inRange=false
        ActionButton_UpdateRangeIndicator(button,true,false); assertRed(button)
        actions[1].usable=false; button:UpdateUsable(); assertRed(button)
        actions[1].inRange=true
        ActionButton_UpdateRangeIndicator(button,true,true); assertColor(button,0.4,0.4,0.4)
        ''')

    def test_unknown_range_and_non_range_action_restore_normal_icon(self):
        self.load_addon()
        self.lua.execute('''
        assertRed(second)
        ActionButton_UpdateRangeIndicator(second,false,false); assertColor(second,0.5,0.5,1)
        actions[2].inRange=nil; second:Update(); assertColor(second,0.5,0.5,1)
        ''')

    def test_page_slot_changes_and_empty_button_do_not_retain_red(self):
        self.load_addon()
        self.lua.execute('''
        assertRed(second)
        second.action=1; second:Update(); assertColor(second,1,1,1)
        second.action=2; second:Update(); assertRed(second)
        second.action=nil; second:Update(); assertColor(second,0.5,0.5,1)
        ''')

    def test_newly_registered_buttons_get_hooks_and_toggle_restores_immediately(self):
        self.load_addon()
        self.lua.execute('''
        local late=makeButton(2); assertRed(late)
        SlashCmdList.QOL(); clickSetting(5,false)
        assertColor(late,0.5,0.5,1); assertColor(second,0.5,0.5,1)
        late:UpdateUsable(); ActionButton_UpdateRangeIndicator(late,true,false)
        assertColor(late,0.5,0.5,1)
        clickSetting(5,true); assertRed(late); assertRed(second)
        ''')

    def test_saved_disabled_preference_restores_icons_after_addon_load(self):
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))
        self.lua.execute('''
        BetaQoLDB={rangeColor=false}; emit('ADDON_LOADED','BetaQoL')
        assertColor(second,0.5,0.5,1)
        ActionButton_UpdateRangeIndicator(second,true,false); assertColor(second,0.5,0.5,1)
        ''')

    def test_late_actionbar_load_and_repeated_load_events_do_not_stack_hooks(self):
        self.lua.execute('savedManager=ActionBarButtonEventsFrame; ActionBarButtonEventsFrame=nil')
        self.load_addon()
        self.lua.execute('''
        ActionBarButtonEventsFrame=savedManager; emit('ADDON_LOADED','Blizzard_ActionBar')
        emit('PLAYER_LOGIN'); emit('ADDON_LOADED','AnotherAddon')
        assertRed(second)
        second:UpdateUsable(); ActionButton_UpdateRangeIndicator(second,true,true)
        assertColor(second,0.5,0.5,1)
        ''')
