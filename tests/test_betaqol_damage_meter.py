"""Removing the shortcut leaves native meter handlers and menu selection unchanged."""
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
NATIVE+='\nDamageMeterSessionWindowMixin={}\n'
NATIVE+=native_between('Blizzard_DamageMeter/DamageMeterSessionWindow.lua','function DamageMeterSessionWindowMixin:InitializeSessionDropdown(','function DamageMeterSessionWindowMixin:InitializeSettingsDropdown(')

ENGINE=r'''
Enum.DamageMeterSessionType={Overall=0,Current=1}
assertsafe=assert
DamageMeterPerCharacterSettings={windowDataList={}}
function securecallfunction(fn,...)
    return fn(...)
end
MenuInputContext={None=1,MouseButton=2,MouseWheel=3}
function HasLongSessionTypeShortNames() return false end
C_DamageMeter={GetAvailableCombatSessions=function() return {{sessionID=42,name='Prior encounter'}} end}
function hooksecurefunc(target,name,callback)
    local previous=target[name]
    target[name]=function(...) previous(...); callback(...) end
end
function createMeter()
    DamageMeter=setmetatable({windowDataList={}},{__index=DamageMeterMixin})
    function DamageMeter:SetupSessionWindow(index)
        local w=CreateFrame('Frame'); w.index=index; w.sessionType=1; w.updates=0
        local b=CreateFrame('Button'); w.SessionDropdown=b
        function b:SetWidth() end
        function w:GetSessionDropdown() return b end
        function w:GetSessionType() return self.sessionType end
        function w:GetDamageMeterOwner() return DamageMeter end
        function w:GetSessionWindowIndex() return self.index end
        function w:SetSession(kind,id)
            self.sessionType=kind; self.sessionID=id; self.updates=self.updates+1
        end
        function w:GetSessionID() return self.sessionID end
        function b:SetupMenu(generator) self.generator=generator end
        function b:GenerateMenu()
            assert(not insideShortcut, 'Shortcut must not regenerate native menu')
            local root={entries={}}
            function root:SetTag() end
            function root:CreateDivider() end
            function root:EnumerateElementDescriptions() return ipairs(self.entries) end
            function root:CreateRadio(label,isSelected,responder,data)
                local entry={}
                function entry:GetData() return data end
                function entry:IsSelectionIgnored() return false end
                function entry:IsSelected() return isSelected(data) end
                function entry:IsRadio() return true end
                function entry:CanSelect() return true end
                function entry:Pick(context,button)
                    b.radioPicks=(b.radioPicks or 0)+1
                    b.pickedEntry=self; b.pickContext=context; b.pickButton=button
                    securecallfunction(responder,data)
                    return true
                end
                table.insert(self.entries,entry)
            end
            self.generator(self,root)
            self.menuDescription=root
        end
        function b:GetMenuDescription() return self.menuDescription end
        function b:UpdateToMenuSelections() end
        DamageMeterSessionWindowMixin.InitializeSessionDropdown(w)
        b.previousCalls=0
        b:SetScript('OnDoubleClick',function(self) self.previousCalls=self.previousCalls+1 end)
        function b:IsMenuOpen() return self.menu~=nil end
        function b:SetMenuOpen(open)
            if open then
                self:GenerateMenu()
                self.menu={Close=function() end}
            else self:CloseMenu() end
        end
        function b:SignalUpdate()
            assert(not insideShortcut, 'Shortcut must not force dropdown updates')
        end
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
    insideShortcut=true
    if handler then handler(b,button or 'LeftButton') end
    insideShortcut=false
end
'''

class DamageMeterSuspension(unittest.TestCase):
    def setUp(self):
        self.lua=LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST+UI_ENGINE+NATIVE+ENGINE)
        self.lua.execute("createMeter(); originalSetup=DamageMeter.SetupSessionWindow; originalClick=DamageMeter.windowDataList[1].sessionWindow.SessionDropdown:GetScript('OnDoubleClick')")
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))
        self.lua.execute("BetaQoLDB={damageMeterDoubleClick=true}; emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()")

    def test_saved_enabled_preference_cannot_attach_or_reenable_unsafe_switch(self):
        self.lua.execute("""
        local w=DamageMeter.windowDataList[1].sessionWindow
        assert(DamageMeter.SetupSessionWindow==originalSetup, 'Native setup was hooked')
        assert(w.SessionDropdown:GetScript('OnDoubleClick')==originalClick)
        assert(#checkboxes==15 and checkboxes[15].Text.text=='Whisper Tab Doubleclick Close')
        assert(BetaQoLDB.damageMeterDoubleClick==nil, 'Obsolete enabled flag must be removed')
        doubleClick(w)
        assert(w.updates==0 and w.sessionType==1)
        """)

    def test_late_load_and_new_windows_keep_native_handlers(self):
        self.lua.execute("""
        DamageMeter=nil; emit('ADDON_LOADED','Other')
        createMeter(); local setup=DamageMeter.SetupSessionWindow
        local b=DamageMeter.windowDataList[1].sessionWindow.SessionDropdown
        local original=b:GetScript('OnDoubleClick')
        emit('ADDON_LOADED','Blizzard_DamageMeter'); emit('PLAYER_LOGIN')
        assert(DamageMeter.SetupSessionWindow==setup and b:GetScript('OnDoubleClick')==original)
        DamageMeter:SetupSessionWindow(2)
        doubleClick(DamageMeter.windowDataList[2].sessionWindow)
        assert(DamageMeter.windowDataList[2].sessionWindow.updates==0)
        """)

    def test_normal_menu_selection_still_uses_native_saved_selection(self):
        self.lua.execute("""
        local w=DamageMeter.windowDataList[1].sessionWindow; local b=w.SessionDropdown
        b:GetScript('OnMouseDown')(b,'LeftButton')
        b.menuDescription.entries[3]:Pick(MenuInputContext.MouseButton,'LeftButton')
        assert(w.sessionType==0 and DamageMeterPerCharacterSettings.windowDataList[1].sessionType==0)
        b.menuDescription.entries[2]:Pick(MenuInputContext.MouseButton,'LeftButton')
        assert(w.sessionType==1 and DamageMeterPerCharacterSettings.windowDataList[1].sessionType==1)
        """)
