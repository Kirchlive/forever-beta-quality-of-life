"""Quest drop estimates use native objective ownership and exact NPC/item pairs."""
import unittest
from test_forever_quick_accept import HOST, SOURCE, LuaRuntime
from settings_ui import UI_ENGINE

ENGINE = r'''
Enum.TooltipDataLineType={QuestTitle=17,QuestObjective=8,QuestPlayer=18}
Enum.TooltipDataType={Unit=2}
TooltipDataProcessor={AddTooltipPostCall=function(kind,fn) assert(kind==2); dropCallback=fn end}
secret={}
function issecretvalue(v) return v==secret end
function UnitName() return 'Zeig Mal' end
NameUtil={GetUnitFirstName=function() return 'Zeig' end}
C_QuestLog={IsOnQuest=function(id) return id==844 end,
 GetQuestObjectives=function() return objectives end}
objectives={{type='item',text='Plainstrider Beak: 1/7',finished=false}}
C_Item={GetItemNameByID=function(id) return id==5087 and localizedName or nil end}
function GetLocale() return locale or 'enUS' end
BetaQoLQuestDrops={names={[5087]='Plainstrider Beak',[999]='Beak'},
 npcs={[2955]={[5087]=35,[999]=90},[2956]={[5087]=12.5}}}
GameTooltip={added={}, rows={}}
function GameTooltip:IsForbidden() return forbidden end
function GameTooltip:AddLine(text) self.added[#self.added+1]=text end
function GameTooltip:Hide() self.hidden=true end
function GameTooltip:IsShown() return true end
function makeData(npc)
 return {guid='Creature-0-1-1-1-'..(npc or 2955)..'-0000000001',lines={
 {type=17,id=844},{type=8,leftText='1/7 Plainstrider Beak',numFulfilled=1,numRequired=7,completed=false}}}
end
function prepare(data)
 GameTooltip.added={};GameTooltip.rows={}
 for index,line in ipairs(data.lines) do
  local row={text=line.leftText,color='native'}
  function row:GetText() return self.text end
  function row:SetText(text) self.text=text end
  function row:GetTextColor()
   if line.type==17 then return unpack(line.rgb or {1,0.82,0}) end
   return unpack(line.rgb or (line.completed and {0.5,0.5,0.5} or {1,1,1}))
  end
  row.original=line.leftText
  GameTooltip.rows[index]=row
  _G['GameTooltipTextLeft'..index]=row
  line.lineIndex=index
 end
end
function render(data)
 data=data or makeData();prepare(data)
 if dropCallback then dropCallback(GameTooltip,data) end
 assert(#GameTooltip.added==0, 'Must not append a separate tooltip line')
 local count=0
 for _,row in ipairs(GameTooltip.rows) do
  if type(row.text)=='string' and row.text~=row.original then count=count+1 end
 end
 return count
end
'''

class QuestDropBehaviour(unittest.TestCase):
 def setUp(self):
  self.lua=LuaRuntime(unpack_returned_tuples=True)
  self.lua.execute(HOST+UI_ENGINE+ENGINE)
  self.lua.execute(SOURCE.read_text(encoding='utf-8'))
  self.lua.execute("emit('ADDON_LOADED','BetaQoL');runTimers()")
 def test_known_pair_and_no_duplicate_on_native_rebuild(self):
  self.lua.execute("assert(render()==1); assert(GameTooltip.rows[2].text=='1/7 Plainstrider Beak |cffffd100(35%)|r'); assert(render()==1); assert(render(makeData(2956))==1); assert(GameTooltip.rows[2].text:find('13%%'))")
 def test_unknown_and_kill_objectives_omitted(self):
  self.lua.execute("assert(render(makeData(99999))==0); objectives[1].type='monster'; assert(render()==0)")
 def test_multiple_items_for_one_mob_each_keep_their_own_rate_and_completion_color(self):
  self.lua.execute("""
  objectives={{type='item',text='Plainstrider Beak: 1/7',finished=false},
   {type='item',text='Beak: 5/5',finished=true}}
  local d=makeData()
  table.insert(d.lines,{type=8,leftText='5/5 Beak',completed=true})
  assert(render(d)==2)
  assert(GameTooltip.rows[2].text=='1/7 Plainstrider Beak |cffffd100(35%)|r')
  assert(GameTooltip.rows[3].text=='5/5 Beak (90%)')
  dropCallback(GameTooltip,d)
  assert(GameTooltip.rows[2].text=='1/7 Plainstrider Beak |cffffd100(35%)|r')
  assert(GameTooltip.rows[3].text=='5/5 Beak (90%)')
  """)
 def test_multiple_item_quests_for_one_mob_are_independent_when_one_leaves_log(self):
  self.lua.execute("""
  local active={[844]=true,[845]=true}
  C_QuestLog.IsOnQuest=function(id) return active[id] end
  C_QuestLog.GetQuestObjectives=function(id)
   return {{type='item',text=id==844 and 'Plainstrider Beak: 1/7' or 'Beak: 0/3'}}
  end
  local d=makeData()
  table.insert(d.lines,{type=17,id=845})
  table.insert(d.lines,{type=8,leftText='0/3 Beak',completed=false})
  assert(render(d)==2)
  assert(GameTooltip.rows[2].text=='1/7 Plainstrider Beak |cffffd100(35%)|r')
  assert(GameTooltip.rows[4].text=='0/3 Beak |cffffd100(90%)|r')
  active[844]=nil
  assert(render(d)==1)
  assert(GameTooltip.rows[2].text=='1/7 Plainstrider Beak')
  assert(GameTooltip.rows[4].text=='0/3 Beak |cffffd100(90%)|r')
  """)
 def test_group_only_own_open_objective(self):
  self.lua.execute("local d=makeData(); table.insert(d.lines,2,{type=18,leftText='Other'}); assert(render(d)==0); d.lines[2].leftText='Zeig'; assert(render(d)==1); d.lines[1].id=999; assert(render(d)==0)")
 def test_exact_name_and_multiple_quest_deduplication(self):
  self.lua.execute("local d=makeData(); d.lines[2].leftText='1/7 Giant Plainstrider Beak'; assert(render(d)==0); d=makeData(); table.insert(d.lines,{type=17,id=844}); table.insert(d.lines,{type=8,leftText='1/7 Plainstrider Beak'}); assert(render(d)==2)")
 def test_localized_names_and_uncached_data(self):
  self.lua.execute("locale='deDE'; local d=makeData(); d.lines[2].leftText='1/7 Ebenenschreiterschnabel'; objectives[1].text='Ebenenschreiterschnabel: 1/7'; assert(render(d)==0); localizedName='Ebenenschreiterschnabel'; assert(render(d)==1)")
 def test_disabled_and_saved_preference(self):
  self.lua.execute("SlashCmdList.QOL(); assert(BetaQoLDB.questDropRate and checkboxes[3]:GetChecked()); clickSetting(3,false); assert(render()==0); clickSetting(3,true); assert(render()==1)")
 def test_secret_forbidden_and_non_unit_values(self):
  self.lua.execute("local d=makeData(); d.guid=secret; assert(render(d)==0); d=makeData(); d.lines[2].leftText=secret; assert(render(d)==0); forbidden=true; assert(render()==0); forbidden=false; d=makeData(); d.guid='Player-1-123'; assert(render(d)==0)")
 def test_missing_quest_or_source_data(self):
  self.lua.execute("objectives=nil; assert(render()==0); objectives={}; assert(render()==0); BetaQoLQuestDrops=nil; assert(render()==0)")

 def test_ambiguous_item_names_do_not_guess_a_rate(self):
  self.lua.execute("BetaQoLQuestDrops.names[999]='Plainstrider Beak'; assert(render()==0)")
 def test_group_guid_takes_precedence_over_abbreviated_name(self):
  self.lua.execute("function UnitGUID() return 'Player-1-self' end; local d=makeData(); table.insert(d.lines,2,{type=18,leftText='Zeig',guid='Player-1-other'}); assert(render(d)==0); d.lines[2].guid='Player-1-self'; d.lines[2].leftText='Wrong Display'; assert(render(d)==1)")
 def test_packaged_database_is_usable_and_valid(self):
  self.lua.execute((SOURCE.parent/'Data/QuestItemDrops.lua').read_text(encoding='utf-8'))
  self.lua.execute("assert(render(makeData(3244))==1); assert(GameTooltip.rows[2].text:find('(80%%)')); for npc,items in pairs(BetaQoLQuestDrops.npcs) do assert(npc>0); for item,rate in pairs(items) do assert(BetaQoLQuestDrops.names[item]); assert(rate>0 and rate<=100) end end")

 def test_completed_kidney_objective_keeps_rate_until_quest_leaves_log(self):
  self.lua.execute((SOURCE.parent/'Data/QuestItemDrops.lua').read_text(encoding='utf-8'))
  self.lua.execute("""
  local inLog=true
  C_QuestLog.IsOnQuest=function(id) return inLog and id==822 end
  objectives={{type='item',text='Plainstrider Kidney: 5/5',finished=true}}
  local d=makeData(3245)
  d.lines[1].id=822
  d.lines[2]={type=8,leftText='5/5 Plainstrider Kidney',numFulfilled=5,numRequired=5,completed=true}
  assert(render(d)==1, 'Completed objective must still show a known rate')
  assert(GameTooltip.rows[2].text=='5/5 Plainstrider Kidney (40%)')
  inLog=false
  assert(render(d)==0, 'Turned-in or abandoned quests must not show a rate, even with stale tooltip data')
  inLog=true
  assert(render(d)==1, 'Reaccepted quests must not retain a stale exclusion')
  """)
 def test_forever_raider_and_new_item_use_observed_rates(self):
  self.lua.execute((SOURCE.parent/'Data/QuestItemDrops.lua').read_text(encoding='utf-8'))
  self.lua.execute("""
  local inLog=true
  C_QuestLog.IsOnQuest=function(id) return inLog and (id==899 or id==95774) end
  objectives={{type='item',text='Bristleback Quilboar Tusk: 1/60',finished=false}}
  local d=makeData(268624);d.lines[1].id=899
  d.lines[2]={type=8,leftText='1/60 Bristleback Quilboar Tusk'}
  assert(render(d)==1)
  assert(GameTooltip.rows[2].text=='1/60 Bristleback Quilboar Tusk |cffffd100(70%)|r')
  objectives={{type='item',text="Olgra's Adornments: 1/1",finished=true}}
  d.lines[1].id=95774;d.lines[2]={type=8,leftText="1/1 Olgra's Adornments",completed=true}
  assert(render(d)==1)
  assert(GameTooltip.rows[2].text=="1/1 Olgra's Adornments (20%)")
  inLog=false;assert(render(d)==0)
  inLog=true;d.guid=makeData(999999).guid;assert(render(d)==0)
  """)
 def test_completed_own_group_goal_shows_but_other_player_goal_does_not(self):
  self.lua.execute("""
  objectives[1].finished=true; objectives[1].text='Plainstrider Beak: 7/7'
  local d=makeData(); d.lines[2]={type=8,leftText='7/7 Plainstrider Beak',numFulfilled=7,numRequired=7,completed=true}
  table.insert(d.lines,2,{type=18,leftText='Zeig'})
  assert(render(d)==1)
  d.lines[2].leftText='Other'; assert(render(d)==0)
  """)

 def test_inline_suffix_uses_native_line_index_preserves_text_and_does_not_duplicate(self):
  self.lua.execute("""
  local d=makeData()
  prepare(d)
  -- A native/custom line before the objective changes the displayed row number.
  local row=GameTooltip.rows[2]
  row.text='1/7 Plainstrider Beak'
  _G.GameTooltipTextLeft5=row; d.lines[2].lineIndex=5
  dropCallback(GameTooltip,d); dropCallback(GameTooltip,d)
  assert(row.text=='1/7 Plainstrider Beak |cffffd100(35%)|r')
  assert(row.color=='native' and #GameTooltip.added==0)
  assert(d.lines[2].leftText=='1/7 Plainstrider Beak','Do not mutate shared tooltip data')
  """)
 def test_missing_native_row_or_secret_rendered_text_is_not_modified(self):
  self.lua.execute("""
  local d=makeData();prepare(d);_G.GameTooltipTextLeft2=nil
  dropCallback(GameTooltip,d);assert(#GameTooltip.added==0)
  prepare(d);GameTooltip.rows[2].text=secret;dropCallback(GameTooltip,d)
  assert(GameTooltip.rows[2].text==secret)
  """)

 def test_rounding_boundaries_and_positive_subpercent_values_preserve_database(self):
  self.lua.execute("""
  local cases={{69.4,'70'},{20.5,'20'},{20,'20'},{19.6,'20'},{19.4,'20'},{19,'20'},{18.9,'19'},{18.4,'18'},
   {21,'20'},{21.1,'21'},{23.9,'24'},{26.1,'26'},{31,'30'},
   {31.1,'31'},{34,'35'},{36,'35'},{39,'40'},{41,'40'},{99,'100'},
   {22.49,'22'},{22.5,'23'},{27.8,'28'},{28.9,'29'},{29,'30'},
   {26,'25'},{26.01,'26'},{23.99,'24'},{24,'25'},{12.5,'13'},{7.1,'7'},{0.1,'<1'},{0.001,'<1'},
   {0.5,'1'},{1.4,'1'},{97.5,'98'},{100,'100'}}
  for _,case in ipairs(cases) do
   BetaQoLQuestDrops.npcs[2955][5087]=case[1]
   assert(render()==1)
   assert(GameTooltip.rows[2].text=='1/7 Plainstrider Beak |cffffd100('..case[2]..'%)|r')
   assert(BetaQoLQuestDrops.npcs[2955][5087]==case[1])
  end
  """)
 def test_color_follows_each_quest_header_and_completed_native_row(self):
  self.lua.execute("""
  local d=makeData();d.lines[1].rgb={0.8,0.6,0.2}
  assert(render(d)==1)
  assert(GameTooltip.rows[2].text=='1/7 Plainstrider Beak |cffcc9933(35%)|r')
  assert(GameTooltip.rows[2].text:find('|cffcc9933',1,true))
  table.insert(d.lines,{type=17,id=844,rgb={1,0.7,0}})
  table.insert(d.lines,{type=8,leftText='1/7 Plainstrider Beak'})
  assert(render(d)==2);assert(GameTooltip.rows[4].text:find('|cffffb300',1,true))
  d.lines[2].completed=true;d.lines[2].rgb={0.42,0.42,0.42}
  assert(render(d)==2);assert(GameTooltip.rows[2].text=='1/7 Plainstrider Beak (35%)')
  assert(GameTooltip.rows[2]:GetTextColor()==0.42)
  """)
 def test_reached_counts_gray_without_completed_flag_and_repeat_does_not_stack(self):
  self.lua.execute("""
  local d=makeData();prepare(d);dropCallback(GameTooltip,d)
  d.lines[2].completed=nil;d.lines[2].numFulfilled=7
  dropCallback(GameTooltip,d);dropCallback(GameTooltip,d)
  assert(GameTooltip.rows[2].text=='1/7 Plainstrider Beak (35%)')
  """)
 def test_secret_heading_color_falls_back_without_comparing_secret(self):
  self.lua.execute("""
  local d=makeData();prepare(d)
  GameTooltip.rows[1].GetTextColor=function() return secret,0.8,0 end
  dropCallback(GameTooltip,d)
  assert(GameTooltip.rows[2].text=='1/7 Plainstrider Beak |cffffd100(35%)|r')
  """)
