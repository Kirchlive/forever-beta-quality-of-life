# Licensing and asset notices

The [MIT License](LICENSE) applies to original BetaQoL code, tools, tests,
documentation and the original generated minimap artwork. Copyright (c) 2026
Kirchlive and contributors. The canonical license text is published by the
[Open Source Initiative](https://opensource.org/license/mit).

The repository and release archive also contain the separately attributed
materials below. The root MIT license does not relicense those materials or
replace their notices. Preserve both MIT and applicable third-party notices
when redistributing the package.

| Material | Scope and attribution |
| --- | --- |
| `Data/QuestItemDrops.lua` | Generated database containing Questie-derived data; distributed under GPL-3.0 as recorded in [Data/NOTICE.md](Data/NOTICE.md). |
| `Data/Source/classicItemDrops.lua`, `Data/Source/itemDropCorrections.lua` | Original Questie Forever v27 tables, with upstream comments retained. GPL-3.0; complete license in [Data/COPYING.txt](Data/COPYING.txt). |
| `Data/Source/wowheadForeverDrops.json` | Separately attributed factual snapshot of Wowhead Forever observations. Source URLs, counts, coverage and hashes are retained. No ownership of Wowhead content is claimed; see [Data/NOTICE.md](Data/NOTICE.md). |
| `Media/Icon.png`, `Media/Icon.tga` | User-supplied settings-window portrait and its format conversion. The upstream source and reuse license have not been documented. These images are excluded from the MIT grant; confirm provenance before the public 1.0.0 release. |
| `Media/Screenshots/*.png` | Four in-game captures supplied by the user on September 26, 2026, included unchanged for documentation. They depict World of Warcraft artwork/UI; the root MIT grant does not relicense Blizzard artwork. The menu capture is dev.24 and predates the final label changes. |
| Native UI artwork and Primal Mana icon 132849 | Referenced from the installed World of Warcraft client, not copied into the release. Blizzard artwork is not covered by this project's MIT license. |
| `.test-ui/` | Pinned Blizzard UI source used only by local tests, fetched from Gethe/wow-ui-source. Ignored by Git and excluded from release archives; not relicensed under MIT. |

`Media/SquareMinimapBorder5.tga` and `Media/SquareMinimapMask3.tga` are original
procedurally generated artwork, covered by MIT. Their editable generator is
`tools/generate_minimap_art.py` in the repository.

The addon code does not require Questie to be installed. The release includes
the quest-data source tables, importer scripts, provenance and full GPL text to
keep the distributed database reproducible. See [CONTRIBUTING.md](CONTRIBUTING.md)
for builds and [RELEASE.md](RELEASE.md) for the distribution checklist.
