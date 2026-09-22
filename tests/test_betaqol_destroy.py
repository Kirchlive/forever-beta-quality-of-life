"""Backspace routing plus the native Forever item-delete confirmation path."""
import unittest

from test_forever_quick_accept import HOST, ROOT, SOURCE, LuaRuntime
from settings_ui import UI_ENGINE
import test_betaqol_popups as popups

NATIVE = (ROOT / '.test-ui/Blizzard_ObjectAPI/Mainline/ItemLocation.lua').read_text(encoding='utf-8')
NATIVE += '\nGameEvent={}\n' + popups.native_between(
    'Blizzard_Game/Camelot/EventImplementation.lua',
    'function GameEvent.HandleDeleteItemConfirm(', 'function GameEvent.HandleCursorChanged(')

ENGINE = r'''
function CreateFromMixins(mixin)
    local instance={}; for k,v in pairs(mixin) do instance[k]=v end; return instance
end
local create=CreateFrame
function CreateFrame(...)
    local frame=create(...)
    function frame:EnableKeyboard(value) self.keyboard=value end
    function frame:SetPropagateKeyboardInput(value)
        assert(not combat,'Changed protected keyboard propagation in combat')
        self.propagate=value
    end
    return frame
end
NUM_TOTAL_EQUIPPED_BAG_SLOTS=5
Enum.ItemQuality={Rare=3,Heirloom=7}
combat,ctrl,alt=false,false,false
cursorKind,cursorLocation,keyboardFocus=nil,nil,nil
confirmations,normalKeys={},0
function hooksecurefunc(target,name,callback)
    local previous=target[name]
    target[name]=function(...) previous(...); callback(...) end
end
C_Container={SplitContainerItem=function(bag)
    pickup('item',bag,'Original-Stack')
end}
function InCombatLockdown() return combat end
function IsControlKeyDown() return ctrl end
function IsAltKeyDown() return alt end
function GetCurrentKeyBoardFocus() return keyboardFocus end
function CursorHasItem() return cursorKind=='item' end
C_Cursor.GetCursorItem=function() return cursorLocation end
C_Item.DoesItemExist=function(location) return location and location.guid~=nil end
C_Item.GetItemGUID=function(location) return location.guid end
C_AzeriteEmpoweredItem={IsAzeriteEmpoweredItem=function() return false end}
InputUtil={IsGamepadUIEnabled=function() return false end}
function StaticPopup_Show(which,text,unused,data)
    local dialog=newDialog()
    if StaticPopupDialogs[which].hasEditBox then
        newEditBox(dialog,StaticPopupEditBoxMixin.OnEnterPressed)
        keyboardFocus=dialog:GetEditBox()
    end
    latestPopup=showDialog(dialog,which,data)
    return latestPopup
end
C_Item.ConfirmDeleteItem=function(guid)
    assert(guid==cursorLocation.guid,'Requested the wrong item')
    confirmations[#confirmations+1]=guid
    GameEvent.HandleDeleteItemConfirm(nil,'DELETE_ITEM_CONFIRM','Test item',quality or 1,nil,questItem and 1 or 0,guid)
end
function pickup(kind,bag,guid)
    cursorKind=kind; cursorLocation=nil
    if bag then
        cursorLocation=ItemLocation:CreateFromBagAndSlot(bag,1)
        cursorLocation.guid=guid
    end
    emit('CURSOR_CHANGED')
end
function press(key,release)
    local consumed=false
    for _,frame in ipairs(frames) do
        if frame.keyboard and frame:IsShown() and frame:GetScript('OnKeyDown') then
            frame:GetScript('OnKeyDown')(frame,key)
            consumed=consumed or frame.propagate==false
        end
    end
    if not consumed then normalKeys=normalKeys+1 end
    if release~=false then
        for _,frame in ipairs(frames) do
            if frame.keyboard and frame:IsShown() and frame:GetScript('OnKeyUp') then
                frame:GetScript('OnKeyUp')(frame,key)
            end
        end
    end
    return consumed
end
'''


class DestroyBehaviour(unittest.TestCase):
    def setUp(self):
        self.lua=LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST + UI_ENGINE + popups.ENGINE + popups.NATIVE + NATIVE + ENGINE)
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))
        self.lua.execute("emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL(); clickSetting(7,true)")

    def test_default_does_not_intercept_backspace_until_enabled(self):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(HOST + UI_ENGINE + popups.ENGINE + popups.NATIVE + NATIVE + ENGINE)
        lua.execute(SOURCE.read_text(encoding='utf-8'))
        lua.execute('''
        pickup('item',0,'Item-A'); assert(not press('BACKSPACE'))
        emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()
        assert(BetaQoLDB.backspaceDestroy==false and not checkboxes[7]:GetChecked())
        assert(not press('BACKSPACE') and #confirmations==0)
        clickSetting(7,true); assert(press('BACKSPACE') and #confirmations==1)
        ''')

    def test_backspace_opens_native_confirmation_without_deleting(self):
        self.lua.execute('''
        pickup('item',0,'Item-A'); assert(press('BACKSPACE'))
        assert(#confirmations==1 and deletions==0 and normalKeys==0)
        assert(latestPopup.which=='DELETE_ITEM' and latestPopup.data.itemGUID=='Item-A')
        key(latestPopup,'ENTER'); assert(deletions==1 and deletedGUID=='Item-A')
        ''')

    def test_empty_cursor_and_other_cursor_types_keep_normal_keys(self):
        self.lua.execute('''
        for _,kind in ipairs({'empty','spell','macro','money','merchant'}) do
            pickup(kind); assert(not press('BACKSPACE'))
        end
        assert(#confirmations==0 and normalKeys==5)
        ''')

    def test_items_without_a_bag_location_or_guid_and_bank_items_are_ignored(self):
        self.lua.execute('''
        pickup('item'); assert(not press('BACKSPACE'))
        pickup('item',0); assert(not press('BACKSPACE'))
        pickup('item',-1,'Bank-A'); assert(not press('BACKSPACE'))
        pickup('item',6,'Bank-B'); assert(not press('BACKSPACE'))
        cursorLocation=ItemLocation:CreateFromEquipmentSlot(1); cursorLocation.guid='Equipment'
        emit('CURSOR_CHANGED'); assert(not press('BACKSPACE'))
        assert(#confirmations==0)
        ''')

    def test_text_focus_other_keys_and_modifiers_are_not_consumed(self):
        self.lua.execute('''
        pickup('item',1,'Item-A'); keyboardFocus={}; assert(not press('BACKSPACE'))
        keyboardFocus=nil; assert(not press('A')); assert(not press('ENTER'))
        ctrl=true; assert(not press('BACKSPACE')); ctrl=false
        alt=true; assert(not press('BACKSPACE')); alt=false
        shift=true; assert(not press('BACKSPACE')); shift=false
        assert(#confirmations==0 and normalKeys==6)
        assert(press('BACKSPACE') and #confirmations==1)
        ''')

    def test_cursor_is_rechecked_on_keypress_even_without_event(self):
        self.lua.execute('''
        pickup('item',0,'Item-A'); cursorKind='spell'; assert(not press('BACKSPACE'))
        assert(#confirmations==0)
        ''')

    def test_disabling_with_an_item_picked_up_restores_backspace_immediately(self):
        self.lua.execute('''
        pickup('item',0,'Item-A'); SlashCmdList.QOL(); clickSetting(7,false)
        assert(not press('BACKSPACE') and not BetaQoLDB.backspaceDestroy)
        clickSetting(7,true); assert(press('BACKSPACE') and #confirmations==1)
        ''')

    def test_combat_releases_keyboard_and_resumes_after_combat(self):
        self.lua.execute('''
        pickup('item',0,'Item-A'); combat=true; emit('PLAYER_REGEN_DISABLED')
        assert(not press('BACKSPACE') and #confirmations==0)
        combat=false; emit('PLAYER_REGEN_ENABLED'); assert(press('BACKSPACE'))
        ''')

    def test_key_repeat_does_not_reopen_dialog(self):
        self.lua.execute('''
        pickup('item',0,'Item-A'); press('BACKSPACE',false); press('BACKSPACE',false)
        assert(#confirmations==1)
        ''')

    def test_rare_item_uses_native_typed_confirmation_and_backspace_edits_text(self):
        self.lua.execute('''
        quality=3; pickup('item',0,'Item-Rare'); press('BACKSPACE')
        assert(latestPopup.which=='DELETE_GOOD_ITEM' and not latestPopup:GetButton1():IsEnabled())
        assert(not press('BACKSPACE') and #confirmations==1)
        editEnter(latestPopup:GetEditBox()); assert(deletions==0)
        latestPopup:GetButton1():Enable(); editEnter(latestPopup:GetEditBox())
        assert(deletions==1 and deletedGUID=='Item-Rare')
        ''')

    def test_quest_item_uses_native_quest_confirmation(self):
        self.lua.execute('''
        questItem=true; pickup('item',0,'Item-Quest'); press('BACKSPACE')
        assert(latestPopup.which=='DELETE_QUEST_ITEM' and deletions==0)
        key(latestPopup,'ESCAPE'); assert(deletions==0 and not latestPopup:IsShown())
        ''')

    def test_cursor_change_inside_confirmation_does_not_leak_triggering_key(self):
        self.lua.execute('''
        local original=C_Item.ConfirmDeleteItem
        C_Item.ConfirmDeleteItem=function(guid)
            original(guid); pickup('empty')
        end
        pickup('item',0,'Item-A'); assert(press('BACKSPACE') and normalKeys==0)
        assert(not press('BACKSPACE') and normalKeys==1)
        ''')

    def test_saved_disabled_preference_keeps_normal_backspace(self):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(HOST + UI_ENGINE + popups.ENGINE + popups.NATIVE + NATIVE + ENGINE)
        lua.execute(SOURCE.read_text(encoding='utf-8'))
        lua.execute('''
        BetaQoLDB={backspaceDestroy=false}; emit('ADDON_LOADED','BetaQoL')
        pickup('item',0,'Item-A'); assert(not press('BACKSPACE') and #confirmations==0)
        ''')

    def test_split_stack_is_ignored_until_cursor_is_cleared(self):
        self.lua.execute('''
        C_Container.SplitContainerItem(0,1,2)
        assert(not press('BACKSPACE') and #confirmations==0)
        emit('CURSOR_CHANGED'); assert(not press('BACKSPACE'))
        pickup('empty'); pickup('item',0,'Whole-Stack')
        assert(press('BACKSPACE') and confirmations[1]=='Whole-Stack')
        ''')
