"""Arrow-key scrolling in the visible guild chat, alongside recipe navigation."""
import unittest
import test_betaqol_professions as professions

GUILD = r'''
function makeGuildUI()
 CommunitiesFrame=CreateFrame('Frame')
 CommunitiesFrame.level=20
 function CommunitiesFrame:GetFrameLevel() return self.level end
 local chat=CreateFrame('Frame',nil,CommunitiesFrame); CommunitiesFrame.Chat=chat
 local message=CreateFrame('ScrollingMessageFrame',nil,chat); chat.MessageFrame=message
 message.position=30; message.calls=0
 function message:ScrollByAmount(amount)
  assert(amount==3 or amount==-3)
  self.position=math.max(0,math.min(100,self.position+amount)); self.calls=self.calls+1
 end
end
makeGuildUI()
ProfessionsFrame:Hide()
emit('ADDON_LOADED','Blizzard_Communities')
'''


class GuildArrows(unittest.TestCase):
    def setUp(self):
        fixture=professions.ProfessionNavigation()
        fixture.setUp()
        self.lua=fixture.lua
        self.lua.execute(GUILD)

    def test_three_lines_with_delay_repeat_and_release(self):
        self.lua.execute('''
        local m=CommunitiesFrame.Chat.MessageFrame
        assert(press('UP',false)); assert(m.position==33)
        tick(.24); assert(m.position==33)
        tick(.02); assert(m.position==36)
        tick(.04); assert(m.position==36)
        tick(.02); assert(m.position==39)
        release('UP'); tick(1); assert(m.position==39)
        assert(press('DOWN')); assert(m.position==36)
        assert(selections==0)
        ''')

    def test_text_modifiers_and_hidden_chat_do_not_intercept(self):
        self.lua.execute('''
        keyboardFocus={}; assert(not press('UP')); keyboardFocus=nil
        shift=true; assert(not press('UP')); shift=false
        ctrl=true; assert(not press('UP')); ctrl=false
        alt=true; assert(not press('UP')); alt=false
        assert(not press('LEFT'))
        CommunitiesFrame.Chat:Hide(); assert(not press('UP'))
        CommunitiesFrame.Chat:Show(); assert(press('UP'))
        assert(CommunitiesFrame.Chat.MessageFrame.calls==1)
        ''')

    def test_typing_combat_and_disable_cancel_repeat(self):
        self.lua.execute('''
        local m=CommunitiesFrame.Chat.MessageFrame
        press('UP',false); keyboardFocus={}; tick(.6); keyboardFocus=nil; tick(.6)
        assert(m.calls==1)
        press('UP',false); combat=true; emit('PLAYER_REGEN_DISABLED'); tick(.6)
        combat=false; emit('PLAYER_REGEN_ENABLED'); tick(.6); assert(m.calls==2)
        press('UP',false); SlashCmdList.QOL(); clickSetting(16,false); tick(.6)
        clickSetting(16,true); tick(.6); assert(m.calls==3)
        ''')

    def test_only_foreground_window_responds_when_both_open(self):
        self.lua.execute('''
        ProfessionsFrame:Show(); ProfessionsFrame.level=10
        function ProfessionsFrame:GetFrameLevel() return self.level end
        assert(press('UP')); assert(selections==0 and CommunitiesFrame.Chat.MessageFrame.calls==1)
        ProfessionsFrame.level=30
        assert(press('DOWN')); assert(selections==1 and CommunitiesFrame.Chat.MessageFrame.calls==1)
        ''')

    def test_new_guild_frame_replaces_old_listener(self):
        self.lua.execute('''
        press('UP',false); local old=CommunitiesFrame.Chat.MessageFrame
        makeGuildUI(); emit('ADDON_LOADED','Blizzard_Communities')
        tick(1); assert(old.calls==1 and CommunitiesFrame.Chat.MessageFrame.calls==0)
        assert(press('DOWN')); assert(CommunitiesFrame.Chat.MessageFrame.position==27 and old.calls==1)
        ''')

    def test_renames_and_saved_shared_switch(self):
        self.lua.execute('''
        SlashCmdList.QOL()
        assert(checkboxes[12].Text.text=='Chatbox Arrow Keys')
        assert(checkboxes[16].Text.text=='Panel Arrow Keys |cff999999(guild and professions)|r')
        clickSetting(16,false); assert(not press('UP'))
        CommunitiesFrame:Hide(); ProfessionsFrame:Show(); assert(not press('DOWN'))
        clickSetting(16,true); assert(press('DOWN'))
        ''')
