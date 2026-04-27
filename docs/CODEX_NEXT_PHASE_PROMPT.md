# Codex Prompt: ColorBot v2 Interactive Setup + GUI

You are working in an existing Python project named `colorbot_v1`.

The current project is a lightweight desktop automation utility. It watches configured screen regions for target RGB colors and then executes simple user-defined desktop action scripts. It is intended for legitimate desktop automation only. Do not add stealth, evasion, anti-detection, game-cheat, web-spam, credential-harvesting, CAPTCHA-bypass, or ToS-violating behavior.

## Current Project Structure

```text
colorbot_v1/
  colorbot/
    __init__.py
    main.py
  config/
    rules.json
  tools/
    pick_pixel.py
    pick_region.py
    record_actions.py
    test_config_once.bat
  docs/
    CODEX_NEXT_PHASE_PROMPT.md
  logs/
  README.md
  requirements.txt
  run_dry.bat
  run_live.bat
```

## Current v1 Behavior

- `colorbot/main.py` loads `config/rules.json`
- Uses `mss` to capture small screen regions
- Uses `numpy` to detect matching RGB pixels within tolerance
- Supports cooldowns and stable-scan requirements
- Executes actions with `pyautogui`
- Supports dry-run mode
- Supports logging to JSONL
- Includes helper scripts for pixel/region/action recording

## Goal for v2

Turn this from a manual JSON config tool into a small interactive desktop app that lets the user create and test rules without hand-editing JSON.

The app should still stay lightweight and local-first.

## Required Features

### 1. Rule Manager GUI

Create a simple GUI app, preferably using `tkinter` to avoid heavy dependencies.

The GUI should allow the user to:

- View existing rules from `config/rules.json`
- Add a new rule
- Edit a rule
- Duplicate a rule
- Enable/disable a rule
- Delete a rule
- Save rules back to JSON
- Start bot in dry-run mode
- Start bot in live mode
- Stop bot safely
- View recent log events

Suggested file:

```text
colorbot/gui.py
```

Add a launcher:

```text
run_gui.bat
```

### 2. Interactive Region Picker

Add an interactive region picker that lets the user draw a rectangle on the screen.

Implementation options:

- Full-screen transparent/semi-transparent tkinter overlay
- Click-drag-release to define rectangle
- Return region as `{left, top, width, height}`

The region picker should integrate with the GUI rule editor.

Suggested file:

```text
colorbot/region_picker.py
```

### 3. Interactive Color Picker

Add a color picker that lets the user sample the pixel under their mouse, preferably with:

- A countdown mode
- A live preview mode if easy
- Output RGB value
- Optional small color swatch in GUI

Suggested file:

```text
colorbot/color_picker.py
```

### 4. Action Script Builder

Add a GUI action editor for sequences like:

```json
[
  {"type": "click", "x": 940, "y": 520},
  {"type": "wait", "seconds": 0.25},
  {"type": "press", "key": "enter"}
]
```

It should support:

- Add click at current mouse position
- Add double click at current mouse position
- Add right click at current mouse position
- Add wait
- Add key press
- Add hotkey
- Add type text
- Add scroll
- Reorder actions
- Delete action
- Test selected action
- Test full action sequence in dry-run or live test mode

Suggested file:

```text
colorbot/action_editor.py
```

### 5. Visual Debug Overlay

Add an optional overlay that shows watched regions as boxes while the bot is running.

Minimum version:

- A transparent always-on-top tkinter window with rectangles around watched regions
- Rule names shown near rectangles
- Different border style for enabled/disabled if possible

Suggested file:

```text
colorbot/overlay.py
```

### 6. Safer Runtime Controller

Refactor `main.py` so the bot loop can be started/stopped from GUI without spawning messy duplicate processes.

Suggested approach:

- Move scanning/action logic into a class:

```python
class ColorBotRuntime:
    def __init__(self, config_path: Path, dry_run: bool = False): ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def run_forever(self) -> None: ...
    def scan_once(self) -> list[DetectionEvent]: ...
```

- Use a thread for GUI runtime
- Keep CLI compatibility working:

```bash
python -m colorbot.main --dry-run
python -m colorbot.main --once --verbose
```

### 7. Config Validation

Add validation for rule JSON.

Minimum validation should check:

- rule name exists and is unique
- region has left/top/width/height integers
- target_rgb has exactly 3 integers from 0 to 255
- tolerance is non-negative
- min_pixels is positive
- cooldown is non-negative
- actions are recognized and contain required fields

Suggested file:

```text
colorbot/config_schema.py
```

Do not add a heavy validation library unless necessary.

### 8. Logging Improvements

Improve logs so GUI can read them easily:

- Keep JSONL event log
- Add event types: started, stopped, triggered, action_started, action_finished, action_error, config_error
- Add clear error messages

### 9. Documentation Updates

Update README.md with:

- GUI usage
- CLI usage
- How to create a rule
- How to use dry-run safely
- Troubleshooting
- Emergency stop instructions

## Nice-to-Have Features

Add only if the required features are already working:

- Import/export individual rules
- Screenshot preview of watched region
- Test detection on a single rule
- Per-rule action dry-run preview
- Light/dark GUI toggle
- Sound notification action
- Desktop notification action

## Implementation Rules

- Keep it Windows-friendly.
- Keep dependencies minimal.
- Do not remove the CLI workflow.
- Keep the project understandable for a beginner.
- Add comments where the code would otherwise be confusing.
- Prefer small modules over one giant file.
- Do not introduce async complexity unless clearly needed.
- Keep pyautogui failsafe enabled.
- Preserve emergency stop hotkey behavior where possible.

## Testing / Validation

After implementation, run or create checks for:

```bash
python -m colorbot.main --dry-run --once --verbose
python -m colorbot.main --help
python -m py_compile colorbot/main.py colorbot/gui.py
```

If a GUI cannot be fully tested in the environment, still validate imports and explain what must be manually tested on Windows.

## Deliverables

When finished:

1. Summarize changed files.
2. Explain how to launch the GUI.
3. Explain how to create the first rule using the GUI.
4. Mention any manual Windows tests still needed.
5. Do not claim it is fully tested unless it was actually run.
