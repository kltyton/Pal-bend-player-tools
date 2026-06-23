#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert PAL/BlockBench animations JSON to PAL/Emotecraft emote JSON.

This script accepts either:
- normal PAL/Bedrock animations JSON;
- player_model.geo helper-bend animations, where *_bend.rotation.x previews bend.

For player_model.geo helper-bend input, the script first converts helper bones
back into PAL bend tracks, then emits emote JSON using pal_source_lib.py.
"""
from __future__ import annotations
import argparse
import copy
import os
import sys
from typing import Any, Dict

from pal_source_lib import (
    load_json, dump_json, parse_animations_to_ir, parse_emote_to_ir,
    ir_to_emote_json, compare_ir_sample_points,
)

HELPER_SUFFIX = "_bend"


def is_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


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


def normalize_track(track: Any) -> Dict[str, Any]:
    if track is None:
        return {}
    if isinstance(track, dict):
        if looks_like_single_keyframe(track):
            return {"0": track}
        return dict(track)
    return {"0": track}


def helper_frame_to_bend_frame(frame: Any, helper_sign: float) -> Dict[str, Any]:
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
        if "easing" in frame:
            out["easing"] = frame["easing"]
        for key in ("easingArgs", "easingX", "easingY", "easingZ", "easingArgsX", "easingArgsY", "easingArgsZ"):
            if key in frame:
                out[key] = copy.deepcopy(frame[key])
        if not out:
            out["post"] = apply_sign(extract_x(frame), helper_sign)
        return out
    return {"post": apply_sign(extract_x(frame), helper_sign)}


def model_animations_to_pal_bend(data: Dict[str, Any], *, helper_sign: float = 1.0, keep_helpers: bool = False) -> Dict[str, Any]:
    """Convert player_model.geo helper bones into PAL bend fields.

    Default helper_sign=1 matches this project: PAL bend = *_bend.rotation.x.
    """
    out = copy.deepcopy(data)
    animations = out.get("animations")
    if not isinstance(animations, dict):
        return out
    for anim in animations.values():
        if not isinstance(anim, dict):
            continue
        bones = anim.get("bones")
        if not isinstance(bones, dict):
            continue
        for helper_name in list(bones.keys()):
            if not helper_name.endswith(HELPER_SUFFIX):
                continue
            helper = bones.get(helper_name)
            if not isinstance(helper, dict) or "rotation" not in helper:
                continue
            base_name = helper_name[:-len(HELPER_SUFFIX)]
            bend_track = {str(t): helper_frame_to_bend_frame(f, helper_sign) for t, f in normalize_track(helper.get("rotation")).items()}
            base = bones.setdefault(base_name, {})
            if not isinstance(base, dict):
                base = {}
                bones[base_name] = base
            existing = base.get("bend") if isinstance(base.get("bend"), dict) else {}
            merged = copy.deepcopy(existing)
            merged.update(bend_track)
            base["bend"] = merged
            if not keep_helpers:
                remaining = copy.deepcopy(helper)
                remaining.pop("rotation", None)
                if remaining:
                    bones[helper_name] = remaining
                else:
                    bones.pop(helper_name, None)
    return out


def has_helper_bones(data: Dict[str, Any]) -> bool:
    animations = data.get("animations")
    if not isinstance(animations, dict):
        return False
    for anim in animations.values():
        if not isinstance(anim, dict):
            continue
        bones = anim.get("bones")
        if isinstance(bones, dict) and any(name.endswith(HELPER_SUFFIX) for name in bones):
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="PAL animations/player_model.geo helper animations -> emote converter")
    ap.add_argument("input", help="input animations JSON")
    ap.add_argument("output", help="output emote JSON")
    ap.add_argument("--animation-name", default=None, help="which animation map key to convert; default: first")
    ap.add_argument("--name", default=None, help="emote name")
    ap.add_argument("--author", default="", help="emote author")
    ap.add_argument("--description", default="", help="emote description")
    ap.add_argument("--degrees", action="store_true", help="write emote rotations as degrees instead of radians")
    ap.add_argument("--legacy-easing", action="store_true", help="omit easeBeforeKeyframe=true; not recommended for exact conversion")
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--model-format", action="store_true", help="force treating input as player_model.geo helper-bend animations")
    group.add_argument("--no-model-format", action="store_true", help="do not convert *_bend helper bones")
    ap.add_argument("--helper-sign", type=float, default=1.0, help="sign multiplier when converting *_bend.rotation.x to PAL bend; default 1 for player_model.geo")
    ap.add_argument("--keep-helper-bones", action="store_true", help="keep *_bend helper bones in the intermediate PAL animation before conversion")
    ap.add_argument("--validate", action="store_true", help="parse output again and compare PAL-like IR")
    args = ap.parse_args()

    data = load_json(args.input)
    if args.model_format or (not args.no_model_format and has_helper_bones(data)):
        data_for_parse = model_animations_to_pal_bend(data, helper_sign=args.helper_sign, keep_helpers=args.keep_helper_bones)
    else:
        data_for_parse = data

    anims = parse_animations_to_ir(data_for_parse, args.animation_name)
    if args.animation_name is None:
        anim_name, ir = next(iter(anims.items()))
    else:
        anim_name = args.animation_name
        ir = anims[anim_name]
    out_name = args.name or anim_name or os.path.splitext(os.path.basename(args.input))[0]
    out = ir_to_emote_json(
        ir,
        name=out_name,
        author=args.author,
        description=args.description,
        degrees=args.degrees,
        version=3,
        ease_before_keyframe=not args.legacy_easing,
    )
    dump_json(out, args.output)

    if args.validate and not args.legacy_easing:
        parsed = parse_emote_to_ir(load_json(args.output), name_hint=out_name)
        ok, errors = compare_ir_sample_points(ir, parsed)
        if not ok:
            print("验证未完全一致：", file=sys.stderr)
            for e in errors[:50]:
                print("  -", e, file=sys.stderr)
            if len(errors) > 50:
                print(f"  ... 还有 {len(errors) - 50} 条", file=sys.stderr)
            return 2
        print("验证通过：输出 emote 再按 PlayerAnimatorLoader 解析后，与输入 animations 的 PAL 内部关键帧等价。")
    elif args.validate and args.legacy_easing:
        print("--legacy-easing 会触发 PlayerAnimatorLoader 的 easing 位移，跳过严格验证。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
