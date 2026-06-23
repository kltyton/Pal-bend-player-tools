#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert player_model.geo / BlockBench helper-bend animations to PAL bend animations.

Input helper form:

    "right_arm_bend": {
      "rotation": {
        "0.5": {"post": [46, 0, 0]}
      }
    }

Output PAL bend form:

    "right_arm": {
      "bend": {
        "0.5": {"post": 46}
      }
    }

For this player_model.geo project, PAL bend = *_bend.rotation.x by default.
Use --helper-sign -1 only if you intentionally want opposite-sign conversion.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Dict

HELPER_SUFFIX = "_bend"


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def clean_zero(x: Any) -> Any:
    if isinstance(x, float) and abs(x) < 1e-12:
        return 0
    return x


def apply_sign(value: Any, sign: float) -> Any:
    if sign == 1:
        return value
    if is_number(value):
        return clean_zero(float(value) * sign)
    if isinstance(value, str):
        if value.strip() in ("0", "0.0"):
            return value
        return f"({sign})*({value})"
    return value


def extract_x(value: Any) -> Any:
    if is_number(value) or isinstance(value, str):
        return value
    if isinstance(value, list):
        return value[0] if value else 0
    if isinstance(value, dict):
        if "value" in value:
            return extract_x(value["value"])
        if "vector" in value:
            return extract_x(value["vector"])
        if "post" in value:
            return extract_x(value["post"])
        if "pre" in value:
            return extract_x(value["pre"])
    return 0


def looks_like_single_keyframe(obj: Dict[str, Any]) -> bool:
    return any(k in obj for k in ("vector", "value", "pre", "post", "lerp_mode", "easing"))


def frame_to_bend_frame(frame: Any, default_lerp: str | None, helper_sign: float) -> Dict[str, Any]:
    if isinstance(frame, dict):
        out: Dict[str, Any] = {}
        if "pre" in frame:
            out["pre"] = apply_sign(extract_x(frame["pre"]), helper_sign)
        if "post" in frame:
            out["post"] = apply_sign(extract_x(frame["post"]), helper_sign)
        elif "vector" in frame or "value" in frame:
            out["post"] = apply_sign(extract_x(frame), helper_sign)
        if "lerp_mode" in frame:
            out["lerp_mode"] = frame["lerp_mode"]
        elif default_lerp and "easing" not in frame:
            out["lerp_mode"] = default_lerp
        for key in ("easing", "easingArgs", "easingX", "easingY", "easingZ", "easingArgsX", "easingArgsY", "easingArgsZ"):
            if key in frame:
                out[key] = copy.deepcopy(frame[key])
        if not out:
            out["post"] = apply_sign(extract_x(frame), helper_sign)
            if default_lerp:
                out["lerp_mode"] = default_lerp
        return out
    out = {"post": apply_sign(extract_x(frame), helper_sign)}
    if default_lerp:
        out["lerp_mode"] = default_lerp
    return out


def rotation_track_to_bend(rotation_track: Any, default_lerp: str | None, helper_sign: float) -> Dict[str, Any]:
    if rotation_track is None:
        return {}
    if isinstance(rotation_track, dict):
        if looks_like_single_keyframe(rotation_track):
            return {"0": frame_to_bend_frame(rotation_track, default_lerp, helper_sign)}
        return {str(t): frame_to_bend_frame(f, default_lerp, helper_sign) for t, f in rotation_track.items()}
    return {"0": frame_to_bend_frame(rotation_track, default_lerp, helper_sign)}


def merge_tracks(existing: Any, incoming: Dict[str, Any]) -> Dict[str, Any]:
    merged = copy.deepcopy(existing) if isinstance(existing, dict) else {}
    merged.update(incoming)
    return merged


def convert_animation(anim: Dict[str, Any], suffix: str, default_lerp: str | None, keep_helpers: bool, helper_sign: float) -> int:
    bones = anim.get("bones")
    if not isinstance(bones, dict):
        return 0
    converted = 0
    for helper_name in list(bones.keys()):
        if not helper_name.endswith(suffix):
            continue
        helper = bones.get(helper_name)
        if not isinstance(helper, dict) or "rotation" not in helper:
            continue
        base_name = helper_name[:-len(suffix)]
        bend_track = rotation_track_to_bend(helper.get("rotation"), default_lerp, helper_sign)
        if not bend_track:
            continue
        base = bones.setdefault(base_name, {})
        if not isinstance(base, dict):
            base = {}
            bones[base_name] = base
        base["bend"] = merge_tracks(base.get("bend"), bend_track)
        converted += 1
        if keep_helpers:
            continue
        remaining = copy.deepcopy(helper)
        remaining.pop("rotation", None)
        if remaining:
            bones[helper_name] = remaining
            print(f"[warn] {helper_name} still has non-rotation tracks; kept helper bone without rotation.", file=sys.stderr)
        else:
            bones.pop(helper_name, None)
    return converted


def convert_file(data: Dict[str, Any], suffix: str, default_lerp: str | None, keep_helpers: bool, helper_sign: float) -> tuple[Dict[str, Any], int]:
    result = copy.deepcopy(data)
    total = 0
    if isinstance(result.get("animations"), dict):
        for anim in result["animations"].values():
            if isinstance(anim, dict):
                total += convert_animation(anim, suffix, default_lerp, keep_helpers, helper_sign)
    elif isinstance(result.get("bones"), dict):
        total += convert_animation(result, suffix, default_lerp, keep_helpers, helper_sign)
    else:
        raise ValueError("No animations/bones object found.")
    return result, total


def ask_catmullrom() -> bool:
    if not sys.stdin.isatty():
        print("[info] Non-interactive stdin detected; defaulting to no catmullrom. Use --catmullrom to force it.")
        return False
    print('是否给缺少 lerp_mode 的 bend 关键帧添加："lerp_mode": "catmullrom" ?')
    print("  Y = 添加 catmullrom，动作更平滑，但可能过冲")
    print("  N = 不添加，PAL 默认 LINEAR，最稳定")
    answer = input("请选择 [y/N]: ").strip().lower()
    return answer in {"y", "yes", "1", "true", "是", "加", "添加"}


def resolve_default_lerp(args: argparse.Namespace) -> str | None:
    if args.catmullrom and args.no_catmullrom:
        raise ValueError("--catmullrom and --no-catmullrom cannot be used together.")
    if args.default_lerp:
        return args.default_lerp
    if args.catmullrom:
        return "catmullrom"
    if args.no_catmullrom:
        return None
    return "catmullrom" if ask_catmullrom() else None


def main() -> None:
    parser = argparse.ArgumentParser(description="player_model.geo helper-bend animations -> PAL bend animations")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--suffix", default=HELPER_SUFFIX)
    parser.add_argument("--helper-sign", type=float, default=1.0, help="PAL bend = helper_sign * *_bend.rotation.x; default 1 for player_model.geo")
    parser.add_argument("--catmullrom", action="store_true", help="Add lerp_mode=catmullrom when source keyframe has no lerp_mode/easing.")
    parser.add_argument("--no-catmullrom", action="store_true", help="Do not ask; do not add any default lerp_mode.")
    parser.add_argument("--default-lerp", default="", help="Advanced: custom default lerp_mode, e.g. catmullrom. Overrides the prompt.")
    parser.add_argument("--keep-helper-bones", action="store_true")
    args = parser.parse_args()
    default_lerp = resolve_default_lerp(args)
    data = json.load(args.input.open("r", encoding="utf-8"))
    result, total = convert_file(data, args.suffix, default_lerp, args.keep_helper_bones, args.helper_sign)
    json.dump(result, args.output.open("w", encoding="utf-8"), ensure_ascii=False, indent=4)
    args.output.write_text(args.output.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    if default_lerp:
        print(f"Converted {total} helper bend bone(s). Added default lerp_mode={default_lerp!r} where missing. helper_sign={args.helper_sign}")
    else:
        print(f"Converted {total} helper bend bone(s). Did not add default lerp_mode. helper_sign={args.helper_sign}")


if __name__ == "__main__":
    main()
