#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert PAL/Emotecraft emote JSON to PAL Bedrock/BlockBench animations JSON.

This script mirrors PlayerAnimatorLoader.java for the first conversion stage.
At export time it can optionally convert PAL bend tracks into helper-bone
rotation tracks for player_model.geo.json, e.g.:

    right_arm.bend -> right_arm_bend.rotation.x
    torso.bend     -> torso_bend.rotation.x

The optional model-format stage is meant for editing/previewing with the
bendable BlockBench geo model.  If you want to feed the animation directly to
PAL's AnimationLoader with real `bend` fields, do NOT enable model format.
"""
from __future__ import annotations

import argparse
import copy
import os
import sys
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    from pal_source_lib import (
        load_json, dump_json, parse_emote_to_ir, parse_animations_to_ir,
        ir_to_animations_json, compare_ir_sample_points,
    )
except ModuleNotFoundError:
    # The v4 package used this file name.  Keep a fallback so the script works
    # when copied next to either pal_source_lib.py or pal_source_exact_common.py.
    from pal_source_exact_common import (  # type: ignore
        load_json, dump_json, parse_emote_to_ir, parse_animations_to_ir,
        ir_to_animations_json, compare_ir_sample_points,
    )


BENDABLE_MODEL_NAME = "player_model.geo.json"
BEND_HELPER_BONES: Dict[str, str] = {
    "torso": "torso_bend",
    "right_arm": "right_arm_bend",
    "left_arm": "left_arm_bend",
    "right_leg": "right_leg_bend",
    "left_leg": "left_leg_bend",
}


def prompt_yes_no(question: str, default: bool = False) -> bool:
    """Ask an interactive yes/no question.  Non-interactive callers should use flags."""
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        ans = input(f"{question} {suffix}: ").strip().lower()
        if not ans:
            return default
        if ans in ("y", "yes", "是", "对", "1", "true"):
            return True
        if ans in ("n", "no", "否", "不", "0", "false"):
            return False
        print("请输入 y 或 n。")


def choose_model_format(args: argparse.Namespace) -> bool:
    if args.model_format:
        return True
    if args.no_model_format:
        return False
    if not sys.stdin.isatty():
        print(
            f"未检测到交互式终端，默认不转换为 {BENDABLE_MODEL_NAME} 格式。"
            "如需强制转换，请加 --model-format。"
        )
        return False
    print()
    print(f"是否再转换为 {BENDABLE_MODEL_NAME} 可用的传统骨骼动画格式？")
    print("  Y = 将 PAL 的 bend 字段改成 *_bend.rotation.x，方便 BlockBench/该 geo 模型使用")
    print("  N = 保持 PAL bend 字段，适合直接给 PAL AnimationLoader 读取")
    return prompt_yes_no("请选择", default=False)


def is_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def is_skip(x: Any) -> bool:
    return isinstance(x, str) and x in ("pal.skip", "pal.disabled")


def clean_zero(x: Any) -> Any:
    if isinstance(x, float) and abs(x) < 1e-12:
        return 0
    return x


def first_non_skip(values: Iterable[Any], default: Any = 0) -> Any:
    for v in values:
        if not is_skip(v):
            return v
    return default


def vector_x(value: Any, default: Any = 0) -> Any:
    """Extract the X component from Bedrock/PAL keyframe data.

    Supports numbers, strings/Molang expressions, vectors, and objects with
    value/vector/pre/post.  For bend -> helper rotation we only need X because
    PAL only uses bend X.
    """
    if value is None:
        return default
    if is_number(value) or isinstance(value, str):
        return clean_zero(value)
    if isinstance(value, list):
        if not value:
            return default
        return clean_zero(first_non_skip(value, default))
    if isinstance(value, dict):
        if "value" in value:
            return vector_x(value.get("value"), default)
        if "vector" in value:
            return vector_x(value.get("vector"), default)
        if "post" in value:
            return vector_x(value.get("post"), default)
        if "pre" in value:
            return vector_x(value.get("pre"), default)
    return default


def copy_lerp_from_bend_key(value: Any) -> Optional[Any]:
    if not isinstance(value, dict):
        return None
    # ir_to_animations_json writes "easing".  BlockBench-style post frames use
    # "lerp_mode".  If both exist, keep the explicit BlockBench name.
    easing = value.get("lerp_mode", value.get("easingX", value.get("easing")))
    if easing is None:
        return None
    if str(easing).replace("_", "").replace("-", "").lower() == "linear":
        return None
    return easing


def apply_helper_sign(value: Any, helper_sign: float) -> Any:
    if helper_sign == 1:
        return value
    if is_number(value):
        return clean_zero(float(value) * helper_sign)
    if isinstance(value, str):
        if value.strip() in ("0", "0.0"):
            return value
        return f"({helper_sign})*({value})"
    return value

def bend_key_to_helper_rotation_key(value: Any, helper_sign: float = 1.0) -> Dict[str, Any]:
    """Convert one PAL bend keyframe value into a BlockBench helper rotation key.

    For this player_model.geo project, helper rotation uses the opposite sign
    of PAL bend by default, so helper_sign=1.
    """
    out: Dict[str, Any] = {"post": [apply_helper_sign(vector_x(value, 0), helper_sign), 0, 0]}
    if isinstance(value, dict) and "pre" in value:
        out["pre"] = [apply_helper_sign(vector_x(value.get("pre"), 0), helper_sign), 0, 0]
    lerp = copy_lerp_from_bend_key(value)
    if lerp is not None:
        out["lerp_mode"] = lerp
    return out


def normalize_keyframe_map(track: Any) -> Dict[str, Any]:
    """Return a timestamp -> keyframe map for a transform track."""
    if track is None:
        return {}
    if isinstance(track, dict):
        # A direct keyframe object like {"vector": ...} means t=0.
        if any(k in track for k in ("value", "vector", "pre", "post")):
            return {"0": track}
        return dict(track)
    # Constant/list track means t=0.
    return {"0": track}


def merge_track(dst: Dict[str, Any], src: Dict[str, Any], *, overwrite: bool = False) -> None:
    for t, v in src.items():
        if overwrite or t not in dst:
            dst[t] = v


def merge_bone(dst: Dict[str, Any], src: Dict[str, Any], *, overwrite: bool = False) -> None:
    """Merge transform tracks from src into dst."""
    for transform, src_track in src.items():
        if transform not in dst or not isinstance(dst.get(transform), dict) or not isinstance(src_track, dict):
            if overwrite or transform not in dst:
                dst[transform] = copy.deepcopy(src_track)
            continue
        merge_track(dst[transform], src_track, overwrite=overwrite)


def remove_empty_bones(bones: Dict[str, Any]) -> None:
    for name in list(bones.keys()):
        bone = bones[name]
        if isinstance(bone, dict) and not bone:
            bones.pop(name, None)


def convert_to_bendable_model_format(
    animations_json: Dict[str, Any],
    *,
    keep_pal_bend: bool = False,
    body_to_torso: bool = False,
    helper_sign: float = 1.0,
) -> Dict[str, Any]:
    """Make the generated animations convenient for the bendable geo model.

    - parent.bend is moved to parent_bend.rotation.x.
    - body can optionally be merged into torso via --body-to-torso, but is kept
      by default because player_model.geo.json has a
      real body root bone and PAL old emotes often intentionally animate it.
    """
    out = copy.deepcopy(animations_json)
    animations = out.get("animations", {})
    if not isinstance(animations, dict):
        return out

    for _anim_name, anim_obj in animations.items():
        if not isinstance(anim_obj, dict):
            continue
        bones = anim_obj.get("bones")
        if not isinstance(bones, dict):
            continue

        if body_to_torso and "body" in bones:
            body_bone = bones.pop("body")
            torso_bone = bones.setdefault("torso", {})
            if isinstance(body_bone, dict) and isinstance(torso_bone, dict):
                merge_bone(torso_bone, body_bone, overwrite=False)
            else:
                bones["torso"] = copy.deepcopy(body_bone)

        for parent, helper in BEND_HELPER_BONES.items():
            parent_bone = bones.get(parent)
            if not isinstance(parent_bone, dict) or "bend" not in parent_bone:
                continue

            bend_track = normalize_keyframe_map(parent_bone.get("bend"))
            if not bend_track:
                if not keep_pal_bend:
                    parent_bone.pop("bend", None)
                continue

            helper_bone = bones.setdefault(helper, {})
            if not isinstance(helper_bone, dict):
                helper_bone = {}
                bones[helper] = helper_bone
            helper_rotation = helper_bone.setdefault("rotation", {})
            if not isinstance(helper_rotation, dict):
                helper_rotation = {}
                helper_bone["rotation"] = helper_rotation

            converted: Dict[str, Any] = {}
            for timestamp, value in bend_track.items():
                converted[str(timestamp)] = bend_key_to_helper_rotation_key(value, helper_sign)
            merge_track(helper_rotation, converted, overwrite=True)

            if not keep_pal_bend:
                parent_bone.pop("bend", None)

        remove_empty_bones(bones)

    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="PAL source-exact emote -> animations converter")
    ap.add_argument("input", help="input emote JSON")
    ap.add_argument("output", help="output animations JSON")
    ap.add_argument("--animation-name", default="animation", help="animations map key to write, default: animation")
    ap.add_argument("--validate", action="store_true", help="parse the source-exact output again and compare PAL-like IR before optional model-format conversion")

    model_group = ap.add_mutually_exclusive_group()
    model_group.add_argument("--model-format", action="store_true", help=f"do not ask; convert output to {BENDABLE_MODEL_NAME} helper-bone format")
    model_group.add_argument("--no-model-format", action="store_true", help="do not ask; keep normal PAL bend animation format")
    ap.add_argument("--keep-pal-bend", action="store_true", help="when using --model-format, keep parent.bend as well as writing *_bend.rotation")
    ap.add_argument("--body-to-torso", action="store_true", help="when using --model-format, merge body tracks into torso; default keeps body because the geo model has a body root")
    ap.add_argument("--helper-sign", type=float, default=1.0, help="sign multiplier when writing PAL bend to *_bend.rotation.x; default 1 for player_model.geo")
    args = ap.parse_args()

    data = load_json(args.input)
    ir = parse_emote_to_ir(data, name_hint=os.path.splitext(os.path.basename(args.input))[0])
    source_exact_out = ir_to_animations_json(ir, args.animation_name)

    if args.validate:
        parsed = parse_animations_to_ir(source_exact_out, args.animation_name)[args.animation_name]
        ok, errors = compare_ir_sample_points(ir, parsed)
        if not ok:
            print("验证未完全一致：", file=sys.stderr)
            for e in errors[:50]:
                print("  -", e, file=sys.stderr)
            if len(errors) > 50:
                print(f"  ... 还有 {len(errors) - 50} 条", file=sys.stderr)
            return 2
        print("验证通过：正常 PAL animations 输出再按 AnimationLoader 解析后，与输入 emote 的 PAL 内部关键帧等价。")

    use_model_format = choose_model_format(args)
    if use_model_format:
        out = convert_to_bendable_model_format(
            source_exact_out,
            keep_pal_bend=args.keep_pal_bend,
            body_to_torso=args.body_to_torso,
            helper_sign=args.helper_sign,
        )
        print(f"已转换为 {BENDABLE_MODEL_NAME} 可用格式：PAL bend -> *_bend.rotation.x")
        if args.body_to_torso:
            print("已按 --body-to-torso 将 body 动画合并到 torso。")
        else:
            print("body 动画保持为 body；该模型有 body 根骨骼。如需改到 torso，请加 --body-to-torso。")
        if args.keep_pal_bend:
            print("已按 --keep-pal-bend 同时保留 parent.bend。")
    else:
        out = source_exact_out

    dump_json(out, args.output)
    print(f"已导出: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
