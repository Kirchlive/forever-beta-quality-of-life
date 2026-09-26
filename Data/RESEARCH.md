# Forever quest and loot data review — updated September 26, 2026

## What is integrated

Wowhead's [Forever quest page for Consumed by Hatred](https://www.wowhead.com/forever/quest=899/consumed-by-hatred)
links both older Bristleback creatures and the new Razormane Raider to item 5085.
The important missing evidence was in the **item's embedded `dropped-by` table**,
not just the visible quest description. The item and NPC pages agree on
268 observations out of 386 for this exact NPC/item pair. They also contain
the new item Olgra's Adornments, linked to Her Name Is Olgra (95774).

We inspected the complete 2,133-entry quest-item catalog with drop sources using
non-overlapping ID filters to avoid Wowhead's 1,000-result display cap:

- [IDs below 10,000](https://www.wowhead.com/forever/items/quest?filter=128:151;4:5;0:10000): 796.
- [IDs 10,000–199,999](https://www.wowhead.com/forever/items/quest?filter=128:151:151;4:2:5;0:10000:200000): 777.
- [IDs 200,000 and above](https://www.wowhead.com/forever/items/quest?filter=128:151;4:2;0:200000): 560.

The catalog marks 289 items new, 130 updated and 1,714 unchanged. The completed
September 26 fetch supplies all 2,133 pages, with no missing or invalid pages.
Of these, 176 contain eligible observations for 337 NPC/item pairs across 283 NPCs.
The initial 279-page pass stopped on HTTP 403; a later separate fetch completed
the remaining pages without reported block responses. No access-control bypass
was used. The final snapshot was reproduced from the full validated cache.

This completes the catalog fetch, **not** exhaustive probability coverage of
Forever quests. Old-NPC/old-item observations do not supersede the Classic baseline,
and entries without eligible counts do not produce rates. See [NOTICE.md](NOTICE.md)
for exact inclusion rules and limitations.

## Quest addons and alternative databases

| Source reviewed | What it actually provides | Integration decision |
| --- | --- | --- |
| [Questie Forever v27](https://www.curseforge.com/wow/addons/questie-forever/files/8931795) | Classic drop lookup and explicit Era corrections. | Already bundled as the fallback baseline, with original GPL data and attribution. |
| [Questie upstream / QuestieDB](https://github.com/Questie/QuestieDB) | Inspected source `114f00b` and published DB v1.0.3. Forever uses the Classic baseline; no exact NPC 268624 entry or drop rate. | No additional verified rates for the reported new mob. |
| [EverythingQuests 1.50.0](https://github.com/wheelbarrel00/EverythingQuests/tree/a9a9ccf57a8cfc6bc1908615d4a8e9aaa1e52b68) | 25 extra Forever quests, source/objective associations and map coordinates. Its generator's `KEEP_SHARE=0.5` is an attribution filter, not a 50% drop chance. | No probability table to import. BetaQoL already reads current quest objectives from the client; copying a separate map database would not fill the missing percentage. |
| [Quester Forever 0.5.3](https://github.com/HerrHaseGermany/Quester/tree/e4a651cced2e7414940531446c3a38140c23b338) | Learns exact NPC-to-objective associations from native typed tooltips and active quests, grouped by client build and locale. Explicitly does not learn drop chances. | Confirms the usefulness of native quest data, but supplies no probability records. |
| [Where Do I Get It? Forever 1.2.14](https://www.curseforge.com/wow/addons/where-do-i-get-it-forever/files/8922205) | Static item-source percentages shown on item tooltips. Its inspected database lacks NPC 268624 / Razormane Raider. | No missing-pair fix from this package. All-rights-reserved tables were inspected, not copied. |
| [AtlasLoot Classic Continued 12466](https://www.curseforge.com/wow/addons/atlasloot-continued/files/8969507) | Dungeon/raid loot lists, with incomplete new Forever boss coverage. No relevant entries for items 5085/4894 or NPC 268624 found in inspected Lua. | No relevant quest-item rate supplement. |
| [Thottbot4ever](https://thottbot4ever.com/addon) | Public collector 0.1.2 and an emerging database. Retrieved item 5085 was a Classic seed with `sources: []`; NPC 268624 search was empty. | No usable rate for the example in the inspected responses. |
| [Forever Scribe 1.2.1](https://www.curseforge.com/wow/addons/forever-scribe) | Advertises collected quests, NPCs, items and drops plus a merged community database distributed through its Discord. | Description reviewed; actual export and collector code were not obtained. A database export remains a candidate for further analysis, not a verified percentage source. |

Local-statistics addons were also inspected:
[ForeverFarm](https://github.com/Yzeyr/WOWFOREVER),
[DropRate](https://github.com/L0ngb0w/DropRate) and
[KillTracker](https://github.com/Scarmonit/KillTracker).
Their counters use different denominators (loot-source corpses, current looted
targets or credited kills). Some count item quantities rather than whether a
corpse dropped the item; none of the inspected implementations establishes a
complete personal quest-eligible sample across empty corpses and area looting.
Their displayed percentages should not be imported as authoritative server rates.

## Consequences for BetaQoL

- New and changed quests already work with native quest-progress and nameplate
  detection when the client exposes their objectives. They do not require a
  duplicate quest database in this addon.
- Drop percentages additionally require a known exact NPC/item pair. This
  update supplies real new pairs rather than equating similarly named mobs.
- Completed collection objectives continue to show a known rate while the quest
  is in the player's log. Turning in or abandoning it removes that eligibility.
- Future supplements can be built from reviewed page snapshots or other
  legitimately obtained datasets with explicit IDs and usable observation counts.
  Bare quest associations, old comments and unknown denominators cannot safely
  supply a missing percentage.
