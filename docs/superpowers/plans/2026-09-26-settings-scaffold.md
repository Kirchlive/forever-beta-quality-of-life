# Native settings scaffold implementation plan

**Historical plan:** Implemented for dev.9, then superseded by the user-approved
single-list design in dev.10 and later polish. The current design and behavior
are documented in [README](../../../README.md) and [CONTRIBUTING](../../../CONTRIBUTING.md).

**Goal:** Implement the user's approved Professions/LFG-inspired two-pane settings window.
**Architecture:** Replace only the lazy settings builder in BetaQoL.lua; keep the existing setting keys and feature callbacks. Use shared native visual templates, never gameplay window mixins.
**Tech stack:** WoW Forever 1.60.1 Lua 5.1, pinned Blizzard UI templates, Python/Lupa tests.
**Spec:** User's reference image and approved two-pane layout in this task (2026-09-26).

## Design

Portrait frame, native GameFont styles, left-aligned text. Native assets determine colors: dark brown/black (#191510), bronze (#806035), gold (#FFD100), light text (#FFFFFF), muted gray (#808080). No web-style cards or added animation.
864 x 620 initial size; left list about 440 pixels, right details about 376. Shrink only when necessary to fit UIParent. Icons are provisional native assets.

## Constraints and review focus

- Preserve all 19 switches, saved false values and feature callbacks; no Damage Meter or Shoot feature.
- Clicking a label selects; only the checkbox toggles. Include full English names and descriptions.
- Search is literal and case-insensitive; empty results must be clear. Searching temporarily expands matching categories without losing collapse choices.
- Filtering/collapsing clamps scroll offset; closing/reopening keeps a usable selection.
- Search does not take focus on opening; Escape and drag work; long names wrap; UIParent size changes must fit the window.
- Native assets/API compatibility must be checked against pinned client source. Actual rendering requires the user's live-client screenshot.

## Steps

- [x] Extend the frame fixture and add behavioral tests; observe expected failures.
- [x] Implement categories, native list/search/scroll, independent selection and right-hand descriptions.
- [x] Run the complete suite; request a bounded independent UI code review.
- [x] Update docs/version, build dev.9, install and byte-verify the local addon and output mirror.

## Execution record

Continue inline under existing user authorization. Retain the existing working tree with prior tested development changes. No public release in this step.

265 tests passed. Independent review found no blocking issue; moved search to x=82 to clear the portrait rim. Built the 15-file ZIP and byte-verified both local installations. Existing live files were backed up before replacement. Live rendering and final icon choices remain for the next user-guided design pass.
