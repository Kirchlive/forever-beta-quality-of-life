# Forever Beta Quality of Life

**Version 0.8.1** · WoW Forever Beta 1.60.1 · Interface 16001 · No dependencies.

## Features

- **Quest Auto Accept (hold Shift to disable):** Automatically accepts ordinary NPC quest offers.
- **Quest Auto Turn-in (hold Shift to disable):** Automatically turns in completed NPC quests.
  Multiple reward choices and quests requiring gold remain manual.
- **Fast Autoloot:** Speeds up native auto-looting and hides the loot window.
  Manual looting remains available when an item cannot be collected automatically.
- **Enter Confirm Dialog-Box:** Confirms the main button of standard WoW dialogs
  with Enter, including selling junk, deleting items, purchases and party invitations.
  Required confirmation text must still be entered; Escape cancels.
- **Spellicon Range Color:** Colors the whole spell icon red when it is out of
  range, then restores the normal icon color when it is back in range.
- **Whisper Tab Doubleclick Close:** Close a regular or Battle.net whisper tab
  with a left double-click, using the same close action as its context menu.
- **Backspace Destroy Select Item:** Press Backspace with an item picked up from
  your bags to open its normal delete confirmation. Works outside combat;
  Backspace keeps its usual behavior in text fields and without a picked-up item.
  Split stacks are excluded; whole items and whole stacks are supported.
- **Square Minimap:** Displays the standard minimap as a square with rounded corners and a
  bronze-toned WoW-style border. The day/night icon sits at the top-right corner
  and the group-finder eye at the bottom-left. Disable to restore the round map
  and native icon positions. Map position, size, and button actions are preserved.
  Disabled by default; enable it in `/qol`.

**Settings menu:** Type `/qol` in chat to enable or disable features.

## Installation and updates

1. Download **BetaQoL-0.8.1.zip** from [Releases](https://github.com/Kirchlive/forever-beta-quality-of-life/releases/latest).
2. Extract the `BetaQoL` folder into
   `World of Warcraft\_classic_beta_\Interface\AddOns\`.
   `BetaQoL.toc` must be directly inside `AddOns\BetaQoL`. Keep the included `Media` folder.
3. For a first installation, restart WoW and enable **Beta Quality of Life**.
   For updates, replace the files and run `/reload`.

## Usage

- `/qol`: Open a small settings window with one checkbox per feature. Square Minimap
  starts disabled; the other seven features start enabled. Changes apply immediately and are saved across reloads
  and restarts for all characters on the account.
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

Development notes, version history and technical details: [DEVLOG.md](DEVLOG.md).
