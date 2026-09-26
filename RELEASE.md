# Release 1.0.1

Current release: **1.0.1**, targeting WoW Forever Beta 1.60.1, build 70009,
Interface 16001. GitHub tag: `v1.0.1`; archive: `BetaQoL-1.0.1.zip`.
The release is marked **Latest**, so [the stable download link](https://github.com/Kirchlive/forever-beta-quality-of-life/releases/latest)
opens 1.0.1. The older dev.25 prerelease remains available separately.

## Included and verified

- 19 independently switchable features, saved keys preserved. Missing Spell Check
  now defaults off; explicit saved choices are preserved.
- Final Controls ordering: Panel Arrow Keys first, followed by the Backspace,
  Enter and reload shortcuts.
- Compact searchable settings window and Primal Mana minimap launcher.
- Completed quest-item catalog snapshot with 17,015 NPC/item pairs.
- MIT license for original work, separate GPL data and third-party notices.
- Four unchanged user-supplied README screenshots, bundled in the archive.
- 275 passing automated tests; ZIP integrity and contents checked against source.

Tests do not run the game renderer, server or secret-value/taint VM. Earlier live
feedback is recorded in DEVLOG. The comprehensive regression checklist in
CONTRIBUTING remains relevant for future changes; this release record does not
claim every listed case has been repeated in the final build.

## Documentation follow-ups

The README menu image is a dev.24 capture, explicitly labeled because it predates
the final labels and Controls order. Refresh it when a new capture is available;
an additional capture can show the Mana launcher. The three feature captures
illustrate quest XP, inline quest-item rates and Square Minimap.

The supplied settings portrait's upstream source/reuse license has not yet been
documented. Its exclusion from the MIT grant remains explicit in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Record its provenance when known.

## Future release procedure

1. Review changes and the relevant live checks in CONTRIBUTING. Damage-meter
   switching and Shoot spam remain excluded unless explicitly revisited.
2. Set the new version in the TOC and current documentation; retain historical
   changelog/devlog version headings. Confirm the supported client interface.
3. Run the full tests and `git diff --check`, then `python tools/build_release.py`.
4. Check the ZIP's single `BetaQoL/` root, runtime files, Media assets, editable
   data/importers, documentation, LICENSE and Data/COPYING.txt.
5. Install the exact archive while preserving SavedVariables. Restart for a first
   installation or `/reload` for an update. Compare installed/archive bytes.
6. When publication is requested, commit and tag the reviewed source and upload
   its matching archive. Use an ordinary release with Latest enabled for a stable
   release; a prerelease should not replace the latest stable release.
7. Verify the published tag/commit, download the uploaded ZIP and compare its
   SHA256 with the local artifact. Check the latest-release endpoint explicitly.

Keep screenshots under `Media/Screenshots/`, unchanged unless editing is requested,
with descriptive alt text and captions. Update their version labels honestly and
include all README images in the build manifest.
