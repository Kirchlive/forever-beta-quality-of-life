import unittest

from test_forever_quick_accept import HOST, SOURCE, LuaRuntime
from settings_ui import UI_ENGINE


class SettingsLayout(unittest.TestCase):
    def setUp(self):
        self.create_ui()

    def create_ui(self, saved=None):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST + UI_ENGINE)
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))
        if saved is not None:
            self.lua.globals().BetaQoLDB = self.lua.table_from(saved, recursive=True)
        self.lua.execute('''
        GameTooltip={}
        function GameTooltip:SetOwner(owner) self.owner=owner end
        function GameTooltip:IsOwned(owner) return self.owner==owner end
        function GameTooltip:SetText(text) self.lines={text} end
        function GameTooltip:AddLine(text) table.insert(self.lines,text) end
        function GameTooltip:Show() self.shown=true end
        function GameTooltip:Hide() self.shown=false end
        ''')
        self.lua.execute('SlashCmdList.QOL(); window=BetaQoLSettingsFrame')

    def test_hover_explains_without_toggling_and_click_changes_setting(self):
        self.lua.execute('''
        local row=window.FeatureRows.lowSpellReminder
        row:GetScript('OnEnter')(row)
        assert(BetaQoLDB.lowSpellReminder)
        assert(GameTooltip.lines[1]=='Low Spell Rank Check')
        assert(GameTooltip.lines[2]:find('highest',1,true))
        assert(window.Details==nil)
        row:GetScript('OnClick')(row)
        assert(not BetaQoLDB.lowSpellReminder and not checkboxes[18]:GetChecked())
        row:GetScript('OnLeave')(row)
        assert(not GameTooltip.shown)
        clickSetting(18,true)
        assert(BetaQoLDB.lowSpellReminder)
        ''')

    def test_lfg_dimensions_indentation_and_tooltip_cleanup(self):
        self.lua.execute('''
        assert(window:GetWidth()==458 and window:GetHeight()==582)
        assert(window.TitleText.text=='Forever Beta Quality of Life')
        local row=window.FeatureRows.flightMasterInstantMap
        assert(row.point[2]>window.CategoryHeaders['World & Interface'].point[2])
        assert(checkboxes[14].Text.font=='GameFontNormal')
        assert(row:GetHeight()<32)
        row:GetScript('OnEnter')(row)
        assert(GameTooltip.lines[1]=='Flight Master Auto Map')
        for _,line in ipairs(GameTooltip.lines) do
            assert(line~='Enabled' and line~='How it works')
        end
        window.SearchBox:SetText('Questlog')
        assert(not GameTooltip.shown)
        window.SearchBox:SetText('')
        row:GetScript('OnEnter')(row)
        SlashCmdList.QOL()
        assert(not GameTooltip.shown)
        ''')

    def test_search_literal_case_insensitive_and_no_results(self):
        self.lua.execute('''
        window.SearchBox:SetText('QUESTLOG')
        assert(window.FeatureRows.questLogXP:IsShown())
        assert(not window.FeatureRows.autoAccept:IsShown())
        window.SearchBox:SetText('%[')
        assert(window.EmptyText:IsShown())
        for _,row in pairs(window.FeatureRows) do assert(not row:IsShown()) end
        window.SearchBox:SetText('')
        assert(not window.EmptyText:IsShown())
        for _,row in pairs(window.FeatureRows) do assert(row:IsShown()) end
        ''')

    def test_search_temporarily_expands_category_and_clamps_scroll(self):
        self.lua.execute('''
        local header=window.CategoryHeaders.Quests
        header:GetScript('OnClick')(header)
        assert(not window.FeatureRows.questDropRate:IsShown())
        window.SearchBox:SetText('Drop Rate')
        assert(window.FeatureRows.questDropRate:IsShown())
        window.SearchBox:SetText('')
        assert(not window.FeatureRows.questDropRate:IsShown())
        header:GetScript('OnClick')(header)
        window.ListScroll:SetVerticalScroll(200)
        window.SearchBox:SetText('Questlog')
        assert(window.ListScroll:GetVerticalScroll()==0)
        assert(window.ListContent:GetHeight()>=window.ListScroll:GetHeight())
        ''')

    def test_native_window_reopens_refreshes_and_fits_small_parent(self):
        self.lua.execute('''
        assert(window.template=='PortraitFrameTemplate')
        assert(window.SearchBox.autoFocus==false)
        assert(#UISpecialFrames==1 and #checkboxes==19)
        clickSetting(1,false); SlashCmdList.BETAQOL()
        assert(checkboxes[1]:GetChecked())
        SlashCmdList.QOL()
        UIParent.width=700; UIParent.height=500
        SlashCmdList.QOL()
        assert(window:GetWidth()*window.scale<=UIParent.width)
        assert(window:GetHeight()*window.scale<=UIParent.height)
        assert(#UISpecialFrames==1 and #checkboxes==19)
        ''')

    def test_bottom_controls_are_hidden_and_disabled(self):
        self.lua.execute('''
        local height=window.ListScroll:GetHeight()
        assert(window.FooterPanel:IsShown())
        assert(not window.FooterToggle:IsEnabled() and not window.CategoryToggle:IsEnabled())
        window.FooterToggle:GetScript('OnClick')()
        window.CategoryToggle:GetScript('OnClick')()
        assert(not window.FooterToggle:IsShown() and not window.CategoryToggle:IsShown())
        assert(window.FooterPanel:IsShown() and window.ListScroll:GetHeight()==height)
        for _,header in pairs(window.CategoryHeaders) do assert(header:IsShown()) end
        for _,box in ipairs(checkboxes) do assert(box:GetChecked()) end
        ''')

    def test_flat_list_removes_headers_gaps_and_collapsed_category_filter(self):
        self.create_ui({'settingsUI': {'showCategories': False}})
        self.lua.execute('''
        local visible={}
        for _,header in pairs(window.CategoryHeaders) do assert(not header:IsShown()) end
        for _,row in pairs(window.FeatureRows) do
            assert(row:IsShown())
            table.insert(visible,row)
        end
        table.sort(visible,function(a,b) return a.point[3]>b.point[3] end)
        for i=2,#visible do
            assert(visible[i].point[2]==visible[1].point[2])
            assert(visible[i].point[3]==visible[i-1].point[3]-visible[i-1]:GetHeight())
        end
        window.SearchBox:SetText('Quests')
        assert(window.FeatureRows.autoAccept:IsShown() and not window.FeatureRows.fastLoot:IsShown())
        window.SearchBox:SetText('')
        window.CategoryToggle:GetScript('OnClick')()
        assert(not window.CategoryHeaders.Quests:IsShown() and window.FeatureRows.autoAccept:IsShown())
        ''')

    def test_layout_preferences_survive_reload_without_affecting_feature_choices(self):
        self.create_ui({'settingsUI': {'showCategories': False, 'bottomExpanded': False}})
        self.lua.execute('''
        window.FooterToggle:GetScript('OnClick')()
        window.CategoryToggle:GetScript('OnClick')()
        clickSetting(1,false)
        ''')
        saved_ui = dict(self.lua.globals().BetaQoLDB.settingsUI.items())
        fresh = LuaRuntime(unpack_returned_tuples=True)
        fresh.execute(HOST + UI_ENGINE)
        fresh.execute(SOURCE.read_text(encoding='utf-8'))
        fresh.globals().BetaQoLDB = fresh.table_from({
            'autoAccept': False, 'settingsUI': fresh.table_from(saved_ui)})
        fresh.execute('''
        SlashCmdList.QOL()
        assert(not BetaQoLSettingsFrame.FooterPanel:IsShown())
        for _,header in pairs(BetaQoLSettingsFrame.CategoryHeaders) do assert(not header:IsShown()) end
        assert(not checkboxes[1]:GetChecked() and checkboxes[2]:GetChecked())
        assert(#checkboxes==19)
        ''')

    def test_new_labels_gray_qualifiers_and_plain_search(self):
        self.lua.execute('''
        assert(checkboxes[4].Text.text=='Quest Icon Target Nameplate')
        assert(checkboxes[5].Text.text=='Questlog XP |cff999999(+ item rewards)|r')
        assert(checkboxes[9].Text.text=='Backspace Leave Quest Details Window')
        assert(checkboxes[10].Text.text=='Backspace Destroy Item Dialog')
        assert(checkboxes[11].Text.text=='Enter Confirm Dialog Box')
        assert(checkboxes[17].Text.text=='Multiline Scroll |cff999999(chatframe and guild)|r')
        window.SearchBox:SetText('(+ item rewards)')
        assert(window.FeatureRows.questLogXP:IsShown())
        window.SearchBox:SetText('999999')
        assert(window.EmptyText:IsShown())
        ''')


if __name__ == '__main__':
    unittest.main()
