from __future__ import annotations

import argparse
import json
import signal
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import mss
import numpy as np
import pyautogui

try:
    import keyboard  # type: ignore
except Exception:  # pragma: no cover - keyboard can fail without permissions
    keyboard = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "rules.json"

STOP_REQUESTED = False


@dataclass
class DetectionResult:
    found: bool
    matching_pixels: int
    centroid_screen: Optional[Tuple[int, int]] = None


def request_stop(*_: Any) -> None:
    global STOP_REQUESTED
    STOP_REQUESTED = True


def load_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if "rules" not in data or not isinstance(data["rules"], list):
        raise ValueError("Config must contain a top-level 'rules' list.")
    return data


def log_event(log_file: Path, event: Dict[str, Any]) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    event = {"timestamp": datetime.now().isoformat(timespec="seconds"), **event}
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def validate_region(region: Dict[str, int]) -> None:
    for key in ("left", "top", "width", "height"):
        if key not in region:
            raise ValueError(f"Region missing key: {key}")
        if not isinstance(region[key], int):
            raise ValueError(f"Region key must be int: {key}")
    if region["width"] <= 0 or region["height"] <= 0:
        raise ValueError("Region width/height must be positive.")


def scan_region_for_color(sct: mss.mss, rule: Dict[str, Any]) -> DetectionResult:
    region = rule["region"]
    validate_region(region)

    screenshot = sct.grab(region)
    arr = np.asarray(screenshot)[:, :, :3]

    # mss returns BGRA/BGR order; convert BGR -> RGB.
    rgb_arr = arr[:, :, ::-1]

    target = np.array(rule["target_rgb"], dtype=np.int16)
    tolerance = int(rule.get("tolerance", 20))
    min_pixels = int(rule.get("min_pixels", 1))

    diff = np.abs(rgb_arr.astype(np.int16) - target)
    mask = np.all(diff <= tolerance, axis=2)
    ys, xs = np.where(mask)
    count = int(len(xs))

    if count < min_pixels:
        return DetectionResult(False, count, None)

    centroid_x = int(xs.mean()) + int(region["left"])
    centroid_y = int(ys.mean()) + int(region["top"])
    return DetectionResult(True, count, (centroid_x, centroid_y))


def run_actions(actions: List[Dict[str, Any]], dry_run: bool = False) -> None:
    for action in actions:
        action_type = action.get("type")

        if dry_run:
            print(f"  DRY-RUN action: {action}")
            if action_type == "wait":
                time.sleep(float(action.get("seconds", 0)))
            continue

        if action_type == "click":
            pyautogui.click(int(action["x"]), int(action["y"]))
        elif action_type == "double_click":
            pyautogui.doubleClick(int(action["x"]), int(action["y"]))
        elif action_type == "right_click":
            pyautogui.rightClick(int(action["x"]), int(action["y"]))
        elif action_type == "move":
            pyautogui.moveTo(int(action["x"]), int(action["y"]), duration=float(action.get("duration", 0)))
        elif action_type == "wait":
            time.sleep(float(action["seconds"]))
        elif action_type == "press":
            pyautogui.press(str(action["key"]))
        elif action_type == "hotkey":
            keys = action.get("keys")
            if not isinstance(keys, list) or not keys:
                raise ValueError("hotkey action requires non-empty 'keys' list")
            pyautogui.hotkey(*[str(k) for k in keys])
        elif action_type == "type":
            pyautogui.write(str(action.get("text", "")), interval=float(action.get("interval", 0.01)))
        elif action_type == "scroll":
            pyautogui.scroll(int(action["amount"]))
        else:
            raise ValueError(f"Unsupported action type: {action_type}")


def install_emergency_hotkey(hotkey: str) -> None:
    if not hotkey:
        return
    if keyboard is None:
        print("keyboard module unavailable; emergency hotkey disabled. PyAutoGUI failsafe still active.")
        return
    try:
        keyboard.add_hotkey(hotkey, request_stop)
        print(f"Emergency stop hotkey active: {hotkey}")
    except Exception as exc:
        print(f"Could not install emergency hotkey '{hotkey}': {exc}")
        print("PyAutoGUI failsafe still active: move mouse to top-left corner.")


def main() -> int:
    parser = argparse.ArgumentParser(description="ColorBot v1 - region color watcher + action runner")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to rules JSON config")
    parser.add_argument("--dry-run", action="store_true", help="Detect and log, but do not perform actions")
    parser.add_argument("--once", action="store_true", help="Scan once, then exit")
    parser.add_argument("--verbose", action="store_true", help="Print non-trigger scan counts")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    config = load_config(config_path)
    settings = config.get("settings", {})
    rules = [r for r in config.get("rules", []) if r.get("enabled", True)]

    if not rules:
        print("No enabled rules found. Edit config/rules.json and set enabled=true for a rule.")
        return 1

    pyautogui.PAUSE = float(settings.get("pyautogui_pause_seconds", 0.03))
    pyautogui.FAILSAFE = True

    scan_delay = float(settings.get("scan_delay_seconds", 0.05))
    log_file = PROJECT_ROOT / str(settings.get("log_file", "logs/colorbot_events.jsonl"))

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    install_emergency_hotkey(str(settings.get("emergency_stop_hotkey", "ctrl+shift+q")))

    print("ColorBot v1 running.")
    print(f"Config: {config_path}")
    print(f"Rules enabled: {len(rules)}")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print("Emergency: Ctrl+C, configured hotkey, or mouse to top-left corner.")

    last_triggered: Dict[str, float] = {r["name"]: 0.0 for r in rules}
    stable_counts: Dict[str, int] = {r["name"]: 0 for r in rules}

    with mss.mss() as sct:
        while not STOP_REQUESTED:
            now = time.time()

            for rule in rules:
                name = str(rule["name"])
                cooldown = float(rule.get("cooldown_seconds", 0.5))
                required_stable = int(rule.get("require_stable_scans", 1))

                if now - last_triggered[name] < cooldown:
                    continue

                result = scan_region_for_color(sct, rule)

                if result.found:
                    stable_counts[name] += 1
                else:
                    stable_counts[name] = 0

                if args.verbose:
                    print(f"[{name}] found={result.found} pixels={result.matching_pixels} stable={stable_counts[name]}")

                if result.found and stable_counts[name] >= required_stable:
                    print(f"[{name}] triggered | pixels={result.matching_pixels} | centroid={result.centroid_screen}")
                    log_event(log_file, {
                        "rule": name,
                        "event": "triggered",
                        "matching_pixels": result.matching_pixels,
                        "centroid_screen": result.centroid_screen,
                        "dry_run": args.dry_run,
                    })
                    run_actions(rule.get("actions", []), dry_run=args.dry_run)
                    last_triggered[name] = time.time()
                    stable_counts[name] = 0

            if args.once:
                break
            time.sleep(scan_delay)

    print("ColorBot stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
