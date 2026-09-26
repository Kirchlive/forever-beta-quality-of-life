"""Reload keyboard handling without the non-dispatching LSHIFT click binding."""
import unittest
from test_forever_quick_accept import HOST, SOURCE, LuaRuntime
from settings_ui import UI_ENGINE

ENGINE=r'''
combat,leftShift,rightShift,ctrl,alt=false,false,false,false,false
reloads,normalKeys=0,0
function InCombatLockdown() return combat end
function IsLeftShiftKeyDown() return leftShift end
function IsControlKeyDown() return ctrl end
function IsAltKeyDown() return alt end
function ReloadUI() reloads=reloads+1 end
function SetBinding() error('Must not change saved bindings') end
function SetOverrideBindingClick() error('Left-shift click binding does not dispatch in the live client') end
local create=CreateFrame
function CreateFrame(...)
    local f=create(...)
    function f:EnableKeyboard(value) self.keyboard=value end
    function f:SetPropagateKeyboardInput(value)
        assert(not combat,'Changed protected propagation in combat')
        self.propagate=value
    end
    return f
end
function pressKey(key, release)
    emit("MODIFIER_STATE_CHANGED","LSHIFT",leftShift and 1 or 0)
    for _,f in ipairs(frames) do
        if f.keyboard and f:IsShown() then
            f:GetScript('OnKeyDown')(f,key)
            assert(f.propagate==true,'Must preserve normal key routing')
        end
    end
    normalKeys=normalKeys+1
    if release~=false then
        for _,f in ipairs(frames) do
            if f.keyboard and f:IsShown() then f:GetScript('OnKeyUp')(f,key) end
        end
    end
end
'''

class ReloadBehaviour(unittest.TestCase):
    def setUp(self):
        self.lua=LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST+UI_ENGINE+ENGINE)
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))

    def test_left_shift_escape_reloads_without_binding_dispatch(self):
        self.lua.execute("emit('ADDON_LOADED','BetaQoL'); leftShift=true; pressKey('ESCAPE'); assert(reloads==1)")

    def test_plain_escape_right_shift_and_additional_modifiers_do_not_reload(self):
        self.lua.execute('''
        emit('ADDON_LOADED','BetaQoL'); pressKey('ESCAPE')
        rightShift=true; pressKey('ESCAPE'); rightShift=false
        leftShift=true; ctrl=true; pressKey('ESCAPE'); ctrl=false
        alt=true; pressKey('ESCAPE'); alt=false; pressKey('A')
        assert(reloads==0 and normalKeys==5)
        pressKey('ESCAPE'); assert(reloads==1)
        ''')

    def test_toggle_and_saved_off(self):
        self.lua.execute('''
        BetaQoLDB={shiftEscapeReload=false}; emit('ADDON_LOADED','BetaQoL')
        leftShift=true; pressKey('ESCAPE'); assert(reloads==0)
        SlashCmdList.QOL(); clickSetting(13,true); pressKey('ESCAPE'); assert(reloads==1)
        clickSetting(13,false); pressKey('ESCAPE'); assert(reloads==1)
        ''')

    def test_active_shortcut_in_combat_does_not_change_protected_input_routing(self):
        self.lua.execute('''
        emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()
        combat=true; leftShift=true; pressKey('ESCAPE'); assert(reloads==1)
        clickSetting(13,false); pressKey('ESCAPE'); assert(reloads==1)
        ''')

    def test_initialization_in_combat_waits_until_combat_ends(self):
        self.lua.execute('''
        combat=true; emit('ADDON_LOADED','BetaQoL'); leftShift=true
        pressKey('ESCAPE'); assert(reloads==0)
        combat=false; emit('PLAYER_REGEN_ENABLED'); pressKey('ESCAPE'); assert(reloads==1)
        ''')

    def test_repeated_events_and_held_escape_do_not_duplicate_reload(self):
        self.lua.execute('''
        emit('ADDON_LOADED','BetaQoL'); emit('PLAYER_LOGIN'); emit('PLAYER_REGEN_ENABLED')
        leftShift=true; pressKey('ESCAPE',false); pressKey('ESCAPE'); assert(reloads==1)
        pressKey('ESCAPE'); assert(reloads==2)
        ''')

    def test_existing_reload_preference_migrates_and_new_preference_wins(self):
        self.lua.execute("BetaQoLDB={ctrlEscapeReload=false}; emit('ADDON_LOADED','BetaQoL'); "
                         "assert(BetaQoLDB.shiftEscapeReload==false); leftShift=true; pressKey('ESCAPE'); assert(reloads==0)")
        fresh=LuaRuntime(unpack_returned_tuples=True)
        fresh.execute(HOST+UI_ENGINE+ENGINE)
        fresh.execute(SOURCE.read_text(encoding='utf-8'))
        fresh.execute("BetaQoLDB={ctrlEscapeReload=false,shiftEscapeReload=true}; emit('ADDON_LOADED','BetaQoL'); "
                      "leftShift=true; pressKey('ESCAPE'); assert(reloads==1)")

    def test_left_shift_events_work_when_left_shift_query_returns_false(self):
        self.lua.execute("IsLeftShiftKeyDown=function() return false end; emit('ADDON_LOADED','BetaQoL'); "
                         "leftShift=true; pressKey('ESCAPE'); assert(reloads==1)")

    def test_normal_escape_with_missing_key_up_does_not_block_later_reload(self):
        self.lua.execute('''
        emit('ADDON_LOADED','BetaQoL')
        -- Opening/closing a native panel may redirect key-up away from the listener.
        pressKey('ESCAPE',false); assert(reloads==0)
        leftShift=true; pressKey('ESCAPE'); assert(reloads==1)
        ''')

    def test_rejected_modifier_combo_with_missing_key_up_does_not_arm_reload_latch(self):
        self.lua.execute('''
        emit('ADDON_LOADED','BetaQoL'); leftShift=true; ctrl=true
        pressKey('ESCAPE',false); assert(reloads==0)
        ctrl=false; pressKey('ESCAPE'); assert(reloads==1)
        ''')
