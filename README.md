# Forever Beta Quality of Life

**Version 0.9.8** · WoW Forever Beta 1.60.1 · Interface 16001 · No dependencies.

## Features

- **Quest Auto Accept (shift disable):** Automatically accepts ordinary NPC quest offers.

- **Quest Auto Turn-in (shift disable):** Automatically turns in completed NPC quests.
  Multiple reward choices and quests requiring gold remain manual.

- **Quest Item Drop Rate:** Adds a percentage in the quest title's yellow directly after each matching quest item
  in the standard mob tooltip, for example `0/5 Plainstrider Kidney (40%)`.
  Only your own item quests still in the quest log are included.
  At full progress (such as 5/5), the percentage inherits the item row's gray.
  Remains visible until turn-in or abandonment.
  Display rounds to whole percentages. At or above 19%, it uses a 5% step only
  when the raw rate is within 1 percentage point of that step (69.4% → 70%,
  20.5% → 20%, but 27.8% → 28%). Positive values rounding to zero display `<1%`.
  Thus 19–21% → 20%, 24–26% → 25%, 29–31% → 30%, and so on.
  Below 19% and between these bands, standard whole-percent rounding applies.
  Original data is retained.
  Uses a local database with Questie Forever v27 Classic estimates and 337 additional
  NPC/item pairs from Wowhead Forever observations, covering 176 items and 283 NPCs.
  All 2,133 pages in the September 25 quest-item catalog were parsed successfully.
  The combined lookup contains 17,015 pairs across 4,400 NPCs and 1,407 items.
  This includes new Forever items and new sources for existing quest items, such as
  Razormane Raider / Bristleback Quilboar Tusk (70%). No extra addon is required.
  **Classic values are transferred estimates; Forever values are observed loot frequencies,
  not guaranteed server drop probabilities.** Samples may be small or include players
  without the relevant quest. They are not a per-kill guarantee or automatically updated.
  Unknown drops and ambiguous item names are omitted. A complete catalog fetch
  does not provide usable rates for every quest item;
  new quests can use known pairs, while new unknown NPC/item pairs need a data update.
  Quest progress and nameplate markers already use the current client's quest data.
  Group members' objectives do not trigger the display. Enabled by default.
  [Data sources, license and reproduction](Data/NOTICE.md).

- **Quest Target Nameplate Icon:** Shows a small bag to the left of a mob's standard nameplate
  while it contributes to one of your unfinished quest objectives (items, kills, or
  interactions). Hides when that mob's relevant goals are complete. Enabled by default; toggle it in `/qol`.

- **Questlog Quest XP (+ for item rewards):** Shows the XP reward between quest level and title in
  the quest log overview, for example `[16] (4,400) Returning the Lost Satchel`.
  Adds `+` when guaranteed or selectable item rewards are available, such as
  `(4,400+)`. Uses the current client reward value and number formatting. Missing or hidden
  rewards are omitted; disabling restores the standard titles.

- **Fast Autoloot:** Speeds up native auto-looting and hides the loot window.
  Manual looting remains available when an item cannot be collected automatically.

- **Square Minimap (forever look):** Displays the standard minimap as a square with rounded corners and a
  bronze-toned WoW-style border. The day/night icon sits at the top-right corner
  and the group-finder eye at the bottom-left. Disable to restore the round map
  and native icon positions. Map position, size, and button actions are preserved.
  Enabled by default; toggle it in `/qol`.

- **Spellicon Range Color:** Colors the whole spell icon red when it is out of
  range, then restores the normal icon color when it is back in range.

- **Backspace Leave Quest Details:** Press Backspace in the quest log details to
  activate the native Back button and return to the overview. Enabled by default
  with its own `/qol` switch. Works outside
  combat; typing, modified keys and picked-up items keep their normal behavior.

- **Backspace Destroy Select Item:** Press Backspace with an item picked up from
  your bags to open its normal delete confirmation. Works outside combat;
  Backspace keeps its usual behavior in text fields and without a picked-up item.
  Split stacks are excluded; whole items and whole stacks are supported.

- **Enter Confirm Dialog Box:** Confirms the main button of standard WoW dialogs
  with Enter, including selling junk, deleting items, purchases and party invitations.
  Required confirmation text must still be entered; Escape cancels.

- **Arrow Keys Chat Control:** Use Left/Right to move the cursor and Up/Down for
  input history without holding Alt while a standard chat input has focus. Also
  works in new whisper windows. Remembers up to 32 entries per chat input during
  the current session, starting when the addon loads. Protected commands such as
  `/cast` remain in the native Alt+Up/Down history. Disable to restore the previous
  arrow-key mode.

- **Left Shift Escape Reload:** Hold the left Shift key and press Escape to reload
  the UI. Enabled by default with its own switch after Arrow Keys Chat Control.
  Observes keyboard input directly without changing bindings. Right Shift alone,
  Ctrl/Alt combinations and ordinary Escape do not trigger a reload. The initial
  keyboard listener setup waits until combat ends if necessary.

- **Flight Master Auto Map (shift disable):** Opens the flight map automatically when the NPC offers
  the standard flight-master dialog. Enabled by default, independently switchable under
  `/qol`. Hold Shift when speaking to the NPC to keep the entire conversation manual,
  even after releasing Shift. Quest acceptance
  and turn-in retain priority when enabled. Choose your destination on the map as usual.

- **Whisper Tab Doubleclick Close:** Close a regular or Battle.net whisper tab
  with a left double-click, using the same close action as its context menu.

**Settings menu:** Type `/qol` in chat to enable or disable features.

## Installation and updates

1. Download the latest **BetaQoL ZIP** from [Releases](https://github.com/Kirchlive/forever-beta-quality-of-life/releases/latest).
2. Extract the `BetaQoL` folder into
   `World of Warcraft\_classic_beta_\Interface\AddOns\`.
   `BetaQoL.toc` must be directly inside `AddOns\BetaQoL`. Keep the included `Media` and `Data` folders.
3. For a first installation, restart WoW and enable **Beta Quality of Life**.
   For updates, replace the files and run `/reload`.

**Updating from 0.9.7:** Damage Meter Doubleclick Switch has been removed after
reproducible Lua errors. Its menu entry and obsolete saved setting are removed;
use Blizzard's normal Current/Overall menu. Reload after updating to clear any
previously affected runtime state. If you enabled diagnostic logging during testing,
run `/console taintLog 0` before reloading. The other fifteen features remain available.

## Usage

- `/qol`: Open a small settings window with one checkbox per feature. Available features
  start enabled. Changes apply immediately; existing saved on/off choices are preserved
  when the client restores SavedVariables. Settings are shared across characters on the account.
- `/betaqol` or `/fqa`: Toggle Quest Auto Accept and save the choice.
- Hold Shift when opening a quest conversation to pause both acceptance and turn-in
  for that entire conversation, even after releasing Shift.
- Enable Auto Loot in WoW for Fast Autoloot. The native auto-loot modifier still works.
- Quest Auto Turn-in has its own switch and works with Auto Accept disabled.
  It collects a sole reward automatically; choosing between rewards stays manual.
- Enter supports standard Blizzard popups; custom windows may need separate integration.
- Range coloring follows WoW's range checks on its standard action bars.
  Custom replacement bars and pet bars are not covered.
- Double-click the whisper tab itself with the left mouse button to close it.
  Single-click selection, right-click menus, and other chat tabs work as usual.
- Pick up an item from your backpack or carried bags, then press Backspace.
  Confirm the native dialog to destroy it, or cancel to keep it. Required
  confirmation text is preserved. No permanent key binding is changed.
- Square Minimap supports Blizzard's standard minimap. Icon repositioning during
  combat applies after combat ends. Custom minimap replacements are not covered.

- Quest markers use the quest objectives supplied by the client for each NPC.
  Objectives absent from the native tooltip cannot be inferred. Group members'
  objectives do not keep your completed marker visible. Custom nameplates are not covered.

The Forever beta has a reported SavedVariables loading bug: preferences may reset
to defaults even when correctly saved. See [ForeverSVFix](https://github.com/nobewayo/ForeverSVFix)
for the community report and workaround. This addon does not include that workaround.

Development notes, version history and technical details: [DEVLOG.md](DEVLOG.md).

## Next milestone: 1.0.0

- Final UI design polish and layout review.
- An addon minimap icon for opening the settings.
- Final live-client checks and release documentation.

The damage-meter shortcut remains excluded. Its feasibility may be revisited
later; it is not a requirement for 1.0.0 and will not return without live validation.
