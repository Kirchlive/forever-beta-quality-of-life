"""Package the addon files and minimap textures under BetaQoL/ in a versioned release ZIP."""

from pathlib import Path
import re
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
FILES = ('BetaQoL.lua', 'BetaQoL.toc', 'README.md', 'DEVLOG.md',
         'Data/QuestItemDrops.lua', 'Data/NOTICE.md', 'Data/COPYING.txt',
         'Data/Source/classicItemDrops.lua', 'Data/Source/itemDropCorrections.lua',
         'Data/Source/wowheadForeverDrops.json', 'Data/RESEARCH.md',
         'tools/import_questie_drops.py', 'tools/import_wowhead_drops.py',
         'Media/SquareMinimapBorder5.tga', 'Media/SquareMinimapMask3.tga')


def main():
    contents = {name: (ROOT / name).read_bytes() for name in FILES}
    toc = contents['BetaQoL.toc'].decode('utf-8-sig')
    match = re.search(r'^## Version:\s*([0-9A-Za-z][0-9A-Za-z._+-]*)\s*$', toc, re.MULTILINE)
    if not match:
        raise ValueError('BetaQoL.toc must contain a valid ## Version: line.')
    destination = ROOT / 'dist' / f'BetaQoL-{match.group(1)}.zip'
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, 'w', compression=ZIP_DEFLATED) as archive:
        for name, content in contents.items():
            archive.writestr(f'BetaQoL/{name}', content)
    with ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('Release ZIP failed its integrity check.')
        for name, content in contents.items():
            if archive.read(f'BetaQoL/{name}') != content:
                raise RuntimeError(f'Release ZIP content mismatch: {name}')
    print(f'Built {destination.relative_to(ROOT)} ({len(FILES)} files).')


if __name__ == '__main__':
    main()
