"""Recipe navigation through native selection, respecting visible tree entries."""
import unittest
from test_forever_quick_accept import HOST, SOURCE, LuaRuntime
from settings_ui import UI_ENGINE
import test_betaqol_destroy as destroy
import test_betaqol_popups as popups
from test_betaqol_quest_back import ENGINE as VISIBILITY

NATIVE = 'ProfessionsRecipeListMixin={}\n' + popups.native_between(
    'Blizzard_ProfessionsTemplates/Blizzard_ProfessionsRecipeList.lua',
    'function ProfessionsRecipeListMixin:SelectRecipe(',
    'function ProfessionsRecipeListMixin:ClearSelectedRecipe(')

ENGINE = r'''
function tick(elapsed)
 for _,frame in ipairs(frames) do
  local update=frame:GetScript('OnUpdate')
  if update and frame:IsShown() then update(frame,elapsed) end
 end
end
function release(key)
 for _,frame in ipairs(frames) do
  local up=frame:GetScript('OnKeyUp')
  if frame.keyboard and frame:IsShown() and up then up(frame,key) end
 end
end
function hideProfessions()
 local shown={}
 for _,frame in ipairs(frames) do if frame:IsShown() then shown[#shown+1]=frame end end
 ProfessionsFrame:Hide()
 for _,frame in ipairs(shown) do
  if not frame:IsShown() and frame:GetScript('OnHide') then frame:GetScript('OnHide')(frame) end
 end
end
function makeProfessionUI()
 ProfessionsFrame=CreateFrame('Frame')
 local page=CreateFrame('Frame',nil,ProfessionsFrame)
 ProfessionsFrame.CraftingPage=page
 local list=CreateFrame('Frame',nil,page); page.RecipeList=list
 local function node(data) return {GetData=function() return data end} end
 rows={node({categoryInfo={}}),node({recipeInfo={recipeID=10}}),
       node({isDivider=true}),node({recipeInfo={recipeID=20}}),
       node({recipeInfo={recipeID=30}})}
 visible=rows; selected=rows[2]; selections=0; scrolled=nil
 list.ScrollBox={}
 function list.ScrollBox:HasDataProvider() return visible~=nil end
 function list.ScrollBox:EnumerateDataProvider() return ipairs(visible) end
 function list.ScrollBox:EnumerateDataProviderEntireRange() error('Must exclude collapsed recipes') end
 function list.ScrollBox:ScrollToElementData(node) assert(node); scrolled=node end
 list.selectionBehavior={}
 function list.selectionBehavior:IsElementDataSelected(node) return node==selected end
 function list.selectionBehavior:SelectElementDataByPredicate(predicate)
   for _,node in ipairs(visible) do
     if predicate(node) then selected=node; selections=selections+1; return node end
   end
 end
 list.SelectRecipe=ProfessionsRecipeListMixin.SelectRecipe
end
'''

class ProfessionNavigation(unittest.TestCase):
    def setUp(self):
        self.lua=LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST+UI_ENGINE+popups.ENGINE+popups.NATIVE+destroy.NATIVE+destroy.ENGINE+VISIBILITY+NATIVE+ENGINE)
        self.lua.execute('makeProfessionUI()')
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))
        self.lua.execute("emit('ADDON_LOADED','BetaQoL')")

    def test_arrows_select_recipes_skip_headers_and_scroll_into_view(self):
        self.lua.execute('''
        assert(press('DOWN')); assert(selected==rows[4] and scrolled==selected)
        assert(press('UP')); assert(selected==rows[2])
        assert(press('UP')); assert(selected==rows[2] and selections==2)
        selected=rows[5]; assert(press('DOWN')); assert(selected==rows[5])
        ''')

    def test_filtered_collapsed_empty_and_no_selection(self):
        self.lua.execute('''
        visible={rows[1],rows[2],rows[5]}; assert(press('DOWN')); assert(selected==rows[5])
        selected=nil; assert(press('DOWN')); assert(selected==rows[2])
        visible={rows[1]}; assert(not press('DOWN'))
        visible=nil; assert(not press('DOWN'))
        ''')

    def test_text_modifiers_hidden_and_disabled_leave_keys_alone(self):
        self.lua.execute('''
        keyboardFocus={}; assert(not press('DOWN')); keyboardFocus=nil
        shift=true; assert(not press('DOWN')); shift=false
        ctrl=true; assert(not press('DOWN')); ctrl=false
        alt=true; assert(not press('DOWN')); alt=false
        assert(not press('LEFT'))
        ProfessionsFrame:Hide(); assert(not press('DOWN')); ProfessionsFrame:Show()
        SlashCmdList.QOL(); clickSetting(16,false); assert(not press('DOWN'))
        assert(selections==0)
        clickSetting(16,true); assert(press('DOWN'))
        ''')

    def test_combat_release_and_recreated_late_window(self):
        self.lua.execute('''
        combat=true; emit('PLAYER_REGEN_DISABLED'); assert(not press('DOWN'))
        combat=false; emit('PLAYER_REGEN_ENABLED'); assert(press('DOWN'))
        makeProfessionUI(); emit('ADDON_LOADED','Blizzard_Professions')
        assert(press('DOWN')); assert(selections==1 and selected==rows[4])
        ''')

    def test_hold_has_initial_delay_then_repeats_and_release_stops(self):
        self.lua.execute('''
        press('DOWN',false); assert(selected==rows[4] and selections==1)
        tick(.49); assert(selections==1)
        tick(.02); assert(selected==rows[5] and selections==2)
        selected=rows[2]; tick(.09); assert(selections==2)
        tick(.02); assert(selected==rows[4] and selections==3)
        release('DOWN'); tick(1); assert(selections==3)
        ''')

    def test_os_repeat_does_not_duplicate_or_reset_delay_and_direction_restarts(self):
        self.lua.execute('''
        press('DOWN',false); tick(.3); press('DOWN',false)
        assert(selections==1); tick(.21); assert(selections==2)
        press('UP',false); assert(selected==rows[4] and selections==3)
        release('DOWN'); tick(.49); assert(selections==3)
        tick(.02); assert(selected==rows[2] and selections==4)
        release('UP'); tick(1); assert(selections==4)
        ''')

    def test_repeat_cancels_on_text_focus_modifiers_and_hide_without_resuming(self):
        for cancel, restore in (
            ('keyboardFocus={}', 'keyboardFocus=nil'),
            ('shift=true', 'shift=false'),
            ('ctrl=true', 'ctrl=false'),
            ('alt=true', 'alt=false'),
            ('hideProfessions()', 'ProfessionsFrame:Show()'),
        ):
            with self.subTest(cancel=cancel):
                self.setUp()
                self.lua.execute("press('DOWN',false); "+cancel+"; tick(.6); "+restore+"; tick(1); assert(selections==1)")

    def test_repeat_cancels_on_disable_combat_and_window_replacement(self):
        self.lua.execute('''
        press('DOWN',false); SlashCmdList.QOL(); clickSetting(16,false)
        tick(.6); clickSetting(16,true); tick(.6); assert(selections==1)
        press('DOWN',false); combat=true; emit('PLAYER_REGEN_DISABLED')
        tick(.6); combat=false; emit('PLAYER_REGEN_ENABLED'); tick(.6); assert(selections==2)
        press('UP',false); makeProfessionUI(); emit('ADDON_LOADED','Blizzard_Professions')
        tick(1); assert(selections==0)
        ''')

    def test_no_catchup_burst_and_boundary_stays_selected(self):
        self.lua.execute('''
        press('DOWN',false); selected=rows[2]; tick(3)
        assert(selected==rows[4] and selections==2)
        tick(.11); assert(selected==rows[5] and selections==3)
        tick(1); assert(selected==rows[5] and selections==3)
        release('DOWN')
        ''')

    def test_physical_release_recovers_when_key_up_was_not_delivered(self):
        self.lua.execute('''
        local down=true
        function IsKeyDown(key) assert(key=='DOWN'); return down end
        press('DOWN',false); tick(.51); assert(selections==2)
        selected=rows[2]; down=false; tick(.11); assert(selections==2)
        down=true; tick(1); assert(selections==2)
        ''')
