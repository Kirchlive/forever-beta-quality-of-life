"""Quest XP titles through the pinned native Forever title-building functions."""
import unittest

from test_forever_quick_accept import HOST, ROOT, SOURCE, LuaRuntime
from test_betaqol_popups import native_between
from settings_ui import UI_ENGINE

NATIVE = (ROOT / '.test-ui/Blizzard_UIPanels_Game/Camelot/QuestMapFrameOverrides.lua').read_text(encoding='utf-8')
NATIVE += '\n' + native_between(
    'Blizzard_UIPanels_Game/Mainline/QuestMapFrame.lua',
    'local function QuestLogQuests_GetTitle(',
    'local function QuestLogQuests_ShouldShowQuestButton(',
).replace('local function QuestLogQuests_GetTitle', 'function QuestLogQuests_GetTitle', 1)

ENGINE = r'''
C_QuestLog = {}
xp, ready, elite, partyCount, refreshes, requests = {}, {}, {}, 0, 0, {}
itemRewards, itemChoices = {}, {}
function GetNumQuestLogRewards(id) assert(id); return itemRewards[id] or 0 end
function GetNumQuestLogChoices(id, includeCurrencies)
    assert(id and not includeCurrencies); return itemChoices[id] or 0
end
function C_QuestLog.IsEliteQuest(id) return elite[id] end
function C_QuestLog.ShouldShowQuestRewards(id) return id ~= 99 end
function C_QuestLog.SetSelectedQuest() error('Must not change quest selection') end
function C_QuestLog.RequestLoadQuestByID(id) requests[id]=(requests[id] or 0)+1 end
function GetQuestLogRewardXP(id) assert(id); if xp[id]=='error' then error('unavailable') end; return xp[id] end
function HaveQuestRewardData(id) return ready[id] ~= false end
function BreakUpLargeNumbers(n)
    local value=tostring(n)
    while true do local count; value,count=value:gsub('^(%d+)(%d%d%d)','%1,%2'); if count==0 then break end end
    return value
end
function QuestUtils_GetNumPartyMembersOnQuest() return partyCount end
QuestScrollFrame={visible=true}
function QuestScrollFrame:IsVisible() return self.visible end
function QuestLogQuests_Update() refreshes=refreshes+1 end
function title(id, level, name)
    return QuestLogQuests_GetTitle({}, {questID=id,difficultyLevel=level,title=name})
end
'''


class QuestXPBehaviour(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST + UI_ENGINE + ENGINE + NATIVE)
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))

    def test_native_title_places_xp_between_level_and_name_without_duplicates(self):
        self.lua.execute('''
        xp[5724]=4400; emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()
        assert(checkboxes[5].Text.text=='Questlog Quest XP (+ for item rewards)')
        for i=1,3 do assert(title(5724,16,'Returning the Lost Satchel')=='[16] (4,400) Returning the Lost Satchel') end
        elite[5724]=true; partyCount=2
        assert(title(5724,16,'Satchel')=='[2] [16+] (4,400) Satchel')
        ''')

    def test_toggle_updates_visible_list_and_preserves_saved_false(self):
        self.lua.execute('''
        BetaQoLDB={questLogXP=false}; xp[1]=1200
        emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()
        assert(title(1,10,'Quest')=='[10] Quest')
        local before=refreshes; clickSetting(5,true); runTimers()
        assert(refreshes>before and title(1,10,'Quest')=='[10] (1,200) Quest')
        clickSetting(5,false); runTimers(); assert(title(1,10,'Quest')=='[10] Quest')
        ''')

    def test_missing_hidden_and_invalid_rewards_do_not_break_native_title(self):
        self.lua.execute('''
        emit('ADDON_LOADED','BetaQoL')
        for _,value in ipairs({'error',-10,'unknown'}) do
            xp[1]=value; assert(title(1,10,'Quest')=='[10] Quest')
        end
        xp[1]=nil; assert(title(1,10,'Quest')=='[10] Quest')
        xp[99]=999; assert(title(99,10,'Hidden')=='[10] Hidden')
        xp[1]=0; assert(title(1,10,'Quest')=='[10] (0) Quest')
        ''')

    def test_late_reward_data_and_level_changes_refresh_without_stale_cache(self):
        self.lua.execute('''
        emit('ADDON_LOADED','BetaQoL'); runTimers()
        ready[1]=false; xp[1]=0; assert(title(1,10,'Quest')=='[10] Quest')
        ready[1]=true; xp[1]=4400
        local before=refreshes; emit('QUEST_DATA_LOAD_RESULT',1,true); runTimers()
        assert(refreshes>before and title(1,10,'Quest')=='[10] (4,400) Quest')
        xp[1]=2200; emit('PLAYER_LEVEL_UP',30); runTimers()
        assert(title(1,10,'Quest')=='[10] (2,200) Quest')
        ''')

    def test_hidden_log_does_not_rebuild_and_late_ui_load_is_supported(self):
        self.lua.execute('''
        local native=QuestMapFrameOverrides; QuestMapFrameOverrides=nil
        emit('ADDON_LOADED','BetaQoL'); runTimers()
        QuestMapFrameOverrides=native; QuestScrollFrame.visible=false
        emit('ADDON_LOADED','Blizzard_UIPanels_Game'); runTimers()
        xp[1]=42; assert(title(1,10,'Quest')=='[10] (42) Quest')
        local before=refreshes; emit('PLAYER_LEVEL_UP',30); runTimers()
        assert(refreshes==before)
        ''')

    def test_event_bursts_coalesce_and_do_not_duplicate_prefix_wrapper(self):
        self.lua.execute('''
        emit('ADDON_LOADED','BetaQoL'); runTimers()
        local before=refreshes
        emit('QUEST_DATA_LOAD_RESULT',1,true); emit('QUEST_DATA_LOAD_RESULT',2,true)
        emit('PLAYER_LEVEL_UP',20); runTimers(); assert(refreshes==before+1)
        emit('ADDON_LOADED','Other'); xp[1]=10
        assert(title(1,10,'Quest')=='[10] (10) Quest')
        ''')

    def test_plus_marks_guaranteed_and_choice_items_once(self):
        self.lua.execute('''
        emit('ADDON_LOADED','BetaQoL'); xp[1]=4400
        itemRewards[1]=1; assert(title(1,16,'Quest')=='[16] (4,400+) Quest')
        itemRewards[1]=0; itemChoices[1]=3
        assert(title(1,16,'Quest')=='[16] (4,400+) Quest')
        itemRewards[1]=2; assert(title(1,16,'Quest')=='[16] (4,400+) Quest')
        itemRewards[1]=0; itemChoices[1]=0
        assert(title(1,16,'Quest')=='[16] (4,400) Quest')
        xp[1]=0; itemRewards[1]=1; assert(title(1,16,'Quest')=='[16] (0+) Quest')
        ''')

    def test_missing_item_api_does_not_hide_xp_and_toggle_removes_plus(self):
        self.lua.execute('''
        emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL(); xp[1]=4400
        GetNumQuestLogRewards=function() error('unavailable') end
        GetNumQuestLogChoices=nil
        assert(title(1,16,'Quest')=='[16] (4,400) Quest')
        GetNumQuestLogRewards=function(id) assert(id==1); return 1 end
        assert(title(1,16,'Quest')=='[16] (4,400+) Quest')
        clickSetting(5,false); assert(title(1,16,'Quest')=='[16] Quest')
        ''')
