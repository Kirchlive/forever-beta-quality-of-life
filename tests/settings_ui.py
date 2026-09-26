"""Small frame/input fixture for the lazy settings window."""

UI_ENGINE = r'''
UIParent, UISpecialFrames, checkboxes = {width=1920,height=1080}, {}, {}
function UIParent:GetWidth() return self.width end
function UIParent:GetHeight() return self.height end
tinsert = table.insert
local function settingsUIRegion()
    local r={}
    function r:SetPoint(...) self.point={...} end
    function r:ClearAllPoints() self.point=nil end
    function r:SetAllPoints() end
    function r:SetSize(w,h) self.width=w; self.height=h end
    function r:SetWidth(w) self.width=w end
    function r:SetHeight(h) self.height=h end
    function r:SetText(value) self.text=value end
    function r:GetText() return self.text or '' end
    function r:SetFontObject(font) self.font=font end
    function r:SetTextColor(...) self.color={...} end
    function r:SetJustifyH() end
    function r:SetJustifyV() end
    function r:SetWordWrap() end
    function r:GetStringHeight()
        local plain=(self.text or ''):gsub('|c%x%x%x%x%x%x%x%x',''):gsub('|r','')
        return 12*math.max(1,math.ceil(#plain*6/(self.width or 1000)))
    end
    function r:SetTexture(value) self.texture=value end
    function r:SetColorTexture(...) self.color={...} end
    function r:SetVertexColor(...) self.vertexColor={...} end
    function r:SetDesaturated(value) self.desaturated=value end
    function r:SetHorizTile() end
    function r:SetVertTile() end
    function r:SetAtlas(value) self.atlas=value end
    function r:SetAlpha(value) self.alpha=value end
    function r:SetTexCoord() end
    function r:Show() self.shown=true end
    function r:Hide() self.shown=false end
    function r:SetShown(value) self.shown=value end
    function r:IsShown() return self.shown~=false end
    return r
end
local originalCreateFrame = CreateFrame
function CreateFrame(kind, name, parent, template)
    local f = originalCreateFrame(kind, name, parent, template)
    f.template=template
    if name then _G[name] = f end
    function f:SetSize(w,h) self.width=w; self.height=h end
    function f:SetWidth(w) self.width=w end
    function f:SetHeight(h) self.height=h end
    function f:GetWidth() return self.width or 0 end
    function f:GetHeight() return self.height or 0 end
    function f:SetPoint(...) self.point={...} end
    function f:ClearAllPoints() end
    function f:SetFrameStrata() end
    function f:SetScale(scale) self.scale=scale end
    function f:SetClampedToScreen() end
    function f:SetHitRectInsets() end
    function f:SetTitle(title) self.TitleText:SetText(title) end
    function f:SetPortraitToAsset() end
    function f:SetMovable() end
    function f:EnableMouse() end
    function f:RegisterForDrag() end
    function f:StartMoving() end
    function f:StopMovingOrSizing() end
    function f:Show() self.shown=true; if self:GetScript('OnShow') then self:GetScript('OnShow')(self) end end
    function f:Hide()
        local wasShown=self:IsShown()
        self.shown=false
        if wasShown and self:GetScript('OnHide') then self:GetScript('OnHide')(self) end
    end
    function f:IsShown() return self.shown~=false end
    function f:SetShown(value) if value then self:Show() else self:Hide() end end
    function f:HookScript(event, callback)
        local previous=self:GetScript(event)
        self:SetScript(event,function(...) if previous then previous(...) end; callback(...) end)
    end
    function f:SetChecked(value) self.checked=value end
    function f:GetChecked() return self.checked end
    function f:SetEnabled(value) self.enabled=value end
    function f:IsEnabled() return self.enabled~=false end
    function f:CreateFontString() return settingsUIRegion() end
    function f:CreateTexture() return settingsUIRegion() end
    function f:SetHighlightAtlas() end
    function f:SetNormalFontObject(font) self.normalFont=font end
    function f:SetAutoFocus(value) self.autoFocus=value end
    function f:ClearFocus() self.focus=false end
    function f:SetMaxLetters() end
    function f:GetText() return self.text or '' end
    function f:SetText(value)
        self.text=value
        if self:GetScript('OnTextChanged') then self:GetScript('OnTextChanged')(self) end
    end
    function f:SetScrollChild(child) self.child=child end
    function f:GetVerticalScrollRange() return math.max(0,self.child:GetHeight()-self:GetHeight()) end
    function f:GetVerticalScroll() return self.offset or 0 end
    function f:SetVerticalScroll(value) self.offset=value end
    f.Text=f:CreateFontString(); f.TitleText=f:CreateFontString()
    if template=='PortraitFrameTemplate' then
        f.PortraitContainer={portrait=settingsUIRegion()}
        function f:GetPortrait() return self.PortraitContainer.portrait end
    end
    if template=='ScrollFrameTemplate' then
        f.ScrollBar=CreateFrame('EventFrame')
        function f.ScrollBar:SetHideIfUnscrollable() end
    elseif template=='ListHeaderVisualTemplate' then
        f.CollapseButton=CreateFrame('Button')
        function f.CollapseButton:UpdateCollapsedState(value) self.collapsed=value end
        function f:SetHeaderText(value) self.Text:SetText(value) end
        function f:CheckHighlightTitle() end
    end
    if kind=='CheckButton' then table.insert(checkboxes,f) end
    return f
end
function clickSetting(index, value)
    local checkbox=assert(checkboxes[index], 'Settings checkbox missing')
    checkbox:SetChecked(value)
    checkbox:GetScript('OnClick')(checkbox)
end
'''
