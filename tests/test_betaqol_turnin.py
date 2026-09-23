"""Quest turn-in flow with a simulated quest journal and server events."""
import unittest

from test_forever_quick_accept import HOST, SOURCE, LuaRuntime
from settings_ui import UI_ENGINE

ENGINE = r'''
activeQuests, selectedActive, rewards, progressRequests = {}, {}, {}, {}
rewardChoices, requiredMoney, currentQuestID, completable = 0, 0, 0, false
function C_GossipInfo.GetActiveQuests() return activeQuests end
function C_GossipInfo.SelectActiveQuest(id)
    for _,q in ipairs(activeQuests) do
        if q.questID==id then
            assert(q.isComplete and not q.isIgnored, 'Selected unfinished/ignored quest')
            currentQuestID=id; completable=true
            selectedActive[#selectedActive+1]=id
            queue[#queue+1]='QUEST_PROGRESS'
            return
        end
    end
    error('Modern gossip needs a quest ID, not an index')
end
function GetNumActiveQuests() return #activeQuests end
function GetActiveTitle(index)
    local q=assert(activeQuests[index]); return q.title or 'Quest', q.isComplete
end
function SelectActiveQuest(index)
    local q=assert(activeQuests[index], 'Legacy greeting needs an index')
    C_GossipInfo.SelectActiveQuest(q.questID)
end
function GetQuestID() return currentQuestID end
function IsQuestCompletable() return completable end
function GetNumQuestChoices() return rewardChoices end
function GetQuestMoneyToGet() return requiredMoney end
function CompleteQuest()
    assert(completable and currentQuestID>0, 'Advanced an incomplete quest')
    progressRequests[#progressRequests+1]=currentQuestID
    queue[#queue+1]='QUEST_COMPLETE'
end
function GetQuestReward(choice)
    assert(currentQuestID>0 and rewardChoices<=1, 'Selected a reward for the player')
    assert(choice==rewardChoices, 'Wrong reward index for zero/one reward')
    assert(requiredMoney==0, 'Skipped the native gold confirmation')
    rewards[#rewards+1]={id=currentQuestID,choice=choice}
    if finishSynchronously then emit('QUEST_FINISHED') end
end
'''


class TurnInBehaviour(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST + UI_ENGINE + ENGINE)
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))

    def test_modern_gossip_selects_one_completed_quest_before_new_offers(self):
        self.lua.execute('''
        activeQuests={{questID=11,isComplete=false},{questID=22,isComplete=true,isIgnored=true},
            {questID=33,isComplete=true},{questID=44,isComplete=true}}
        offers={{questID=9173}}
        emit('GOSSIP_SHOW')
        assert(#selectedActive==1 and selectedActive[1]==33 and #choices==0)
        drain(); assert(#rewards==1 and rewards[1].id==33)
        ''')

    def test_legacy_greeting_uses_active_index(self):
        self.lua.execute('''
        activeQuests={{questID=31,isComplete=false},{questID=97,isComplete=true}}
        emit('QUEST_GREETING'); drain()
        assert(#rewards==1 and rewards[1].id==97)
        ''')

    def test_direct_progress_reaches_reward_without_choice(self):
        self.lua.execute('''
        currentQuestID=31; completable=true; emit('QUEST_PROGRESS'); drain()
        assert(#progressRequests==1 and #rewards==1 and rewards[1].choice==0)
        ''')

    def test_only_reward_is_collected_automatically(self):
        self.lua.execute('''
        currentQuestID=31; rewardChoices=1; emit('QUEST_COMPLETE')
        assert(#rewards==1 and rewards[1].choice==1)
        ''')

    def test_multiple_rewards_and_gold_cost_remain_manual(self):
        self.lua.execute('''
        currentQuestID=31; rewardChoices=2; emit('QUEST_COMPLETE'); assert(#rewards==0)
        rewardChoices=0; requiredMoney=100; emit('QUEST_COMPLETE'); assert(#rewards==0)
        ''')

    def test_incomplete_quest_and_missing_npc_are_not_advanced(self):
        self.lua.execute('''
        currentQuestID=31; emit('QUEST_PROGRESS'); assert(#progressRequests==0)
        npcGUID=nil; completable=true; emit('QUEST_PROGRESS'); emit('QUEST_COMPLETE')
        assert(#progressRequests==0 and #rewards==0)
        ''')

    def test_shift_latches_for_turnin_after_release_and_clears_on_new_conversation(self):
        self.lua.execute('''
        currentQuestID=31; completable=true; shift=true; emit('GOSSIP_SHOW')
        emit('GOSSIP_CLOSED',true); shift=false; emit('QUEST_PROGRESS'); emit('QUEST_COMPLETE')
        assert(#rewards==0 and #progressRequests==0)
        emit('QUEST_FINISHED'); emit('GOSSIP_CLOSED',false); runTimers()
        emit('QUEST_PROGRESS'); drain(); assert(#rewards==1)
        ''')

    def test_shift_pressed_at_reward_page_prevents_collection(self):
        self.lua.execute('''
        currentQuestID=31; completable=true; emit('QUEST_PROGRESS')
        shift=true; drain(); shift=false; emit('QUEST_COMPLETE')
        assert(#progressRequests==1 and #rewards==0)
        ''')

    def test_turnin_enabled_with_accept_disabled_and_vice_versa(self):
        self.lua.execute('''
        SlashCmdList.QOL(); clickSetting(1,false)
        activeQuests={{questID=31,isComplete=true}}; emit('GOSSIP_SHOW'); drain()
        assert(#rewards==1)
        emit('QUEST_FINISHED'); clickSetting(2,false); clickSetting(1,true)
        currentQuestID=32; emit('QUEST_PROGRESS'); emit('QUEST_COMPLETE'); assert(#rewards==1)
        offers={{questID=9173}}; emit('GOSSIP_SHOW'); drain(); assert(journal[9173])
        ''')

    def test_disabling_between_progress_and_reward_stops_turnin(self):
        self.lua.execute('''
        SlashCmdList.QOL(); currentQuestID=31; completable=true; emit('QUEST_PROGRESS')
        clickSetting(2,false); drain(); assert(#rewards==0)
        ''')

    def test_duplicate_events_do_not_resend_and_reopening_allows_retry(self):
        self.lua.execute('''
        currentQuestID=31; completable=true
        emit('QUEST_PROGRESS'); emit('QUEST_PROGRESS'); drain(); emit('QUEST_COMPLETE')
        assert(#progressRequests==1 and #rewards==1)
        emit('QUEST_FINISHED'); emit('QUEST_COMPLETE'); assert(#rewards==2)
        ''')

    def test_consecutive_quests_and_synchronous_finish_are_independent(self):
        self.lua.execute('''
        finishSynchronously=true; currentQuestID=31; emit('QUEST_COMPLETE')
        currentQuestID=32; emit('QUEST_COMPLETE')
        assert(#rewards==2 and rewards[1].id==31 and rewards[2].id==32)
        ''')

    def test_existing_preferences_survive_upgrade_and_turnin_defaults_on(self):
        self.lua.execute('''
        BetaQoLDB={autoAccept=false,fastLoot=false,enterConfirm=false,rangeColor=false}
        emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()
        assert(#checkboxes==9 and checkboxes[2]:GetChecked() and BetaQoLDB.autoTurnIn and checkboxes[6]:GetChecked() and checkboxes[7]:GetChecked())
        assert(not checkboxes[1]:GetChecked() and not checkboxes[3]:GetChecked()
            and not checkboxes[4]:GetChecked() and not checkboxes[5]:GetChecked())
        ''')
