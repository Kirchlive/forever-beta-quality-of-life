import unittest

from test_forever_quick_accept import HOST, SOURCE, LuaRuntime
from settings_ui import UI_ENGINE
import test_betaqol_fastloot as loot_tests
import test_betaqol_popups as popup_tests


class SettingsBehaviour(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST + UI_ENGINE)
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))

    def test_window_is_lazy_reusable_and_has_independent_working_checkboxes(self):
        self.lua.execute('''
        assert(#checkboxes==0)
        SlashCmdList.QOL()
        assert(#checkboxes==5 and #UISpecialFrames==1)
        for _,box in ipairs(checkboxes) do assert(box:GetChecked()) end
        clickSetting(1,false); emit('QUEST_DETAIL'); assert(not journal[9173])
        assert(BetaQoLDB.fastLoot and BetaQoLDB.enterConfirm and BetaQoLDB.rangeColor)
        SlashCmdList.BETAQOL(); assert(checkboxes[1]:GetChecked())
        emit('QUEST_DETAIL'); assert(journal[9173])
        SlashCmdList.QOL(); SlashCmdList.QOL(); assert(#checkboxes==5)
        ''')

    def test_saved_false_values_loaded_after_lua_are_preserved(self):
        self.lua.execute('''
        BetaQoLDB={autoAccept=false, autoTurnIn=false, fastLoot=false, enterConfirm=false, rangeColor=false}
        emit('ADDON_LOADED','AnotherAddon')
        emit('ADDON_LOADED','BetaQoL')
        SlashCmdList.QOL()
        for _,box in ipairs(checkboxes) do assert(not box:GetChecked()) end
        emit('QUEST_DETAIL'); assert(not journal[9173])
        loot={12}; emit('LOOT_READY',true); assert(#lootCalls==0)
        ''')

    def test_saved_settings_round_trip_across_fresh_lua_runtime(self):
        self.lua.execute("SlashCmdList.QOL(); clickSetting(1,false); clickSetting(2,false); clickSetting(4,false)")
        values = {key: self.lua.globals().BetaQoLDB[key]
                  for key in ('autoAccept', 'autoTurnIn', 'fastLoot', 'enterConfirm', 'rangeColor')}
        fresh = LuaRuntime(unpack_returned_tuples=True)
        fresh.execute(HOST + UI_ENGINE)
        fresh.execute(SOURCE.read_text(encoding='utf-8'))
        fresh.globals().BetaQoLDB = fresh.table_from(values)
        fresh.execute("emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL(); "
                      "assert(not checkboxes[1]:GetChecked() and not checkboxes[2]:GetChecked() and checkboxes[3]:GetChecked()); "
                      "assert(not checkboxes[4]:GetChecked() and checkboxes[5]:GetChecked())")

    def test_missing_or_invalid_preferences_get_defaults_without_overwriting_false(self):
        self.lua.execute('''
        BetaQoLDB={autoAccept=false, fastLoot='false', enterConfirm=0}
        emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()
        assert(not BetaQoLDB.autoAccept and BetaQoLDB.fastLoot and BetaQoLDB.enterConfirm and BetaQoLDB.rangeColor)
        ''')


class FeatureSwitchBehaviour(unittest.TestCase):
    def test_disabling_during_loot_close_preserves_native_cleanup(self):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(HOST + loot_tests.ENGINE + UI_ENGINE)
        lua.execute(loot_tests.NATIVE.read_text(encoding='utf-8'))
        lua.execute('createNative()')
        lua.execute(SOURCE.read_text(encoding='utf-8'))
        lua.execute('''
        emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()
        fill({id=11}); emit('LOOT_OPENED',true,false); advance(0)
        emit('LOOT_CLOSED'); assert(LootFrame.HideAnim:IsPlaying())
        clickSetting(3,false); advance(0.2)
        assert(not LootFrame:IsShown() and lootButton.click)
        ''')

    def test_fastloot_switch_restores_active_window_and_cancels_pending_work(self):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(HOST + loot_tests.ENGINE + UI_ENGINE)
        lua.execute(loot_tests.NATIVE.read_text(encoding='utf-8'))
        lua.execute('createNative()')
        lua.execute(SOURCE.read_text(encoding='utf-8'))
        lua.execute('''
        emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()
        blockedLoot=true; fill({id=11}); emit('LOOT_OPENED',true,false); advance(0)
        assert(LootFrame:GetAlpha()==0 and not lootButton.click)
        local calls=#lootCalls
        clickSetting(3,false)
        assert(LootFrame:GetAlpha()==1 and lootButton.click)
        advance(2); assert(#lootCalls==calls)
        emit('LOOT_CLOSED'); advance(0.2)
        emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); advance(2)
        assert(#lootCalls==calls and LootFrame:IsVisible())
        emit('LOOT_CLOSED'); advance(0.2); clickSetting(3,true)
        blockedLoot=false; fill({id=22}); emit('LOOT_READY',true)
        assert(inventory[1]==22)
        ''')

    def test_popup_switch_removes_and_reinstates_handlers_on_already_open_dialog(self):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(HOST + UI_ENGINE + popup_tests.ENGINE + popup_tests.NATIVE)
        lua.execute(SOURCE.read_text(encoding='utf-8'))
        lua.execute('''
        emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()
        local dialog=openDialog('DELETE_ITEM')
        clickSetting(4,false); key(dialog,'ENTER')
        assert(deletions==0 and dialog:IsShown())
        clickSetting(4,true); key(dialog,'ENTER')
        assert(deletions==1 and not dialog:IsShown())
        clickSetting(4,false); dialog=openDialog('DELETE_ITEM'); key(dialog,'ENTER')
        assert(deletions==1 and dialog:IsShown())
        ''')
