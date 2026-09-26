# Changelog

Current release: **1.0.0**.
Intermediate builds and research are recorded in [DEVLOG.md](DEVLOG.md).

## 1.0.0 - 2026-09-26

Published the complete development series as the latest stable release, including
all features listed below, the Mana minimap launcher, MIT licensing and illustrated
documentation. Panel Arrow Keys is first under Controls. Existing settings and
the quest-item snapshot are preserved. The archived dev.25 prerelease remains
available separately.

## 1.0.0-dev.26 - local, unpublished

Moved Panel Arrow Keys (guild and professions) to the first position in Controls.
The remaining feature order, labels, saved keys and behavior are unchanged.

## 1.0.0-dev.25 - 2026-09-26 (prerelease)

### Added

- Panel Arrow Keys (guild and professions), with held-key repeat and text-input
  protection. Guild scrolls three lines; professions navigates recipes.
- Multiline Scroll (chatframe and guild), keeping standard chat at three lines
  per wheel step and preserving native Communities scrolling.
- Separate Low Spell Rank Check (at launch) and Missing Spell Check (at launch).
  Both run once per login/reload, inspect direct spell actions and never edit bars.
- Searchable native-style settings window with grouped switches, hover help,
  gray qualifiers, custom portrait and a continuous dark footer.
- Primal Mana minimap launcher for the same settings window.
- MIT license for original project work, explicit third-party notices and release
  preparation documentation.

### Changed

- Finalized feature labels without changing saved keys or category order.
- Spell rank checks compare the highest placed rank per spell, preventing warnings
  about lower duplicates when the highest learned rank is already on a bar.
- Guild held-key repeat uses a 0.25-second initial delay and 0.05-second interval;
  professions keeps 0.5/0.1 seconds.
- Settings use a compact single list, replacing the early two-pane prototype.

### Retained

- All existing quest, loot, input, minimap, range and whisper features.
- Completed quest-item catalog snapshot: 17,015 NPC/item pairs, including 337
  Forever observations. No data changes in dev.25.
- Damage-meter switching and Shoot spam remain excluded.

## 0.9.8 - 2026-09-26

Removed Damage Meter Doubleclick Switch after reproducible taint errors. Removed
its settings entry and obsolete saved flag; native Current/Overall selection
remains available. Retained the completed quest-item snapshot from 0.9.7.

Earlier release history: [DEVLOG.md](DEVLOG.md).
