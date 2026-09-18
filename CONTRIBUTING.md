# Contributing

Run these commands from the repository root with Python 3.9 or newer. A virtual
environment is recommended.

```sh
python -m pip install -r requirements-dev.txt
python tools/fetch_test_ui.py
python -m unittest discover -s tests -v
python tools/build_release.py
```

The tests use `lupa.lua51` to run the addon with simulated client APIs. Loot,
popup, and action bar tests also execute selected native UI code, including
`ActionButton.lua`. The fetcher downloads only the seven required files from
[Gethe/wow-ui-source at the pinned commit](https://github.com/Gethe/wow-ui-source/tree/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e)
into `.test-ui/`. These external files are ignored by Git and excluded from
release archives. Fetching them requires internet access.

This suite does not run the game client, renderer, or server. Check gameplay
changes in the supported client as well. For settings changes, verify each
checkbox takes effect immediately and remains selected after `/reload` and a
restart. For range coloring, check entering and leaving range, changing targets
and action pages, insufficient resources, and switching the feature off.
For quest turn-in, check the independent toggle, Shift across conversation
pages, incomplete quests, zero/one/multiple reward choices, and quests with a
gold cost. Reward choices and native payment confirmation must remain manual.

The build command reads the version from `BetaQoL.toc` and creates
`dist/BetaQoL-<version>.zip`. It contains only `BetaQoL.lua`, `BetaQoL.toc`,
`README.md`, and `DEVLOG.md` inside a `BetaQoL/` folder.
