# Contributing

Run these commands from the repository root with Python 3.9 or newer. A virtual
environment is recommended.

```sh
python -m pip install -r requirements-dev.txt
python tools/fetch_test_ui.py
python -m unittest discover -s tests -v
python tools/build_release.py
```

The tests use `lupa.lua51` to run the addon with simulated client APIs. Loot,
popup, action bar, whisper tab, and item deletion tests also execute selected native UI code,
including the chat tab's XML double-click handler, Forever's minimap rotation skin,
native Edit Mode scaling, quest-title formatting and return-from-quest-details behavior.
The fetcher downloads only the required files from
[Gethe/wow-ui-source at the pinned commit](https://github.com/Gethe/wow-ui-source/tree/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e)
into `.test-ui/`. These external files are ignored by Git and excluded from
release archives. Fetching them requires internet access.

This suite does not run the game client, renderer, or server. Check gameplay
changes in the supported client as well. For settings changes, verify each
checkbox takes effect immediately and remains selected after `/reload` and a
restart. For range coloring, check entering and leaving range, changing targets
and action pages, insufficient resources, and switching the feature off.
For quest turn-in, check the independent toggle, Shift across conversation
pages, incomplete quests, zero/one/multiple reward choices, and quests with a
gold cost. Reward choices and native payment confirmation must remain manual.
For whisper tabs, check docked/undocked and newly opened conversations, regular
and Battle.net whispers, single/right clicks, other chat tabs, and the toggle.
For Backspace Destroy Select Item, check cursor-only activation, normal text editing, modifiers,
combat transitions, whole stacks, and native deletion confirmations. Split
stacks must leave Backspace unchanged until the cursor has been cleared.
Never use a valuable item for an actual destruction test.
For Backspace Leave Quest Details, check the native Back action, hidden map/details,
text focus, modifier keys, combat transitions, late quest-UI loading, its independent
switch and item-deletion priority when carrying an item on the cursor.
For Flight Master Auto Map (shift disable), check a normal flight master including Devrak with
`orderIndex=0`, Shift bypass, the saved toggle, duplicate gossip events and quest
priority. Destination selection and flight payment remain manual.
For Questlog Quest XP, check `[15] (1,350+)` formatting, native level/group
prefixes, item rewards, missing reward data and immediate restoration when disabled.
For Left Shift Escape Reload, verify direct key-down handling in the game client,
left versus right Shift, Ctrl/Alt combinations, held-key repeat, the independent
saved toggle, ordinary Escape routing and delayed initial setup during combat.
No permanent or override binding should be created.
Damage Meter Doubleclick Switch is removed. Verify that an old saved enabled flag
is cleared, the settings show fifteen features and no meter setup/click hooks are
installed, including on late-loaded or additional windows. Normal native menu
selection must continue working. Do not reintroduce a switch based only on passing
Lua fixtures: they cannot emulate the client's secret-value/taint VM. Any future
implementation needs separate live validation through repeated switches and combat
updates. Do not repeat the `taintLog 2` experiment on build 70009: it coincided with
a native-menu assertion and earlier gamepad errors; its causal role is unproven.
For Square Minimap, check the square border, toggling back to the round map,
rotation on/off, zoom, clicks, zone transitions, and persistence after `/reload`.
Check day/night and group-finder corner positions, native restoration when
disabled, UI scale changes, and deferred repositioning after combat.

The build command reads the version from `BetaQoL.toc` and creates
`dist/BetaQoL-<version>.zip`. It contains only `BetaQoL.lua`, `BetaQoL.toc`,
`README.md`, `DEVLOG.md`, the two `Media/*.tga` textures, and the drop database
with attribution, license, original data and importer inside a `BetaQoL/` folder.
Rebuild the drop lookup with `python tools/import_questie_drops.py`; this reads
the included `Data/Source` files without network access.
For drop tooltips, check own and grouped quests, incomplete and completed item
objectives, turn-in and abandonment, yellow inline percentages, and unknown
NPC/item pairs. Include Razormane Raider / Bristleback Quilboar Tusk (70%) and
a new item such as Olgra's Adornments (20%), alongside the unchanged Classic
Ornery Plainstrider / Plainstrider Kidney (40%) example. Classic estimates and
Wowhead observations do not guarantee actual quest-eligible server probabilities.
See `Data/NOTICE.md` for snapshot coverage and the offline supplement extractor.
Regenerate the original minimap artwork with `python tools/generate_minimap_art.py`.

## Next development session

Prepare 1.0.0 with the final settings UI design pass and an addon minimap icon.
Review icon placement and settings access alongside Square Minimap on/off, scaling,
saved preferences and combat transitions. These are planned work, not features of
0.9.8. Damage-meter switching remains out of scope unless explicitly revisited.

## Release after an external data fetch

Keep a development version until the final fetch/import output is available.
Do not publish an intermediate dataset as the completed fetch. An external build
may predate local gameplay changes: integrate the data snapshot and reviewed
importer changes, then build the release from this repository's current code.

1. Preserve the previous snapshot and obtain the final coverage report with the
   updated `Data/Source/wowheadForeverDrops.json` (or full page cache and catalog).
2. Review missing/invalid pages, included pairs and provenance. A downloaded page
   without usable loot counts is not a supported drop-rate pair.
3. Rebuild `Data/QuestItemDrops.lua` with `tools/import_questie_drops.py` and confirm
   existing Classic values and known Forever examples remain valid.
4. Update README, DEVLOG, Data/NOTICE and release notes from the actual generated
   totals. State any remaining gaps; do not equate catalog coverage with all quests.
5. Set the final version consistently, run the full test suite and build the ZIP.
   Verify archive contents, install the matching files, commit, tag and publish
   that exact archive only after the agreed final dataset has been integrated.
