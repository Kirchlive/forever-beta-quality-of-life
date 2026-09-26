"""Fetch only the pinned upstream UI files used by the integration tests."""

from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
COMMIT = '70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e'
BASE_URL = f'https://raw.githubusercontent.com/Gethe/wow-ui-source/{COMMIT}/Interface/AddOns/'
FILES = (
    'Blizzard_DamageMeter/DamageMeter.lua',
    'Blizzard_Menu/DropdownButton.lua',
    'Blizzard_UIPanels_Game/Camelot/QuestMapFrameOverrides.lua',
    'Blizzard_UIPanels_Game/Mainline/QuestMapFrame.lua',
    'Blizzard_FrameXMLUtil/Camelot/NameUtil.lua',
    'Blizzard_NamePlates/Blizzard_NamePlateBase.lua',
    'Blizzard_EditMode/Shared/EditModeSystemTemplates.lua',
    'Blizzard_Minimap/Camelot/Skin.lua',
    'Blizzard_Game/Camelot/EventImplementation.lua',
    'Blizzard_ObjectAPI/Mainline/ItemLocation.lua',
    'Blizzard_ChatFrameBase/Mainline/FloatingChatFrame.lua',
    'Blizzard_ChatFrameBase/Mainline/FloatingChatFrame.xml',
    'Blizzard_ActionBar/Shared/ActionButton.lua',
    'Blizzard_UIPanels_Game/Mainline/LootFrame.lua',
    'Blizzard_UIPanels_Game/Mainline/MerchantFrame.lua',
    'Blizzard_StaticPopup/StaticPopup.lua',
    'Blizzard_StaticPopup/SharedTemplates.lua',
    'Blizzard_StaticPopup_Game/GameDialogDefs.lua',
    'Blizzard_StaticPopup_Game/Mainline/GameDialogDefs.lua',
)


def main():
    for name in FILES:
        with urlopen(BASE_URL + name, timeout=30) as response:
            content = response.read()
        destination = ROOT / '.test-ui' / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        print(f'Fetched {name}')
    print(f'Fetched {len(FILES)} UI files from commit {COMMIT}.')


if __name__ == '__main__':
    main()
