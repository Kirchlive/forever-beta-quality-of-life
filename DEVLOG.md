# Forever Beta Quality of Life – Devlog

Detailed development notes, research, and validation.
The concise feature overview and installation instructions are in the [README](README.md).

On September 18, 2026, the user confirmed that Enter confirmation worked in the
running game. The detailed README was then moved into this devlog, and a concise
README was added.

A small addon for World of Warcraft: Forever Beta 1.60.1, Interface 16001.
Version 0.3.0, updated September 18, 2026. Technical addon name: BetaQoL.

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

## Usage

- Interact with a quest NPC yourself. The addon selects offered quests and accepts
  normal quest offers as soon as the client sends the `QUEST_DETAIL` event.
  Server response times and network latency still apply.
- When several quests are available, the addon selects one at a time. It processes
  further offers when the client displays the quest list again. If the NPC dialog
  closes after a quest is accepted, interact with the NPC again.
- Hold Shift when interacting with a quest giver, and keep it held until the
  first conversation or quest window opens. Autoaccept then stays disabled for
  the entire conversation, even after you release Shift. You can select and
  accept quests manually during that conversation. After it closes, autoaccept
  is active again the next time you interact normally, unless you have disabled
  it with `/betaqol`.
- `/betaqol` (or the existing alias `/fqa`) toggles automatic quest acceptance
  off or on. It is enabled again after `/reload` or a restart. The addon does not
  save settings.

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

This feature is independent of the `/betaqol` quest toggle and remains active
whenever BetaQoL is loaded. Running `/reload` is enough to load this update.
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

When switching from the previous addon name to BetaQoL, fully quit and restart
WoW once so that the new addon folder is detected reliably. The old
`ForeverQuickAccept` folder must not remain active at the same time.
For future updates to existing Lua files, `/reload` is sufficient.

The quest feature automates acceptance of quests offered by NPCs. You handle
quest turn-ins, reward selection, and general conversation options yourself.
Ignored quests are skipped in the modern quest list. PvP quests retain manual
acceptance and confirmation. Item quests, adventure map quests, and special
group confirmation flows receive no additional automation.

## Technical Design and Research

Two files are loaded: the `.toc` contains `## Interface: 16001` and references
the `.lua`. No libraries or other addons are required.

Quest acceptance responds to three events:

| Event | Action |
| --- | --- |
| `GOSSIP_SHOW` | Read `C_GossipInfo.GetAvailableQuests()` and select exactly one quest with `C_GossipInfo.SelectAvailableQuest(questID)`. |
| `QUEST_GREETING` | Call `SelectAvailableQuest(1)` with a list index through the legacy greeting interface. |
| `QUEST_DETAIL` | Call `AcceptQuest()` for normal offers. Close offers that have already been accepted automatically with `CloseQuest()`. |

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

Primary sources, accessed September 18, 2026:

- [Extracted Blizzard UI code for Forever 1.60.1, build 69913](https://github.com/Gethe/wow-ui-source/commit/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e)
- [Forever QuestFrame.lua: events, acceptance, and special cases](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_UIPanels_Game/Mainline/QuestFrame.lua)
- [Forever GossipFrameShared.lua: selection by quest ID](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_UIPanels_Game/Shared/GossipFrameShared.lua)
- [Forever LootDocumentation.lua: LOOT_READY with the autoloot decision](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_APIDocumentationGenerated/LootDocumentation.lua)
- [Forever LootFrame.lua: window setup and CloseLoot when hidden](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_UIPanels_Game/Mainline/LootFrame.lua)
- [Forever ScrollingFlatPanel.xml: opening and closing animations](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_UIPanels_Game/Mainline/ScrollingFlatPanel.xml)
- [Forever PlayerInteractionManager: native interaction states](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_APIDocumentationGenerated/PlayerInteractionManagerDocumentation.lua)
- [Forever StaticPopup.lua: popup events and native confirmation](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_StaticPopup/StaticPopup.lua)
- [Forever MerchantFrame.lua: confirmation for selling gray items](https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_UIPanels_Game/Mainline/MerchantFrame.lua)
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
