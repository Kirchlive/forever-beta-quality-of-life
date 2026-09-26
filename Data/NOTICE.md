# Quest item drop data

The generated lookup combines the Classic baseline below with a separately
attributed Wowhead Forever supplement. It contains **4,400 NPCs, 1,407 items and
17,015 NPC/item pairs**. Neither source guarantees current server probabilities.

## Wowhead Forever observations — September 26, 2026

`Source/wowheadForeverDrops.json` records numerical facts from the public
Wowhead Forever item pages: item/NPC IDs and names, observed `count` and `outof`,
quest references, source URLs and SHA256 hashes of the inspected pages.
No Wowhead addon code, page scripts, comments, images or quest prose are copied.
This supplement is separate from Questie's original GPL source tables.

Added **337 pairs, 176 items and 283 NPCs**. Each included pair has at least one
entity explicitly marked `new` by Wowhead's Forever comparison and usable positive
normal-mode counts. Only `dropped-by` creature loot is used; references with
unknown counts, invalid ratios, other loot modes and non-creature sources are
omitted. Rates are `100 * count / outof`, not stack quantities divided by kills.
Exact NPC/item IDs are retained; names never substitute for an unknown NPC ID.

Examples, cross-checked against the corresponding NPC loot page:

- [Bristleback Quilboar Tusk (5085)](https://www.wowhead.com/forever/item=5085/bristleback-quilboar-tusk):
  [Razormane Raider (268624)](https://www.wowhead.com/forever/npc=268624/razormane-raider),
  268 / 386 = approximately 69.43%, displayed as 70%, for Consumed by Hatred (899).
- [Olgra's Adornments (277277)](https://www.wowhead.com/forever/item=277277/olgras-adornments):
  the same NPC, 79 / 386 = approximately 20.47%, displayed as 20%, for Her Name Is Olgra (95774).

The UI rounds to whole percentages. For rates >=19%, it instead uses the nearest
5% step only if the raw rate is within 1 percentage point: 69.4% → 70%,
20.5% → 20%, but 27.8% → 28%.
Positive values rounding to zero display `<1%`. This is presentation only; all
source counts and generated lookup values retain their original precision.

These are observed loot frequencies, not confirmed quest-eligible server rates.
The source does not establish that every counted loot event came from a player
who still needed the item. Small samples are retained, with their counts in the
editable snapshot; 1/1 is an observation, not proof of a guaranteed drop.

The September 25 quest-item/drop-source catalog contains 2,133 items. All 2,133
item pages were successfully parsed by September 26: zero missing pages and zero
invalid pages. The initial 279-page snapshot supplied 291 pairs; completion added
46 pairs while retaining every earlier observation. The shipped snapshot was
independently reproduced from the full cache, including the recorded page hashes.

Complete coverage of this catalog does not mean every Forever quest item has a
known drop chance. A catalog entry or quest association without usable eligible
loot counts produces no percentage. The catalog covers the Quest item category,
not every trade good a quest may use. The `coverage` object records all totals.

Old-NPC/old-item statistics on a `/forever/` page can contain inherited Classic
observations. They do **not** replace the existing Classic baseline merely because
of that URL or an `updated` flag. The supplement requires a `new` entity; a
matching supplemental pair takes precedence over the baseline. The addon never
queries websites in-game and does not record or learn drops automatically.

Rebuild the shipped lookup from both included source datasets:

```text
python tools/import_questie_drops.py
```

To prepare a new supplement from legally obtained local item-page snapshots
named `<itemID>.html` and a JSON catalog containing `id` entries:

```text
python tools/import_wowhead_drops.py path/to/cache path/to/catalog.json
python tools/import_questie_drops.py
```

The extractor validates Forever page metadata and the exact requested item ID,
parses literal JSON only, and never runs downloaded JavaScript or Lua. Check its
coverage report before replacing the snapshot. [Other sources reviewed](RESEARCH.md).

## Classic baseline — Questie Forever v27

The Classic portion of `QuestItemDrops.lua` is a transformed subset of the database shipped with
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
The baseline contains 4,303 NPCs, 1,251 items and 16,678 NPC/item pairs.

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
