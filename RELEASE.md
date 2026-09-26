# Preparing 1.0.0

Current prerelease: **1.0.0-dev.25**, targeting WoW Forever Beta 1.60.1,
build 70009, Interface 16001. This document is a checklist, not a publication
record. Version 1.0.0 is not yet released.

## Current state

- All 19 features are implemented. Existing saved settings retain their keys.
- The quest-item fetch and import are complete for the documented catalog.
- The compact settings UI and minimap launcher are implemented.
- MIT covers original project work; the separate quest-data GPL notices remain.
- The automated suite has 274 passing tests. Tests do not prove live rendering
  or the client's secret-value/taint behavior.

## Remaining live checks

- [ ] Confirm the latest feature names, category order and readable gray qualifiers.
- [ ] Review settings at normal UI scale and a smaller screen: compact search,
  portrait, scrollbar, long labels, continuous footer, no old footer buttons.
- [ ] Verify the Mana button opens/closes the same window and leaves native zoom
  controls usable with square and round minimaps, including combat transitions.
- [ ] Recheck the critical gameplay cases in CONTRIBUTING, including Shift bypass,
  ordinary Escape followed by left Shift+Escape, recipe/guild repeat cancellation,
  direct spell-rank comparisons and completed quest-item rows.
- [ ] Confirm the supplied portrait (`Media/Icon.png` / `.tga`) source and reuse
  rights, or replace it with artwork whose provenance can be documented.
- [x] Add the four supplied menu, questlog XP, quest-item rate and minimap captures.
- [ ] Refresh the dev.24 menu capture to show the final feature labels and version;
  optionally add a separate capture of the Mana launcher.

## README screenshots

Use actual game captures of the final build, not edited images implying untested
behavior. Keep chat/player information out of the crop where practical.

1. Settings window with the final title, labels and layout.
2. Minimap launcher and square border, with the menu access visible.
3. Quest tooltip showing an inline item rate; optionally show completed gray text.
4. Optional spell-check chat messages illustrating red/yellow prefixes.

The README now uses four unchanged, user-supplied captures under
`Media/Screenshots/`, with relative links, descriptive alt text and captions.
The build manifest includes all four so the packaged README also renders them.
The settings screenshot is explicitly labeled dev.24 because it predates the
latest names. The minimap screenshot illustrates Square Minimap, not the new
Mana launcher. Replace the menu capture before the final 1.0.0 presentation.

## Build and verify

1. Resolve the remaining checks and review intended changes. Keep disabled
   damage-meter and Shoot experiments out of runtime code and settings.
2. Change the TOC version to `1.0.0` and update README, CHANGELOG, this checklist
   and release notes to the actual release state. Do not rewrite historical devlog
   version headings. Confirm Interface 16001 matches the tested client.
3. Run the full test suite and `git diff --check`.
4. Run `python tools/build_release.py`. Check the ZIP contains a single `BetaQoL/`
   root with TOC/runtime files, Media assets, data and editable sources/importers,
   docs, LICENSE, THIRD_PARTY_NOTICES and Data/COPYING.txt.
5. Install that exact archive in `World of Warcraft/_classic_beta_/Interface/AddOns/`.
   Preserve SavedVariables. Restart for first installation; use `/reload` for
   updates. Perform the final smoke test and compare installed/archive bytes.
6. When publication is requested, commit the reviewed changes, tag that commit
   as `v1.0.0`, and upload its matching `BetaQoL-1.0.0.zip`. Verify the published
   download and release notes refer to the same version and data snapshot.

Development snapshots can be published as prereleases. Version 1.0.0-dev.25
is the current prerelease; this checklist tracks the remaining work for the final
1.0.0 release. The previous stable release remains v0.9.8.

## Release notes content

Summarize the compact settings menu, minimap access, 19 independent defaults,
new spell checks, panel navigation and multiline chat scrolling. Link the
[README](README.md), [changelog](CHANGELOG.md) and
[license notices](THIRD_PARTY_NOTICES.md). Explain that drop percentages combine
Classic estimates and observed Forever frequencies, not guaranteed server rates.
Mention that macros/gamepad/pet actions are outside the spell checks' scope and
that Damage Meter Doubleclick Switch and Shoot spam are not included.
