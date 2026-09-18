"""Lua 5.1 integration fixture: actual Forever LootFrame OnEvent + fake engine.

The client/renderer/server cannot run here. Keep the native OnEvent real so that
opening/closing the Blizzard UI is tested, rather than assuming it is harmless.
"""
import unittest
from test_forever_quick_accept import HOST, ROOT, SOURCE, LuaRuntime

NATIVE = ROOT / '.test-ui/Blizzard_UIPanels_Game/Mainline/LootFrame.lua'
ENGINE = r'''
local engineEmit=emit
function emit(event,...)
    if event=='LOOT_READY' or event=='LOOT_OPENED' then engineActive=true end
    if event=='LOOT_CLOSED' then engineActive=false end
    return engineEmit(event,...)
end
local engineCreateFrame=CreateFrame
function CreateFrame(...)
    local f=engineCreateFrame(...)
    f.alpha=1; f.click=true; f.motion=true; f.children={}
    function f:HookScript(name,fn)
        local prior=self:GetScript(name)
        self:SetScript(name,function(...) if prior then prior(...) end; fn(...) end)
    end
    function f:GetChildren() return unpack(self.children) end
    function f:IsMouseClickEnabled() return self.click end
    function f:IsMouseMotionEnabled() return self.motion end
    function f:SetMouseClickEnabled(value) self.click=value end
    function f:SetMouseMotionEnabled(value) self.motion=value end
    function f:SetAlpha(value) self.alpha=value end
    function f:GetAlpha() return self.alpha end
    return f
end
function hooksecurefunc(target,name,hook)
    local original=target[name]
    target[name]=function(...) local result=original(...); hook(...); return result end
end
GameMenuEscPriority = { AddOnPost2 = 1 }
function RegisterGameMenuEscHandler() end
function CreateFromMixins(...)
    local result = {}
    for _, mixin in ipairs({...}) do for k,v in pairs(mixin) do result[k]=v end end
    return result
end
SOUNDKIT = { UI_CONTAINER_ITEM_OPEN=1, FISHING_REEL_IN=2, LOOT_WINDOW_OPEN_EMPTY=3 }
function PlaySound() end
function IsFishingLoot() return false end
ERR_INV_FULL, ERR_ITEM_MAX_COUNT = 'Bags full', 'Too many of that item'
nativeOpens, nativeCloses, hiddenCalls = 0, 0, 0
reportedErrors = {}
function geterrorhandler() return function(message) reportedErrors[#reportedErrors+1]=message end end
autoDefault, lootModifier, slotCount = true, false, 0
function GetCVarBool(name) assert(name=='autoLootDefault'); return autoDefault end
function IsModifiedClick(name) assert(name=='AUTOLOOTTOGGLE'); return lootModifier end
function GetNumLootItems() return slotCount end
function GetLootSlotType(slot) return loot[slot] and (loot[slot].kind or 1) or 0 end
function GetLootSlotInfo(slot)
    local item=loot[slot]
    if item then return 1, 'Item', 1, nil, 1, item.locked or false end
end
function fill(...)
    loot = {...}; slotCount=#loot
end
function LootSlot(slot)
    assert(loot[slot], 'Tried a cleared slot; indices do not compact in WoW')
    assert(not loot[slot].locked, 'Tried locked loot')
    lootCalls[#lootCalls+1] = slot
    if errorInAPI then error('Simulated client API failure') end
    if closeDuringRequest then emit('LOOT_CLOSED'); return end
    if bindDuringRequest then emit('LOOT_BIND_CONFIRM',slot); return end
    if errorDuringRequest then emit('UI_ERROR_MESSAGE',1,ERR_INV_FULL); return end
    if reentrantLoot then reentrantLoot=false; emit('LOOT_READY',true) end
    if not blockedLoot then
        inventory[#inventory+1]=loot[slot].id
        loot[slot]=nil
        emit('LOOT_SLOT_CLEARED',slot)
    end
end
function CloseLoot() assert(not engineActive, 'Addon closed active loot') end
C_Timer.After = function(delay, callback)
    timers[#timers+1]={at=now+delay, callback=callback}
end
function advance(seconds)
    local stop=now+seconds
    local iterations=0
    while true do
        local first
        for i,t in ipairs(timers) do
            if t.at<=stop and (not first or t.at<timers[first].at) then first=i end
        end
        if not first then break end
        iterations=iterations+1; assert(iterations<1000, 'Unbounded timer loop')
        local timer=table.remove(timers,first)
        now=timer.at; timer.callback()
    end
    now=stop
end
function createNative()
    LootFrame=CreateFrame('Frame')
    for k,v in pairs(LootFrameMixin) do LootFrame[k]=v end
    LootFrame.ScrollBox={
        GetDataProvider=function() return { IsEmpty=function() return slotCount==0 end } end,
        FindFrameByPredicate=function() return nil end,
    }
    local function animationGroup(onFinish)
        local alpha={from=1,to=0}
        function alpha:GetObjectType() return 'Alpha' end
        function alpha:GetFromAlpha() return self.from end
        function alpha:GetToAlpha() return self.to end
        function alpha:SetFromAlpha(v) self.from=v end
        function alpha:SetToAlpha(v) self.to=v end
        local group={revision=0}
        function group:GetAnimations() return alpha end
        function group:Stop() self.revision=self.revision+1; self.playing=false end
        function group:IsPlaying() return self.playing or false end
        function group:Play(reverse)
            self:Stop(); self.playing=true; local revision=self.revision
            LootFrame:SetAlpha(reverse and alpha.to or alpha.from)
            C_Timer.After(0.1,function()
                if self.revision~=revision then return end
                self.playing=false
                LootFrame:SetAlpha(reverse and alpha.from or alpha.to)
                if onFinish then onFinish() end
            end)
        end
        return group
    end
    LootFrame.ShowAnim=animationGroup()
    LootFrame.HideAnim=animationGroup(function() LootFrame:Hide() end)
    function LootFrame:StopAllAnimations() self.ShowAnim:Stop(); self.HideAnim:Stop() end
    function LootFrame:Open()
        local wasShown=self.shown; self.shown=true; nativeOpens=nativeOpens+1
        if not wasShown and self:GetScript('OnShow') then self:GetScript('OnShow')(self) end
        self.HideAnim:Stop(); self.ShowAnim:Play(true)
    end
    function LootFrame:Close() nativeCloses=nativeCloses+1; self.ShowAnim:Stop(); self.HideAnim:Play(false) end
    function LootFrame:IsShown() return self.shown or false end
    function LootFrame:Hide()
        if not self.shown then return end
        hiddenCalls=hiddenCalls+1; self.shown=false; CloseLoot()
        if self:GetScript('OnHide') then self:GetScript('OnHide')(self) end
    end
    function LootFrame:IsVisible() return self:IsShown() and self:GetAlpha()>0 end
    lootButton=CreateFrame('Button'); lootButton.motion=false
    LootFrame.children={lootButton}
    LootFrame:RegisterEvent('LOOT_OPENED')
    LootFrame:RegisterEvent('LOOT_CLOSED')
    LootFrame:SetScript('OnEvent',function(self,event,...) return self:OnEvent(event,...) end)
    originalNativeScript=LootFrame:GetScript('OnEvent')
end
'''

class FastLootBehaviour(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST + ENGINE)
        self.lua.execute(NATIVE.read_text(encoding='utf-8'))
        self.lua.execute('createNative()')
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))
        self.lua.execute("emit('PLAYER_LOGIN')")

    def test_success_never_opens_or_closes_native_window(self):
        self.lua.execute("fill({id=11},{id=22}); emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); assert(not LootFrame:IsVisible()); advance(0.2); assert(not LootFrame:IsVisible()); emit('LOOT_CLOSED'); assert(not LootFrame:IsVisible(), 'Closing animation flashed'); advance(2); assert(#inventory==2 and not LootFrame:IsVisible()); assert(LootFrame:GetScript('OnEvent')==originalNativeScript, 'Must preserve native secure event dispatch')")

    def test_opened_event_alone_collects_and_suppresses(self):
        self.lua.execute("fill({id=11}); emit('LOOT_OPENED',true,false); advance(0); assert(#inventory==1, 'Missing readiness must not disable fast loot'); assert(not LootFrame:IsVisible())")

    def test_late_items_are_retried_without_another_ready(self):
        self.lua.execute("emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); fill({id=11}); advance(0.3); assert(inventory[1]==11, 'No retry for delayed loot data'); assert(not LootFrame:IsVisible())")

    def test_temporarily_blocked_loot_retries_then_stops_after_close(self):
        self.lua.execute("blockedLoot=true; fill({id=11}); emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); advance(0.15); blockedLoot=false; advance(0.3); assert(inventory[1]==11, 'Transient failure is never retried'); emit('LOOT_CLOSED'); local calls=#lootCalls; advance(2); assert(#lootCalls==calls and not LootFrame:IsVisible())")

    def test_locked_and_cleared_slots_are_skipped_then_unlock_retried(self):
        self.lua.execute("fill({id=11},{id=22,locked=true},{id=33}); emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); assert(#inventory==2); loot[2].locked=false; advance(0.3); assert(#inventory==3 and inventory[3]==22); assert(not LootFrame:IsVisible())")

    def test_stalled_loot_reveals_manual_window_once_and_stops(self):
        self.lua.execute("blockedLoot=true; fill({id=11}); emit('LOOT_READY',true); emit('LOOT_OPENED',true,true); advance(1.2); assert(LootFrame:IsVisible(), 'Stalled loot remains inaccessible'); assert(LootFrame.acquiredFromItem==true); local calls=#lootCalls; emit('LOOT_READY',true); advance(2); assert(#lootCalls==calls and nativeOpens==1)")

    def test_manual_false_payload_keeps_native_window(self):
        self.lua.execute("fill({id=11}); emit('LOOT_READY',false); emit('LOOT_OPENED',false,true); advance(2); assert(#lootCalls==0 and nativeOpens==1); emit('LOOT_CLOSED'); assert(nativeCloses==1)")

    def test_missing_payload_uses_native_preference_and_toggle(self):
        for default, modifier, expected in [(True,False,1),(True,True,0),(False,True,1),(False,False,0)]:
            with self.subTest(default=default, modifier=modifier):
                self.setUp()
                self.lua.execute(f"autoDefault={str(default).lower()}; lootModifier={str(modifier).lower()}; fill({{id=11}}); emit('LOOT_READY'); emit('LOOT_OPENED'); advance(0.15); assert(#inventory=={expected}, 'Missing payload ignores native settings'); assert(LootFrame:IsVisible()=={str(not expected).lower()})")

    def test_bind_before_open_cancels_retries_and_exposes_manual_ui(self):
        self.lua.execute("bindDuringRequest=true; fill({id=11},{id=22}); emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); advance(2); assert(#lootCalls==1, 'Repeated attempts during bind confirmation'); assert(LootFrame:IsVisible())")

    def test_inventory_full_before_open_does_not_lose_fallback(self):
        self.lua.execute("errorDuringRequest=true; fill({id=11},{id=22}); emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); advance(2); assert(#lootCalls==1 and nativeOpens==1, 'Full bags must release manual UI')")

    def test_bind_after_open_replays_native_open_once(self):
        self.lua.execute("blockedLoot=true; fill({id=11}); emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); emit('LOOT_BIND_CONFIRM',1); emit('LOOT_BIND_CONFIRM',1); advance(2); assert(nativeOpens==1 and LootFrame:IsVisible()); emit('LOOT_CLOSED'); assert(nativeCloses==1)")

    def test_old_retry_cannot_touch_new_manual_session(self):
        self.lua.execute("blockedLoot=true; fill({id=11}); emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); emit('LOOT_CLOSED'); fill({id=22}); emit('LOOT_READY',false); emit('LOOT_OPENED',false,false); local calls=#lootCalls; advance(2); assert(#lootCalls==calls and #inventory==0 and LootFrame:IsVisible())")

    def test_synchronous_close_stops_remaining_slot_requests(self):
        self.lua.execute("closeDuringRequest=true; fill({id=11},{id=22}); emit('LOOT_OPENED',true,false); advance(2); assert(#lootCalls==1, 'Continued LootSlot after synchronous close'); assert(not LootFrame:IsVisible())")

    def test_closed_delivery_order_does_not_expose_hidden_window(self):
        self.lua.execute("local native=table.remove(frames,1); frames[#frames+1]=native; fill({id=11}); emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); emit('LOOT_CLOSED'); assert(not LootFrame:IsVisible()); advance(0.2); assert(not LootFrame:IsVisible())")

    def test_reentrant_ready_does_not_duplicate_sweeps(self):
        self.lua.execute("fill({id=11},{id=22}); reentrantLoot=true; emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); advance(0.3); assert(#lootCalls==2 and #inventory==2 and not LootFrame:IsVisible())")

    def test_visible_native_window_remains_usable(self):
        self.lua.execute("LootFrame.shown=true; blockedLoot=true; fill({id=11}); emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); advance(2); assert(LootFrame:IsShown() and nativeOpens==1 and hiddenCalls==0)")

    def test_edit_mode_is_not_suppressed(self):
        self.lua.execute("LootFrame.isInEditMode=true; fill({id=11}); emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); assert(nativeOpens==1 and hiddenCalls==0)")

    def test_api_error_releases_native_ui_and_remains_reported(self):
        self.lua.execute("errorInAPI=true; fill({id=11}); emit('LOOT_OPENED',true,false); advance(2); assert(nativeOpens==1 and #reportedErrors==1 and #lootCalls==1)")

    def test_world_transition_invalidates_retries(self):
        self.lua.execute("blockedLoot=true; fill({id=11}); emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); emit('PLAYER_ENTERING_WORLD'); local calls=#lootCalls; advance(2); assert(#lootCalls==calls); emit('LOOT_CLOSED'); advance(0.2); fill({id=22}); blockedLoot=false; emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); assert(inventory[1]==22 and not LootFrame:IsVisible())")

    def test_modifier_release_does_not_change_a_manual_session(self):
        self.lua.execute("lootModifier=true; fill({id=11}); emit('LOOT_READY'); lootModifier=false; emit('LOOT_OPENED'); advance(2); assert(#lootCalls==0 and nativeOpens==1)")

    def test_unrelated_combat_error_does_not_open_loot_window(self):
        self.lua.execute("blockedLoot=true; fill({id=11}); emit('LOOT_OPENED',true,false); emit('UI_ERROR_MESSAGE',2,'Not enough energy'); blockedLoot=false; advance(0.3); emit('LOOT_CLOSED'); assert(inventory[1]==11 and not LootFrame:IsVisible())")

    def test_late_native_frame_is_hooked_on_addon_load(self):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(HOST + ENGINE)
        lua.execute(NATIVE.read_text(encoding='utf-8'))
        lua.execute(SOURCE.read_text(encoding='utf-8'))
        lua.execute("createNative(); emit('ADDON_LOADED','Blizzard_UIPanels_Game'); fill({id=11}); emit('LOOT_OPENED',true,false); advance(0); emit('LOOT_CLOSED'); assert(inventory[1]==11 and not LootFrame:IsVisible())")

    def test_hidden_mouse_targets_are_restored_with_original_flags(self):
        self.lua.execute("blockedLoot=true; fill({id=11}); emit('LOOT_OPENED',true,false); assert(not lootButton.click and not lootButton.motion and not LootFrame.click); emit('LOOT_BIND_CONFIRM',1); assert(lootButton.click and not lootButton.motion and LootFrame.click and LootFrame:IsVisible()); emit('LOOT_CLOSED'); advance(0.2); local a=LootFrame.HideAnim:GetAnimations(); assert(a:GetFromAlpha()==1 and a:GetToAlpha()==0)")

    def test_rapid_auto_sessions_do_not_flash_between_close_and_open(self):
        self.lua.execute("fill({id=11}); emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); emit('LOOT_CLOSED'); fill({id=22}); emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); advance(0.2); assert(#inventory==2 and not LootFrame:IsVisible()); emit('LOOT_CLOSED'); advance(0.2); assert(not LootFrame:IsShown() and lootButton.click)")

    def test_world_change_during_close_does_not_leave_a_visible_window(self):
        self.lua.execute("fill({id=11}); emit('LOOT_READY',true); emit('LOOT_OPENED',true,false); emit('LOOT_CLOSED'); emit('PLAYER_ENTERING_WORLD'); advance(1); assert(not LootFrame:IsShown(), 'World reset cancelled native window cleanup'); assert(lootButton.click)")

if __name__ == '__main__':
    unittest.main(verbosity=2)
