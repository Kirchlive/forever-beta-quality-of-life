"""Small frame/input fixture for the lazy settings window."""

UI_ENGINE = r'''
UIParent, UISpecialFrames, checkboxes = {}, {}, {}
tinsert = table.insert
local originalCreateFrame = CreateFrame
function CreateFrame(kind, name, parent, template)
    local f = originalCreateFrame(kind, name, parent, template)
    if name then _G[name] = f end
    function f:SetSize() end
    function f:SetPoint() end
    function f:SetFrameStrata() end
    function f:SetMovable() end
    function f:EnableMouse() end
    function f:RegisterForDrag() end
    function f:StartMoving() end
    function f:StopMovingOrSizing() end
    function f:Show() self.shown=true; if self:GetScript('OnShow') then self:GetScript('OnShow')(self) end end
    function f:Hide() self.shown=false end
    function f:IsShown() return self.shown~=false end
    function f:SetChecked(value) self.checked=value end
    function f:GetChecked() return self.checked end
    function f:CreateFontString()
        local text={}
        function text:SetPoint() end
        function text:SetText(value) self.text=value end
        return text
    end
    f.Text=f:CreateFontString(); f.TitleText=f:CreateFontString()
    if kind=='CheckButton' then table.insert(checkboxes,f) end
    return f
end
function clickSetting(index, value)
    local checkbox=assert(checkboxes[index], 'Settings checkbox missing')
    checkbox:SetChecked(value)
    checkbox:GetScript('OnClick')(checkbox)
end
'''
