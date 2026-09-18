"""Real Forever popup lifecycle/acceptance in Lua 5.1 with a small UI engine.

Only client frame/input primitives and inventory/merchant APIs are simulated.
The addon, native popup callbacks and relevant dialog definitions execute as-is.
"""
import re
import unittest

from test_forever_quick_accept import HOST, ROOT, SOURCE, LuaRuntime

UI = ROOT / '.test-ui'


def native_between(path, start, end):
    source = (UI / path).read_text(encoding='utf-8-sig')
    return source[source.index(start):source.index(end, source.index(start))]


def native_definition(path, name):
    source = (UI / path).read_text(encoding='utf-8-sig')
    match = re.search(r'StaticPopupDialogs\["' + name + r'"\] = \{.*?^\};', source, re.S | re.M)
    if not match:
        raise ValueError(f'Native definition missing: {name}')
    return match.group()


NATIVE = '\n'.join([
    native_between('Blizzard_StaticPopup/StaticPopup.lua',
                   'function StaticPopup_ReleaseInsertedFrame(', 'function StaticPopup_OnCloseButtonClicked('),
    native_between('Blizzard_StaticPopup/StaticPopup.lua',
                   'function StaticPopup_OnClick(', 'local nextDialogFallbackID'),
    native_between('Blizzard_StaticPopup/SharedTemplates.lua',
                   'function StaticPopupEditBoxMixin:OnEnterPressed()', 'function StaticPopupEditBoxMixin:OnEscapePressed()'),
    native_between('Blizzard_UIPanels_Game/Mainline/MerchantFrame.lua',
                   'function MerchantFrame_OnSellAllJunkButtonConfirmed()', 'local popupData ='),
    *(native_definition('Blizzard_StaticPopup_Game/GameDialogDefs.lua', name)
      for name in ('DELETE_ITEM', 'DELETE_QUEST_ITEM', 'GENERIC_CONFIRMATION', 'CONFIRM_LOOT_ROLL')),
    native_definition('Blizzard_StaticPopup_Game/Mainline/GameDialogDefs.lua', 'DELETE_GOOD_ITEM'),
])

ENGINE = r'''
StaticPopupDialogs, shownDialogs = {}, {}
shownDialogFrames = shownDialogs
function ipairs_reverse(values)
    local index=#values+1
    return function() index=index-1; if index>0 then return index,values[index] end end
end
StaticPopupEditBoxMixin = {}
highestFrameLevel=0
YES,NO,OKAY,CANCEL='Yes','No','Okay','Cancel'
deletions, sales, cursorClears, screenshots, refundResets = 0, 0, 0, 0, 0
function DeleteCursorItem() deletions=deletions+1 end
C_Item = { DeleteItem=function(guid) deletedGUID=guid; deletions=deletions+1 end }
C_MerchantFrame = { SellAllJunkItems=function() sales=sales+1 end }
C_Cursor = { GetCursorItem=function() return nil end }
ChatFrameUtil = { FocusActiveWindow=function() end }
GameTooltip = { GetOwner=function() return nil end }
function ClearCursor() cursorClears=cursorClears+1 end
function ConfirmLootRoll(id,rollType) confirmedRoll,confirmedRollType=id,rollType end
function MerchantFrame_ResetRefundItem() refundResets=refundResets+1 end
function GetBindingFromClick(key)
    return key=='ESCAPE' and 'TOGGLEGAMEMENU' or key=='PRINTSCREEN' and 'SCREENSHOT' or ''
end
function RunBinding(binding) assert(binding=='SCREENSHOT'); screenshots=screenshots+1 end
function AutoCompleteEditBox_OnEnterPressed(editBox) return editBox.autoCompleteHandled end
function StaticPopup_CollapseTable()
    for i=#shownDialogs,1,-1 do
        if not shownDialogs[i]:IsShown() then table.remove(shownDialogs,i) end
    end
end
function StaticPopup_ForEachShownDialog(callback)
    for _,dialog in ipairs(shownDialogs) do callback(dialog) end
end
function StaticPopup_FindVisible(which)
    for _,dialog in ipairs(shownDialogs) do if dialog.which==which then return dialog end end
end
function makePopupManager()
    local manager={listeners={}}
    function manager:RegisterCallback(event,callback,owner)
        self.listeners[event]=self.listeners[event] or {}
        table.insert(self.listeners[event],{callback=callback,owner=owner})
    end
    function manager:TriggerEvent(event,...)
        for _,listener in ipairs(self.listeners[event] or {}) do
            listener.callback(listener.owner,...)
        end
    end
    return manager
end
PopupEventManager=makePopupManager()
function newButton()
    local button={shown=true,enabled=true}
    function button:IsShown() return self.shown end
    function button:IsVisible() return self.shown end
    function button:IsEnabled() return self.enabled end
    function button:Enable() self.enabled=true end
    function button:Disable() self.enabled=false end
    function button:SetText(text) self.text=text end
    return button
end
function newDialog()
    local dialog=CreateFrame('Frame')
    dialog.buttons={newButton(),newButton()}
    dialog.button1,dialog.button2=unpack(dialog.buttons)
    dialog.shown=false
    function dialog:IsShown() return self.shown end
    function dialog:IsVisible() return self.shown end
    function dialog:Raise() highestFrameLevel=highestFrameLevel+1; self.level=highestFrameLevel end
    function dialog:GetFrameLevel() return self.level or 0 end
    function dialog:GetFrameStrata() return 'DIALOG' end
    function dialog:GetButton(index) return self.buttons[index] end
    function dialog:GetButton1() return self.buttons[1] end
    function dialog:GetButton2() return self.buttons[2] end
    function dialog:GetEditBox() return self.editBox end
    function dialog:SetFormattedText(text) self.text=text end
    function dialog:Hide()
        if self.shown then self.shown=false; StaticPopup_OnHide(self) end
    end
    function dialog:SetPropagateKeyboardInput(value) self.propagate=value end
    return dialog
end
function newEditBox(dialog,handler)
    local editBox=CreateFrame('EditBox')
    editBox.text=''; editBox.shown=true
    function editBox:GetParent() return dialog end
    function editBox:IsShown() return self.shown end
    function editBox:IsVisible() return self.shown and dialog:IsShown() end
    function editBox:GetText() return self.text end
    function editBox:SetText(text) self.text=text end
    function editBox:SetFocus() self.focus=true end
    function editBox:HasFocus() return self.focus end
    editBox:SetScript('OnEnterPressed',handler)
    dialog.editBox=editBox
    return editBox
end
function showDialog(dialog,which,data)
    assert(not dialog.shown, 'Hide the prior popup before reusing its frame')
    dialog.which,dialog.data=which,data
    dialog.enterClicksFirstButton=StaticPopupDialogs[which].enterClicksFirstButton
    dialog.hideOnEscape=StaticPopupDialogs[which].hideOnEscape
    dialog.shown=true
    table.insert(shownDialogs,dialog)
    StaticPopup_OnShow(dialog)
    return dialog
end
function openDialog(which,data) return showDialog(newDialog(),which,data) end
function key(dialog,key)
    local handler=dialog:GetScript('OnKeyDown')
    if handler then handler(dialog,key) end
end
function editEnter(editBox)
    local handler=editBox:GetScript('OnEnterPressed')
    if handler then handler(editBox) end
end
'''


class PopupBehaviour(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST)
        self.lua.execute(ENGINE)
        self.lua.execute(NATIVE)

    def load_addon(self, before=''):
        self.lua.execute(before)
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))

    def test_deletion_waits_for_enter_then_runs_native_acceptance_and_close(self):
        self.load_addon()
        self.lua.execute('''
        local dialog=openDialog('DELETE_ITEM')
        assert(deletions==0 and dialog:IsShown(), 'Opening must not delete automatically')
        key(dialog,'ENTER')
        assert(deletions==1, 'Enter did not delete the ordinary cursor item')
        assert(not dialog:IsShown() and refundResets==1, 'Native acceptance/hide lifecycle was bypassed')
        ''')

    def test_quest_item_numpad_enter_passes_guid_to_native_acceptance(self):
        self.load_addon()
        self.lua.execute('''
        local dialog=openDialog('DELETE_QUEST_ITEM',{itemGUID='Item-Quest-42'})
        key(dialog,'NUMPADENTER')
        assert(deletions==1 and deletedGUID=='Item-Quest-42', 'Numpad Enter did not accept quest-item deletion')
        assert(not dialog:IsShown())
        ''')

    def test_sell_junk_confirmation_only_sells_after_enter(self):
        self.load_addon()
        self.lua.execute('''
        local dialog=openDialog('GENERIC_CONFIRMATION',{text='Sell junk?',callback=MerchantFrame_OnSellAllJunkButtonConfirmed})
        assert(sales==0 and dialog:IsShown(), 'Showing the confirmation must not sell items')
        key(dialog,'ENTER')
        assert(sales==1 and not dialog:IsShown(), 'Enter did not confirm the native sell-junk dialog')
        ''')

    def test_arbitrary_generic_confirmation_accepts_enter_and_restores_prior_handler(self):
        self.load_addon()
        self.lua.execute('''
        local customKeys,accepted=0,0
        local prior=function() customKeys=customKeys+1 end
        local dialog=newDialog(); dialog:SetScript('OnKeyDown',prior)
        showDialog(dialog,'GENERIC_CONFIRMATION',{text='Unrelated',callback=function() accepted=accepted+1 end})
        key(dialog,'ENTER')
        assert(accepted==1 and customKeys==0 and not dialog:IsShown(), 'Arbitrary confirmation did not accept Enter')
        assert(dialog:GetScript('OnKeyDown')==prior, 'Prior generic dialog script was not restored')
        ''')

    def test_other_standard_confirmation_runs_native_accept_with_both_data_arguments(self):
        self.load_addon()
        self.lua.execute('''
        local dialog=newDialog(); dialog.data2=2
        showDialog(dialog,'CONFIRM_LOOT_ROLL',719)
        key(dialog,'ENTER')
        assert(confirmedRoll==719 and confirmedRollType==2, 'Other standard confirmation lost its native callback/data')
        assert(not dialog:IsShown())
        ''')

    def test_disabled_accept_is_neither_accepted_nor_replaced_with_cancel(self):
        self.load_addon()
        self.lua.execute('''
        local dialog=openDialog('DELETE_ITEM')
        dialog:GetButton1():Disable()
        key(dialog,'ENTER'); key(dialog,'NUMPADENTER')
        assert(deletions==0 and cursorClears==0 and dialog:IsShown(), 'Disabled accept must not fall through to Cancel')
        dialog:GetButton1():Enable(); key(dialog,'ENTER')
        assert(deletions==1 and not dialog:IsShown(), 'Enabling accept should make Enter work')
        ''')

    def test_hidden_accept_cannot_be_confirmed(self):
        self.load_addon()
        self.lua.execute('''
        local dialog=openDialog('DELETE_ITEM')
        dialog:GetButton1().shown=false; key(dialog,'ENTER')
        assert(deletions==0 and cursorClears==0 and dialog:IsShown())
        dialog:GetButton1().shown=true; key(dialog,'ENTER')
        assert(deletions==1)
        ''')

    def test_existing_keyboard_handler_receives_other_keys_and_is_restored(self):
        self.load_addon()
        self.lua.execute('''
        local seen={}
        local prior=function(dialog,pressed) table.insert(seen,pressed) end
        local dialog=newDialog(); dialog:SetScript('OnKeyDown',prior)
        showDialog(dialog,'DELETE_ITEM')
        key(dialog,'PRINTSCREEN'); key(dialog,'ESCAPE'); key(dialog,'ENTER')
        assert(#seen==2 and seen[1]=='PRINTSCREEN' and seen[2]=='ESCAPE', 'Prior script lost non-confirmation keys')
        assert(deletions==1 and dialog:GetScript('OnKeyDown')==prior, 'Closing must restore the existing script')
        ''')

    def test_native_screenshot_and_escape_work_without_a_prior_keyboard_script(self):
        self.load_addon()
        self.lua.execute('''
        local dialog=openDialog('DELETE_ITEM')
        key(dialog,'PRINTSCREEN')
        assert(screenshots==1 and deletions==0, 'Native screenshot binding was swallowed')
        key(dialog,'ESCAPE')
        assert(not dialog:IsShown() and deletions==0 and cursorClears==1, 'Native Escape cancellation was swallowed')
        ''')

    def test_reused_frame_restores_and_reinstalls_enter_handler_for_its_current_action(self):
        self.load_addon()
        self.lua.execute('''
        local dialog=openDialog('DELETE_ITEM')
        dialog:Hide()
        assert(dialog:GetScript('OnKeyDown')==nil, 'Closing must remove a newly installed script')
        local accepted=0
        showDialog(dialog,'GENERIC_CONFIRMATION',{text='Other',callback=function() accepted=accepted+1 end})
        key(dialog,'ENTER')
        assert(accepted==1 and deletions==0 and not dialog:IsShown(), 'Reused popup ran a stale callback')
        assert(dialog:GetScript('OnKeyDown')==nil, 'Second close retained a stale script')
        showDialog(dialog,'DELETE_ITEM'); key(dialog,'ENTER')
        assert(deletions==1, 'Reopening an eligible popup must install a fresh shortcut')
        ''')

    def test_only_latest_visible_popup_can_be_confirmed(self):
        self.load_addon()
        self.lua.execute('''
        local deletion=openDialog('DELETE_ITEM')
        local sale=openDialog('GENERIC_CONFIRMATION',{text='Sell junk?',callback=MerchantFrame_OnSellAllJunkButtonConfirmed})
        key(deletion,'ENTER')
        assert(deletions==0 and sales==0 and deletion:IsShown(), 'Background popup consumed Enter')
        key(sale,'ENTER')
        assert(sales==1 and deletions==0, 'Selected popup was not confirmed exactly once')
        key(deletion,'ENTER')
        assert(deletions==1, 'Remaining popup should become eligible after the top popup closes')
        ''')

    def test_unrelated_top_popup_blocks_background_deletion(self):
        self.load_addon()
        self.lua.execute('''
        local deletion=openDialog('DELETE_ITEM')
        local other=openDialog('GENERIC_CONFIRMATION',{text='Other',callback=function() error('Unrelated acceptance') end})
        key(deletion,'ENTER')
        assert(deletions==0 and deletion:IsShown(), 'Unrelated foreground popup did not block background Enter')
        other:Hide(); key(deletion,'ENTER'); assert(deletions==1)
        ''')

    def test_raising_an_earlier_popup_makes_it_the_enter_target(self):
        self.load_addon()
        self.lua.execute('''
        local deletion=openDialog('DELETE_ITEM')
        local sale=openDialog('GENERIC_CONFIRMATION',{text='Sell junk?',callback=MerchantFrame_OnSellAllJunkButtonConfirmed})
        deletion:Raise()
        key(sale,'ENTER')
        assert(sales==0 and sale:IsShown(), 'Last-created popup incorrectly outranked a raised popup')
        key(deletion,'ENTER')
        assert(deletions==1 and sales==0, 'Raised popup did not become the Enter target')
        ''')

    def test_typed_good_item_confirmation_keeps_native_validation(self):
        self.load_addon()
        self.lua.execute('''
        local dialog=newDialog()
        local nativeEnter=StaticPopupEditBoxMixin.OnEnterPressed
        local editBox=newEditBox(dialog,nativeEnter)
        showDialog(dialog,'DELETE_GOOD_ITEM')
        key(dialog,'ENTER')
        assert(deletions==0 and dialog:IsShown(), 'Dialog Enter bypassed typed confirmation')
        assert(editBox:GetScript('OnEnterPressed')==nativeEnter, 'Native typed edit-box handler was replaced')
        editEnter(editBox)
        assert(deletions==0 and dialog:IsShown(), 'Unvalidated typed confirmation was bypassed')
        dialog:GetButton1():Enable()
        editEnter(editBox)
        assert(deletions==1 and not dialog:IsShown(), 'Native validated edit-box Enter must still work')
        ''')

    def test_editbox_without_native_definition_enter_confirms_and_restores_original_script(self):
        self.load_addon()
        self.lua.execute('''
        StaticPopupDialogs.BETA_TEST_PROMPT={
            hasEditBox=1,button1='Accept',button2='Cancel',
            OnAccept=function(dialog) acceptedText=dialog:GetEditBox():GetText() end,
        }
        for _,original in ipairs({false,StaticPopupEditBoxMixin.OnEnterPressed}) do
            local dialog=newDialog()
            local editBox=newEditBox(dialog,original or nil)
            showDialog(dialog,'BETA_TEST_PROMPT')
            editBox:SetText('Current user input')
            editEnter(editBox)
            assert(acceptedText=='Current user input' and not dialog:IsShown(), 'Edit-box Enter fallback did not confirm')
            assert(editBox:GetScript('OnEnterPressed')==(original or nil), 'Closing did not restore original edit-box script')
            acceptedText=nil
        end
        ''')

    def test_editbox_autocomplete_consumes_enter_before_confirmation(self):
        self.load_addon()
        self.lua.execute('''
        local accepted=0
        StaticPopupDialogs.BETA_TEST_PROMPT={
            hasEditBox=1,button1='Accept',button2='Cancel',
            OnAccept=function() accepted=accepted+1 end,
        }
        local dialog=newDialog()
        local editBox=newEditBox(dialog,StaticPopupEditBoxMixin.OnEnterPressed)
        editBox.hasAutoComplete=true; editBox.autoCompleteHandled=true
        showDialog(dialog,'BETA_TEST_PROMPT'); editEnter(editBox)
        assert(accepted==0 and dialog:IsShown(), 'Autocomplete Enter prematurely confirmed the popup')
        editBox.autoCompleteHandled=false; editEnter(editBox)
        assert(accepted==1 and not dialog:IsShown(), 'Enter after autocomplete did not confirm')
        ''')

    def test_ignore_keys_dialog_cannot_be_accepted_by_enter(self):
        self.load_addon()
        self.lua.execute('''
        StaticPopupDialogs.DELETE_ITEM.ignoreKeys=true
        local dialog=openDialog('DELETE_ITEM'); key(dialog,'ENTER')
        assert(deletions==0 and dialog:IsShown(), 'ignoreKeys popup accepted Enter')
        ''')

    def test_focused_chat_prevents_popup_acceptance(self):
        self.load_addon()
        self.lua.execute('''
        local dialog=openDialog('DELETE_ITEM')
        local focused={}
        function GetCurrentKeyBoardFocus() return focused end
        key(dialog,'ENTER')
        assert(deletions==0 and dialog:IsShown(), 'Typing Enter in another editbox confirmed the popup')
        focused=nil; key(dialog,'ENTER')
        assert(deletions==1 and not dialog:IsShown())
        ''')

    def test_focused_popup_editbox_owns_enter_without_parent_acceptance(self):
        self.load_addon()
        self.lua.execute('''
        local accepted=0
        StaticPopupDialogs.BETA_TEST_PROMPT={
            hasEditBox=1,button1='Accept',button2='Cancel',
            OnAccept=function() accepted=accepted+1 end,
        }
        local dialog=newDialog()
        local editBox=newEditBox(dialog,StaticPopupEditBoxMixin.OnEnterPressed)
        function GetCurrentKeyBoardFocus() return editBox end
        showDialog(dialog,'BETA_TEST_PROMPT')
        key(dialog,'ENTER')
        assert(accepted==0 and dialog:IsShown(), 'Parent accepted before editbox handled Enter')
        editEnter(editBox)
        assert(accepted==1 and not dialog:IsShown(), 'Focused editbox did not confirm exactly once')
        ''')

    def test_money_input_fields_confirm_and_restore_their_scripts(self):
        self.load_addon()
        self.lua.execute('''
        StaticPopupDialogs.BETA_TEST_MONEY={
            hasMoneyInputFrame=1,button1='Accept',button2='Cancel',
            OnAccept=function(dialog) acceptedGold=dialog.MoneyInputFrame.gold:GetText() end,
        }
        for _,field in ipairs({'gold','silver','copper'}) do
            local dialog=newDialog()
            dialog.MoneyInputFrame={}
            for _,name in ipairs({'gold','silver','copper'}) do
                dialog.MoneyInputFrame[name]=newEditBox(dialog,nil)
            end
            showDialog(dialog,'BETA_TEST_MONEY')
            dialog.MoneyInputFrame.gold:SetText('42')
            editEnter(dialog.MoneyInputFrame[field])
            assert(acceptedGold=='42' and not dialog:IsShown(), 'Money-field Enter did not submit current value')
            for _,box in pairs(dialog.MoneyInputFrame) do
                assert(box:GetScript('OnEnterPressed')==nil, 'Money-field Enter handler leaked after close')
            end
            acceptedGold=nil
        end
        ''')

    def test_late_loaded_popup_api_is_hooked_on_addon_loaded_or_login(self):
        for event in ('ADDON_LOADED', 'PLAYER_LOGIN'):
            with self.subTest(event=event):
                self.setUp()
                self.load_addon('PopupEventManager=nil')
                self.lua.execute(f"PopupEventManager=makePopupManager(); emit('{event}','Blizzard_StaticPopup'); emit('{event}','OtherAddon')")
                self.lua.execute('''
                local dialog=openDialog('DELETE_ITEM'); key(dialog,'ENTER')
                assert(deletions==1 and not dialog:IsShown(), 'Popup feature did not initialize after delayed UI load')
                ''')


if __name__ == '__main__':
    unittest.main(verbosity=2)
