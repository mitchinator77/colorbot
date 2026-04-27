# ColorBot v1

Ultra-light Python desktop color monitor + action runner.

This v1 watches specific screen regions for specific RGB colors, then runs simple scripted desktop actions such as clicks, waits, key presses, hotkeys, and typing.

Designed for normal desktop automation. Do not use it to violate app/game/site terms, spam services, bypass protections, or automate anything you are not allowed to automate.

## Features

- Multiple rules from `config/rules.json`
- Region scanning using `mss`
- RGB target matching with tolerance and minimum pixel count
- Cooldowns to prevent rapid re-triggering
- Dry-run mode for safe testing
- Emergency stop hotkey
- JSONL logging
- Pixel inspector tool
- Region helper tool
- Action recorder tool

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On Windows, run PowerShell or CMD from this folder.

## Run

Dry-run first:

```bash
python -m colorbot.main --dry-run
```

Live mode:

```bash
python -m colorbot.main
```

Use a custom config:

```bash
python -m colorbot.main --config config/rules.json
```

## Emergency Stop

Default hotkey: `ctrl+shift+q`

Also, PyAutoGUI failsafe is enabled: slam your mouse into the top-left corner of the screen to stop.

## Helper Tools

Pick a pixel color:

```bash
python tools/pick_pixel.py
```

Capture a region using two mouse positions:

```bash
python tools/pick_region.py
```

Record a simple click/wait/key script:

```bash
python tools/record_actions.py
```

## Rule Format

```json
{
  "name": "example_green_button",
  "enabled": true,
  "region": {"left": 900, "top": 500, "width": 120, "height": 60},
  "target_rgb": [40, 220, 90],
  "tolerance": 25,
  "min_pixels": 20,
  "cooldown_seconds": 2.0,
  "require_stable_scans": 2,
  "actions": [
    {"type": "click", "x": 940, "y": 520},
    {"type": "wait", "seconds": 0.25},
    {"type": "click", "x": 1100, "y": 650}
  ]
}
```

## Supported Actions

- `click`
- `double_click`
- `right_click`
- `move`
- `wait`
- `press`
- `hotkey`
- `type`
- `scroll`

## Notes

Start with small regions, not full-screen scanning. Small regions are faster and reduce false triggers.

Use `dry-run` until detection looks reliable.
