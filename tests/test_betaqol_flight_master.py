"""Flight-map gossip selection, with the client's option fields and index API."""
import unittest

from test_forever_quick_accept import HOST, SOURCE, LuaRuntime
from settings_ui import UI_ENGINE

ENGINE = r'''
Enum.GossipOptionStatus = {Available=0, Unavailable=1, Locked=2}
options, selectedOptions = {}, {}
function C_GossipInfo.GetOptions() return options end
function C_GossipInfo.SelectOptionByIndex(index, text, confirmed)
    assert(text==nil and confirmed==nil, 'Must preserve native confirmations')
    selectedOptions[#selectedOptions+1]=index
end
function TakeTaxiNode() error('Must not choose or pay for a flight') end
function flightOption(index)
    return {orderIndex=index, gossipOptionID=8000+index, icon=132057,
            name='Ich brauche einen Flug.', status=0}
end
'''


class FlightMasterBehaviour(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST + UI_ENGINE + ENGINE)
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))
        self.lua.execute("emit('ADDON_LOADED','BetaQoL')")

    def test_selects_localized_taxi_by_native_order_index_not_array_or_option_id(self):
        self.lua.execute('''
        options={{orderIndex=2,icon=132060,status=0},flightOption(7)}
        options[2].gossipOptionID=nil
        emit('GOSSIP_SHOW')
        assert(#selectedOptions==1 and selectedOptions[1]==7)
        ''')

    def test_unavailable_locked_and_non_taxi_options_remain_manual(self):
        self.lua.execute('''
        options={flightOption(1)}
        for _,status in ipairs({1,2,3}) do
            options[1].status=status; emit('GOSSIP_SHOW')
        end
        options={{orderIndex=3,icon=132060,status=0,name='I need a ride.'}}
        emit('GOSSIP_SHOW'); assert(#selectedOptions==0)
        options={flightOption(7)}; emit('GOSSIP_SHOW'); assert(selectedOptions[1]==7)
        ''')

    def test_devrak_live_option_with_zero_order_index_opens_map_once(self):
        self.lua.execute('''
        npcGUID='Creature-0-6783-1-395-3615-000036BBC1'
        options={{rewards={},flags=0,gossipOptionID=95583,name='I need a ride.',
                  status=0,orderIndex=0,icon=132057,selectOptionWhenOnlyOption=false}}
        emit('GOSSIP_SHOW'); emit('GOSSIP_SHOW')
        assert(#selectedOptions==1 and selectedOptions[1]==0)
        ''')

    def test_saved_off_and_independent_toggle(self):
        self.lua.execute('''
        SlashCmdList.QOL(); clickSetting(14,false)
        options={flightOption(4)}; emit('GOSSIP_SHOW'); assert(#selectedOptions==0)
        clickSetting(1,false); clickSetting(2,false); clickSetting(14,true)
        emit('GOSSIP_SHOW'); assert(selectedOptions[1]==4)
        ''')

    def test_shift_keeps_dialog_manual_until_conversation_ends(self):
        self.lua.execute('''
        options={flightOption(4)}; shift=true; emit('GOSSIP_SHOW')
        shift=false; emit('GOSSIP_SHOW'); assert(#selectedOptions==0)
        emit('GOSSIP_CLOSED',false); runTimers()
        emit('GOSSIP_SHOW'); assert(selectedOptions[1]==4)
        ''')

    def test_duplicate_events_select_once_but_reopening_allows_selection(self):
        self.lua.execute('''
        options={flightOption(4)}; emit('GOSSIP_SHOW'); emit('GOSSIP_SHOW')
        assert(#selectedOptions==1)
        emit('GOSSIP_CLOSED',false); emit('GOSSIP_SHOW')
        assert(#selectedOptions==2)
        npcGUID='Creature-Other'; emit('GOSSIP_SHOW'); assert(#selectedOptions==3)
        ''')

    def test_quest_offer_keeps_priority_over_flight_map(self):
        self.lua.execute('''
        options={flightOption(4)}; offers={{questID=9173}}
        emit('GOSSIP_SHOW'); assert(#choices==1 and #selectedOptions==0)
        drain(); emit('GOSSIP_SHOW'); assert(selectedOptions[1]==4)
        ''')

    def test_missing_api_or_invalid_index_leaves_dialog_available(self):
        self.lua.execute('''
        options={flightOption(4)}; options[1].orderIndex=nil
        emit('GOSSIP_SHOW'); assert(#selectedOptions==0)
        C_GossipInfo.GetOptions=nil; emit('GOSSIP_SHOW')
        assert(#selectedOptions==0)
        ''')
