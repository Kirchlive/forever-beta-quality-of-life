# Forever Beta Quality of Life – Devlog

Detailed development notes, research, and validation.
The concise feature overview and installation instructions are in the [README](README.md).
Entries below are historical records, including superseded experiments. Current
release status and remaining checks are in [RELEASE.md](RELEASE.md).

## Version 1.0.0 - Latest stable release

Published the current code and documentation as v1.0.0 at the user's request,
with the final Controls ordering from dev.26. The previous dev.25 prerelease
was excluded from GitHub's latest-stable link, which still resolved to v0.9.8.
The new non-prerelease is explicitly marked Latest; README downloads now use
that stable link. The earlier tag and assets are preserved.

Validation: 274 tests pass; the 26-file release archive includes screenshots,
source data, MIT and GPL notices. Publication verification compares the uploaded
ZIP to the local build and checks that releases/latest resolves to v1.0.0.
The menu screenshot remains an explicitly labeled dev.24 capture; unknown
portrait provenance remains disclosed in THIRD_PARTY_NOTICES.md.

## Version 1.0.0-dev.26 - Controls ordering

Moved Panel Arrow Keys (guild and professions) to the first row under Controls,
with matching README ordering. Existing setting keys, feature names and behavior
are unchanged. Local build only; the published dev.25 archive remains intact.

## Version 1.0.0-dev.25 - Naming, MIT license and documentation refresh

Documentation follow-up: included four unchanged user-supplied game captures
under Media/Screenshots. The README leads with the settings panel and places
quest-item rate, questlog XP and minimap examples beside their features. Each
has a caption, alt text and a full-size link. The dev.24 menu image is labeled
as such; final feature names remain those in the live code and feature list.
All four images are included in the ZIP; runtime code/version is unchanged.

Renamed Panel Arrow Keys (guild and professions) and Multiline Scroll (chatframe
and guild), preserving keys, category order and behavior. Added the MIT license
for original project code, documentation and generated minimap artwork, plus
explicit notices for GPL quest data, the Wowhead snapshot and client artwork.
The user-supplied portrait's upstream provenance remains a public-release check.

Refreshed the README around the actual 19-feature interface, completed minimap
launcher, spell checks, scrolling timings and data limitations. Reorganized
contributor guidance; added a concise changelog and 1.0.0 release checklist.
Marked the earlier two-pane settings plan as historical and repaired known
encoding corruption in old development headings. Data contents are unchanged.

Validation: 274 automated tests pass; the release archive includes MIT and GPL
licenses, third-party notices, current user/developer docs and source data.
Published as the v1.0.0-dev.25 prerelease after the user requested upload.
The archive includes all four README captures, MIT/GPL notices and editable data
sources. Version 0.9.8 remains the latest stable release; final 1.0.0 is pending.

## Version 1.0.0-dev.24 - Minimap launcher and final feature names

Added an addon-owned 32-pixel minimap button using the native Primal Mana icon
(file ID 132849) and standard minimap button artwork. Left-click opens or closes
the same lazy settings window as /qol. A tooltip explains the action. The button
sits on the right edge below center, clear of the native zoom controls, and
inherits minimap scaling. Creation and positioning wait until combat ends; late
minimap loading is handled by the existing minimap events. No external library
or bundled icon download is required. Native click handlers remain untouched.

Renamed Chatbox Arrow Keys, Panel Arrow Keys (Professions and Guild), Low Spell
Rank Check (at launch), and Missing Spell Check (at launch). Saved setting keys,
feature order and spell-check behavior at login/reload are unchanged.

Validation: 274 automated tests pass, including four launcher lifecycle, click,
shape and tooltip ownership checks. In-game placement/artwork review is pending.

## Version 1.0.0-dev.23 - Darker footer

Lowered the footer rock texture tint from 0.24 to 0.18 per color channel for a
slightly darker bottom bar. Texture, text colors and layout remain unchanged.

## Version 1.0.0-dev.22 - Compact search strip and continuous footer

Reduced the upper strip by 60 UI pixels and moved a 200 x 22 search box to its
right edge. The window is now 458 x 582; feature-list and footer heights stay
unchanged. Both disabled footer controls are now hidden. Extended the footer's
rock texture to the bottom border so the version sits on the same background
as the hints, without a separate gray strip. Feature order, portrait positioning
and saved layout preferences remain unchanged.

Validation: 270 automated tests pass; native rendering awaits in-game review.

## Version 1.0.0-dev.21 - Settings polish and quicker guild arrows

Changed the title bar to Forever Beta Quality of Life and increased window height
by 20%, from 535 to 642 pixels. Replaced the LFG scene and role-section image with
neutral, dark desaturated rock textures. The top texture now fills the strip
without embedded artwork borders. Search sits near its bottom, with its visible
left border aligned to the feature checkboxes. Parenthetical label text is gray;
search still uses the plain labels. Renamed the requested six labels (Enter
Confirm Dialog Box already matched) without changing feature keys or ordering.
The two footer buttons are visible but disabled; existing layout choices persist.
The 50-pixel portrait and its previously approved offsets remain unchanged.

Guild/Communities arrow scrolling keeps three lines per step but halves initial
delay to 0.25 seconds and repeat interval to 0.05 seconds. Profession navigation
retains 0.5/0.1-second timings. Release, text focus, modifiers, combat and hidden
panels still cancel repetition.

Validation: 270 tests pass, including precise guild-repeat boundaries, unchanged
profession timing, disabled footer controls, retained layout choices, gray labels
and plain-text search. Live review remains necessary for texture tone and spacing.

## Version 1.0.0-dev.20 - Portrait size and horizontal alignment

Set the portrait to 50 x 50 UI pixels and moved its center one pixel left.
Preserved the previously approved two-pixel upward offset. The top-left anchor
is now (0, 3), accounting for the larger image while keeping its vertical center.

## Version 1.0.0-dev.19 - Portrait vertical alignment

Moved the 48 x 48 window portrait upward by two UI pixels at the user's request.
Its size and horizontal position are unchanged.

## Version 1.0.0-dev.18 - 48-pixel portrait

Adjusted the window portrait to 48 x 48 UI pixels after the user's 32-pixel
comparison. Retains the native portrait center and unchanged outer frame.

## Version 1.0.0-dev.17 - 32-pixel portrait test

Set the window portrait to 32 x 32 UI pixels at the user's request. Its center
remains at the native portrait center; outer frame and artwork are unchanged.

## Version 1.0.0-dev.16 - Further portrait size adjustment

The user's in-game diagnostic confirmed the dev.15 portrait was 58 x 58; the
client did not reset its dimensions. The user still perceived the icon as too
large. Reduced it to 54 x 54 (another four pixels in each dimension), centered
on the native portrait position. This is a visual adjustment, not a verified
fix for a client size override. The outer frame and source artwork stay intact.

## Version 1.0.0-dev.15 - Inset window icon

Reduced the displayed portrait from the native 62 x 62 to 58 x 58 UI pixels.
Adjusted its anchor by two pixels per edge to keep the image centered in the
unchanged circular frame. The source artwork remains unchanged.

## Version 1.0.0-dev.14 - Custom window portrait

Replaced the placeholder book portrait with the user's Media/Icon.png artwork.
Preserved the source PNG and converted its pixels to an uncompressed 32-bit TGA
for the in-game texture. Both files are included in the release archive. The
native circular mask and portrait border remain unchanged.

## Version 1.0.0-dev.13 - Shorter window and illustrated top strip

Reduced the window height by one fifth, from 669 to 535 pixels, retaining its
458-pixel width. The scroll viewport adapts in both bottom-bar states. Replaced
the top strip's rock texture with the native LFG role-section image
(Interface/LFGFrame/UI-LFG-BlueBG), desaturated and darkened while preserving
visible image structure. Checkbox alignment and saved layout choices remain.

## Version 1.0.0-dev.12 - Keep checkbox alignment when hiding headings

Hiding category headings now removes only headings and vertical gaps. Feature
rows keep the same 18-pixel horizontal inset in both views, so checkboxes and
labels no longer move sideways when toggling T.

## Version 1.0.0-dev.11 - LFG bars and compact-list controls

Matched the upper strip to native LFG proportions (102 pixels beneath the title)
and replaced the flat fill with a dark desaturated native rock texture. Restored
an expanded 120-pixel bottom section, including a permanent 37-pixel button strip.
The small bottom-left minus/plus control collapses the extra 83 pixels and returns
that space to the scrolling list. An adjacent T button toggles category headings.

With headings hidden, all matching features form a continuous uniformly indented
list without category gaps. Collapsed categories do not hide their features in
flat mode; their collapse choices return when headings are shown again. Both
window layout choices are saved in BetaQoLDB.settingsUI independently of the
19 feature switches. Both controls stay accessible in the collapsed layout.
Window size, native title bar and outer border remain unchanged.

Validation: 269 automated tests pass, including footer resize/reopen, continuous
flat rows, collapsed categories in flat mode, search and cross-runtime saved
layout/feature preferences. Actual texture darkness still needs live visual review.

## Version 1.0.0-dev.10 - Compact LFG-style settings

Reworked the settings scaffold after the user's live visual feedback. The window
now matches the native LFG width (458) and is about 25% taller (669 versus 535).
Removed the right-hand detail pane. All five category headings remain left aligned
in a single list, with features indented underneath. The list uses GameFontNormal
instead of GameFontNormalSmall and 22-pixel minimum rows with additional height
only when labels wrap. The portrait, title bar and outer border remain native;
the toolbar is neutral gray and the groupfinder backdrop is desaturated/darkened.

Descriptions and usage notes are available on hover. Tooltip headings omit
parenthetical qualifiers, and Enabled/How it works headings are removed. Clicking
a label or checkbox toggles the feature once. Hover alone does not toggle it.
Owned tooltips are dismissed on leave, filtering, scrolling and closing. Search,
category collapse, saved preferences, dragging, Escape and screen fitting remain.

Validation: 266 automated tests pass. A focused read-only review found no blocking
issues in native APIs, layout bounds, click handling or tooltip cleanup. Built and
installed locally for the next visual check; no public release in this step.

## Version 1.0.0-dev.9 - Native two-pane settings scaffold

Replaced the tall checkbox window with an 864 x 620 portrait frame inspired by
Forever's Professions and LFG panels. The left pane groups all 19 features into
Quests, Chat, Controls, World & Interface, and Spells. Native category headers,
search, scrollbar and recipe selection art provide the first visual scaffold.
The right pane shows a provisional icon, full feature name, current enabled state,
description and usage notes. Row selection is separate from checkbox activation.
Existing setting keys, feature behavior and saved preferences are retained.

Search matches feature/category names literally and case-insensitively, including
punctuation. Search expands matching categories temporarily; clearing it restores
collapse choices. Filter/collapse changes clamp the scroll offset. The frame is
movable, closes with Escape, clears search focus on closing and scales down only
when needed to fit the UI parent. All visuals belong to the addon's own window;
no native gameplay frames or global handlers are replaced.

Validation: 265 automated tests pass, including selection versus toggling, status
refresh, search/empty results, collapse restoration, scroll clamping and window
reuse/fit. A focused independent review checked shared templates against the
pinned Forever UI source; search was moved clear of the portrait rim. Actual
texture appearance, font wrapping and mouse dispatch still need live-client
verification. Final icons, minimap button and 1.0.0 release remain later steps.

## Version 1.0.0-dev.8 - Restore three-line guild arrows

The user found five-line jumps difficult to follow during live testing. Restored
three lines per Up/Down step, including held-key repeats. Repeat timings,
profession navigation and mousewheel behavior remain unchanged.

## Version 1.0.0-dev.7 — Five-line guild arrow test

Changed Guild/Communities Up/Down navigation from three to five lines per step
at the user's request. Repeat timing remains 0.5 seconds initially / 0.1 seconds
thereafter. Recipe navigation and mousewheel scrolling are unchanged.

## Version 1.0.0-dev.6 — Interface arrows for professions and guild chat

Renamed `Professions Book Arrow Keys` to
`Arrow Keys Interface (Professions and Guild)` and `Arrow Keys Chat Control` to
`Arrow Keys Chatbox`, retaining both saved keys and user preferences.
The interface option now also scrolls `CommunitiesFrame.Chat.MessageFrame` by
three lines per Up/Down step. Both targets share the same controller implementation
and native-style 0.5-second initial delay / 0.1-second repetition. Profession
selection behavior stays the same. No native mousewheel scripts are changed by
this option, and no chat messages are sent.

Only the visible target with the higher parent window frame level handles input
when both panels are open (professions wins a tie). Text focus and modifier keys
retain priority. Independent held-key state per target prevents switching panels
from carrying a repeat across; hide, combat, disabling and target replacement
cancel it. The user confirmed profession repeats before this extension.

Validation: 261 automated tests pass, including all previous recipe repeat tests
and new guild tests for three-line steps, delay/release, text focus, modifiers,
hidden chat, combat, disabling, late loading/replacement and simultaneous windows.
Guild keyboard dispatch still needs live-client confirmation.

## Version 1.0.0-dev.5 — Hold-to-repeat recipe navigation

Renamed the setting to `Professions Book Arrow Keys`, preserving its saved key.
Up/Down still selects immediately. Holding waits 0.5 seconds before repeating
every 0.1 seconds, matching `panDelay` and `panRepeatTime` from the pinned native
`Blizzard_SharedXML/Shared/Scroll/ScrollBar.xml`. An OnUpdate handler exists only
while a navigation key is held. OS repeat events do not add duplicate steps or
restart the delay. Direction changes start a new delay; frame stalls never cause
a burst of catch-up selections, and list boundaries do not wrap.

Release, physical key-up recovery, text focus, modifiers, hiding/replacing the
window, disabling the option and entering combat cancel the repeat. Reopening
the window does not resume an old hold. No crafting actions or bindings change.
Validation: 255 automated tests pass. The user confirmed the earlier recipe
navigation, faster chat scrolling and both spell checks in the live client;
hold-to-repeat behavior still needs live confirmation.

## Version 1.0.0-dev.4 — Separate rank and missing-spell checks

Renamed the existing option to `Low Spell Rank Check (at launch and reload)`
while retaining its saved key and existing preference. Removed `Higher` from
the red-prefix message. Added the independent, default-enabled
`Missing Spell Check (at launch and reload)` with a yellow-prefix message:
`BetaQoL: Smite not in actionbar.`

Both options share one deferred login/reload scan. Missing checks ignore rank:
any directly placed rank satisfies a spell family. Only active learned spells
outside `Enum.SpellBookSkillLineIndex.General` participate. Passive, future and
off-spec entries remain excluded; missing category metadata suppresses missing
warnings rather than guessing. Standard mouse/keyboard actions remain the scope;
macro branches and pet/gamepad bars are not inspected. Neither check changes bars.
The settings window now has nineteen options with slightly tighter row spacing.

Validation: 249 automated tests pass, including independent toggles, exact
message colors/text, General exclusion, missing-family deduplication, any-rank
presence, reload/zone transitions, saved preferences and combat deferral.
The user subsequently confirmed the new missing check working in the live client.

## Version 1.0.0-dev.3 — Shorter rank reminder

Live testing confirmed correct reminders after deliberately replacing four spells
with lower ranks. Shortened the message to, for example,
`BetaQoL: Higher Smite Rank 3 available. Check your spellbook.`
Only the `BetaQoL:` prefix is red; the remaining text uses the normal chat color.
Rank detection is unchanged.

## Version 1.0.0-dev.2 — Compare the highest placed rank per spell

The first live reminder test exposed two problems: it warned per lower-rank
placement even when the highest learned rank was also on a bar, and the default
All actionbar set included extra stored starter ranks. The user's diagnostic
showed Smite rank 3 in slot 1 and Lesser Heal rank 3 in slot 62, alongside rank 1
copies in slots 200 and 197.

The reminder now groups active spellbook entries by their native spell name,
identifies the highest learned rank using the native low-rank predicate, and
checks direct actions in the explicit Mkb actionbar set. Candidate lookup is not
treated as an exact spell match: actual slot IDs must match a spellbook spellID.
It reports a family once only when some rank is placed but no highest learned
rank is present. Spells absent from those bars are ignored. No localized rank
number parsing or static rank table is needed. The message names the available
higher rank instead of claiming a particular lower rank is on the bar.

Regression tests cover the supplied slot/rank example, several lower copies,
highest-plus-lower placements, base-ID aliases, broad candidate results and
gamepad-only spells. Subsequent live confirmation is recorded under dev.3 above.

## Version 1.0.0-dev.1 — Leveling helpers (local test build)

Adds three independent, default-enabled options after the existing fifteen.
Recipe arrow keys use the native recipe-list selection and scrolling methods,
enumerating only expanded, filtered entries. A child keyboard listener stays
inactive while typing, using modifiers, or in combat. Chat scrolling replaces
each standard chat frame's mousewheel handler with a three-line step and restores
the original on disable. Review caught that FloatingChatFrame_OnMouseScroll is
not the active ordinary-chat handler in the pinned client. The actual ScrollUtil
initializer already installs a three-step callback; tests now cover that path
as well as older one-step handlers. The separate Communities handler is untouched.

Low Spell Reminder follows the user's requested login-only behavior, also running
after a UI reload for testing. It uses the player's native spellbook low-rank
predicate and exact direct-action IDs. Duplicate placements are combined and
checks defer until out of combat. No action slots, spellbook entries or native
frames are modified. No cast observer, trainer cache, chat broadcasting or static
rank database is involved. Macros and pet actions are outside this first scope.

Research inspected actual sources from
[RankUp 1.3.0](https://www.curseforge.com/wow/addons/rankup/files/8915594),
[Nova Spell Rank Checker 1.63](https://www.curseforge.com/wow/addons/nova-spell-rank-checker/files/8948193),
[Ranksmith 0.3.2](https://www.curseforge.com/wow/addons/ranksmith/files/8969642), and
[RankSentinel 2.6.6](https://github.com/valkyrnstudios/RankSentinel/tree/v2.6.6).
Their approaches differ: actionbar upgrades, manual rank scans, trainer-service
reminders and combat-log checks respectively. BetaQoL's implementation is original;
it does not copy their code. In particular, Nova's source is All Rights Reserved.
Native API/source comparison uses the existing pinned Forever UI commit.

Validation: 239 automated tests pass. Verification covers native recipe selection, categories/filters, text
focus, combat, late-loaded windows, saved toggles, native chat scrolling, exact
rank matching, duplicate placements, unavailable APIs and delayed login checks.
Live confirmation is still required, especially native rank lookup in Forever.
Settings design, minimap access, licensing and release images remain separate
1.0.0 work. Damage-meter switching remains removed. Quest-drop data is unchanged.

## Version 0.9.8 — Remove unsafe damage-meter shortcut

Released September 26, 2026, after the user approved keeping Damage Meter
Doubleclick Switch disabled and hidden. The addon no longer attaches any meter
setup or click hooks. Its settings entry/default and obsolete saved flag are
removed. The other fifteen features keep their order and saved choices; the
settings window is shortened to fit. Native Current/Overall menu selection remains
available. This release removes the faulty integration; it does not claim to fix
or replace the switching implementation or establish the client crash's cause.

The quest-item database is unchanged from 0.9.7: 17,015 NPC/item pairs, including
337 supplemental Forever pairs from the completed 2,133-page catalog fetch.
The latest user screenshot shows the inline yellow percentage next to Bristleback
Quilboar Tusk while the separate kill objective receives no item percentage.

Validation: 225 automated tests pass. Coverage includes old saved enabled flags,
absence of meter hooks, normal native menu selection, settings persistence and
the shifted Whisper Tab checkbox. User testing confirmed normal meter selection
without the shortcut. Release packaging is verified independently of tests;
fixtures cannot prove the absence of all client taint errors.

Next session toward 1.0.0: final UI design polish, an addon minimap icon for settings
access, live-client checks and final release documentation. The damage-meter
shortcut stays excluded; an optional later feasibility review is separate from
the 1.0.0 release requirements.

### Development history: 0.9.8-dev.4 — Hide suspended shortcut

At the user's request, Damage Meter Doubleclick Switch is completely absent from
settings. Its inactive checkbox and default are removed, and the obsolete saved
flag is cleared on load. The settings window now fits fifteen features; Whisper
Tab Doubleclick Close follows Flight Master Auto Map. No damage-meter hooks or
switching scripts run. Normal native menus remain available. This is still a
local development build, not a repaired switching implementation.

Validation: 225 tests pass, including obsolete enabled settings, native meter
handlers, normal menu selection, remaining settings and whisper-tab toggling.

### Development history: 0.9.8-dev.3 — Suspend unsafe damage-meter shortcut

The user confirmed normal menu selection with the shortcut disabled produces no
damage-meter errors. Enabling `taintLog 2` and reloading produced many native
GamepadActionBars nil-call errors before switching. Clicking the session button
then caused a client assertion at `lua-5.1/src/ldebug.c:747` on build 1.60.1.70009.
The saved crash stack is in native `MenuVariants:CreateRadio` while opening the
menu, with no BetaQoL callback on that stack. This does not prove whether logging,
addon taint or another client defect caused the assertion. No taint log was found.
Do not repeat this logging experiment. Crash text, minidump and attempted code
were backed up locally outside the repository; no private crash data is shipped.

The damage-meter integration is removed from active code. Its checkbox is locked
off, including when SavedVariables contain `true`; the saved preference itself
is retained. No native setup hook or double-click handler is attached. Other
features and normal meter menus remain available. This is a containment measure,
not a working replacement for the shortcut. No new public release was made.

Validation: 225 tests pass. Replacement tests verify no hooks with saved enabled
preferences, no reactivation from settings, late/new windows left alone and native
menu selection/persistence. The unsupported switching tests were replaced rather
than counted as proof that taint was fixed. User action: disable logging with
`/console taintLog 0` and reload to clear previous runtime state.

### Earlier 0.9.8 development attempts — Native damage-meter menu selection

**Not fixed / not released:** the user also reproduced the secret-value error
with 0.9.8-dev.2 after the first double-click (`sourceDisplayType`, 2026-09-26
06:10:59). All three switching approaches have now failed live validation.
Do not treat the passing routing tests as evidence of taint safety. Further
implementation is paused pending the first taint-write trace; no `taint.log`
was present in the local client's Logs directory when inspected. Temporary
workaround: disable this shortcut and reload before using the native menu.

The user reported a secret-number comparison in Blizzard's `SetSessionDuration`
after spell casts, with execution attributed to BetaQoL. Version 0.9.7 called
`SetSessionWindowSessionID` directly from addon execution, which writes native
session and saved state before refreshing the meter. This is a plausible source
of persistent taint in later native timer updates.

The first development fix called native menu generation, radio navigation and
closing through `securecallfunction`. Live testing disproved that fix: errors
began after the first double-click and persisted after disabling the feature,
including failures in both timer and damage-entry updates. A wrapper alone did
not prevent persistent taint; the earlier simulated security-context test was
not evidence about WoW's actual taint VM.

The user's `issecurevariable` diagnostic found `sessionType`, `sessionID` and
`onUpdateReasons` secure, but `localPlayerIndex` tainted by BetaQoL. The latter is
read and rewritten in native `BuildDataProvider`, consistent with contamination
persisting through subsequent refreshes. This localizes affected display state;
it does not yet prove which earlier menu operation introduced the taint.

In 0.9.8-dev.2, the handler only reads the existing menu built by the native first
mouse-down, finds the opposite session entry by its data, and invokes that entry's
`Pick(MouseButton, LeftButton)` action through `securecallfunction`, the same
selection action used by `MenuTemplates`' native `OnButtonClick`. No generation,
navigation, forced refresh, manual close or direct session writes remain in the
addon handler. A missing entry is left alone. Blizzard's responder owns the
selection, persistence and resulting UI updates; combat data and timers are not
modified by BetaQoL.

Validation: 231 tests pass. The tests reject additional menu generation or
dropdown updates during our handler, verify original entry identity, mouse-click
arguments, native responder dispatch, saved selection and missing/reordered
entries. They cannot establish absence of client taint. Live verification after
`/reload`, repeated switches and spell casts is still required. Reload is necessary
to clear state affected by earlier attempts; toggling the feature off alone does
not undo existing taint.

## Version 0.9.7 — Quest tools and complete catalog import

Released September 26, 2026. All sixteen features default on with independent
saved switches; the settings names and order match the final user-approved list.

### New shortcuts and navigation

- **Backspace Leave Quest Details** invokes the native Back button, preserving
  the return map and quest overview. Text focus, modifiers, picked-up items,
  hidden details and disabled buttons retain their native behavior. It yields
  in combat and supports quest UI loaded later.
- **Flight Master Auto Map (shift disable)** selects the available taxi option
  through the native gossip API, including Devrak's `orderIndex=0`. Enabled
  quest handling keeps priority. Holding Shift while speaking to the NPC keeps
  the entire conversation manual, even after release. No destination is selected
  and no fare is confirmed. The addon adds no transition timer.
- **Damage Meter Doubleclick Switch (current and overall)** switches the clicked
  native window through its owner's saved-session method. Single-click menus,
  individual encounter selections and other windows stay unchanged.
- **Left Shift Escape Reload** observes physical LSHIFT events and Escape directly.
  The former Ctrl+Escape shortcut conflicted with Windows. A diagnostic showed
  click callbacks but a false IsLeftShiftKeyDown result in the live client, so
  the implementation uses key events and MODIFIER_STATE_CHANGED. It preserves
  normal key routing and does not alter bindings. Ordinary Escape never arms the
  repeat guard, preventing a lost key-up from blocking a later reload. Initial
  protected keyboard setup is deferred if the addon loads during combat.

Quest XP now uses parentheses: `[15] (1,350+) Chen's Empty Keg`.
The plus still identifies guaranteed or selectable item rewards.

### Quest-item data and presentation

All 2,133 pages from the quest-item/drop-source catalog were parsed, with zero
missing or invalid pages. The shipped Wowhead Forever supplement contains
337 NPC/item pairs covering 176 items and 283 NPCs: 46 additional pairs compared
with the development snapshot, with all 291 prior observations retained.
The combined lookup has **17,015 pairs, 4,400 NPCs and 1,407 items**.

The importer validates the Forever environment, exact item IDs and normal-mode
loot counts. Each supplemental pair requires a newly marked NPC or item. Original
Classic pairs remain intact: no removed or changed baseline pairs. This avoids
mistaking inherited Classic observations for verified Forever probabilities.
Source counts, URLs and page hashes ship in the snapshot. The complete catalog
fetch does not supply usable rates for all quests; unknown pairs stay omitted.

Percentages inherit the native quest-heading yellow; completed objectives inherit
the item row's gray while the quest remains in the player's log. Every matching
item uses its own NPC/item rate. Values round to whole percentages; rates >=19%
snap to the nearest 5% step only within one percentage point (69.4 → 70,
20.5 → 20, 27.8 → 28). Positive values rounding to zero show `<1%`.
Raw values remain unchanged. Repeat tooltip updates do not stack suffixes.
See `Data/NOTICE.md` and `Data/RESEARCH.md` for provenance and scope.

### Verification

All **227 automated tests pass**. The final supplement was independently rebuilt
from every cached page and matched exactly, including page hashes. The generated
combined lookup reproduces byte-for-byte from the included source data. A separate
read-only review found no blocking correctness or regression issues.

The user confirmed XP formatting, flight-map opening, Backspace quest navigation,
damage-meter double-click switching and the final reload shortcut/normal-Escape
fix in the live client. Data coverage is validated offline; every new NPC/item
pair has not been individually exercised in-game. The release ZIP is built from
this current code, preserving gameplay changes made during the external fetch.

### Deferred experiment — Shoot Spam By Default

The user-confirmed manual-reset Shoot prototype remains excluded from the addon
and settings. Reliable automatic reset in combat is unresolved. The community
report [forever-bugs #114](https://github.com/ClassicWoWCommunity/forever-bugs/issues/114)
matched the observed `/cast !Shoot` toggle problem; at the September 26 check it
was open without a confirmed workaround. No Shoot functionality is shipped.

## Version 0.9.6 — Quest Item Drop Rate

Adds a default-on `/qol` option for quest-item drop estimates in the standard
mob tooltip. Native typed quest lines determine ownership;
`C_QuestLog.GetQuestObjectives` restricts the display to item objectives from quests
still in the player's log. Completed objectives remain eligible (including 5/5);
turn-in or abandonment removes eligibility even if native tooltip data is stale.
Grouped player sections use GUIDs when available, with the existing Forever
first-name fallback. Exact objective/item names are matched against the NPC's
item candidates; ambiguous names are omitted. Localized names come from C_Item,
with English source names as an English-client fallback. Missing localized item
names are requested once and picked up on subsequent native tooltip builds.

Research of Questie Forever v27 found its drop display uses Classic database
lookups by NPC/item pair: explicit Era corrections, then CMaNGOS, then Wowhead.
BetaQoL bundles a generated lookup with that same precedence. The Classic
provenance and lack of verified Forever-specific probabilities are explained in the README. Rates appear as a yellow `(40%)` suffix on the native
quest-item row, using its recorded `lineIndex`. No extra tooltip line is added;
native colors and completion icons are preserved. Shared tooltip data is not
modified and repeat callbacks do not duplicate the suffix. There is no made-up
default rate, loot recorder, network access or external addon dependency. Original data, GPLv3 notice and the reproducible
Python importer ship with the package. See `Data/NOTICE.md`.

Tests cover known and unknown NPC/item pairs, incomplete/completed item goals,
kill objectives, own/group sections and GUIDs, exact and ambiguous item names,
localized/uncached data, rebuild deduplication, settings persistence, secret and
forbidden values, and all packaged rate ranges. All 183 automated tests pass.
The user confirmed the Classic Ornery Plainstrider
(NPC 3245) / Plainstrider Kidney (4894) value of 40% in the live client.
The final inline styling is covered by automated tests and native UI source
inspection; live visual confirmation remains pending.
Released September 25, 2026.

## Version 0.9.5 — Questlog Quest XP (+ for item rewards)

Adds **Questlog Quest XP (+ for item rewards)**, enabled by default with its own `/qol` switch.
The quest overview displays `[level] [XP] title` using the client-provided
`GetQuestLogRewardXP(questID)` value and localized number formatting. The explicit
quest ID avoids changing quest selection. Hidden, unavailable, or invalid reward
values do not add a label; a known zero reward displays `[0]`. A `+` inside the
brackets indicates guaranteed or selectable item rewards. Money, reputation
and currency rewards alone do not add the marker.

Extends the native Camelot title prefix before title measurement and layout,
keeping native level/elite notation, party counts, title colors, and wrapping.
Native quest-list rebuilds pick up current values without a reward cache;
data-load and player-level events also refresh the visible list. The setting
restores native titles immediately when disabled.

Eight new tests run the pinned native title builder and Camelot prefix, covering
format/order, repeated builds, elite/group markers, saved settings and toggles,
missing/hidden rewards, delayed data, level changes, late UI loading and event
coalescing. All 168 automated tests pass. The user confirmed the XP values,
layout, and item-reward markers in the live client. Missing reward data is
displayed when supplied by the client; this feature does not initiate additional
reward-data requests.
Released September 25, 2026.

## Version 0.9.4 — Chat Input History Recall

The user found that Up/Down still required Alt after the 0.9.3 release. Setting
`SetAltArrowKeyMode(false)` alone enables cursor movement but does not supply
unmodified input-history recall. The original tests verified arrow-mode state,
not recalled text, and missed this behavior.

Adds a bounded, per-edit-box session history by observing native `AddHistoryLine`
calls. Up/Down browse those entries, preserving the current draft. Existing native
history and send handlers remain untouched. Focus, modifiers, autocomplete,
disabling the feature, and clearing history are respected. Protected commands
are excluded to avoid re-inserting them through an insecure addon execution path;
they remain available through native Alt+Up/Down. History is not saved to disk
and starts with messages entered after the addon attaches to the edit box.

Five new regression cases fail against 0.9.3 and pass with the correction.
A sixth parser-aware case verifies that returning to a whisper draft also restores
its recipient and chat type after recalling a public message. All 160 tests pass.
The user confirmed Up/Down recall works in the live client.
Released September 25, 2026.

## Version 0.9.3 — Chat Arrow Keys, Grouped Quest Names and Defaults

Adds **Arrow Keys Chat Control**, enabled by default and independently switchable
under `/qol`. Native chat edit boxes use `SetAltArrowKeyMode(false)` for cursor
movement and input history while focused. Existing and newly opened chat/whisper
windows are covered. Disabling restores each edit box's previous mode; active
autocomplete keeps its arrow navigation and restores the correct mode afterward.
No global key bindings or unrelated edit boxes are changed. The settings window
now accommodates ten features. All 154 automated tests pass, including five new
chat-mode tests. The user confirmed Arrow Keys Chat Control works in the live client.

Fixes a grouped-tooltip name mismatch: the user's live API dump returns
`Zeig Mal, nil` from both `UnitName` and `UnitNameUnmodified`, while `UnitFullName`
returns `Zeig Mal, ClassicBetaPvE`. The grouped quest tooltip displays only
`Zeig` (3/8) and `Dark` (5/8). Exact comparison with the combined name rejected
all of the player's objectives in a group, even before any kill.

The matcher now uses Forever's native `NameUtil.GetUnitFirstName` to recognize
the short tooltip name. Full display-name and realm-qualified fallbacks remain
supported. Completed own objectives still hide markers while another player's
objectives remain incomplete. The 0.9.2 visibility fix remains.

All ten features now default to enabled at the user's request. Explicit restored
on/off preferences are still preserved. The community project
[ForeverSVFix](https://github.com/nobewayo/ForeverSVFix) reports a beta-client bug
that writes SavedVariables but fails to restore them. Our simulated restart tests
validate addon logic only; they cannot establish that the client loader works.
The workaround has not been installed or bundled.

Grouped-name tests execute the pinned native Camelot `NameUtil`
against the captured API values, covering the first sighting while grouped,
solo-to-group transitions, own completion and full/single-name fallbacks.
The reproduced group cases fail without the name change. The user confirmed the
grouped display after enabling the option.
Released September 25, 2026.

## Version 0.9.2 — Stable Quest Nameplate Icons

Fixes an unnecessary hide/show cycle: removing any nameplate previously hid all
quest markers until a deferred refresh. Refreshes also hid and re-showed every
eligible icon even when its state had not changed. Two regression tests reproduce
both behaviors in 0.9.1 and pass with this change.

Removal now hides only the departing unit's marker. Refreshes reconcile visibility
once after scanning, leaving unchanged icons shown. Completed objectives, missing
or restricted data, disabled settings and pooled-frame reuse still hide markers
as before. The feature remains disabled by default; saved choices are preserved.

All 145 automated tests pass. The user reports that the movement-related flicker
appears resolved after testing the local fix in the live client.
Released September 23, 2026.

## Version 0.9.1 — Quest Icon Disabled by Default

Quest Target Nameplate Icon now starts disabled for new installations and when
its saved setting is missing or invalid. Enable it in `/qol`. Existing explicit
on/off preferences are preserved. Square Minimap also remains disabled by default.
Released September 23, 2026. All 143 automated tests pass, covering both default-off
initialization and continued operation with a saved enabled preference.

## Version 0.9.0 — Quest Target Nameplate Icon

Adds a ninth `/qol` option, enabled by default. A non-interactive native purse
texture appears to the left of the standard nameplate health bar for NPCs with
unfinished objectives of the player's active quests. Item drops, kills and
non-count interactions use the same typed quest-objective data. A completed
objective for this NPC does not remain marked merely because a different
objective of the same quest is incomplete. Another open quest for the same NPC
keeps the marker visible. Explicit preferences are preserved.

The live Forever 1.60.1 capture supplied by the user contains QuestTitle type 17
with `id=844`, followed by QuestObjective type 8 with `completed=false`,
`numFulfilled=1` and `numRequired=7`. Eligibility uses `C_QuestLog.IsOnQuest(id)`
and these objective fields. QuestPlayer blocks restrict progress to the local
player. Missing, restricted or unavailable data produces no marker. No tooltip
CVars are changed, and no mob/drop database or additional addon is required.

Quest/nameplate events coalesce refreshes. A half-second refresh while plates
are present handles delayed server data; disabling the feature stops polling.
Textures follow the native health-bar pool, hide on unit removal, and do not
alter click areas, scale or targeting. They also disappear with the health bar.

Validation: 143 automated tests pass, including the captured live tooltip,
objective completion, multiple quests, party filtering, pooled-frame reuse
using the pinned native NamePlateBaseMixin, delayed data and saved settings.
The user confirmed the feature works in the live client and supplied a screenshot
showing the marker beside a Greater Plainstrider. Grouped QuestPlayer formatting
remains covered by simulated data, not a captured live group tooltip.
Released September 23, 2026.

## Version 0.8.2 — Narrower Minimap Rim and Refactor

Compresses the Square Minimap rim from 10.2 to 8.2 UI units: its outer edge
moves inward by one unit and its inner edge outward by one unit. The centerline
and bronze color profile are preserved. The rounded mask expands to meet the
new inner edge, retaining the small overlap that prevents transparent seams.
Icon positions and settings remain unchanged. Square Minimap remains disabled
by default; existing saved preferences are preserved.

Separates border creation and native ring visibility into focused Lua helpers.
The artwork generator now names its UI-space geometry explicitly. The refactor
preserves the narrower artwork byte for byte. All 129 automated tests pass.
Released September 23, 2026.

## Version 0.8.1 — Brighter Minimap Highlight

Brightens only the central bronze highlight and its immediate shoulders.
Border geometry, inner/outer contours, shadow, mask, and icon positions stay
unchanged. Texture revision 4 avoids reusing the client's cached release art.
Released September 23, 2026. The user tested and approved the updated appearance
in the running Forever client. All 129 automated tests pass. Square Minimap
remains disabled by default; existing saved preferences are preserved.

## Version 0.8.0 — Square Minimap

Released September 23, 2026. Adds an eighth `/qol` option, disabled by default,
for a square minimap with rounded corners and a bronze frame matching the
native UI. Existing settings are preserved. Disabling restores the round map,
ring opacity, shape provider, and original icon positions.

The frame uses original 512x512 RGBA artwork generated by
`tools/generate_minimap_art.py`. Four area samples per pixel smooth the edges.
The 10.2-unit rim includes dark inner and outer bands, a bronze highlight,
and a subtle exterior shadow. Side and upper bevels are lighter than the
bottom. Rounded corners blend the profiles smoothly. The mask slightly
underlaps the frame to prevent transparent seams when downsampled.
The generated TGA files are included in the release's `Media/` directory;
regeneration needs only Python's standard library.

The frame ignores mouse input. The map's size, position, and rotation preference
are preserved. Native compass ring textures are transparent while enabled.
A secure mask hook handles native rotation updates, and `GetMinimapShape`
reports `SQUARE`. The native mask fallback is specific to Forever.

The day/night icon sits near the top-right corner (8 units inward); the
group-finder eye sits near the bottom-left (11 units inward). Native anchor
updates are tracked for restoration, including layout/scale changes and late
loading. Visibility, scale, click handlers, and tooltip behavior remain native.
Icon anchor changes are deferred until combat ends. When Edit Mode scales a
button using its current square anchor, the saved native offsets are rescaled
without replacing their original anchor; this has a regression test using
Blizzard's native scaling function.

Validation: all 129 automated tests pass, covering reversible styling, native
rotation updates, saved preferences, late loading, icon restoration, and combat
deferral. On September 23, the user approved the frame and final icon positions
in the running Forever client. Other supported transitions remain covered by
the automated suite and the gameplay checklist in CONTRIBUTING.md. Custom
minimap replacements and special hybrid maps are outside this feature's scope.

Source: [Forever minimap skin, build 69913](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_Minimap/Camelot/Skin.lua).

## Published version history

On September 18, 2026, the user confirmed that Enter confirmation worked in the
running game. The detailed README was then moved into this devlog, and a concise
README was added.

A small addon for World of Warcraft: Forever Beta 1.60.1, Interface 16001.
Version 0.9.2, updated September 23, 2026. Technical addon name: BetaQoL.

New in 0.7.0: Backspace Destroy Select Item. Outside combat, press Backspace
while holding a carried bag item on the cursor to open its native deletion
confirmation. Text fields and unrelated keys retain their normal behavior.
Split stacks are excluded until the cursor is cleared: the native GUID-based
confirmation may refer to the original stack rather than its picked-up portion.
The new seventh setting defaults to enabled and preserves existing preferences.

New in 0.6.0: Whisper Tab Doubleclick Close. Left-double-click a regular or
Battle.net whisper tab to close it using Blizzard's context-menu close path.
The new sixth setting defaults to enabled; existing preferences are preserved.

New in 0.5.0: Quest Auto Turn-in as a separate saved setting, with the same
conversation-wide Shift pause as Quest Auto Accept. Range coloring is now named
Spellicon Range Color in the menu and documentation. Existing settings are
preserved; the new turn-in feature defaults to enabled.

New in 0.4.0: Whole-icon range coloring on standard action bars and a compact
`/qol` settings window. Each of the four features can be enabled or disabled
independently, with immediate effect. Settings are saved for the account.

New in 0.3.0: Enter confirmation for all standard Blizzard confirmation dialogs,
including deleting items, selling gray items, accepting group invitations, and
confirming purchases.

New in 0.2.3: Bounded retries for Fast Autoloot and suppression of the standard
autoloot window. Manual interaction remains available when loot is blocked.

New in 0.2.2: Full display name and a Shift pause for the entire NPC conversation.

New in 0.2.1: Renamed Forever Quick Accept to BetaQoL.

New in 0.2.0: Faster native autoloot.

## Installation

1. Extract the ZIP.
2. Copy the included `BetaQoL` folder into `Interface\AddOns` in your
   Forever Beta installation. The current beta folder is usually
   `World of Warcraft\_classic_beta_`.
3. The file must then be located directly at
   `Interface\AddOns\BetaQoL\BetaQoL.toc`.
   Avoid an extra nested folder. If you create the files yourself, make sure
   their actual extensions are `.toc` and `.lua`, without an extra `.txt`.
4. For a first installation, fully restart WoW and enable "Beta Quality of Life"
   in the addon list. To apply this update to an existing BetaQoL installation,
   replace the files in its folder and run `/reload`.

When switching from the previous addon name to BetaQoL, fully quit and restart
WoW once so that the new addon folder is detected reliably. The old
`ForeverQuickAccept` folder must not remain active at the same time.
For future updates to existing Lua files, `/reload` is sufficient.

## Usage

- `/qol` opens a small window with nine checkboxes: Quest Auto Accept, Quest Auto
  Turn-in, Fast Autoloot, Enter Confirm Dialog-Box, Spellicon Range Color,
  Whisper Tab Doubleclick Close, Backspace Destroy Select Item, Square Minimap, and Quest Target Nameplate Icon.
  All ten features start enabled. Changes apply immediately; restored saved choices
  are preserved and shared across characters on the account. The beta client may
  fail to restore SavedVariables, as described above.
- Interact with a quest NPC yourself. The addon selects offered quests and accepts
  normal quest offers as soon as the client sends the `QUEST_DETAIL` event.
  Server response times and network latency still apply.
- When several quests are available, the addon selects one at a time. It processes
  further offers when the client displays the quest list again. If the NPC dialog
  closes after a quest is accepted, interact with the NPC again.
- Hold Shift when interacting with a quest giver, and keep it held until the
  first conversation or quest window opens. Acceptance and turn-in stay paused for
  the entire conversation, even after you release Shift. You can select and
  accept or turn in quests manually during that conversation. After it closes,
  each enabled feature resumes the next time you interact normally.
- `/betaqol` (or the existing alias `/fqa`) toggles automatic quest acceptance
  off or on and updates the same saved setting as its checkbox in `/qol`.
  Before version 0.4.0, this toggle reset to enabled after a reload or restart.

Quest Auto Accept automates acceptance of quests offered by NPCs. Quest Auto
Turn-in separately handles completed NPC quests. Choosing between rewards and
general conversation options remain manual.
Ignored quests are skipped in the modern quest list. PvP quests retain manual
acceptance and confirmation. Item quests, adventure map quests, and special
group confirmation flows receive no additional automation.

### Quest Auto Turn-in

The addon opens one completed quest at a time from the NPC's active quest list,
before selecting new offers. Unfinished quests are skipped, as are ignored
quests in modern gossip. A completable progress page advances to its reward page.
Quests with no reward choice or one reward are then submitted automatically.

When several rewards are offered, choose and confirm the reward yourself.
Quests requiring gold also remain manual so the native payment confirmation
is preserved. Quest popups without a current NPC receive no turn-in automation.
The addon does not repeatedly retry rejected reward requests; reopen the quest
after resolving an issue such as full bags.

This feature has its own checkbox in `/qol` and works with Quest Auto Accept
disabled. Hold Shift when starting the conversation to pause both features for
that conversation. Shift pressed on a later quest page also pauses automation
from that page onward; it cannot undo a request already sent to the server.

### Confirming with Enter

- Enter activates the primary button of the topmost standard Blizzard dialog.
  This also applies to dialogs loaded later and addon dialogs that use the
  standard Blizzard popup system. The added keyboard handlers also support
  Numpad Enter.
- At a vendor, click the button to sell all gray items, then press Enter to
  confirm the dialog. Numpad Enter also works for this dialog.
- The Yes/No dialog for deleting a normal item or a quest item can also be
  confirmed with Enter.
- If WoW requires confirmation text for a valuable item, enter it as usual.
  The game's existing Enter confirmation then works. The addon does not skip
  the text requirement.
- A disabled confirmation button is not activated. Escape and mouse controls
  remain available. The dialog is confirmed only when you provide input;
  opening it does not sell or delete anything.

This feature is independent of the `/betaqol` quest toggle and has its own
checkbox in `/qol`. Disabling it restores the handlers of dialogs already open;
enabling it also applies to dialogs already open. Native Enter handling remains
available where Blizzard already provides it.
Standalone windows outside the Blizzard popup system, such as custom interfaces
from other addons, may need a separate integration. The feature does not bind
Enter outside an open dialog.

### Fast Autoloot

As soon as the client makes loot available for a native autoloot operation, the
addon processes the loot slots directly, speeding up the existing autoloot
behavior. WoW still chooses between automatic and manual looting based on your
setting and the configured autoloot modifier key. No WoW settings are changed.

The first pass starts without an added delay. If needed, further attempts follow
at intervals of approximately 0.1 seconds, for no more than one second in total.
Locked and already emptied loot slots are skipped. If the initial readiness
event is missing or loot data arrives late, the opening sequence or a retry
can take over.

The loot window is hidden during normal autoloot. It becomes available for
manual interaction if your bags are full, an item limit is reached, a binding
confirmation is required, or loot remains after the retry period expires.
Confirmations are not accepted automatically. A window that is already visible
and Edit Mode are not suppressed. Manual looting also remains visible.
The addon cannot eliminate server response times or network latency.

Fast Autoloot is independent of `/betaqol`, `/fqa`, and the quest Shift pause.
Looting uses the native autoloot modifier key, which may also be set to Shift.
Its checkbox in `/qol` switches off the addon's acceleration and window masking
without changing WoW's native Auto Loot setting. Pending addon retries are
cancelled, and an open loot window returns to its normal appearance. If the
native closing animation is already running, its normal cleanup finishes first.

### Spellicon Range Color

When WoW reports that an action is out of range, the entire spell icon becomes
red. Returning to range restores the normal icon appearance, including native
colors for insufficient mana or an otherwise unusable action. The feature uses
the game's own range determination and follows target and action changes.

The checkbox in `/qol` immediately enables or removes the added coloring.
Standard Blizzard action bars are supported. Pet bars and custom replacement
action bars are outside the supported scope.

### Whisper Tab Doubleclick Close

Left-double-click a temporary whisper tab to close it. Regular character
whispers and Battle.net whispers are supported, whether docked or undocked.
This uses the same pop-in action as Close Whisper Window in the context menu,
including restoration of message routing to the main chat and cleanup of the
temporary conversation window.

Single clicks still select the tab, and right clicks still open its menu.
General, combat log, voice transcription, custom permanent tabs, and other
temporary window types keep their native behavior. Disabling the feature in
`/qol` immediately restores normal double-click behavior, including minimizing
undocked windows. The setting persists across reloads and restarts.

### Backspace Destroy Select Item

Pick up an item from the backpack or an equipped bag and press Backspace to
request deletion. Blizzard's normal confirmation dialog opens; the shortcut
does not delete the item directly. Rare items retain their typed confirmation,
and quest items retain their quest-specific dialog. Enter Confirm Dialog-Box
can confirm eligible dialogs when that separate feature is enabled.

Backspace is intercepted only with a real carried bag item on the cursor,
outside combat, and with no text field focused. Empty cursors, spell/macro
cursors, bank items, equipment-slot items, and modified Backspace combinations
keep their ordinary behavior. After putting the item down or disabling the
feature in `/qol`, the keyboard listener is hidden. It also pauses during combat
and resumes afterward. No permanent key bindings or override bindings are set.
Split stacks are excluded until the cursor is cleared; whole stacks are supported.

## Technical Design and Research

Two files are loaded: the `.toc` contains `## Interface: 16001`, declares
`## SavedVariables: BetaQoLDB`, and references the `.lua`. No libraries or other
addons are required.

The saved table contains nine Boolean settings: `autoAccept`, `autoTurnIn`, `fastLoot`,
`enterConfirm`, `rangeColor`, `whisperDoubleClick`, `backspaceDestroy`, `squareMinimap`, and `questNameplateBag`.
Missing or invalid values use `true` for all ten features. Explicit Boolean choices
are preserved. Initialization waits for the addon's own
`ADDON_LOADED` event so it reads the table loaded by WoW. The `/qol` window is
created only when first requested, using native frame and checkbox templates.
Checkboxes apply changes directly, without an Apply button or a required reload.

Quest acceptance responds to three events:

| Event | Action |
| --- | --- |
| `GOSSIP_SHOW` | Read `C_GossipInfo.GetAvailableQuests()` and select exactly one quest with `C_GossipInfo.SelectAvailableQuest(questID)`. |
| `QUEST_GREETING` | Call `SelectAvailableQuest(1)` with a list index through the legacy greeting interface. |
| `QUEST_DETAIL` | Call `AcceptQuest()` for normal offers. Close offers that have already been accepted automatically with `CloseQuest()`. |

With turn-in enabled, `GOSSIP_SHOW` first selects a completed, non-ignored active
quest through `C_GossipInfo.SelectActiveQuest(questID)`. `QUEST_GREETING` uses
`GetActiveTitle(index)` and `SelectActiveQuest(index)` for the legacy equivalent.
Each event selects only one quest and waits for the server's next quest page.
`QUEST_PROGRESS` calls `CompleteQuest()` only when `IsQuestCompletable()` is true.
`QUEST_COMPLETE` calls `GetQuestReward(0)` for no choice or `GetQuestReward(1)` for
a sole reward, provided `GetQuestMoneyToGet()` reports no gold cost. Multiple
reward choices remain manual. Request markers prevent duplicate submissions
on repeated events and reset when the quest closes, the NPC changes, or the
player changes worlds.

The Shift pause is stored for each NPC conversation. `QUEST_PROGRESS` and
`QUEST_COMPLETE` also capture Shift so that follow-up quests after a manual
turn-in remain manual. `GOSSIP_CLOSED` does not clear the pause while the
interaction continues. When a closing event occurs, the addon waits until the
next UI update to check whether the native Gossip/QuestGiver interaction has
actually ended. A new dialog step invalidates an earlier closing check.
A different NPC or a world transition starts a new interaction.

A dedicated frame manages looting from `LOOT_READY(autoLoot)`, with
`LOOT_OPENED` as a fallback. Explicit Boolean event values are used directly.
Only when no Boolean value is provided does the addon evaluate the combination
of `autoLootDefault` and `IsModifiedClick("AUTOLOOTTOGGLE")`, once per operation.
Separate handling prevents the quest Shift pause from overriding the loot mode.
`LootSlot(slot)` processes slots in reverse order, skipping locked slots and
slots of type `None`. After each call, the addon checks whether the operation
has ended synchronously or requires manual confirmation. Timers tied to a
previous operation cannot process a new corpse.

Blizzard's native `LootFrame` event handler remains unchanged. Post-hooks hide
the autoloot window using alpha and temporarily disable mouse interaction on
its child frames. The opening animation is paused; the native closing animation
continues at alpha 0, including its normal window cleanup. When the window closes
or falls back to manual interaction, the animation values and original mouse
states are restored. Calling `Hide()` directly while looting would be unsuitable
here: the native `OnHide` handler calls `CloseLoot()`. BetaQoL therefore calls
neither `Hide()` nor `CloseLoot()` and changes no WoW settings. Accelerated loot
requests outside `LOOT_READY` are deferred until the native opening sequence
finishes, to avoid interrupting it with synchronous closing events.

`AcceptQuest()` is a global function in Forever as well. `QUEST_ACCEPTED` would
be the wrong trigger for acceptance: it reports that a quest has already been
accepted. `QUEST_ACCEPT_CONFIRM` is a separate confirmation flow using
`ConfirmAcceptQuest()`; it is not part of normal quest acceptance from an NPC.

The user confirmed the following client details: version 1.60.1, build 69913,
Interface 16001, `AcceptQuest = function`, `C_GossipInfo = table`,
`WOW_PROJECT_ID = 1`. The project ID alone therefore does not distinguish this
client from Retail.

The Enter feature uses the native `PopupOpened` and `PopupClosed` events.
Standard dialog instances temporarily receive a keyboard handler. It checks
the visibility, first button, and frame level of open popups, then calls
`StaticPopup_OnClick`. A disabled primary button does not cause another button
to be selected. The native `ignoreKeys` flag is respected. Input fields retain
their existing Enter handling; if none exists, an additional handler that
accounts for autocomplete is provided. The same applies to money input fields.
A focused input field prevents additional confirmation through the parent frame.
On closing, previous handlers are restored unless they have since been replaced.
Global dialog definitions and key bindings remain unchanged.

Range coloring uses secure post-hooks on native action buttons and
`ActionButton_UpdateRangeIndicator`. It follows the native range events rather
than adding an `OnUpdate` loop or a polling timer. Native usability updates
refresh the stored base icon color before the out-of-range tint is applied.
Action changes and buttons registered later are also handled. Disabling the
feature restores the stored native colors. No secure action attributes or
native range-check registrations are changed.

Whisper closing wraps each native chat tab's `OnDoubleClick` handler. A left
double-click on an active temporary `WHISPER` or `BN_WHISPER` window invokes
`FCF_PopInWindow`, exactly as the native context menu does. Other double-clicks
are passed to the prior handler. `OnClick` remains unchanged. Existing tabs
are discovered through `CHAT_FRAMES`, and a secure post-hook on
`FCF_OpenTemporaryWindow` discovers later tabs. Reused tabs are hooked only
once, with eligibility checked against their current window type on every click.
The client detects double-clicks; no custom timing loop is added.

The Backspace feature follows `CURSOR_CHANGED` and combat transitions. It checks
`C_Cursor.GetCursorItem()` for a carried bag location, resolves its item GUID
through `C_Item.GetItemGUID()`, and rechecks it on the actual key press.
`C_Item.ConfirmDeleteItem(guid)` requests Blizzard's confirmation event, which
selects the appropriate native popup. A small keyboard frame propagates every
unhandled key. Focused edit boxes and Shift/Ctrl/Alt combinations are excluded.
The listener hides during combat so it never changes protected keyboard
propagation then. Repeated key-down events request only one prompt per press.
A secure post-hook on `C_Container.SplitContainerItem` excludes split stacks
until the cursor is empty because GUID-based deletion may target the original stack.

Primary sources, accessed September 18–22, 2026:

- [Extracted Blizzard UI code for Forever 1.60.1, build 69913](https://github.com/Gethe/wow-ui-source/commit/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e)
- [Forever QuestFrame.lua: events, acceptance, and special cases](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_UIPanels_Game/Mainline/QuestFrame.lua)
- [Forever GossipFrameShared.lua: selection by quest ID](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_UIPanels_Game/Shared/GossipFrameShared.lua)
- [Forever LootDocumentation.lua: LOOT_READY with the autoloot decision](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_APIDocumentationGenerated/LootDocumentation.lua)
- [Forever LootFrame.lua: window setup and CloseLoot when hidden](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_UIPanels_Game/Mainline/LootFrame.lua)
- [Forever ScrollingFlatPanel.xml: opening and closing animations](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_UIPanels_Game/Mainline/ScrollingFlatPanel.xml)
- [Forever PlayerInteractionManager: native interaction states](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_APIDocumentationGenerated/PlayerInteractionManagerDocumentation.lua)
- [Forever StaticPopup.lua: popup events and native confirmation](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_StaticPopup/StaticPopup.lua)
- [Forever MerchantFrame.lua: confirmation for selling gray items](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_UIPanels_Game/Mainline/MerchantFrame.lua)
- [Forever QuestFrame.lua: progress, reward indices, and gold confirmation](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_UIPanels_Game/Mainline/QuestFrame.lua)
- [Forever FloatingChatFrame.lua: whisper context menu and native close lifecycle](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_ChatFrameBase/Mainline/FloatingChatFrame.lua)
- [Forever FloatingChatFrame.xml: native chat tab click handlers](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_ChatFrameBase/Mainline/FloatingChatFrame.xml)
- [Forever item API: ConfirmDeleteItem and GetItemGUID](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_APIDocumentationGenerated/ItemDocumentation.lua)
- [Forever cursor API: current item location and cursor events](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_APIDocumentationGenerated/CursorDocumentation.lua)
- [Forever deletion event routing: native confirmation selection](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_Game/Camelot/EventImplementation.lua)
- [Forever ActionButton.lua: native range events and usability colors](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_ActionBar/Shared/ActionButton.lua)
- [Forever ActionBarFrameDocumentation.lua: action range API](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_APIDocumentationGenerated/ActionBarFrameDocumentation.lua)
- [Forever settings implementation guide: saved settings initialization](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_Settings_Shared/Blizzard_ImplementationReadme.lua)
- [Leatrix Plus: release specifically for Forever 1.60.1](https://www.curseforge.com/wow/addons/leatrix-plus/files/8907317)
- [Another addon author: Interface 16001 in ClassicUIForever](https://github.com/wowaddonmaker/classicuiforever/blob/edec276db52f78d214c1d8ef5c22cdc44b7d8246/ClassicUIForever.toc)

## Validation and Initial In-Game Testing

The Lua file was tested under Lua 5.1 with a simulated WoW interface, covering
normal offers, modern and legacy quest lists, multiple offers, the Shift pause,
toggling, already accepted quests, and special cases. Conversation pause tests
also covered releasing Shift, switching pages, follow-up quests, actual
conversation endings, NPC changes, and world transitions. Further tests cover
autoloot versus manual looting, multiple loot slots, independence from the
quest pause, empty and blocked loot, and repeated events. The additional
window tests execute the actual event handler from the extracted Forever UI
code; the game engine, timing, and rendering are simulated. Coverage includes
stable slot indices, delayed data, locked slots, fallback to manual interaction,
confirmations, and stale timers after switching operations. These tests do not
replace testing of the renderer or the protected execution context in the game.
No test in a running Forever client was performed as part of this development
validation; the user's subsequent confirmation of Enter working in-game is
recorded at the start of this devlog.

The Enter feature was also tested under Lua 5.1 using the actual native popup
opening, closing, and confirmation code. Coverage includes normal items and
quest items, selling gray items, general confirmations, disabled or hidden
buttons, multiple or raised windows, Escape, screenshots, text entry,
autocomplete, money fields, and restoration of the original keyboard handlers.
The existing quest and loot tests also continue to pass. These tests simulate
the game engine; actual keyboard handling and protected actions require
testing in the running game.

Version 0.4.0 adds simulated-client checks for saved settings and range coloring,
using selected native action-button code. These checks cannot validate the
client's actual SavedVariables file loading, rendered colors, or protected
execution during combat. The new settings window and range coloring still
require verification in the running Forever client.

Version 0.5.0 adds quest-journal simulations for modern and legacy turn-in,
incomplete quests, independent settings, reward counts, required gold,
conversation-wide Shift pause, duplicate events, and synchronous quest closure.
The native API contracts were checked against the pinned client source; actual
server acceptance and the expanded settings window still need an in-game check.

Version 0.6.0 adds integration checks using the actual native pop-in, close,
message-routing restoration, tab click handler, and XML double-click script.
The tests cover existing/new/reused tabs, character and Battle.net whispers,
docked and undocked windows, other chat types, preserved click handlers, late
chat UI loading, and the saved feature toggle. Actual mouse input and rendering
still require verification in the running client.

Version 0.7.0 adds simulated keyboard routing tests and executes the native
item-location and deletion-event code alongside the existing native popups.
Checks cover empty/non-item cursors, carried bags versus bank/equipment slots,
focused text fields, modifiers, other keys, repeated key-down events, settings,
combat transitions, and normal/rare/quest-item confirmations. The tests cannot
validate real hardware-event restrictions or the client's cursor behavior;
these still require an in-game check.

For an in-game test, interact with an NPC offering a normal available quest.
The quest should appear in your quest log. Next, hold Shift while interacting
with a quest giver, release Shift after the window opens, and select a quest:
it should remain available for manual interaction. Close the conversation and
interact with the same quest giver again without Shift: autoaccept should work
again.

Test Fast Autoloot with native autoloot enabled on a corpse containing multiple
items: loot should be collected without displaying the loot window.
Also try looting two corpses in immediate succession and looting during combat.
Then hold the native autoloot modifier key while looting: with autoloot enabled
by default, the loot should remain available for manual selection and the
window should be visible. Manual interaction must remain accessible when your
bags are full or a binding confirmation is required.

If you encounter a problem, report the exact error message and the type of quest
window. To test Enter, run `/reload`, open a confirmation dialog, and press Enter.
Cancel another dialog with Escape. For a dialog that requires confirmation text,
first try without entering any text: nothing should be activated. Then enter the
required text and confirm with Enter.

For the settings window, run `/qol` and disable each feature independently.
Check that the corresponding behavior stops immediately, then enable it again.
Repeat with a confirmation dialog or loot window already open. Leave one
feature disabled, run `/reload`, and check that its checkbox and behavior remain
disabled. Repeat after restarting WoW and on another character on the account.

For turn-in, test a completed NPC quest with no reward choice, a sole reward,
and several reward choices. The last case must wait for manual selection and
confirmation. Test with Auto Accept disabled, then with Auto Turn-in disabled.
Hold Shift at the start of a conversation and release it before advancing:
both acceptance and turn-in must remain manual until the conversation ends.

For range coloring, target an enemy and move a spell into and out of range.
Check the whole icon, then repeat while lacking mana or another resource.
Change targets, switch action pages, and replace an action in the same slot.
Finally, disable the feature while an icon is red: its normal color should
return immediately. Include combat in the in-game check.

For whisper tabs, open a character or Battle.net whisper and left-double-click
its tab. Repeat with an undocked tab and a conversation opened after closing
another one. Check that one left click selects it, right click opens the menu,
and General/combat log tabs are unaffected. Disable the feature in `/qol` and
check that a double-click no longer closes whisper tabs.

For Backspace, pick up a disposable bag item and verify that one key press opens
the usual confirmation without deleting immediately. Cancel first, then test
the normal confirmation. Check a rare item's text requirement, typing in chat
while holding an item, empty/non-item cursors, setting changes, and entering and
leaving combat. Whole stacks should open confirmation; split stacks must leave
Backspace unchanged until the cursor is cleared.
If needed, temporarily enable Lua error messages:

```text
/console scriptErrors 1
```

Disable them again later:

```text
/console scriptErrors 0
```

Check the version after a beta update:

```text
/run print("Build:",GetBuildInfo())
```

To disable the addon, turn it off in the addon list and run `/reload`.
