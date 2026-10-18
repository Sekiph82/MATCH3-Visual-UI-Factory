"""M09 manual Windows desktop review of exported M08 TEST_ONLY visual packs.

Tk (Python 3.12 standard library) viewer; NO Unity/Engine dependency, game
actions, download, asset overwrite, mobile GPU or owner art approval. Uses
the *actual source PNG pixels* from an export, NOT an invented polished game
screen. Multiple profile/source packs can be compared A/B by file name and
original SHA. FX 4x2 frame-sheet playback is optional, bounded and only a
source-atlas crop; UI/VFX cross-component rendered parity must be tested in
Unity Editor M09 Studio, not this Tk canvas.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from factory.asset_packaging.verify_offline_bundle import verify_exported_pack
from factory.qa.m09_review_inventory import (
    PROFILES, STATES, LOCALES, DEVICES, index_to_case, inventory_report,
)

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ("ui_open", "ui_close", "tile_spawn", "tile_match", "special_trigger",
          "combo_chain", "obstacle_hit", "booster_activate", "level_win",
          "level_fail", "reward_claim", "character_idle",
          "character_celebrate", "region_reveal")
SPEEDS = (.25, .5, 1.0, 2.0)
STAGE = "TK_SOURCE_PREVIEW_OWNER_REVIEW_PENDING"


class WindowsViewerError(ValueError):
    pass


def _validate_folder(folder: Path) -> Path:
    directory = Path(folder).resolve(strict=True)
    if directory.is_relative_to(ROOT) or not directory.is_dir():
        raise WindowsViewerError("review pack must be external and a real folder")
    for part in (Path(folder), *Path(folder).parents):
        if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
            raise WindowsViewerError("symlink/junction pack refused")
    return directory


def source_pack(folder: Path) -> dict:
    directory = _validate_folder(folder)
    proof = verify_exported_pack(directory)
    manifest = json.loads((directory / "visual_manifest.json").read_text())
    indexed = {}
    for asset in manifest["assets"]:
        rel = asset["path"]
        png = directory / rel
        if not png.is_file() or png.is_symlink():
            raise WindowsViewerError("source path is not a real candidate")
        if hashlib.sha256(png.read_bytes()).hexdigest() != asset["sha256"]:
            raise WindowsViewerError("source SHA changed AFTER bundle validation")
        indexed[rel] = {
            "sha256": asset["sha256"],
            "asset_id": asset["asset_id"], "path": png,
        }
    return {"folder": directory, "manifest": manifest,
            "images": indexed, "receipt": proof}


def frame_region(asset_name: str, frame: int, width: int, height: int):
    """Source-sheet-only 8-frame geometry, not Unity frame/alpha acceptance."""
    if (type(frame) is not int or frame not in range(8) or
            type(width) is not int or type(height) is not int or
            width < 32 or height < 64):
        raise WindowsViewerError("invalid bounded source frame geometry")
    if (not asset_name.startswith("fx/") or
            not asset_name.endswith("/fx_sheet.png")):
        raise WindowsViewerError("frame crop applies only to VF06 FX sheet")
    if width % 4 or height % 2:
        raise WindowsViewerError("FX sheet must divide into 4 x 2 frames")
    w, h = width // 4, height // 2
    return ((frame % 4) * w, (frame // 4) * h,
            (frame % 4 + 1) * w, (frame // 4 + 1) * h)


def receipt(pack: dict, relative: str, *, screen_index: int,
            state: str, locale: str, device: str, event: str,
            level: int, seed: int, speed: float, frame: int) -> dict:
    if (relative not in pack["images"] or
            screen_index not in range(28) or
            state not in STATES or locale not in LOCALES or
            device not in DEVICES or event not in EVENTS or
            type(level) is not int or not 1 <= level <= 100 or
            type(seed) is not int or not 0 <= seed <= 65535 or
            type(speed) not in (float, int) or speed not in SPEEDS or
            type(frame) is not int or not 0 <= frame < 8):
        raise WindowsViewerError("viewer source selection invalid")
    selected = pack["images"][relative]
    profile = pack["manifest"]["profile_id"]
    case = index_to_case(
        PROFILES.index(profile) * 28 * 8 * 3 * 5 +
        screen_index * 8 * 3 * 5 +
        STATES.index(state) * 3 * 5 +
        LOCALES.index(locale) * 5 + DEVICES.index(device))
    return {
        "schema_version": 1,
        "stage": STAGE,
        "profile_id": profile,
        "source_png_relative_path": relative,
        "source_png_sha256": selected["sha256"],
        "source_asset_id": selected["asset_id"],
        "candidate_case": case,
        "view_event_log_only": event,
        "mock_level": level, "mock_seed": seed,
        "source_frame_index": frame, "preview_speed": speed,
        "actual_unity_gui_render": False,
        "owner_art_originality_verified": False,
        "independent_game_screen_contract_verified": profile == "Coral_Rescue",
        "real_device_gpu_verified": False,
        "audio_haptic_actuated": False,
        "engine_replay_bound": False,
        "release_allowed": False,
    }


def create_new_receipt(path: Path, record: dict) -> None:
    if not isinstance(record, dict) or record.get("stage") != STAGE or any(
        record.get(k) is not False for k in (
            "actual_unity_gui_render", "owner_art_originality_verified",
            "real_device_gpu_verified", "audio_haptic_actuated",
            "engine_replay_bound", "release_allowed")):
        raise WindowsViewerError("forged owner/Unity acceptance receipt")
    path = Path(path)
    if (path.exists() or path.is_symlink() or
            not path.parent.exists() or
            path.resolve(strict=False).is_relative_to(ROOT) or
            path.suffix.lower() != ".json"):
        raise WindowsViewerError("receipt must be NEW external JSON")
    with path.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")


def run_gui(first_pack: Path, second_pack: Path | None) -> None:
    # Lazy import: pure source validation/tests never require a GUI display.
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    left = source_pack(first_pack)
    right = source_pack(second_pack) if second_pack else None
    root = tk.Tk()
    root.title("VUF M09 | Windows SOURCE candidate viewer (NOT Unity)")
    root.geometry("1120x850")
    chosen = tk.StringVar(value=sorted(left["images"])[0])
    screen = tk.IntVar(value=26)
    state = tk.StringVar(value="Ready")
    locale = tk.StringVar(value="en")
    device = tk.StringVar(value=DEVICES[0])
    event = tk.StringVar(value="tile_match")
    speed = tk.StringVar(value="1.0")
    frame = tk.IntVar(value=0)
    paused = tk.BooleanVar(value=True)
    reduced = tk.BooleanVar(value=True)
    level = tk.IntVar(value=1)
    seed = tk.IntVar(value=7)
    info = tk.StringVar(value="SOURCE ONLY, zero device/GUI approval")
    header = ttk.Frame(root, padding=10)
    header.pack(fill="x")
    ttk.Label(header, text="M09 DESKTOP SOURCE INSPECTOR | Unity rendered UI = N/A",
              font=("Segoe UI", 13, "bold")).grid(row=0, column=0, columnspan=5, sticky="w")
    def combo(label, var, values, row, col):
        ttk.Label(header, text=label).grid(row=row, column=col, sticky="w")
        widget = ttk.Combobox(header, textvariable=var, state="readonly",
                              values=list(values), width=22)
        widget.grid(row=row+1, column=col, padx=2)
        widget.bind("<<ComboboxSelected>>", lambda _=None: draw())
    combo("Source image", chosen, sorted(left["images"]), 1, 0)
    combo("Mock state", state, STATES, 1, 1)
    combo("Mock locale", locale, LOCALES, 1, 2)
    combo("Synthetic device", device, DEVICES, 1, 3)
    combo("View cue LOG ONLY", event, EVENTS, 1, 4)
    combo("Speed", speed, SPEEDS, 3, 0)
    ttk.Label(header, text="Coral screen index 0..27").grid(row=3, column=1)
    tk.Spinbox(header, from_=0, to=27, textvariable=screen, width=9,
               command=lambda: draw()).grid(row=4, column=1)
    ttk.Label(header, text="MOCK Level, Seed").grid(row=3, column=2)
    tk.Spinbox(header, from_=1, to=100, textvariable=level, width=7).grid(row=4, column=2)
    tk.Spinbox(header, from_=0, to=65535, textvariable=seed, width=7).grid(row=4, column=3)
    ttk.Checkbutton(header, text="Pause animation", variable=paused).grid(row=3, column=4)
    ttk.Checkbutton(header, text="Reduced-motion static", variable=reduced).grid(row=4, column=4)
    previews = ttk.Frame(root)
    previews.pack(fill="both", expand=True)
    labels = []
    for i in range(2):
        panel = ttk.Frame(previews, padding=8)
        panel.pack(side="left", fill="both", expand=True)
        ttk.Label(panel, text=("PACK A" if i == 0 else "PACK B / N-A IF MISSING"),
                  font=("Segoe UI", 11, "bold")).pack()
        surface = ttk.Label(panel, text="No source")
        surface.pack(fill="both", expand=True)
        labels.append(surface)
    ttk.Label(root, textvariable=info, wraplength=1050).pack(fill="x", padx=12)
    state_held = {"image": [None, None]}
    def view_image(pack, index):
        if pack is None or chosen.get() not in pack["images"]:
            labels[index].configure(text="N/A: matching source path unavailable", image="")
            state_held["image"][index] = None
            return
        selected = pack["images"][chosen.get()]
        source = tk.PhotoImage(file=str(selected["path"]))
        if chosen.get().startswith("fx/") and chosen.get().endswith("/fx_sheet.png"):
            bounds = frame_region(chosen.get(), frame.get(),
                                  source.width(), source.height())
            cropped = tk.PhotoImage(width=bounds[2]-bounds[0],
                                    height=bounds[3]-bounds[1])
            cropped.tk.call(str(cropped), "copy", str(source),
                            "-from", *bounds, "-to", 0, 0)
            source = cropped
        factor = max(1, (source.width()+399)//400, (source.height()+509)//510)
        source = source.subsample(factor, factor)
        labels[index].configure(image=source, text="")
        state_held["image"][index] = source
    def draw():
        try:
            view_image(left, 0)
            view_image(right, 1)
            case = receipt(left, chosen.get(), screen_index=screen.get(),
                           state=state.get(), locale=locale.get(),
                           device=device.get(), event=event.get(),
                           level=level.get(), seed=seed.get(),
                           speed=float(speed.get()), frame=frame.get())
            info.set(case["candidate_case"]["coverage_status"] +
                     " | FX source frame " + str(frame.get()) +
                     " | NO Unity runtime/owner art/phone sound-haptic validation")
        except Exception as ex:
            info.set("SOURCE PREVIEW REFUSED: " + str(ex))
    def step(amount=1):
        frame.set((frame.get() + amount) % 8)
        draw()
    def cycle():
        if not paused.get() and not reduced.get() and chosen.get().startswith("fx/"):
            step(1)
        root.after(int(400 / max(.25, float(speed.get()))), cycle)
    def export_receipt():
        try:
            selected = receipt(left, chosen.get(), screen_index=screen.get(),
                 state=state.get(), locale=locale.get(), device=device.get(),
                 event=event.get(), level=level.get(), seed=seed.get(),
                 speed=float(speed.get()), frame=frame.get())
            path = filedialog.asksaveasfilename(
                title="NEW external unapproved source receipt only",
                defaultextension=".json", filetypes=[("JSON","*.json")])
            if path: create_new_receipt(Path(path), selected)
        except Exception as ex:
            messagebox.showerror("Refused", str(ex))
    controls = ttk.Frame(root, padding=8)
    controls.pack(fill="x")
    ttk.Button(controls, text="Previous frame", command=lambda: step(-1)).pack(side="left")
    ttk.Button(controls, text="Next frame", command=lambda: step(1)).pack(side="left")
    ttk.Button(controls, text="Draw/recheck source", command=draw).pack(side="left")
    ttk.Button(controls, text="Save NEW unapproved review JSON",
               command=export_receipt).pack(side="right")
    ttk.Label(root, text="Video export: UNSUPPORTED (use Unity GUI/owner recorder). "
              "Source atlas frames are not gameplay or Unity screenshots.",
              wraplength=1050).pack(fill="x")
    draw()
    root.after(800, cycle)
    root.mainloop()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pack-a", required=True, type=Path)
    p.add_argument("--pack-b", type=Path)
    args = p.parse_args(argv)
    run_gui(args.pack_a, args.pack_b)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
