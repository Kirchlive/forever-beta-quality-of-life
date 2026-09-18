from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
from lupa.lua51 import LuaRuntime

SOURCE = ROOT / 'BetaQoL.lua'

# WoW is unavailable here. The external API fixture models a quest offer and
# journal, rejects wrong IDs/indexes and duplicate acceptance, and queues events.
HOST = r'''
frames, queue, journal, choices = {}, {}, {}, {}
offers, current, shift, pvp, automatic, adventure, dialogOpen = {}, 9173, false, false, false, false, true
SlashCmdList = {}
timers, activeInteractions = {}, {}
npcGUID, replacing = 'Creature-Questgiver-A', false
Enum = { PlayerInteractionType = { Gossip = 3, QuestGiver = 4, Merchant = 5 }, LootSlotType = { None = 0, Item = 1, Money = 2, Currency = 3 } }
C_Timer = { After = function(_, callback) timers[#timers+1] = callback end }
C_PlayerInteractionManager = {
    IsInteractingWithNpcOfType = function(kind) return activeInteractions[kind] or false end,
    IsReplacingUnit = function() return replacing end,
}
function UnitGUID(unit)
    assert(unit == 'npc' or unit == 'questnpc')
    return npcGUID
end
function runTimers()
    local pending = timers
    timers = {}
    for _, callback in ipairs(pending) do callback() end
end
function print() end
function CreateFrame()
    local f = { events = {}, scripts = {} }
    function f:RegisterEvent(e) self.events[e] = true end
    function f:UnregisterEvent(e) self.events[e] = nil end
    function f:SetScript(e, fn) self.scripts[e] = fn; if e == 'OnEvent' then self.handler = fn end end
    function f:GetScript(e) return self.scripts[e] end
    frames[#frames+1] = f
    return f
end
function emit(e, ...)
    local arg = ...
    if e == 'GOSSIP_SHOW' then activeInteractions[3] = true end
    if e == 'QUEST_GREETING' or e == 'QUEST_DETAIL' or e == 'QUEST_PROGRESS' or e == 'QUEST_COMPLETE' then
        activeInteractions[4] = true
    end
    if e == 'GOSSIP_CLOSED' then activeInteractions[3] = false end
    if e == 'QUEST_FINISHED' then activeInteractions[4] = false end
    if e == 'PLAYER_INTERACTION_MANAGER_FRAME_HIDE' then activeInteractions[arg] = false end
    for _, f in ipairs(frames) do
        if f.events[e] then f.handler(f, e, ...) end
    end
end
function drain()
    while #queue > 0 do
        local event = table.remove(queue, 1)
        emit(event)
    end
end
function IsShiftKeyDown() return shift end
function QuestFlagsPVP() return pvp end
function QuestGetAutoAccept() return automatic end
function QuestIsFromAdventureMap() return adventure end
function AcceptQuest()
    assert(current, 'No current quest offer')
    assert(not journal[current], 'Quest accepted twice')
    journal[current] = true
end
function CloseQuest() dialogOpen = false end
C_GossipInfo = {}
function C_GossipInfo.GetActiveQuests() return {} end
function GetNumActiveQuests() return 0 end
function GetQuestID() return 0 end
function IsQuestCompletable() return false end
function GetNumQuestChoices() return 0 end
function GetQuestMoneyToGet() return 0 end
function C_GossipInfo.GetAvailableQuests()
    local result = {}
    for _, q in ipairs(offers) do
        if not journal[q.questID] then result[#result+1] = q end
    end
    return result
end
function C_GossipInfo.SelectAvailableQuest(id)
    for _, q in ipairs(C_GossipInfo.GetAvailableQuests()) do
        if q.questID == id then
            current = id
            choices[#choices+1] = id
            queue[#queue+1] = 'QUEST_DETAIL'
            return
        end
    end
    error('Invalid quest ID (modern gossip takes a quest ID, not an index)')
end
function GetNumAvailableQuests() return #offers end
function SelectAvailableQuest(index)
    assert(index == 1, 'Invalid legacy quest index')
    current = offers[index].questID
    queue[#queue+1] = 'QUEST_DETAIL'
end
function CompleteQuest() error('No active turn-in in this fixture') end
function GetQuestReward() error('No active turn-in in this fixture') end
loot, inventory, lootCalls, now = {}, {}, {}, 0
blockedLoot, reentrantLoot = false, false
function GetTime() return now end
function GetNumLootItems() return #loot end
function GetLootSlotType(slot) return loot[slot] and 1 or 0 end
function GetLootSlotInfo(slot) return 1, 'Item', 1, nil, 1, false end
function GetCVarBool() return true end
function IsModifiedClick() return false end
function LootSlot(slot)
    assert(loot[slot], 'Invalid loot slot: an ascending loop can skip items')
    lootCalls[#lootCalls+1] = slot
    if reentrantLoot then
        reentrantLoot = false
        emit('LOOT_READY', true)
    end
    if not blockedLoot then
        inventory[#inventory+1] = table.remove(loot, slot)
    end
end
function CloseLoot() error('The native loot window must remain available') end
function ConfirmLootSlot() error('Loot confirmations must remain manual') end
function SetCVar() error('Native loot preferences must not be changed') end
'''

class QuestBehaviour(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST)
        self.lua.execute(SOURCE.read_text(encoding='utf-8') if SOURCE.exists() else '')

    def run_lua(self, source):
        self.lua.execute(source)

    def test_normal_offer_reaches_journal(self):
        self.run_lua("emit('QUEST_DETAIL'); assert(journal[9173], 'Normal offer was not accepted')")

    def test_modern_gossip_uses_ids_one_offer_at_a_time(self):
        self.run_lua('''
        offers={{questID=9173,isIgnored=false},{questID=9468,isIgnored=false}}
        emit('GOSSIP_SHOW')
        assert(#choices == 1, 'Must select one offer before waiting for its detail')
        drain(); assert(journal[9173] and not journal[9468])
        emit('GOSSIP_SHOW'); drain()
        assert(journal[9468], 'Second offer was not accepted on the next greeting')
        ''')

    def test_legacy_greeting_uses_index(self):
        self.run_lua("offers={{questID=9468}}; emit('QUEST_GREETING'); drain(); assert(journal[9468])")

    def test_shift_pauses_selection_and_acceptance(self):
        self.run_lua("shift=true; offers={{questID=9173}}; emit('GOSSIP_SHOW'); emit('QUEST_DETAIL'); assert(#choices==0 and not journal[9173])")

    def test_toggle_can_stop_and_resume_acceptance(self):
        self.run_lua("assert(SlashCmdList.BETAQOL, 'Toggle missing'); SlashCmdList.BETAQOL(); emit('QUEST_DETAIL'); assert(not journal[9173]); SlashCmdList.BETAQOL(); emit('QUEST_DETAIL'); assert(journal[9173])")

    def test_autoaccepted_quest_is_not_accepted_twice(self):
        self.run_lua("automatic=true; journal[9173]=true; emit('QUEST_DETAIL'); assert(not dialogOpen, 'Already accepted offer must close')")

    def test_pvp_confirmation_remains_manual(self):
        self.run_lua("pvp=true; emit('QUEST_DETAIL'); assert(not journal[9173])")

    def test_item_and_adventure_offers_keep_their_default_flow(self):
        self.run_lua("emit('QUEST_DETAIL',12345); assert(not journal[9173]); adventure=true; emit('QUEST_DETAIL'); assert(not journal[9173])")

    def test_ignored_quest_is_not_selected(self):
        self.run_lua("offers={{questID=9173,isIgnored=true},{questID=9468,isIgnored=false}}; emit('GOSSIP_SHOW'); drain(); assert(not journal[9173] and journal[9468])")

    def test_empty_npc_and_turnin_do_nothing(self):
        self.run_lua("emit('GOSSIP_SHOW'); emit('QUEST_GREETING'); emit('QUEST_PROGRESS'); emit('QUEST_COMPLETE'); assert(not journal[9173] and #choices==0)")

    def test_native_auto_loot_collects_all_slots_immediately(self):
        self.run_lua("loot={101,202,303}; emit('LOOT_READY',true); assert(#loot==0 and #inventory==3, 'Loot was not collected on readiness'); assert(inventory[1]==303 and inventory[3]==101)")

    def test_native_manual_loot_is_untouched(self):
        self.run_lua("loot={101,202}; emit('LOOT_READY',false); assert(#loot==2 and #lootCalls==0)")

    def test_native_auto_loot_is_independent_of_quest_pause(self):
        self.run_lua("shift=true; SlashCmdList.BETAQOL(); loot={101}; emit('LOOT_READY',true); assert(inventory[1]==101, 'Quest pause must not override the native autoloot decision')")

    def test_empty_readiness_does_not_delay_later_loot(self):
        self.run_lua("emit('LOOT_READY',true); loot={101}; emit('LOOT_READY',true); assert(inventory[1]==101)")

    def test_duplicate_ready_events_are_throttled_without_hiding_blocked_loot(self):
        self.run_lua("blockedLoot=true; loot={101}; emit('LOOT_READY',true); emit('LOOT_READY',true); assert(#lootCalls==1 and #loot==1); now=0.11; emit('LOOT_READY',true); assert(#lootCalls==2)")

    def test_next_loot_window_is_not_delayed_by_previous_throttle(self):
        self.run_lua("loot={101}; emit('LOOT_READY',true); emit('LOOT_CLOSED'); loot={202}; emit('LOOT_READY',true); assert(#inventory==2 and inventory[2]==202)")

    def test_reentrant_readiness_does_not_duplicate_requests(self):
        self.run_lua("loot={101,202}; reentrantLoot=true; emit('LOOT_READY',true); assert(#inventory==2 and #lootCalls==2)")

    def test_shift_at_gossip_open_persists_after_key_release_and_page_transition(self):
        self.run_lua("shift=true; emit('GOSSIP_SHOW'); emit('GOSSIP_CLOSED',true); emit('PLAYER_INTERACTION_MANAGER_FRAME_HIDE',3); runTimers(); shift=false; emit('QUEST_DETAIL'); assert(not journal[9173], 'Releasing Shift must not resume during the conversation')")

    def test_shift_at_direct_quest_open_persists_until_dialog_closes(self):
        self.run_lua("shift=true; emit('QUEST_DETAIL'); shift=false; emit('QUEST_DETAIL'); assert(not journal[9173]); emit('QUEST_FINISHED'); runTimers(); emit('QUEST_DETAIL'); assert(journal[9173], 'Reopening normally must resume autoaccept')")

    def test_closed_gossip_does_not_pause_next_conversation_with_same_npc(self):
        self.run_lua("shift=true; emit('GOSSIP_SHOW'); shift=false; emit('GOSSIP_CLOSED',false); runTimers(); offers={{questID=9173}}; emit('GOSSIP_SHOW'); drain(); assert(journal[9173])")

    def test_shift_pause_survives_manual_accept_then_another_offer(self):
        self.run_lua("shift=true; emit('QUEST_DETAIL'); shift=false; journal[9173]=true; emit('QUEST_FINISHED'); current=9468; emit('QUEST_DETAIL'); runTimers(); emit('QUEST_DETAIL'); assert(not journal[9468], 'Finishing one page must not clear the conversation pause')")

    def test_shift_pause_survives_quest_finish_while_gossip_interaction_is_active(self):
        self.run_lua("shift=true; emit('GOSSIP_SHOW'); emit('QUEST_DETAIL'); shift=false; emit('QUEST_FINISHED'); runTimers(); current=9468; emit('QUEST_DETAIL'); assert(not journal[9468])")

    def test_switching_to_another_npc_starts_unpaused(self):
        self.run_lua("shift=true; emit('QUEST_DETAIL'); shift=false; npcGUID='Creature-Questgiver-B'; current=9468; emit('QUEST_DETAIL'); assert(journal[9468])")

    def test_shift_opened_turnin_also_pauses_a_followup_quest(self):
        self.run_lua("shift=true; emit('QUEST_COMPLETE'); shift=false; emit('QUEST_FINISHED'); emit('QUEST_DETAIL'); runTimers(); assert(not journal[9173])")

    def test_world_transition_clears_conversation_pause(self):
        self.run_lua("shift=true; emit('QUEST_DETAIL'); shift=false; emit('PLAYER_ENTERING_WORLD'); emit('QUEST_DETAIL'); assert(journal[9173])")

if __name__ == '__main__':
    unittest.main(verbosity=2)
