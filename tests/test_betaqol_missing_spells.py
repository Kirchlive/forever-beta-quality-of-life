"""Missing-spell checks are independent of rank checks and ignore General."""
import unittest
import test_betaqol_leveling as leveling


class MissingSpells(unittest.TestCase):
    def make(self, setup=''):
        return leveling.LevelingFeatures().make('BetaQoLDB={lowSpellReminder=false,missingSpellCheck=true}; '+setup)

    def test_missing_spell_warns_once_per_family_with_yellow_prefix(self):
        lua=self.make("actions={[1]={'spell',100}}")
        lua.execute('''
        emit('PLAYER_ENTERING_WORLD',true,false); runTimers()
        assert(#messages==1 and messages[1]=='|cffffd100BetaQoL:|r Smite not in actionbar.')
        emit('PLAYER_ENTERING_WORLD',false,false); emit('SPELLS_CHANGED'); runTimers()
        assert(#messages==1)
        ''')

    def test_any_placed_rank_counts_even_without_highest(self):
        lua=self.make()
        lua.execute("emit('PLAYER_ENTERING_WORLD',false,true); runTimers(); assert(#messages==0)")

    def test_general_passive_future_and_offspec_are_excluded(self):
        lua=self.make('''
        actions={}
        C_SpellBook.GetSpellBookSkillLineInfo=function(line)
          return line==1 and {itemIndexOffset=0,numSpellBookItems=2} or {itemIndexOffset=2,numSpellBookItems=2}
        end
        book[3].isPassive=true; book[4].isPassive=true
        book[5]={actionID=300,spellID=300,itemType=2,name='Future'}
        book[6]={actionID=400,spellID=400,itemType=1,name='Offspec',isOffSpec=true}
        local original=C_SpellBook.GetSpellBookSkillLineInfo
        C_SpellBook.GetSpellBookSkillLineInfo=function(line)
          local data=original(line); if line==2 then data.numSpellBookItems=4 end; return data
        end
        ''')
        lua.execute("emit('PLAYER_ENTERING_WORLD',true,false); runTimers(); assert(#messages==0)")

    def test_independent_toggles_and_red_rank_message(self):
        lua=self.make("BetaQoLDB.lowSpellReminder=true; actions={[1]={'spell',100}}")
        lua.execute('''
        emit('PLAYER_ENTERING_WORLD',true,false); runTimers()
        assert(#messages==2)
        assert(messages[1]=='|cffff0000BetaQoL:|r Heal Rank 2 available. Check your spellbook.')
        assert(messages[2]=='|cffffd100BetaQoL:|r Smite not in actionbar.')
        SlashCmdList.QOL()
        assert(checkboxes[18].Text.text=='Low Spell Rank Check |cff999999(at launch)|r')
        assert(checkboxes[19].Text.text=='Missing Spell Check |cff999999(at launch)|r')
        clickSetting(19,false); messages={}
        emit('PLAYER_ENTERING_WORLD',false,true); runTimers()
        assert(#messages==1 and messages[1]:find('Heal'))
        clickSetting(18,false); messages={}
        emit('PLAYER_ENTERING_WORLD',false,true); runTimers(); assert(#messages==0)
        ''')

    def test_combat_defers_and_disabled_pending_check_stays_quiet(self):
        lua=self.make('actions={}; combat=true')
        lua.execute('''
        emit('PLAYER_ENTERING_WORLD',true,false); runTimers(); assert(#messages==0)
        combat=false; emit('PLAYER_REGEN_ENABLED'); runTimers(); assert(#messages==2)
        messages={}; emit('PLAYER_ENTERING_WORLD',false,true)
        SlashCmdList.QOL(); clickSetting(19,false); runTimers(); assert(#messages==0)
        ''')

    def test_unknown_general_category_fails_closed_for_missing_check(self):
        lua=self.make('actions={}; Enum.SpellBookSkillLineIndex=nil')
        lua.execute("emit('PLAYER_ENTERING_WORLD',true,false); runTimers(); assert(#messages==0)")
