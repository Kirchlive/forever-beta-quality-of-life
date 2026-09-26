"""Native chat tab handlers and pop-in/close lifecycle in a simulated client."""
import unittest
from xml.etree import ElementTree

from test_forever_quick_accept import HOST, ROOT, SOURCE, LuaRuntime
from test_betaqol_popups import native_between
from settings_ui import UI_ENGINE

CHAT_LUA = 'Blizzard_ChatFrameBase/Mainline/FloatingChatFrame.lua'
template = ElementTree.parse(ROOT / '.test-ui/Blizzard_ChatFrameBase/Mainline/FloatingChatFrame.xml')
double_click = template.find(".//*[@name='ChatTabTemplate']/{*}Scripts/{*}OnDoubleClick").text
NATIVE = '\n'.join([
    native_between(CHAT_LUA, 'function FCF_PopInWindow(', '-- Tab flashing functions'),
    native_between(CHAT_LUA, 'function IsBuiltinChatWindow(', 'FloatingChatFrameClickAnywhereButtonMixin ='),
    native_between(CHAT_LUA, 'function FCF_Tab_OnClick(', 'function FCF_SetTabPosition('),
    'function nativeDoubleClick(self, button)\n' + double_click + '\nend',
])

ENGINE = r'''
CHAT_FRAMES, unregistered, minimized, menus = {}, {}, 0, 0
GENERAL_CHAT_DOCK={}
function hooksecurefunc(name, hook)
    local original=assert(_G[name])
    _G[name]=function(...) local result=original(...); hook(...); return result end
end
function GetCVar() return 'classic' end
function IsCombatLog(frame) return frame==ChatFrame2 end
function IsVoiceTranscription(frame) return frame==ChatFrame3 end
function FCF_GetChatFrameByID(id) return _G['ChatFrame'..id] end
function FCFDock_GetSelectedWindow() return SELECTED_CHAT_FRAME end
function FCF_SelectDockFrame(frame) SELECTED_CHAT_FRAME=frame end
function FCF_FadeInChatFrame() end
function FCF_Tab_SetupMenu() menus=menus+1 end
function FCF_UnDockFrame(frame) frame.isDocked=false end
function HideUIPanel(frame) frame:Hide() end
function FCF_FlagMinimizedPositionReset(frame) frame.positionReset=true end
function FCFManager_UnregisterDedicatedFrame(frame, kind, target)
    unregistered[#unregistered+1]={frame=frame,kind=kind,target=target}
end
function FCF_MinimizeFrame(frame) minimized=minimized+1; frame.minimized=true end
function makeChat(id, kind, temporary, docked)
    local name='ChatFrame'..id
    local frame=CreateFrame('Frame',name)
    function frame:GetID() return id end
    function frame:GetName() return name end
    function frame:ResetAllFadeTimes() end
    function frame:RemoveAllMessageGroups() self.messageTypeList={} end
    function frame:RemoveAllChannels() self.channelList={} end
    function frame:ReceiveAllPrivateMessages() self.privateMessageList=nil end
    function frame:AddMessageGroup(kind) self.receiving[kind]=true end
    function frame:AddChannel(channel) self.channels[channel]=true end
    function frame:RemoveExcludePrivateMessageTarget(target) self.excluded[target]=nil end
    frame.receiving,frame.channels,frame.excluded={},{},{}
    frame.messageTypeList={kind}; frame.channelList={}; frame.privateMessageList={TestSender=true}
    frame.chatType=kind; frame.chatTarget='TestSender'; frame.isTemporary=temporary
    frame.isDocked=docked; frame.inUse=true; frame.isRegistered=true; frame.editBox={}
    frame:Show()
    local tab=CreateFrame('Button',name..'Tab')
    function tab:GetID() return id end
    tab:SetScript('OnDoubleClick',nativeDoubleClick)
    tab:SetScript('OnClick',FCF_Tab_OnClick)
    tab:Show()
    table.insert(CHAT_FRAMES,name)
    return frame,tab
end
function FCF_OpenTemporaryWindow(kind)
    if reuseFrame then
        local frame=reuseFrame; reuseFrame=nil
        frame.chatType=kind; frame.inUse=true; frame.isRegistered=true; frame.isDocked=true
        frame.messageTypeList={kind}; frame.privateMessageList={TestSender=true}
        frame:Show(); _G[frame:GetName()..'Tab']:Show()
        return frame
    end
    return makeChat(#CHAT_FRAMES+1,kind,true,true)
end
function doubleClick(frame,button)
    local tab=_G[frame:GetName()..'Tab']
    tab:GetScript('OnDoubleClick')(tab,button or 'LeftButton')
end
'''


class WhisperTabBehaviour(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST + UI_ENGINE + NATIVE + ENGINE)
        self.lua.execute('''
        DEFAULT_CHAT_FRAME=makeChat(1,'GENERAL',false,true)
        makeChat(2,'COMBAT_LOG',false,true); makeChat(3,'VOICE_TEXT',false,true)
        SELECTED_CHAT_FRAME=DEFAULT_CHAT_FRAME
        whisper=makeChat(4,'WHISPER',true,true)
        DEFAULT_CHAT_FRAME.excluded.TestSender=true
        ''')

    def load_addon(self):
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))
        self.lua.execute("emit('ADDON_LOADED','BetaQoL')")

    def test_docked_whisper_closes_and_restores_native_message_routing(self):
        self.load_addon()
        self.lua.execute('''
        doubleClick(whisper)
        assert(not whisper:IsShown() and not ChatFrame4Tab:IsShown() and not whisper.inUse)
        assert(not whisper.isRegistered and #unregistered==1 and whisper.positionReset)
        assert(DEFAULT_CHAT_FRAME.receiving.WHISPER and not DEFAULT_CHAT_FRAME.excluded.TestSender)
        assert(minimized==0)
        ''')

    def test_new_battlenet_whisper_closes(self):
        self.load_addon()
        self.lua.execute('''
        local frame=FCF_OpenTemporaryWindow('BN_WHISPER'); doubleClick(frame)
        assert(not frame.inUse and #unregistered==1 and unregistered[1].kind=='BN_WHISPER')
        ''')

    def test_undocked_whisper_closes_without_native_minimize_side_effect(self):
        self.load_addon()
        self.lua.execute('''
        whisper.isDocked=false; doubleClick(whisper)
        assert(not whisper.inUse and minimized==0)
        ''')

    def test_single_click_and_right_click_keep_native_handlers(self):
        self.load_addon()
        self.lua.execute('''
        assert(ChatFrame4Tab:GetScript('OnClick')==FCF_Tab_OnClick)
        ChatFrame4Tab:GetScript('OnClick')(ChatFrame4Tab,'LeftButton')
        assert(SELECTED_CHAT_FRAME==whisper and whisper.inUse)
        ChatFrame4Tab:GetScript('OnClick')(ChatFrame4Tab,'RightButton')
        doubleClick(whisper,'RightButton')
        assert(menus==1 and whisper.inUse and #unregistered==0)
        ''')

    def test_builtin_custom_and_non_whisper_temporary_tabs_are_unchanged(self):
        self.lua.execute("custom=makeChat(5,'WHISPER',false,false); other=FCF_OpenTemporaryWindow('PET_BATTLE_COMBAT_LOG')")
        self.load_addon()
        self.lua.execute('''
        doubleClick(DEFAULT_CHAT_FRAME); doubleClick(ChatFrame2); doubleClick(ChatFrame3)
        doubleClick(custom); doubleClick(other)
        assert(DEFAULT_CHAT_FRAME:IsShown() and ChatFrame2:IsShown() and ChatFrame3:IsShown())
        assert(custom.inUse and other.inUse and #unregistered==0 and minimized==1)
        ''')

    def test_setting_disables_immediately_and_keeps_native_double_click(self):
        self.load_addon()
        self.lua.execute('''
        SlashCmdList.QOL(); clickSetting(16,false)
        whisper.isDocked=false; doubleClick(whisper)
        assert(whisper.inUse and minimized==1 and not BetaQoLDB.whisperDoubleClick)
        clickSetting(16,true); doubleClick(whisper)
        assert(not whisper.inUse and minimized==1)
        ''')

    def test_reused_temporary_frame_is_not_hooked_twice_and_checks_current_type(self):
        self.load_addon()
        self.lua.execute('''
        doubleClick(whisper); assert(#unregistered==1)
        reuseFrame=whisper; FCF_OpenTemporaryWindow('PET_BATTLE_COMBAT_LOG')
        doubleClick(whisper); assert(whisper.inUse and #unregistered==1)
        reuseFrame=whisper; FCF_OpenTemporaryWindow('BN_WHISPER')
        doubleClick(whisper); assert(not whisper.inUse and #unregistered==2)
        ''')

    def test_late_chat_loading_installs_handlers(self):
        self.lua.execute('savedOpen=FCF_OpenTemporaryWindow; FCF_OpenTemporaryWindow=nil')
        self.load_addon()
        self.lua.execute('''
        FCF_OpenTemporaryWindow=savedOpen; emit('ADDON_LOADED','Blizzard_ChatFrameBase')
        emit('PLAYER_LOGIN'); doubleClick(whisper)
        assert(not whisper.inUse and #unregistered==1)
        ''')

    def test_saved_disabled_preference_is_respected(self):
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))
        self.lua.execute('''
        BetaQoLDB={whisperDoubleClick=false}; emit('ADDON_LOADED','BetaQoL')
        doubleClick(whisper); assert(whisper.inUse and #unregistered==0)
        ''')
