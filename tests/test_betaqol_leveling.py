"""Login rank reminders and native mouse-wheel behavior, without actionbar writes."""
import unittest
import xml.etree.ElementTree as ET

from test_forever_quick_accept import HOST, SOURCE, ROOT, LuaRuntime
from settings_ui import UI_ENGINE
from test_betaqol_popups import native_between

SCROLL = native_between(
    'Blizzard_ChatFrameBase/Mainline/FloatingChatFrame.lua',
    'function FloatingChatFrame_OnMouseScroll(',
    '\nend') + '\nend\n'
MODERN_SCROLL = 'ScrollUtil={}\n' + native_between(
    'Blizzard_SharedXML/Shared/Scroll/ScrollUtil.lua',
    'function ScrollUtil.InitScrollingMessageFrameWithScrollBar(',
    '-- Compatible with "ScrollFrameTemplate"')

ENGINE = r'''
combat=false
function InCombatLockdown() return combat end
function hooksecurefunc(name,callback)
    local old=_G[name]
    _G[name]=function(...) old(...); callback(...) end
end
messages={}
function print(message) messages[#messages+1]=message end
Enum.SpellBookSpellBank={Player=0}
Enum.SpellBookSkillLineIndex={General=1}
Enum.ActionBarSet={Mkb=1,Gamepad=2,All=3}
Enum.SpellBookItemType={Spell=1,FutureSpell=2}
book={
 {actionID=100,spellID=100,itemType=1,name='Heal',subName='Rank 1',low=true},
 {actionID=101,spellID=101,itemType=1,name='Heal',subName='Rank 2'},
 {actionID=200,spellID=200,itemType=1,name='Smite',subName='Rank 1',low=true},
 {actionID=201,spellID=201,itemType=1,name='Smite',subName='Rank 2'},
}
actions={[1]={'spell',100},[2]={'spell',100},[180]={'spell',200}}
C_SpellBook={
 GetNumSpellBookSkillLines=function() assert(not combat); return 2 end,
 GetSpellBookSkillLineInfo=function(line) return {itemIndexOffset=0,numSpellBookItems=line==1 and 0 or #book} end,
 GetSpellBookItemInfo=function(i,bank) assert(bank==0); return book[i] end,
 IsSpellBookItemLowRank=function(i) return book[i].low or false end,
}
C_ActionBar={FindSpellActionButtons=function(id,barSet)
 assert(barSet==Enum.ActionBarSet.Mkb)
 local slots={}; for slot,a in pairs(actions) do
   if a[2]==id then slots[#slots+1]=slot end
 end; return slots
end}
function GetActionInfo(slot) return unpack(actions[slot]) end
function PlaceAction() error('Must never change actionbars') end
function PickupSpell() error('Must never change cursor') end
chat=CreateFrame('ScrollingMessageFrame'); chat.position=20
CHAT_FRAMES={'ChatFrame1'}; ChatFrame1=chat
function chat:ScrollByAmount(amount) self.position=math.max(0,math.min(100,self.position+amount)) end
function chat:GetInsertMode() return 'BOTTOM' end
SCROLLING_MESSAGE_FRAME_INSERT_MODE_TOP='TOP'
function chat:ScrollUp() self.position=math.min(100,self.position+1) end
function chat:ScrollDown() self.position=math.max(0,self.position-1) end
'''


class LevelingFeatures(unittest.TestCase):
    def make(self, saved=''):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(HOST+UI_ENGINE+ENGINE+SCROLL)
        lua.execute("chat:SetScript('OnMouseWheel',FloatingChatFrame_OnMouseScroll); function wheel(delta) chat:GetScript('OnMouseWheel')(chat,delta) end")
        lua.execute("BetaQoLDB={missingSpellCheck=false}")
        lua.execute(saved)
        lua.execute(SOURCE.read_text(encoding='utf-8'))
        lua.execute("emit('ADDON_LOADED','BetaQoL')")
        return lua

    def test_login_lists_each_spell_once_including_nonstandard_slots(self):
        lua=self.make()
        lua.execute('''
        emit('PLAYER_ENTERING_WORLD',true,false); runTimers()
        assert(#messages==2)
        assert(messages[1]:find('Heal') and messages[1]:find('Rank 2'))
        assert(messages[2]:find('Smite'))
        emit('PLAYER_ENTERING_WORLD',false,false); emit('SPELLS_CHANGED'); runTimers()
        assert(#messages==2)
        ''')

    def test_highest_rank_present_suppresses_all_lower_copies(self):
        lua=self.make()
        lua.execute("actions={[1]={'spell',100},[2]={'spell',101},[3]={'spell',201}}; emit('PLAYER_ENTERING_WORLD',true,false); runTimers(); assert(#messages==0)")

    def test_multiple_old_ranks_produce_one_reminder_for_highest_learned(self):
        lua=self.make()
        lua.execute('''
        book[2].low=true
        book[#book+1]={actionID=102,spellID=102,itemType=1,name='Heal',subName='Rank 3'}
        actions={[1]={'spell',100},[2]={'spell',101},[3]={'spell',101}}
        emit('PLAYER_ENTERING_WORLD',true,false); runTimers()
        assert(#messages==1 and messages[1]:find('Heal') and messages[1]:find('Rank 3'))
        ''')

    def test_base_action_alias_is_not_evidence_of_a_specific_rank(self):
        lua=self.make()
        lua.execute('''
        book[2].actionID=100
        actions={[1]={'spell',100}}
        emit('PLAYER_ENTERING_WORLD',true,false); runTimers()
        assert(#messages==1 and messages[1]:find('Heal'))
        ''')

    def test_live_report_with_gamepad_starter_ranks_and_broad_candidate_results(self):
        lua=self.make()
        lua.execute('''
        book={
          {actionID=2050,spellID=2050,itemType=1,name='Lesser Heal',subName='Rank 1',low=true},
          {actionID=2052,spellID=2052,itemType=1,name='Lesser Heal',subName='Rank 2',low=true},
          {actionID=2053,spellID=2053,itemType=1,name='Lesser Heal',subName='Rank 3'},
          {actionID=585,spellID=585,itemType=1,name='Smite',subName='Rank 1',low=true},
          {actionID=598,spellID=598,itemType=1,name='Smite',subName='Rank 3'},
        }
        actions={[1]={'spell',598},[61]={'spell',2052},[62]={'spell',2053},
          [197]={'spell',2050},[200]={'spell',585}}
        C_ActionBar.FindSpellActionButtons=function(id,set)
          if set==Enum.ActionBarSet.Mkb then return {1,61,62} end
          return {1,61,62,197,200}
        end
        emit('PLAYER_ENTERING_WORLD',true,false); runTimers(); assert(#messages==0)
        -- A spell absent from mouse/keyboard bars must not be revived by gamepad storage.
        actions[1]={'macro',1}; actions[62]={'spell',2052}
        emit('PLAYER_ENTERING_WORLD',false,true); runTimers()
        assert(#messages==1 and messages[1]:find('Lesser Heal') and messages[1]:find('Rank 3'))
        ''')

    def test_highest_ranks_and_unplaced_spells_do_not_warn(self):
        lua=self.make()
        lua.execute("actions={[1]={'spell',101},[2]={'macro',200}}; emit('PLAYER_ENTERING_WORLD',true,false); runTimers(); assert(#messages==0)")

    def test_only_low_exact_rank_warns_not_family_match_passive_or_future(self):
        lua=self.make()
        lua.execute('''
        actions={[1]={'spell',101},[2]={'spell',200}}
        C_ActionBar.FindSpellActionButtons=function() return {1,2} end
        book[3].isPassive=true
        emit('PLAYER_ENTERING_WORLD',true,false); runTimers(); assert(#messages==0)
        ''')

    def test_reload_checks_once_and_combat_defers_without_querying(self):
        lua=self.make()
        lua.execute('''
        combat=true; emit('PLAYER_ENTERING_WORLD',false,true); runTimers()
        assert(#messages==0)
        combat=false; emit('PLAYER_REGEN_ENABLED'); runTimers(); assert(#messages==2)
        emit('PLAYER_REGEN_ENABLED'); runTimers(); assert(#messages==2)
        ''')

    def test_saved_off_and_missing_api_are_quiet(self):
        for setup in ('BetaQoLDB={lowSpellReminder=false}', 'C_SpellBook=nil'):
            lua=self.make(setup)
            lua.execute("emit('PLAYER_ENTERING_WORLD',true,false); runTimers(); assert(#messages==0)")

    def test_turning_off_before_delayed_scan_suppresses_messages(self):
        lua=self.make()
        lua.execute("emit('PLAYER_ENTERING_WORLD',true,false); SlashCmdList.QOL(); clickSetting(18,false); runTimers(); assert(#messages==0)")

    def test_community_guild_window_keeps_native_three_lines(self):
        xml=ET.parse(ROOT / '.test-ui/Blizzard_Communities/CommunitiesChatFrame.xml')
        handler=next(node.text for node in xml.iter() if node.tag.endswith('OnMouseWheel'))
        lua=self.make()
        lua.execute('community={position=0}; function community:ScrollByAmount(n) self.position=self.position+n end')
        lua.execute('function communityWheel(self,delta) '+handler+' end')
        lua.execute('''
        communityWheel(community,1); assert(community.position==3)
        SlashCmdList.QOL(); clickSetting(17,false)
        communityWheel(community,-1); assert(community.position==0)
        ''')

    def test_chat_scrolls_three_lines_and_toggle_restores_one(self):
        lua=self.make()
        lua.execute('''
        wheel(1); assert(chat.position==23)
        wheel(-1); assert(chat.position==20)
        emit('ADDON_LOADED','Another'); emit('PLAYER_LOGIN')
        wheel(1); assert(chat.position==23)
        SlashCmdList.QOL(); clickSetting(17,false)
        wheel(1); assert(chat.position==24)
        clickSetting(17,true)
        chat.position=1; wheel(-1); assert(chat.position==0)
        ''')

    def test_saved_chat_setting_and_late_native_function(self):
        lua=self.make('BetaQoLDB={fasterChatScroll=false}')
        lua.execute('wheel(1); assert(chat.position==21)')
        lua=self.make('CHAT_FRAMES={}; ChatFrame1=nil')
        lua.execute('''
        CHAT_FRAMES={'ChatFrame1'}; ChatFrame1=chat; emit('ADDON_LOADED','Blizzard_ChatFrameBase')
        wheel(1); assert(chat.position==23)
        ''')

    def test_actual_modern_native_handler_is_not_multiplied_and_is_restored(self):
        setup = MODERN_SCROLL + r'''
        function NegateIf(n,invert) return invert and -n or n end
        function chat:EnableMouseWheel() end
        function chat:AddOnDisplayRefreshedCallback() end
        BaseScrollBoxEvents={OnScroll='OnScroll'}
        local bar={EnableInternalPriority=function() end,EnableSnapToInterval=function() end,RegisterCallback=function() end}
        ScrollUtil.InitScrollingMessageFrameWithScrollBar(chat,bar,false)
        nativeWheel=chat:GetScript('OnMouseWheel')
        '''
        lua=self.make(setup)
        lua.execute('''
        assert(chat:GetScript('OnMouseWheel')~=nativeWheel)
        wheel(1); assert(chat.position==23)
        wheel(-1); assert(chat.position==20)
        SlashCmdList.QOL(); clickSetting(17,false)
        assert(chat:GetScript('OnMouseWheel')==nativeWheel)
        wheel(1); assert(chat.position==23)
        clickSetting(17,true)
        function chat:GetInsertMode() return 'TOP' end
        wheel(1); assert(chat.position==20)
        ''')
