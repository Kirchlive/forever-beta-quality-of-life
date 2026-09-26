"""Double-click routing through the native damage meter's saved window state."""
import unittest
from test_forever_quick_accept import HOST, SOURCE, LuaRuntime
from settings_ui import UI_ENGINE
from test_betaqol_popups import native_between

METER='Blizzard_DamageMeter/DamageMeter.lua'
NATIVE=native_between(METER,'local MAX_DAMAGE_METER_SESSION_WINDOWS','local function IsSavedWindowDataValid')
NATIVE+='\nDamageMeterMixin={}\n'
NATIVE+=native_between(METER,'function DamageMeterMixin:ForEachSessionWindow(','function DamageMeterMixin:GetPrimarySessionWindow(')
NATIVE+=native_between(METER,'function DamageMeterMixin:GetSessionWindowData(','function DamageMeterMixin:ShowNewSecondarySessionWindow(')
NATIVE+=native_between(METER,'function DamageMeterMixin:SetSessionWindowSessionID(','function DamageMeterMixin:GetSessionType(')
NATIVE+='\nDropdownButtonMixin={}\n'
NATIVE+=native_between('Blizzard_Menu/DropdownButton.lua','function DropdownButtonMixin:OnMouseDown_Intrinsic()','function DropdownButtonMixin:OpenMenu()')
NATIVE+=native_between('Blizzard_Menu/DropdownButton.lua','function DropdownButtonMixin:CloseMenu()','function DropdownButtonMixin:SetMenuOpen(')

ENGINE=r'''
Enum.DamageMeterSessionType={Overall=0,Current=1}
assertsafe=assert
DamageMeterPerCharacterSettings={windowDataList={}}
function hooksecurefunc(target,name,callback)
    local previous=target[name]
    target[name]=function(...) previous(...); callback(...) end
end
function createMeter()
    DamageMeter=setmetatable({windowDataList={}},{__index=DamageMeterMixin})
    function DamageMeter:SetupSessionWindow(index)
        local w=CreateFrame('Frame'); w.index=index; w.sessionType=1; w.updates=0
        local b=CreateFrame('Button'); w.SessionDropdown=b
        function w:GetSessionDropdown() return b end
        function w:GetSessionType() return self.sessionType end
        function w:GetDamageMeterOwner() return DamageMeter end
        function w:GetSessionWindowIndex() return self.index end
        function w:SetSession(kind,id) self.sessionType=kind; self.sessionID=id; self.updates=self.updates+1 end
        b.previousCalls=0
        b:SetScript('OnDoubleClick',function(self) self.previousCalls=self.previousCalls+1 end)
        function b:IsMenuOpen() return self.menu~=nil end
        function b:SetMenuOpen(open)
            if open then self.menu={Close=function() end} else self:CloseMenu() end
        end
        function b:SignalUpdate() end
        b.CloseMenu=DropdownButtonMixin.CloseMenu
        b:SetScript('OnMouseDown',DropdownButtonMixin.OnMouseDown_Intrinsic)
        self.windowDataList[index]={sessionWindow=w,sessionType=1,damageMeterType=0}
    end
    DamageMeter:SetupSessionWindow(1)
end
function doubleClick(w,button)
    local b=w.SessionDropdown
    b:GetScript('OnMouseDown')(b,button or 'LeftButton')
    b:GetScript('OnMouseDown')(b,button or 'LeftButton')
    local handler=b:GetScript('OnDoubleClick')
    if handler then handler(b,button or 'LeftButton') end
end
'''

class DamageMeterBehaviour(unittest.TestCase):
    def setUp(self):
        self.lua=LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST+UI_ENGINE+NATIVE+ENGINE)
        self.lua.execute('createMeter()')
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))
        self.lua.execute("emit('ADDON_LOADED','BetaQoL')")

    def test_double_click_swaps_both_directions_and_saves_native_selection(self):
        self.lua.execute('''
        local w=DamageMeter.windowDataList[1].sessionWindow
        doubleClick(w); assert(w.sessionType==0 and w.sessionID==nil and w.updates==1)
        assert(DamageMeterPerCharacterSettings.windowDataList[1].sessionType==0)
        assert(not w.SessionDropdown:IsMenuOpen())
        doubleClick(w); assert(w.sessionType==1 and w.updates==2)
        assert(DamageMeterPerCharacterSettings.windowDataList[1].sessionType==1)
        ''')

    def test_single_click_still_opens_menu_without_switching(self):
        self.lua.execute('''
        local w=DamageMeter.windowDataList[1].sessionWindow; local b=w.SessionDropdown
        b:GetScript('OnMouseDown')(b,'LeftButton')
        assert(b:IsMenuOpen() and w.sessionType==1 and w.updates==0)
        ''')

    def test_disabled_right_click_and_individual_encounter_keep_previous_handler(self):
        self.lua.execute('''
        SlashCmdList.QOL(); clickSetting(15,false)
        local w=DamageMeter.windowDataList[1].sessionWindow
        doubleClick(w); assert(w.updates==0 and w.SessionDropdown.previousCalls==1)
        clickSetting(15,true); doubleClick(w,'RightButton'); assert(w.updates==0)
        w.sessionType=nil; w.sessionID=42
        doubleClick(w); assert(w.sessionID==42 and w.updates==0)
        assert(w.SessionDropdown.previousCalls==3)
        ''')

    def test_new_windows_and_repeated_load_events_switch_only_clicked_window_once(self):
        self.lua.execute('''
        DamageMeter:SetupSessionWindow(2)
        emit('ADDON_LOADED','Other'); emit('PLAYER_LOGIN')
        local w=DamageMeter.windowDataList[2].sessionWindow
        doubleClick(w); assert(w.sessionType==0 and w.updates==1)
        assert(DamageMeter.windowDataList[1].sessionWindow.updates==0)
        ''')

    def test_meter_loaded_after_addon(self):
        self.lua.execute('''
        DamageMeter=nil; emit('ADDON_LOADED','Other')
        createMeter(); emit('ADDON_LOADED','Blizzard_DamageMeter')
        local w=DamageMeter.windowDataList[1].sessionWindow
        doubleClick(w); assert(w.sessionType==0 and w.updates==1)
        ''')
