"""Quest markers using the actual Forever 1.60.1 tooltip fields captured in game."""
import unittest

from test_forever_quick_accept import HOST, ROOT, SOURCE, LuaRuntime
from settings_ui import UI_ENGINE

ENGINE = r'''
Enum.TooltipDataLineType={QuestTitle=17,QuestObjective=8,QuestPlayer=18}
plates, units, textures, ownQuests = {}, {}, {}, {[844]=true,[845]=true}
tooltipReads=0
C_QuestLog={IsOnQuest=function(id) return ownQuests[id] or false end}
C_TooltipInfo={GetUnit=function(unit)
    tooltipReads=tooltipReads+1
    if tooltipError then error('Tooltip data unavailable') end
    return units[unit] and units[unit].data
end}
C_NamePlate={GetNamePlates=function() return plates end}
function UnitIsPlayer(unit) return units[unit] and units[unit].player or false end
function UnitName(unit) assert(unit=='player'); return 'Tester','Test Realm' end
function GetRealmName() return 'Test Realm' end
function issecretvalue(value) return value==secret end
secret={}
function addPlate(unit,data,bar)
    local frame={unit=unit,healthBar=bar}
    if not bar then
        bar={shown=true}; frame.healthBar=bar
        function bar:IsShown() return self.shown end
        function bar:CreateTexture()
            local t={parent=self,shown=false}; textures[#textures+1]=t; self.icon=t
            function t:SetTexture(value) self.texture=value end
            function t:SetSize(w,h) self.width=w;self.height=h end
            function t:SetPoint(...) self.point={...} end
            function t:Show() self.shown=true end
            function t:Hide() self.shown=false end
            function t:IsShown() return self.shown end
            return t
        end
    end
    local plate={UnitFrame=frame,unitToken=unit}
    function plate:GetUnit() return self.unitToken end
    function plate:IsForbidden() return self.forbidden end
    function frame:IsForbidden() return plate.forbidden end
    plates[#plates+1]=plate; units[unit]={data=data}
    emit('NAME_PLATE_UNIT_ADDED',unit)
    return plate,bar
end
function objective(count,required,completed)
    return {type=8,leftText='Plainstrider Beak',numFulfilled=count,numRequired=required,completed=completed}
end
function tooltip(...)
    return {lines={{type=17,id=844,leftText='Plainstrider Menace'},...}}
end
function visible(bar) return bar.icon and bar.icon.shown and bar.shown end
function tick(elapsed)
    for _,frame in ipairs(frames) do
        local fn=frame:GetScript('OnUpdate'); if fn then fn(frame,elapsed) end
    end
    runTimers()
end
'''

NATIVE_BASE = (ROOT / '.test-ui/Blizzard_NamePlates/Blizzard_NamePlateBase.lua').read_text(encoding='utf-8')


class QuestNameplateBehaviour(unittest.TestCase):
    def setUp(self):
        self.lua=LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST + UI_ENGINE + ENGINE)
        self.lua.execute("BetaQoLDB={questNameplateBag=true}")
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))
        self.lua.execute("emit('ADDON_LOADED','BetaQoL'); runTimers()")

    def test_actual_item_progress_shows_bag_left_of_health_bar(self):
        self.lua.execute(r'''
        local plate,bar=addPlate('nameplate1',tooltip(objective(1,7,false)))
        runTimers()
        assert(visible(bar),'Missing marker for captured 1/7 objective')
        assert(bar.icon.point[1]=='RIGHT' and bar.icon.point[2]==bar and bar.icon.point[3]=='LEFT')
        assert(bar.icon.point[4]<0)
        assert(bar.icon.texture=='Interface\\Minimap\\Tracking\\Banker')
        ''')

    def test_completed_mob_objective_hides_without_finishing_whole_quest(self):
        self.lua.execute('''
        local p,bar=addPlate('nameplate1',tooltip(objective(1,7,false)))
        runTimers(); assert(visible(bar))
        units.nameplate1.data=tooltip(objective(7,7,true))
        emit('QUEST_LOG_UPDATE');runTimers()
        assert(not visible(bar) and ownQuests[844])
        ''')

    def test_other_unfinished_quest_for_same_mob_keeps_bag(self):
        self.lua.execute('''
        local p,bar=addPlate('nameplate1',tooltip(objective(7,7,true),
            {type=17,id=845},objective(2,10,false)))
        runTimers(); assert(visible(bar))
        units.nameplate1.data.lines[4]=objective(10,10,true)
        emit('QUEST_LOG_UPDATE');runTimers();assert(not visible(bar))
        ''')

    def test_party_objectives_do_not_keep_own_completed_marker(self):
        self.lua.execute('''
        local p,bar=addPlate('nameplate1',tooltip(
            {type=18,leftText='Tester'},objective(7,7,true),
            {type=18,leftText='Guildmate'},objective(1,7,false)))
        runTimers();assert(not visible(bar))
        units.nameplate1.data=tooltip({type=18,leftText='Guildmate'},objective(1,7,false),
            {type=18,leftText='|cffffffffTester-TestRealm|r'},objective(2,7,false))
        emit('QUEST_LOG_UPDATE');runTimers();assert(visible(bar))
        ''')

    def test_kill_and_non_count_objectives_and_missing_completion_flag(self):
        self.lua.execute('''
        local p,bar=addPlate('nameplate1',tooltip(objective(2,5,false)))
        runTimers();assert(visible(bar))
        units.nameplate1.data=tooltip({type=8,leftText='Free the captive',completed=false})
        emit('QUEST_LOG_UPDATE');runTimers();assert(visible(bar))
        units.nameplate1.data=tooltip({type=8,leftText='Free the captive',completed=true})
        emit('QUEST_LOG_UPDATE');runTimers();assert(not visible(bar))
        units.nameplate1.data=tooltip(objective(7,7,false))
        emit('QUEST_LOG_UPDATE');runTimers();assert(not visible(bar))
        units.nameplate1.data=tooltip(objective(1,7,nil))
        emit('QUEST_LOG_UPDATE');runTimers();assert(visible(bar))
        ''')

    def test_abandoned_quest_and_unrelated_tooltip_never_show_bag(self):
        self.lua.execute('''
        local p,bar=addPlate('nameplate1',tooltip(objective(1,7,false)))
        runTimers();assert(visible(bar))
        ownQuests[844]=nil;emit('QUEST_REMOVED',844);runTimers();assert(not visible(bar))
        ownQuests[844]=true
        units.nameplate1.data={lines={{type=0,leftText='1/7 reputation'},objective(1,7,false)}}
        emit('QUEST_LOG_UPDATE');runTimers();assert(not visible(bar))
        ''')

    def test_removal_and_pool_reuse_cannot_leave_stale_icon(self):
        self.lua.execute('''
        local p,bar=addPlate('nameplate1',tooltip(objective(1,7,false)))
        runTimers();assert(visible(bar))
        emit('NAME_PLATE_UNIT_REMOVED','nameplate1'); assert(not visible(bar))
        plates={};units.nameplate1=nil;runTimers()
        addPlate('nameplate2',{lines={}},bar);runTimers();assert(not visible(bar))
        units.nameplate2.data=tooltip(objective(1,7,false));tick(0.6)
        assert(visible(bar) and #textures==1)
        ''')

    def test_delayed_native_frame_and_tooltip_data_retry_without_mouseover(self):
        self.lua.execute('''
        local p,bar=addPlate('nameplate1',nil)
        local unitFrame=p.UnitFrame;p.UnitFrame=nil
        runTimers();assert(not visible(bar))
        p.UnitFrame=unitFrame;units.nameplate1.data=tooltip(objective(1,7,false))
        tick(0.6);assert(visible(bar))
        ''')

    def test_toggle_hides_immediately_and_disables_polling(self):
        self.lua.execute('''
        local p,bar=addPlate('nameplate1',tooltip(objective(1,7,false)))
        runTimers();SlashCmdList.QOL();assert(visible(bar))
        clickSetting(9,false);assert(not visible(bar) and not BetaQoLDB.questNameplateBag)
        local reads=tooltipReads
        emit('QUEST_LOG_UPDATE');tick(2);assert(tooltipReads==reads)
        clickSetting(9,true);runTimers();assert(visible(bar) and #textures==1)
        ''')

    def test_saved_off_and_missing_api_are_safe(self):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(HOST + UI_ENGINE + ENGINE)
        lua.execute('BetaQoLDB={questNameplateBag=false}')
        lua.execute(SOURCE.read_text(encoding='utf-8'))
        lua.execute('''
        local p,bar=addPlate('nameplate1',tooltip(objective(1,7,false)))
        emit('ADDON_LOADED','BetaQoL');runTimers();assert(not visible(bar))
        SlashCmdList.QOL();C_TooltipInfo=nil;clickSetting(9,true);runTimers()
        assert(not visible(bar))
        ''')

    def test_secret_data_players_and_forbidden_plates_are_skipped(self):
        self.lua.execute('''
        local p,bar=addPlate('nameplate1',tooltip(objective(1,7,false)))
        p.forbidden=true;runTimers();assert(not visible(bar))
        p.forbidden=false;units.nameplate1.player=true;tick(0.6);assert(not visible(bar))
        units.nameplate1.player=false
        units.nameplate1.data=tooltip(objective(secret,7,false));tick(0.6);assert(not visible(bar))
        units.nameplate1.data=tooltip({type=secret,completed=false});tick(0.6);assert(not visible(bar))
        units.nameplate1.data=tooltip(objective(1,7,false));tick(0.6);assert(visible(bar))
        tooltipError=true;tick(0.6);assert(not visible(bar))
        ''')

    def test_event_burst_is_coalesced_and_idle_poll_does_not_scan(self):
        self.lua.execute('''
        local p,bar=addPlate('nameplate1',tooltip(objective(1,7,false)))
        runTimers();local reads=tooltipReads
        for i=1,20 do emit('QUEST_LOG_UPDATE') end
        runTimers();assert(tooltipReads==reads+1)
        plates={};emit('NAME_PLATE_UNIT_REMOVED','nameplate1');runTimers()
        reads=tooltipReads;tick(2);assert(tooltipReads==reads)
        ''')

    def test_native_pool_release_then_acquire_on_another_plate(self):
        self.lua.execute(NATIVE_BASE)
        self.lua.execute('''
        local p,bar=addPlate('nameplate1',tooltip(objective(1,7,false)))
        local pooled=p.UnitFrame
        function CompactUnitFrame_SetUnit(frame,unit) frame.unit=unit end
        function pooled:OnUnitCleared() end
        function pooled:SetParent(parent) self.parent=parent end
        function pooled:SetAllPoints() end
        function pooled:SetNamePlateFrame(plate) self.plate=plate end
        p.driverFrame={ReleaseUnitFrame=function(_,plate) assert(plate.UnitFrame==pooled) end}
        runTimers();assert(visible(bar))
        NamePlateBaseMixin.ClearUnit(p)
        NamePlateBaseMixin.ReleaseUnitFrame(p)
        emit('NAME_PLATE_UNIT_REMOVED','nameplate1')
        assert(p.UnitFrame==nil and not visible(bar))
        plates={};units.nameplate1=nil
        local q=addPlate('nameplate2',{lines={}},bar)
        q.driverFrame={AcquireUnitFrame=function() return pooled end}
        NamePlateBaseMixin.AcquireUnitFrame(q)
        runTimers();assert(not visible(bar))
        units.nameplate2.data=tooltip(objective(3,7,false));tick(0.6)
        assert(visible(bar) and #textures==1 and pooled.parent==q)
        ''')

    def test_hidden_health_bar_and_secret_quest_id_hide_previous_marker(self):
        self.lua.execute('''
        local p,bar=addPlate('nameplate1',tooltip(objective(1,7,false)))
        runTimers();assert(visible(bar))
        bar.shown=false;tick(0.6);assert(not bar.icon.shown)
        bar.shown=true;units.nameplate1.data.lines[1].id=secret
        tick(0.6);assert(not visible(bar))
        ''')
