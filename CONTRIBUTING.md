# Contributing

Target: WoW Forever Beta 1.60.1, build 70009, Interface 16001.
Current behavior and names: [README](README.md). Publication checklist:
[RELEASE.md](RELEASE.md). Historical research: [DEVLOG](DEVLOG.md).

## Development setup

Run these commands from the repository root with Python 3.9 or newer. A virtual
environment is recommended.

```sh
python -m pip install -r requirements-dev.txt
python tools/fetch_test_ui.py
python -m unittest discover -s tests -v
python tools/build_release.py
```

The 274 tests use `lupa.lua51` to run the addon with simulated client APIs. Loot,
popup, action bar, whisper tab, and item deletion tests also execute selected native UI code,
including the chat tab's XML double-click handler, Forever's minimap rotation skin,
native Edit Mode scaling, quest-title formatting and return-from-quest-details behavior.
The fetcher downloads only the required files from
[Gethe/wow-ui-source at the pinned commit](https://github.com/Gethe/wow-ui-source/tree/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e)
into `.test-ui/`. These external files are ignored by Git and excluded from
release archives. Fetching them requires internet access.

## Runtime and live-client validation

Preserve saved setting keys when renaming labels. BetaQoLDB is account-wide;
explicit false values must survive restoration. New switches default on. Most
changes apply immediately; spell checks apply at the next login/reload. The
minimap launcher is settings access, not a twentieth gameplay switch.

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
For Backspace Destroy Item Dialog, check cursor-only activation, normal text editing, modifiers,
combat transitions, whole stacks, and native deletion confirmations. Split
stacks must leave Backspace unchanged until the cursor has been cleared.
Never use a valuable item for an actual destruction test.
For Backspace Leave Quest Details Window, check the native Back action, hidden map/details,
text focus, modifier keys, combat transitions, late quest-UI loading, its independent
switch and item-deletion priority when carrying an item on the cursor.
For Flight Master Auto Map (shift disable), check a normal flight master including Devrak with
`orderIndex=0`, Shift bypass, the saved toggle, duplicate gossip events and quest
priority. Destination selection and flight payment remain manual.
For Questlog XP, check `[15] (1,350+)` formatting, native level/group
prefixes, item rewards, missing reward data and immediate restoration when disabled.
For Left Shift Escape Reload, verify direct key-down handling in the game client,
left versus right Shift, Ctrl/Alt combinations, held-key repeat, the independent
saved toggle, ordinary Escape routing and delayed initial setup during combat.
No permanent or override binding should be created.
Damage Meter Doubleclick Switch is removed. Verify that an old saved enabled flag
is cleared, the settings show nineteen features and no meter setup/click hooks are
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

## Packaging and quest data

The build command reads the version from `BetaQoL.toc` and creates
`dist/BetaQoL-<version>.zip`. The explicit manifest in `tools/build_release.py`
is authoritative. It contains runtime files, four runtime Media assets plus four README screenshots, source data and
importers, user/developer release docs, MIT LICENSE, third-party notices and the
complete quest-data GPL text under a single `BetaQoL/` folder. Tests, caches,
`.test-ui/`, virtual environments and SavedVariables are excluded. The builder
checks ZIP integrity and compares every included file with its source bytes.

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

## Current settings and input checks

The 1.0.0-dev.25 prerelease build uses a compact LFG-style settings list. Open `/qol`:
check portrait/search spacing, the gray toolbar, dark background, full feature names
and left-aligned category headings with indented rows. Hovering a row or checkbox
must show its description without changing the setting; clicking either must toggle
exactly once and persist it. Tooltip titles omit parenthetical qualifiers. Filtering,
scrolling and closing must dismiss owned tooltips without hiding unrelated ones.
Search matching is literal and case-insensitive.
Search temporarily expands matches without discarding category collapse choices.
Check empty results, scrolling after filtering, dragging, Escape, reopening and
small-screen/UI-scale changes. Native rendering still requires a live-client pass.
Verify the 458 x 582 window, neutral textures, gray parenthetical text and search
at the top right. The bottom-left `-` / `+` and `T` buttons must be hidden. Check
the continuous footer texture behind the version, with no separate gray strip. Existing
layout preferences must survive reload without changing feature toggles. Saved
flat mode must still display all matching features without category gaps.

The leveling helpers have passed user testing. Regression checks: Up/Down in multiple
professions, filtered/collapsed categories and text fields; verify no crafting is
triggered. For Panel Arrow Keys (guild and professions), test holding either key in Professions: immediate
selection, a 0.5-second pause, then 0.1-second repeats. Release, text focus, closing
the window and combat must stop repetition without resuming later. Test three-line
wheel scrolling in regular and /g chat plus the native
Communities window. For rank reminders, put an old learned rank on several slots,
keep another spell at its highest learned rank, then login/reload: only the spell
missing its highest rank should be listed once. Add its highest rank without
removing the lower copies and reload: the warning must disappear. Remove all
its normal actionbar placements: it must remain quiet even with old gamepad
copies. Verify disable, combat deferral and no actionbar changes.
This first reminder does not inspect macro branches or pet actions.

In the Guild/Communities chat panel, Up/Down should scroll three lines, then repeat
after 0.25 seconds at 0.05-second intervals. Test chat input focus, switching to non-chat tabs, closing
the panel and opening both professions and guild panels: only the active target
should respond. The interface toggle controls both panels; Chatbox Arrow Keys
remains a separate toggle for standard chat input behavior.

Missing Spell Check is a separate default-on option: remove all ranks of a
class spell from the mouse/keyboard bars, then reload and check for one yellow
message. Place any rank to suppress it. General and passive spells must stay
quiet. Test both options enabled, each option alone, and both disabled.

The addon minimap launcher now uses native icon 132849 with a standard round
border. Verify its position on the right edge below center with Square Minimap on/off, minimap
scaling and other native buttons. Left-click must toggle the existing settings
window without duplicate frames. Its tooltip must disappear on leave, click or
hide without hiding another tooltip. Creation/repositioning waits for combat end.
Complete the final live minimap/UI review and refresh the dev.24 menu screenshot
for 1.0.0. All four supplied documentation captures are already included. MIT covers original project code, documentation and generated artwork;
Questie-derived data retains GPL-3.0. The supplied portrait's source/reuse rights
still need documenting. See THIRD_PARTY_NOTICES.md and RELEASE.md. Damage-meter
switching and Shoot spam remain excluded.

## Future data updates

The September 26 catalog fetch is already integrated: 2,133 pages, 337 Forever
supplement pairs and 17,015 combined pairs across 4,400 NPCs and 1,407 items.
The steps below apply to future updates; no current fetch is outstanding.

Keep a development version until any new fetch/import output is available.
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

## Licensing contributions

Original code, tools, tests, documentation and generated minimap artwork use
[MIT](LICENSE). Do not remove upstream GPL headers or present the complete
data/media bundle as MIT-only. Preserve [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
and [Data/NOTICE.md](Data/NOTICE.md). Historical devlog entries retain the names
and behavior of their time; historical plans are not the current UI specification.
