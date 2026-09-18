# Forever Beta Quality of Life

**Settings menu:** Type `/qol` in chat to enable or disable features.

## Features

- **Quest Auto Accept (hold Shift to disable):** Automatically accepts ordinary NPC quest offers.
- **Fast Autoloot:** Speeds up native auto-looting and hides the loot window.
  Manual looting remains available when an item cannot be collected automatically.
- **Enter Confirm Dialog-Box:** Confirms the main button of standard WoW dialogs
  with Enter, including selling junk, deleting items, purchases and party invitations.
  Required confirmation text must still be entered; Escape cancels.
- **Actionbar Range Coloring:** Colors the whole spell icon red when it is out of
  range, then restores the normal icon color when it is back in range.

**Version 0.4.0** · WoW Forever Beta 1.60.1 · Interface 16001 · No dependencies.

## Installation and updates

1. Download **BetaQoL-0.4.0.zip** from [Releases](https://github.com/Kirchlive/forever-beta-quality-of-life/releases/latest).
2. Extract the `BetaQoL` folder into
   `World of Warcraft\_classic_beta_\Interface\AddOns\`.
   `BetaQoL.toc` must be directly inside `AddOns\BetaQoL`.
3. For a first installation, restart WoW and enable **Beta Quality of Life**.
   For updates, replace the files and run `/reload`.

## Usage

- `/qol`: Open a small settings window with one checkbox per feature. All four
  features start enabled. Changes apply immediately and are saved across reloads
  and restarts for all characters on the account.
- `/betaqol` or `/fqa`: Toggle Quest Auto Accept and save the choice.
- Hold Shift when opening a quest conversation to keep that entire conversation manual.
- Enable Auto Loot in WoW for Fast Autoloot. The native auto-loot modifier still works.
- Quest turn-ins and reward selection remain manual. Enter supports standard
  Blizzard popups; custom windows may need separate integration.
- Range coloring follows WoW's range checks on its standard action bars.
  Custom replacement bars and pet bars are not covered.

Development notes, version history and technical details: [DEVLOG.md](DEVLOG.md).
