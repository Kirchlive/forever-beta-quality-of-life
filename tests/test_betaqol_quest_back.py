"""Backspace quest navigation alongside native item-delete confirmation."""
import unittest

from test_forever_quick_accept import HOST, SOURCE, LuaRuntime
from settings_ui import UI_ENGINE
import test_betaqol_destroy as destroy
import test_betaqol_popups as popups

ENGINE = r'''
local create=CreateFrame
function CreateFrame(kind,name,parent,template)
    local f=create(kind,name,parent,template)
    f.parent=parent
    function f:IsVisible()
        return self.shown~=false and (not self.parent or not self.parent.IsVisible or self.parent:IsVisible())
    end
    f.IsShown=f.IsVisible
    return f
end
returns,backClicks,restoredMap=0,0,nil
function makeQuestUI()
    local map=CreateFrame('Frame')
    local details=CreateFrame('Frame',nil,map)
    local button=CreateFrame('Button',nil,details)
    button.enabled=true
    function button:IsEnabled() return self.enabled end
    function button:Click()
        backClicks=backClicks+1
        QuestMapFrame_ReturnFromQuestDetails()
    end
    function map:SetMapID(id) restoredMap=id end
    QuestMapFrame={DetailsFrame=details,GetParent=function() return map end}
    details.BackFrame={BackButton=button}
    function QuestMapFrame_CloseQuestDetails() details:Hide(); details.questID=nil; returns=returns+1 end
    function QuestMapFrame_UpdateQuestSessionState() end
    details.returnMapID=17; details.questID=5041
    details:Show()
end
'''
NATIVE = popups.native_between(
    'Blizzard_UIPanels_Game/Mainline/QuestMapFrame.lua',
    'function QuestMapFrame_ReturnFromQuestDetails()',
    'function QuestMapFrame_OpenToQuestDetails(')


class QuestBackBehaviour(unittest.TestCase):
    def setUp(self):
        self.lua=LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST+UI_ENGINE+popups.ENGINE+popups.NATIVE+destroy.NATIVE+destroy.ENGINE+ENGINE+NATIVE)
        self.lua.execute('makeQuestUI()')
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))
        self.lua.execute("emit('ADDON_LOADED','BetaQoL')")

    def test_backspace_clicks_native_back_restores_map_and_leaves_details(self):
        self.lua.execute('''
        assert(press('BACKSPACE'))
        assert(returns==1 and backClicks==1 and restoredMap==17)
        assert(not QuestMapFrame.DetailsFrame:IsVisible())
        assert(not press('BACKSPACE') and returns==1)
        ''')

    def test_typing_modifiers_and_other_keys_keep_normal_behavior(self):
        self.lua.execute('''
        keyboardFocus={}; assert(not press('BACKSPACE')); keyboardFocus=nil
        ctrl=true; assert(not press('BACKSPACE')); ctrl=false
        alt=true; assert(not press('BACKSPACE')); alt=false
        shift=true; assert(not press('BACKSPACE')); shift=false
        assert(not press('A') and returns==0)
        assert(press('BACKSPACE') and returns==1)
        ''')

    def test_hidden_map_and_disabled_back_button_do_not_intercept(self):
        self.lua.execute('''
        QuestMapFrame:GetParent():Hide(); assert(not press('BACKSPACE'))
        QuestMapFrame:GetParent():Show()
        QuestMapFrame.DetailsFrame.BackFrame.BackButton.enabled=false
        assert(not press('BACKSPACE') and returns==0)
        ''')

    def test_picked_up_item_keeps_delete_priority(self):
        self.lua.execute('''
        pickup('item',0,'Item-A'); assert(press('BACKSPACE'))
        assert(#confirmations==1 and returns==0 and deletions==0)
        SlashCmdList.QOL(); clickSetting(10,false)
        assert(not press('BACKSPACE') and returns==0)
        ''')

    def test_independent_setting_and_combat_release(self):
        self.lua.execute('''
        SlashCmdList.QOL(); clickSetting(9,false)
        assert(not press('BACKSPACE') and returns==0)
        clickSetting(10,false); clickSetting(9,true)
        combat=true; emit('PLAYER_REGEN_DISABLED')
        assert(not press('BACKSPACE') and returns==0)
        combat=false; emit('PLAYER_REGEN_ENABLED')
        assert(press('BACKSPACE') and returns==1)
        ''')

    def test_late_quest_ui_load(self):
        self.lua.execute('''
        QuestMapFrame:GetParent():Hide(); QuestMapFrame=nil
        emit('ADDON_LOADED','Unrelated')
        makeQuestUI(); emit('ADDON_LOADED','Blizzard_UIPanels_Game')
        assert(press('BACKSPACE') and returns==1)
        ''')
