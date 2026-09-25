# Quest item drop estimates

`QuestItemDrops.lua` is a transformed subset of the drop database shipped with
**Questie Forever beta patch v27**, by Sweettooth91 and the Questie contributors.
The CurseForge project identifies its license as GNU GPL version 3.
The derived database and included original source tables are distributed under
that license; see [COPYING.txt](COPYING.txt). Existing upstream comments are
preserved in `Source/`. No Questie addon code is run or required in the game.

Source package (September 20, 2026):
https://www.curseforge.com/wow/addons/questie-forever/files/8931795

Download:
https://edge.forgecdn.net/files/8931/795/Questie-Forever-beta-patch-v27.zip

Archive SHA256:
`70218f96f71a9172b1c1184b333b76ec387840715b52745e9e75b500a0f01e11`

Original files under `Questie/Database/DropTables/data/`:
- `classicItemDrops.lua`: Wowhead and CMaNGOS Classic data.
- `itemDropCorrections.lua`: Questie corrections; only Era is used.

Changes by BetaQoL, September 25, 2026: resolve the Era correction references,
prefer explicit corrections, then CMaNGOS, then Wowhead, as Questie's DropDB does;
retain positive rates up to 100%; invert item/NPC tables into NPC/item lookups;
retain English item names from source comments. Unknown drops have no fallback.
There are 4,303 NPCs, 1,251 items and 16,678 NPC/item pairs.

**These are Classic estimates, not verified Forever server drop probabilities.**
Forever can change drop rates and introduce new items or creatures. Different
source datasets also use different collection methods. A known number does not
prove that it is correct on the current server.

Reproduce from the included, editable source tables with Python 3:

```text
python tools/import_questie_drops.py
```

Alternatively pass the original ZIP path; its checksum is verified before the
source tables are extracted. The importer does not execute downloaded Lua.
The source tables and importer are included in the addon ZIP for reproducibility,
but only `QuestItemDrops.lua` is loaded by the WoW TOC.
