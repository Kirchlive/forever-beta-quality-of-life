"""Reversible minimap styling against Forever's native rotation skin."""
import unittest

from test_forever_quick_accept import HOST, ROOT, SOURCE, LuaRuntime
from settings_ui import UI_ENGINE
from test_betaqol_popups import native_between

NATIVE = (ROOT / '.test-ui/Blizzard_Minimap/Camelot/Skin.lua').read_text(encoding='utf-8')
NATIVE_SCALE = '\nEditModeSystemMixin={}\n' + native_between(
    'Blizzard_EditMode/Shared/EditModeSystemTemplates.lua',
    'function EditModeSystemMixin:SetScaleOverride(',
    'function EditModeSystemMixin:SetPointOverride(')
ENGINE = r'''
local create=CreateFrame
function CreateFrame(kind,name,parent,template)
    local frame=create(kind,name,parent,template)
    function frame:SetFrameLevel(value) self.level=value end
    function frame:SetBackdrop(value) self.backdrop=value end
    function frame:SetBackdropBorderColor(...) self.borderColor={...} end
    function frame:EnableMouse(value) self.mouseEnabled=value end
    function frame:CreateTexture()
        local texture={}
        function texture:SetAllPoints() end
        function texture:SetTexture(path) self.path=path end
        function texture:SetSnapToPixelGrid() end
        function texture:SetTexelSnappingBias() end
        return texture
    end
    if name=='BetaQoLSquareMinimapBorder' then squareBorder=frame end
    return frame
end
function region()
    local r={alpha=1,shown=true}
    function r:SetAlpha(value) self.alpha=value end
    function r:GetAlpha() return self.alpha end
    function r:SetAtlas(value) self.atlas=value end
    function r:SetSize(w,h) self.width=w; self.height=h end
    function r:Show() self.shown=true end
    function r:Hide() self.shown=false end
    function r:GetFrameLevel() return 2 end
    r.points={}
    function r:ClearAllPoints() self.points={} end
    function r:SetPoint(...) self.points[1]={...} end
    function r:GetNumPoints() return #self.points end
    function r:GetPoint(index) return unpack(self.points[index]) end
    function r:GetScale() return self.scale or 1 end
    function r:SetScaleBase(value) self.scale=value end
    return r
end
Minimap=region()
function Minimap:SetMaskTexture(value) self.mask=value end
MinimapCluster={MinimapContainer=region()}
MinimapCluster.MinimapContainer.Minimap=Minimap
MinimapCluster.DielFrame=region()
MinimapCluster.DielFrame:SetPoint('CENTER',MinimapCluster,'CENTER',63,72)
QueueStatusButton=region()
QueueStatusButton:SetPoint('CENTER',Minimap,'CENTER',-70,-70)
function InCombatLockdown() return combat end
MinimapBackdrop=region()
MinimapCompassTexture=region()
MinimapCompassTextureUnderlay=region()
C_Texture={GetAtlasInfo=function() return {width=215,height=226} end}
CVarCallbackRegistry={}
function CVarCallbackRegistry:SetCVarCachable() end
function CVarCallbackRegistry:GetCVarValueBool() return rotate end
function CVarCallbackRegistry:RegisterCallback(_,fn) self.callback=fn end
function setRotation(value) rotate=value; CVarCallbackRegistry.callback() end
function hooksecurefunc(object,name,callback)
    local original=object[name]
    object[name]=function(...) original(...); callback(...) end
end
'''


class MinimapBehaviour(unittest.TestCase):
    def setUp(self):
        self.lua=LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HOST + UI_ENGINE + ENGINE + NATIVE)
        self.lua.execute('BetaQoLDB={squareMinimap=true}')
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))

    def test_toggle_restores_mask_and_border_opacity(self):
        self.lua.execute(r'''
        MinimapCompassTexture:SetAlpha(0.8)
        emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()
        assert(Minimap.mask=='Interface\\AddOns\\BetaQoL\\Media\\SquareMinimapMask3')
        assert(MinimapCompassTexture:GetAlpha()==0 and MinimapCompassTextureUnderlay:GetAlpha()==0)
        assert(GetMinimapShape()=='SQUARE')
        assert(squareBorder:IsShown() and squareBorder.mouseEnabled==false)
        clickSetting(7,false)
        assert(not squareBorder:IsShown())
        assert(Minimap.mask=='ui-hud-minimap-frame-generic-mask')
        assert(MinimapCompassTexture:GetAlpha()==0.8 and MinimapCompassTextureUnderlay:GetAlpha()==1)
        assert(GetMinimapShape==nil)
        clickSetting(7,true); assert(squareBorder:IsShown()); clickSetting(7,false)
        assert(MinimapCompassTexture:GetAlpha()==0.8)
        ''')

    def test_native_rotation_cannot_restore_round_mask_or_visible_ring(self):
        self.lua.execute(r'''
        emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()
        setRotation(true)
        assert(Minimap.mask=='Interface\\AddOns\\BetaQoL\\Media\\SquareMinimapMask3')
        assert(MinimapCompassTextureUnderlay.shown and MinimapCompassTextureUnderlay:GetAlpha()==0)
        clickSetting(7,false)
        assert(Minimap.mask=='ui-hud-minimap-frame-generic-mask')
        assert(MinimapCompassTextureUnderlay.shown and MinimapCompassTextureUnderlay:GetAlpha()==1)
        ''')

    def test_saved_disabled_does_not_change_minimap(self):
        self.lua.execute('''
        BetaQoLDB={squareMinimap=false}; emit('ADDON_LOADED','BetaQoL')
        emit('PLAYER_LOGIN'); setRotation(true)
        assert(Minimap.mask=='ui-hud-minimap-frame-generic-mask')
        assert(MinimapCompassTexture:GetAlpha()==1 and MinimapCompassTextureUnderlay:GetAlpha()==1)
        assert(GetMinimapShape==nil)
        ''')

    def test_late_loaded_minimap_and_existing_shape_provider(self):
        self.lua.execute('''
        local minimap=Minimap; Minimap=nil
        local original=function() return 'ROUND' end; GetMinimapShape=original
        emit('ADDON_LOADED','BetaQoL')
        Minimap=minimap; emit('ADDON_LOADED','Blizzard_Minimap')
        assert(GetMinimapShape()=='SQUARE')
        SlashCmdList.QOL(); clickSetting(7,false)
        assert(GetMinimapShape==original)
        ''')

    def test_icons_follow_corners_and_restore_native_anchors(self):
        self.lua.execute('''
        emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()
        local sun=MinimapCluster.DielFrame
        assert(sun.points[1][2]==Minimap and sun.points[1][3]=='TOPRIGHT')
        assert(QueueStatusButton.points[1][3]=='BOTTOMLEFT')
        clickSetting(7,false)
        assert(sun.points[1][2]==MinimapCluster and sun.points[1][4]==63)
        assert(QueueStatusButton.points[1][4]==-70)
        ''')

    def test_native_layout_updates_are_preserved_for_round_mode(self):
        self.lua.execute('''
        emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()
        local sun=MinimapCluster.DielFrame
        sun:SetPoint('CENTER',MinimapCluster,'CENTER',50,58)
        QueueStatusButton:ClearAllPoints()
        QueueStatusButton:SetPoint('CENTER',Minimap,'CENTER',-55,-56)
        assert(sun.points[1][3]=='TOPRIGHT' and QueueStatusButton.points[1][3]=='BOTTOMLEFT')
        clickSetting(7,false)
        assert(sun.points[1][4]==50 and sun.points[1][5]==58)
        assert(QueueStatusButton.points[1][4]==-55 and QueueStatusButton.points[1][5]==-56)
        ''')

    def test_hidden_late_loaded_eye_stays_hidden_and_combat_defers_restoration(self):
        self.lua.execute('''
        local eye=QueueStatusButton; QueueStatusButton=nil; eye:Hide()
        emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()
        QueueStatusButton=eye; emit('ADDON_LOADED','Blizzard_QueueStatusFrame')
        assert(eye.points[1][3]=='BOTTOMLEFT' and not eye.shown)
        combat=true; clickSetting(7,false)
        assert(eye.points[1][3]=='BOTTOMLEFT')
        combat=false; emit('PLAYER_REGEN_ENABLED')
        assert(eye.points[1][4]==-70 and not eye.shown)
        ''')

    def test_native_scale_readback_does_not_replace_original_anchor(self):
        self.lua.execute(NATIVE_SCALE)
        self.lua.execute('''
        QueueStatusButton.SetScale=EditModeSystemMixin.SetScaleOverride
        emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()
        QueueStatusButton:SetScale(1.2)
        QueueStatusButton:SetScale(1.5)
        assert(QueueStatusButton.points[1][3]=='BOTTOMLEFT')
        clickSetting(7,false)
        local point=QueueStatusButton.points[1]
        assert(point[3]=='CENTER' and math.abs(point[4]-(-70/1.5))<0.00001)
        assert(math.abs(point[5]-(-70/1.5))<0.00001)
        ''')

    def test_missing_preference_defaults_on_and_user_can_disable_it(self):
        self.lua.execute('''
        BetaQoLDB={}; emit('ADDON_LOADED','BetaQoL'); SlashCmdList.QOL()
        assert(BetaQoLDB.squareMinimap and checkboxes[7]:GetChecked())
        assert(GetMinimapShape()=='SQUARE' and MinimapCluster.DielFrame.points[1][3]=='TOPRIGHT')
        clickSetting(7,false)
        assert(Minimap.mask=='ui-hud-minimap-frame-generic-mask')
        assert(MinimapCluster.DielFrame.points[1][4]==63)
        ''')
