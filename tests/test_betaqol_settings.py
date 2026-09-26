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
        assert(#checkboxes==16 and #UISpecialFrames==1)
        for index,box in ipairs(checkboxes) do assert(box:GetChecked()==true) end
        clickSetting(1,false); emit('QUEST_DETAIL'); assert(not journal[9173])
        assert(BetaQoLDB.fastLoot and BetaQoLDB.enterConfirm and BetaQoLDB.rangeColor)
        SlashCmdList.BETAQOL(); assert(checkboxes[1]:GetChecked())
        emit('QUEST_DETAIL'); assert(journal[9173])
        SlashCmdList.QOL(); SlashCmdList.QOL(); assert(#checkboxes==16)
        ''')

    def test_saved_false_values_loaded_after_lua_are_preserved(self):
        self.lua.execute('''
        BetaQoLDB={autoAccept=false, autoTurnIn=false, fastLoot=false, enterConfirm=false, rangeColor=false, whisperDoubleClick=false, backspaceDestroy=false, backspaceQuestDetails=false, squareMinimap=false, questNameplateBag=false, chatArrowKeys=false, shiftEscapeReload=false, questLogXP=false, questDropRate=false, flightMasterInstantMap=false, damageMeterDoubleClick=false}
        emit('ADDON_LOADED','AnotherAddon')
        emit('ADDON_LOADED','BetaQoL')
        SlashCmdList.QOL()
        for _,box in ipairs(checkboxes) do assert(not box:GetChecked()) end
        emit('QUEST_DETAIL'); assert(not journal[9173])
        loot={12}; emit('LOOT_READY',true); assert(#lootCalls==0)
        ''')

    def test_saved_settings_round_trip_across_fresh_lua_runtime(self):
        self.lua.execute("SlashCmdList.QOL(); clickSetting(1,false); clickSetting(2,false); clickSetting(11,false); clickSetting(16,false); clickSetting(10,false); clickSetting(9,false); clickSetting(7,true); clickSetting(4,false); clickSetting(12,false); clickSetting(13,false); clickSetting(5,false); clickSetting(3,false); clickSetting(14,false); clickSetting(15,false)")
        values = {key: self.lua.globals().BetaQoLDB[key]
                  for key in ('autoAccept', 'autoTurnIn', 'fastLoot', 'enterConfirm', 'rangeColor', 'whisperDoubleClick', 'backspaceDestroy', 'backspaceQuestDetails', 'squareMinimap', 'questNameplateBag', 'chatArrowKeys', 'shiftEscapeReload', 'questLogXP', 'questDropRate', 'flightMasterInstantMap', 'damageMeterDoubleClick')}
        fresh = LuaRuntime(unpack_returned_tuples=True)
        fresh.execute(HOST + UI_ENGINE)
        fresh.execute(SOURCE.read_text(encoding='utf-8'))
        fresh.globals().BetaQoLDB = fresh.table_from(values)
        fresh.execute("emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL(); "
                      "assert(not checkboxes[1]:GetChecked() and not checkboxes[2]:GetChecked() and checkboxes[6]:GetChecked()); "
                      "assert(not checkboxes[11]:GetChecked() and checkboxes[8]:GetChecked() and not checkboxes[16]:GetChecked() and not checkboxes[10]:GetChecked() and not checkboxes[9]:GetChecked() and checkboxes[7]:GetChecked() and not checkboxes[4]:GetChecked() and not checkboxes[12]:GetChecked() and not checkboxes[13]:GetChecked() and not checkboxes[5]:GetChecked() and not checkboxes[3]:GetChecked() and not checkboxes[14]:GetChecked() and not checkboxes[15]:GetChecked())")

    def test_missing_or_invalid_preferences_get_defaults_without_overwriting_false(self):
        self.lua.execute('''
        BetaQoLDB={autoAccept=false, fastLoot='false', enterConfirm=0, squareMinimap='true', questNameplateBag='true'}
        emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()
        assert(not BetaQoLDB.autoAccept and BetaQoLDB.fastLoot and BetaQoLDB.enterConfirm and BetaQoLDB.rangeColor)
        assert(BetaQoLDB.squareMinimap==true and checkboxes[7]:GetChecked())
        assert(BetaQoLDB.questNameplateBag==true and checkboxes[4]:GetChecked())
        ''')

    def test_minimap_and_quest_icon_choices_survive_repeated_runtime_restarts(self):
        self.lua.execute("emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL(); "
                         "assert(checkboxes[7]:GetChecked() and checkboxes[4]:GetChecked())")
        current = self.lua
        for minimap, quest_icon in ((True, True), (False, True), (True, False), (False, False)):
            with self.subTest(minimap=minimap, quest_icon=quest_icon):
                current.execute(f"clickSetting(7,{str(minimap).lower()}); "
                                f"clickSetting(4,{str(quest_icon).lower()})")
                # WoW reload and restart both rebuild Lua, then restore the
                # TOC-declared SavedVariables before the addon's load event.
                for _ in range(2):
                    saved = dict(current.globals().BetaQoLDB.items())
                    fresh = LuaRuntime(unpack_returned_tuples=True)
                    fresh.execute(HOST + UI_ENGINE)
                    fresh.execute(SOURCE.read_text(encoding='utf-8'))
                    fresh.globals().BetaQoLDB = fresh.table_from(saved)
                    fresh.execute("emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()")
                    self.assertEqual(fresh.globals().BetaQoLDB.squareMinimap, minimap)
                    self.assertEqual(fresh.globals().BetaQoLDB.questNameplateBag, quest_icon)
                    self.assertEqual(fresh.globals().checkboxes[7].checked, minimap)
                    self.assertEqual(fresh.globals().checkboxes[4].checked, quest_icon)
                    current = fresh


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
        clickSetting(6,false); advance(0.2)
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
        clickSetting(6,false)
        assert(LootFrame:GetAlpha()==1 and lootButton.click)
        advance(2); assert(#lootCalls==calls)
        emit('LOOT_CLOSED'); advance(0.2)
        emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); advance(2)
        assert(#lootCalls==calls and LootFrame:IsVisible())
        emit('LOOT_CLOSED'); advance(0.2); clickSetting(6,true)
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
        clickSetting(11,false); key(dialog,'ENTER')
        assert(deletions==0 and dialog:IsShown())
        clickSetting(11,true); key(dialog,'ENTER')
        assert(deletions==1 and not dialog:IsShown())
        clickSetting(11,false); dialog=openDialog('DELETE_ITEM'); key(dialog,'ENTER')
        assert(deletions==1 and dialog:IsShown())
        ''')
