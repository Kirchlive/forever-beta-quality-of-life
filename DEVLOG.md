# Forever Beta Quality of Life – Devlog

Detailed development notes, research, and validation.
The concise feature overview and installation instructions are in the [README](README.md).

On September 18, 2026, the user confirmed that Enter confirmation worked in the
running game. The detailed README was then moved into this devlog, and a concise
README was added.

A small addon for World of Warcraft: Forever Beta 1.60.1, Interface 16001.
Version 0.7.0, updated September 22, 2026. Technical addon name: BetaQoL.

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

- `/qol` opens a small window with seven checkboxes: Quest Auto Accept, Quest Auto
  Turn-in, Fast Autoloot, Enter Confirm Dialog-Box, Spellicon Range Color,
  Whisper Tab Doubleclick Close, and Backspace Destroy Select Item. All seven are
  enabled by default. Changes apply immediately and are saved across reloads
  and restarts for all characters on the account.
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

The saved table contains seven Boolean settings: `autoAccept`, `autoTurnIn`, `fastLoot`,
`enterConfirm`, `rangeColor`, `whisperDoubleClick`, and `backspaceDestroy`.
Missing or invalid values default to `true`;
an explicit `false` is preserved. Initialization waits for the addon's own
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
