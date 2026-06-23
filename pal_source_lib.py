#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAL source-exact conversion helpers.

This file mirrors the relevant parts of PlayerAnimationLibrary's Java loaders:
- PlayerAnimatorLoader.java for Emotecraft/PAL emote JSON.
- AnimationLoader.java for Bedrock/BlockBench animations JSON.

It intentionally represents PAL's internal keyframe stacks as absolute end-tick
axis keyframes.  Numeric rotation and bend constants in Bedrock animations are
converted through degrees <-> radians exactly like MolangLoader.parseJson(...,
isForRotation=true, ...).  Molang expressions are preserved where possible, but
full expression algebra/inversion is not attempted.
"""

from __future__ import annotations

import copy
import json
import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

SKIP = "pal.skip"
EPS_TICK = 0.001

# Mirrors PlayerAnimatorLoader.DEFAULT_VALUES
DEFAULT_VALUES: Dict[str, Tuple[float, float, float]] = {
    "right_arm": (-5.0, 2.0, 0.0),
    "left_arm": (5.0, 2.0, 0.0),
    "left_leg": (1.9, 12.0, 0.1),
    "right_leg": (-1.9, 12.0, 0.1),
}

TRANSFORM_AXES = {
    "position": ("x", "y", "z"),
    "rotation": ("pitch", "yaw", "roll"),
    "scale": ("scaleX", "scaleY", "scaleZ"),
    "bend": ("bend",),
}

ANIM_TRANSFORMS = ("position", "rotation", "scale", "bend")

# EasingType names from PAL's EasingType enum.  Values are enum names because
# emote JSON traditionally uses uppercase enum-like spellings.
EASING_NAMES = {
    "linear": "LINEAR",
    "constant": "CONSTANT",
    "step": "STEP",
    "easeinsine": "EASEINSINE",
    "easeoutsine": "EASEOUTSINE",
    "easeinoutsine": "EASEINOUTSINE",
    "easeinquad": "EASEINQUAD",
    "easeoutquad": "EASEOUTQUAD",
    "easeinoutquad": "EASEINOUTQUAD",
    "easeincubic": "EASEINCUBIC",
    "easeoutcubic": "EASEOUTCUBIC",
    "easeinoutcubic": "EASEINOUTCUBIC",
    "easeinquart": "EASEINQUART",
    "easeoutquart": "EASEOUTQUART",
    "easeinoutquart": "EASEINOUTQUART",
    "easeinquint": "EASEINQUINT",
    "easeoutquint": "EASEOUTQUINT",
    "easeinoutquint": "EASEINOUTQUINT",
    "easeinexpo": "EASEINEXPO",
    "easeoutexpo": "EASEOUTEXPO",
    "easeinoutexpo": "EASEINOUTEXPO",
    "easeincirc": "EASEINCIRC",
    "easeoutcirc": "EASEOUTCIRC",
    "easeinoutcirc": "EASEINOUTCIRC",
    "easeinback": "EASEINBACK",
    "easeoutback": "EASEOUTBACK",
    "easeinoutback": "EASEINOUTBACK",
    "easeinelastic": "EASEINELASTIC",
    "easeoutelastic": "EASEOUTELASTIC",
    "easeinoutelastic": "EASEINOUTELASTIC",
    "easeinbounce": "EASEINBOUNCE",
    "easeoutbounce": "EASEOUTBOUNCE",
    "easeinoutbounce": "EASEINOUTBOUNCE",
    "catmullrom": "CATMULLROM",
    "bezier": "BEZIER",
}

# Pretty strings for Bedrock/PAL animation JSON.  EasingType.fromJson lowercases,
# so either lower or camel works.  Camel is easier to read next to BlockBench.
ANIM_EASING_PRETTY = {
    "linear": "linear",
    "constant": "constant",
    "step": "step",
    "catmullrom": "catmullrom",
    "bezier": "bezier",
    "easeinsine": "easeInSine",
    "easeoutsine": "easeOutSine",
    "easeinoutsine": "easeInOutSine",
    "easeinquad": "easeInQuad",
    "easeoutquad": "easeOutQuad",
    "easeinoutquad": "easeInOutQuad",
    "easeincubic": "easeInCubic",
    "easeoutcubic": "easeOutCubic",
    "easeinoutcubic": "easeInOutCubic",
    "easeinquart": "easeInQuart",
    "easeoutquart": "easeOutQuart",
    "easeinoutquart": "easeInOutQuart",
    "easeinquint": "easeInQuint",
    "easeoutquint": "easeOutQuint",
    "easeinoutquint": "easeInOutQuint",
    "easeinexpo": "easeInExpo",
    "easeoutexpo": "easeOutExpo",
    "easeinoutexpo": "easeInOutExpo",
    "easeincirc": "easeInCirc",
    "easeoutcirc": "easeOutCirc",
    "easeinoutcirc": "easeInOutCirc",
    "easeinback": "easeInBack",
    "easeoutback": "easeOutBack",
    "easeinoutback": "easeInOutBack",
    "easeinelastic": "easeInElastic",
    "easeoutelastic": "easeOutElastic",
    "easeinoutelastic": "easeInOutElastic",
    "easeinbounce": "easeInBounce",
    "easeoutbounce": "easeOutBounce",
    "easeinoutbounce": "easeInOutBounce",
}

@dataclass
class AxisKey:
    tick: float
    value: Any
    easing: str = "linear"
    # Easing args are preserved only when we can carry them in animation JSON.
    easing_args: Optional[Any] = None

@dataclass
class BoneIR:
    position: Dict[str, List[AxisKey]] = field(default_factory=lambda: {"x": [], "y": [], "z": []})
    rotation: Dict[str, List[AxisKey]] = field(default_factory=lambda: {"x": [], "y": [], "z": []})
    scale: Dict[str, List[AxisKey]] = field(default_factory=lambda: {"x": [], "y": [], "z": []})
    bend: Dict[str, List[AxisKey]] = field(default_factory=lambda: {"x": []})

@dataclass
class AnimationIR:
    name: str = "animation"
    length_ticks: float = 0.0
    loop: bool = False
    loop_tick: Optional[float] = None
    bones: Dict[str, BoneIR] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(data: Any, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.write("\n")


def clean_number(x: Any, ndigits: int = 12) -> Any:
    if isinstance(x, float):
        if abs(x) < 1e-12:
            return 0
        y = round(x, ndigits)
        if abs(y - int(y)) < 1e-12:
            return int(y)
        return y
    if isinstance(x, list):
        return [clean_number(v, ndigits) for v in x]
    if isinstance(x, dict):
        return {k: clean_number(v, ndigits) for k, v in x.items()}
    return x


def is_num(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def is_skip_value(x: Any) -> bool:
    return isinstance(x, str) and x in ("pal.skip", "pal.disabled")


def get_correct_player_bone_name(name: str) -> str:
    # UniversalAnimLoader.getCorrectPlayerBoneName:
    # UPPERCASE_PATTERN "([A-Z])" -> "_$1", then lower.
    return re.sub(r"([A-Z])", r"_\1", name).lower()


def restore_player_bone_name(name: str) -> str:
    # UniversalAnimLoader.restorePlayerBoneName
    lower = name.lower()
    return re.sub(r"_(.)", lambda m: m.group(1).upper(), lower)


def default_values(bone: str) -> Tuple[float, float, float]:
    return DEFAULT_VALUES.get(bone, (0.0, 0.0, 0.0))


def normalize_easing(s: Optional[str]) -> str:
    """Mimic PlayerAnimatorLoader.easingTypeFromString + EasingType.fromString.

    First tries exact enum name after lowercasing.  If it would become LINEAR,
    PlayerAnimatorLoader tries "ease" + string.  This makes "InOutQuad" style
    strings resolve as "easeInOutQuad" if provided that way.
    """
    if s is None:
        s = "linear"
    key = str(s).replace("_", "").replace("-", "").lower()
    if key in EASING_NAMES:
        return key
    key2 = "ease" + key
    if key2 in EASING_NAMES:
        return key2
    return "linear"


def easing_for_emote(easing: str) -> str:
    return EASING_NAMES.get(normalize_easing(easing), "LINEAR")


def easing_for_animation(easing: str) -> str:
    return ANIM_EASING_PRETTY.get(normalize_easing(easing), normalize_easing(easing))


def transform_type_for_emote_position(bone_name: str) -> Optional[str]:
    # Java passes TransformType.POSITION only for boneName == "body".
    return "position" if bone_name == "body" else None


def should_negate_for_emote(bone: str, transform: str, axis_index: int, transform_type: Optional[str]) -> bool:
    is_item = bone in ("right_item", "left_item")
    is_cape = bone == "cape"
    is_body = bone == "body"
    if transform == "position":
        if axis_index == 0:
            return is_item or is_cape or is_body
        if axis_index == 1:
            return is_item or transform_type is None or (is_body and transform_type == "rotation")
        if axis_index == 2:
            return (is_item and transform_type == "rotation") or is_cape
    if transform == "rotation":
        if axis_index == 0:
            return is_item or is_cape or is_body
        if axis_index == 1:
            return is_item or transform_type is None or (is_body and transform_type == "rotation")
        if axis_index == 2:
            return (is_item and transform_type == "rotation") or is_cape
    if transform == "scale":
        return False
    if transform == "bend":
        return False
    return False


def convert_emote_to_internal_value(
    bone: str,
    transform: str,
    axis_index: int,
    raw_value: float,
    degrees: bool,
    turn: int = 0,
) -> float:
    """Mirror PlayerAnimatorLoader.convertPlayerAnimValue."""
    transform_type: Optional[str]
    if transform == "position":
        transform_type = transform_type_for_emote_position(bone)
    elif transform == "rotation":
        transform_type = "rotation"
    elif transform == "scale":
        transform_type = "scale"
    elif transform == "bend":
        transform_type = "bend"
    else:
        transform_type = None

    value = float(raw_value)
    defs = default_values(bone)
    if transform_type is None:
        value -= defs[axis_index]
    if should_negate_for_emote(bone, transform, axis_index, transform_type):
        value *= -1
    if transform_type == "rotation":
        if degrees:
            value = math.radians(value)
        value += math.pi * 2.0 * float(turn)
    if transform_type == "position":
        value *= 16.0
    return value


def convert_internal_to_emote_value(
    bone: str,
    transform: str,
    axis_index: int,
    internal_value: Any,
    degrees: bool,
) -> Any:
    """Inverse of convert_emote_to_internal_value for numeric constants."""
    if not is_num(internal_value):
        return internal_value

    transform_type: Optional[str]
    if transform == "position":
        transform_type = transform_type_for_emote_position(bone)
    elif transform == "rotation":
        transform_type = "rotation"
    elif transform == "scale":
        transform_type = "scale"
    elif transform == "bend":
        transform_type = "bend"
    else:
        transform_type = None

    value = float(internal_value)
    if transform_type == "position":
        value /= 16.0
    if transform_type == "rotation":
        # We always emit turn: 0, so remove no full turns.  The caller can choose
        # degrees=True or degrees=False for the emote file.
        if degrees:
            value = math.degrees(value)
    if should_negate_for_emote(bone, transform, axis_index, transform_type):
        value *= -1
    if transform_type is None:
        value += default_values(bone)[axis_index]
    # For BEND, PlayerAnimatorLoader does NOT convert degrees; bend stays raw.
    return value


def ensure_bone(ir: AnimationIR, bone_name: str) -> BoneIR:
    if bone_name not in ir.bones:
        ir.bones[bone_name] = BoneIR()
    return ir.bones[bone_name]


def get_axis_list(bone_ir: BoneIR, transform: str, axis: str) -> List[AxisKey]:
    return getattr(bone_ir, transform)[axis]


def append_axis_key(bone_ir: BoneIR, transform: str, axis: str, tick: float, value: Any, easing: str) -> None:
    lst = get_axis_list(bone_ir, transform, axis)
    lst.append(AxisKey(float(tick), value, normalize_easing(easing)))


def correct_easings_for_axis(keys: List[AxisKey]) -> None:
    """Mirror PlayerAnimatorLoader.correctEasings(List<Keyframe>)."""
    if not keys:
        return
    previous_easing = "easeinoutsine"  # EasingType.EASE_IN_OUT_SINE
    for key in keys:
        cur = key.easing
        key.easing = previous_easing
        previous_easing = cur
    # Source appends a 0.001 tick keyframe at the end carrying the last easing.
    last = keys[-1]
    keys.append(AxisKey(last.tick + EPS_TICK, last.value, previous_easing))


def correct_easings_for_bone(bone: BoneIR) -> None:
    for transform in ANIM_TRANSFORMS:
        stacks = getattr(bone, transform)
        for axis_keys in stacks.values():
            correct_easings_for_axis(axis_keys)


def swap_yz_keyframes_for_items(bone: BoneIR) -> None:
    # PlayerAnimatorLoader.swapTheZYAxis on position and rotation only.
    bone.position["y"], bone.position["z"] = bone.position["z"], bone.position["y"]
    bone.rotation["y"], bone.rotation["z"] = bone.rotation["z"], bone.rotation["y"]


def parse_emote_to_ir(data: Dict[str, Any], name_hint: str = "animation") -> AnimationIR:
    if "emote" not in data:
        raise ValueError("not an emote JSON: missing top-level 'emote'")
    node = data["emote"]
    version = int(data.get("version", 1))
    begin_tick = float(node.get("beginTick", 0))
    end_tick = max(float(node.get("endTick", begin_tick + 1)), begin_tick + 1)
    is_loop = str(node.get("isLoop", "false")).lower() == "true" if isinstance(node.get("isLoop"), str) else bool(node.get("isLoop", False))
    return_tick_raw = int(node.get("returnTick", 0)) if "returnTick" in node else 0
    loop_tick = None
    if is_loop:
        loop_tick = max(return_tick_raw - 1, 0)
    stop_tick = float(node.get("stopTick", 0))
    if not is_loop:
        end_tick = end_tick + 3 if stop_tick <= end_tick else stop_tick

    ir = AnimationIR(
        name=data.get("name", name_hint),
        length_ticks=end_tick,
        loop=is_loop,
        loop_tick=loop_tick,
        metadata={
            "name": data.get("name", name_hint),
            "author": data.get("author", ""),
            "description": data.get("description", ""),
            "version": version,
            "beginTick": begin_tick,
            "sourceEndTick": float(node.get("endTick", end_tick)),
            "stopTick": stop_tick,
            "degrees": bool(node.get("degrees", True)),
            "easeBeforeKeyframe": bool(node.get("easeBeforeKeyframe", False)),
        },
    )

    degrees = bool(node.get("degrees", True))
    moves = list(node.get("moves", []))
    # Java sorts using int tick comparison.  Python sort is stable.
    moves.sort(key=lambda e: int(float(e.get("tick", 0))))

    for obj in moves:
        tick = float(obj.get("tick", 0))
        if tick > end_tick:
            continue
        easing = normalize_easing(obj.get("easing", "linear"))
        turn = int(obj.get("turn", 0))
        for raw_bone_name, part_node in obj.items():
            if raw_bone_name in ("tick", "comment", "easing", "turn"):
                continue
            if not isinstance(part_node, dict):
                continue
            bone_name = get_correct_player_bone_name(raw_bone_name)
            if version < 3 and bone_name == "torso":
                bone_name = "body"
            bone_name = get_correct_player_bone_name(bone_name)
            bone_ir = ensure_bone(ir, bone_name)

            # Position
            for idx, field_name in enumerate(("x", "y", "z")):
                if field_name in part_node:
                    value = convert_emote_to_internal_value(bone_name, "position", idx, part_node[field_name], degrees, turn)
                    append_axis_key(bone_ir, "position", ("x", "y", "z")[idx], tick, value, easing)
            # Rotation
            for idx, field_name in enumerate(("pitch", "yaw", "roll")):
                if field_name in part_node:
                    value = convert_emote_to_internal_value(bone_name, "rotation", idx, part_node[field_name], degrees, turn)
                    append_axis_key(bone_ir, "rotation", ("x", "y", "z")[idx], tick, value, easing)
            # Scale
            for idx, field_name in enumerate(("scaleX", "scaleY", "scaleZ")):
                if field_name in part_node:
                    value = convert_emote_to_internal_value(bone_name, "scale", idx, part_node[field_name], degrees, turn)
                    append_axis_key(bone_ir, "scale", ("x", "y", "z")[idx], tick, value, easing)
            # Bend only uses X in PAL.
            if "bend" in part_node:
                value = convert_emote_to_internal_value(bone_name, "bend", 0, part_node["bend"], degrees, turn)
                append_axis_key(bone_ir, "bend", "x", tick, value, easing)

    # Version<3 body bend is transferred to torso by source.  Other body tracks remain body.
    body = ir.bones.get("body")
    if body and body.bend["x"]:
        torso = ensure_bone(ir, "torso")
        torso.bend["x"].extend(body.bend["x"])
        body.bend["x"].clear()
        if not bone_has_any_keyframes(body):
            ir.bones.pop("body", None)

    if not ir.metadata["easeBeforeKeyframe"]:
        for bone_ir in ir.bones.values():
            correct_easings_for_bone(bone_ir)

    for bone_name, bone_ir in list(ir.bones.items()):
        if bone_name in ("right_item", "left_item"):
            swap_yz_keyframes_for_items(bone_ir)

    return ir


def bone_has_any_keyframes(bone: BoneIR) -> bool:
    for transform in ANIM_TRANSFORMS:
        for axis_keys in getattr(bone, transform).values():
            if axis_keys:
                return True
    return False


def parse_timestamp(s: str) -> float:
    try:
        return float(s)
    except Exception:
        return 0.0


def extract_bedrock_keyframe(keyframe: Any) -> List[Any]:
    # AnimationLoader.extractBedrockKeyframe
    if isinstance(keyframe, list):
        return keyframe
    if is_num(keyframe):
        return [keyframe, 0, 0]
    if not isinstance(keyframe, dict):
        raise ValueError(f"Invalid keyframe data: {keyframe!r}")
    if "vector" in keyframe:
        return keyframe["vector"]
    if "pre" in keyframe:
        val = keyframe["pre"]
        return val if isinstance(val, list) else extract_bedrock_keyframe(val)
    val = keyframe.get("post")
    return val if isinstance(val, list) else extract_bedrock_keyframe(val)


def get_animation_entries(element: Any) -> List[Tuple[float, Any]]:
    """Mirror AnimationLoader.getKeyframes enough for PAL JSON files."""
    if element is None:
        return []
    if is_num(element):
        return [(0.0, [element, element, element])]
    if isinstance(element, list):
        return [(0.0, element)]
    if isinstance(element, dict):
        if "vector" in element:
            return [(0.0, element)]
        if "value" in element:
            obj = copy.deepcopy(element)
            obj["vector"] = [obj["value"], 0, 0]
            return [(0.0, obj)]
        out: List[Tuple[float, Any]] = []
        for key, value in element.items():
            timestamp = parse_timestamp(str(key))
            if isinstance(value, dict):
                value = copy.deepcopy(value)
                if "value" in value:
                    value["vector"] = [value["value"], 0, 0]
                    out.append((timestamp, value))
                    continue
                if "vector" not in value:
                    added = False
                    if "pre" in value:
                        pre_vec = extract_bedrock_keyframe(value["pre"])
                        if "easing" in value:
                            obj = {"vector": pre_vec, "easing": value["easing"]}
                            if "easingArgs" in value:
                                obj["easingArgs"] = value["easingArgs"]
                            out.append((timestamp if timestamp == 0 else timestamp - 0.001, obj))
                        else:
                            out.append((timestamp if timestamp == 0 else timestamp - 0.001, pre_vec))
                        added = True
                    if "post" in value:
                        post_vec = extract_bedrock_keyframe(value["post"])
                        if "lerp_mode" in value:
                            out.append((timestamp, {"vector": post_vec, "easing": value["lerp_mode"]}))
                        else:
                            out.append((timestamp, post_vec))
                        continue
                    if added:
                        continue
                    raise ValueError(f"Invalid keyframe object at {key}: expected vector/value/pre/post")
            out.append((timestamp, value))
        out.sort(key=lambda x: x[0])
        return out
    raise ValueError(f"Invalid keyframe element: {element!r}")


def element_vector_and_easing(element: Any) -> Tuple[List[Any], Dict[str, str], Dict[str, Any]]:
    """Return vector, axis easing map, axis easing args map for AnimationLoader entries."""
    if isinstance(element, list):
        return element, {}, {}
    if isinstance(element, dict):
        vector = element.get("vector")
        if vector is None:
            vector = extract_bedrock_keyframe(element)
        base_easing = normalize_easing(element.get("easing", "linear"))
        easings: Dict[str, str] = {}
        args: Dict[str, Any] = {}
        for axis in ("X", "Y", "Z"):
            key = "easing" + axis
            easings[axis.lower()] = normalize_easing(element.get(key, base_easing))
            arg_key = "easingArgs" + axis
            if arg_key in element:
                args[axis.lower()] = element[arg_key]
        # Generic easingArgs if present.
        if "easingArgs" in element:
            for a in ("x", "y", "z"):
                args.setdefault(a, element["easingArgs"])
        return vector, easings, args
    if is_num(element):
        return [element, element, element], {}, {}
    return [element, element, element], {}, {}


def parse_anim_value_to_internal(value: Any, transform: str) -> Any:
    if is_skip_value(value):
        return value
    is_for_rotation = transform in ("rotation", "bend")
    if is_num(value):
        return math.radians(float(value)) if is_for_rotation else float(value)
    # Strings may be Molang expressions.  We cannot safely invert arbitrary
    # expressions; preserve them as strings.  Numeric strings are treated as
    # constants like MolangLoader would.
    if isinstance(value, str):
        stripped = value.strip()
        try:
            n = float(stripped)
            return math.radians(n) if is_for_rotation else n
        except ValueError:
            return value
    return value


def parse_animations_to_ir(data: Dict[str, Any], animation_name: Optional[str] = None) -> Dict[str, AnimationIR]:
    if "animations" not in data:
        raise ValueError("not a Bedrock/PAL animations JSON: missing top-level 'animations'")
    out: Dict[str, AnimationIR] = {}
    items = data["animations"].items()
    if animation_name:
        if animation_name not in data["animations"]:
            raise KeyError(f"animation {animation_name!r} not found")
        items = [(animation_name, data["animations"][animation_name])]

    for name, anim_obj in items:
        bones_obj = anim_obj.get("bones", {}) or {}
        ir = AnimationIR(name=name)
        if "animation_length" in anim_obj:
            ir.length_ticks = float(anim_obj.get("animation_length", 0)) * 20.0
        # loopTick is in seconds in AnimationLoader.
        if "loopTick" in anim_obj:
            ir.loop = True
            ir.loop_tick = float(anim_obj["loopTick"]) * 20.0
        elif anim_obj.get("loop") is True or str(anim_obj.get("loop", "")).lower() == "true":
            ir.loop = True
            ir.loop_tick = 0.0

        max_tick = 0.0
        for raw_bone_name, entry_obj in bones_obj.items():
            bone_name = get_correct_player_bone_name(raw_bone_name)
            bone_ir = ensure_bone(ir, bone_name)
            for transform in ANIM_TRANSFORMS:
                entries = get_animation_entries(entry_obj.get(transform))
                if not entries:
                    continue
                # Axis vectors: rotation/position/scale are x,y,z; bend only x.
                for timestamp, element in entries:
                    vector, easings, args = element_vector_and_easing(element)
                    # Ensure vector has 3 slots for parser parity.
                    vector = list(vector) + [SKIP, SKIP, SKIP]
                    for idx, axis in enumerate(("x", "y", "z")):
                        if transform == "bend" and axis != "x":
                            continue
                        raw_value = vector[idx]
                        if is_skip_value(raw_value):
                            continue
                        internal = parse_anim_value_to_internal(raw_value, transform)
                        easing = easings.get(axis, "linear") if easings else "linear"
                        key = AxisKey(timestamp * 20.0, internal, normalize_easing(easing), args.get(axis) if args else None)
                        getattr(bone_ir, transform)[axis].append(key)
                        max_tick = max(max_tick, key.tick)
        if not ir.length_ticks:
            ir.length_ticks = max_tick if max_tick else float("inf")
        out[name] = ir
    return out


def value_for_animation_json(value: Any, transform: str) -> Any:
    # AnimationLoader converts numeric rotation and bend constants from degrees
    # to radians.  Therefore output degrees for those transforms.
    if is_num(value):
        if transform in ("rotation", "bend"):
            return clean_number(math.degrees(float(value)))
        return clean_number(float(value))
    return value


def add_initial_default_keys_for_animation(axis_keys: List[AxisKey], transform: str) -> List[AxisKey]:
    if not axis_keys:
        return []
    keys = sorted(axis_keys, key=lambda k: k.tick)
    if keys[0].tick <= 0:
        return keys
    default = 1.0 if transform == "scale" else 0.0
    return [AxisKey(0.0, default, "linear")] + keys


def ir_to_animations_json(ir: AnimationIR, animation_name: Optional[str] = None) -> Dict[str, Any]:
    anim_name = animation_name or ir.name or "animation"
    bones_out: Dict[str, Any] = {}
    for bone_name in sorted(ir.bones.keys()):
        bone_ir = ir.bones[bone_name]
        bone_out: Dict[str, Any] = {}
        for transform in ANIM_TRANSFORMS:
            stacks = getattr(bone_ir, transform)
            active_axes = [a for a, ks in stacks.items() if ks]
            if not active_axes:
                continue
            # Build timestamp -> vector + per-axis easing.
            time_map: Dict[float, Dict[str, Any]] = {}
            for axis in active_axes:
                axis_keys = add_initial_default_keys_for_animation(stacks[axis], transform)
                for k in axis_keys:
                    entry = time_map.setdefault(k.tick, {"vector": [SKIP, SKIP, SKIP], "axis_easing": {}})
                    idx = {"x": 0, "y": 1, "z": 2}[axis]
                    entry["vector"][idx] = value_for_animation_json(k.value, transform)
                    entry["axis_easing"][axis] = k.easing
            transform_out: Dict[str, Any] = {}
            for tick in sorted(time_map.keys()):
                entry = time_map[tick]
                vector = entry["vector"]
                if transform == "bend":
                    # Keep a 3-slot vector so pal.skip can suppress Y/Z.
                    pass
                used = [a for a, v in zip(("x", "y", "z"), vector) if not is_skip_value(v)]
                key_obj: Dict[str, Any] = {"vector": clean_number(vector)}
                # Axis-specific easing when not all active axes share one easing.
                easings = entry["axis_easing"]
                if used:
                    vals = [normalize_easing(easings.get(a, "linear")) for a in used]
                    if len(set(vals)) == 1:
                        if vals[0] != "linear":
                            key_obj["easing"] = easing_for_animation(vals[0])
                    else:
                        for a in used:
                            e = normalize_easing(easings.get(a, "linear"))
                            if e != "linear":
                                key_obj["easing" + a.upper()] = easing_for_animation(e)
                transform_out[format_seconds(tick / 20.0)] = key_obj
            bone_out[transform] = transform_out
        if bone_out:
            bones_out[bone_name] = bone_out

    anim_obj: Dict[str, Any] = {
        "animation_length": clean_number(ir.length_ticks / 20.0),
        "bones": bones_out,
    }
    if ir.loop:
        anim_obj["loop"] = True
        if ir.loop_tick and ir.loop_tick > 0:
            anim_obj["loopTick"] = clean_number(ir.loop_tick / 20.0)
    return {"format_version": "1.8.0", "animations": {anim_name: anim_obj}}


def format_seconds(seconds: float) -> str:
    seconds = clean_number(seconds)
    if isinstance(seconds, int):
        return str(seconds)
    return (f"{seconds:.12f}".rstrip("0").rstrip("."))


def format_tick(tick: float) -> Any:
    tick = clean_number(tick)
    return tick


def split_anim_axis_for_emote_items(bone_name: str, target_transform: str, stacks: Dict[str, List[AxisKey]]) -> Dict[str, List[AxisKey]]:
    # For right_item/left_item, PlayerAnimatorLoader swaps Y/Z AFTER parsing.
    # Therefore animations->emote must pre-swap position and rotation.
    if bone_name not in ("right_item", "left_item") or target_transform not in ("position", "rotation"):
        return stacks
    return {"x": stacks.get("x", []), "y": stacks.get("z", []), "z": stacks.get("y", [])}


def ir_to_emote_json(
    ir: AnimationIR,
    name: Optional[str] = None,
    author: str = "",
    description: str = "",
    degrees: bool = False,
    version: int = 3,
    ease_before_keyframe: bool = True,
) -> Dict[str, Any]:
    """Export internal animation as PAL emote JSON.

    For source-exact animations -> emote conversion, easeBeforeKeyframe=true is
    the safest default because AnimationLoader stores the easing on the segment
    ending at a keyframe.  With easeBeforeKeyframe=false, PlayerAnimatorLoader
    shifts easings and appends extra frames.
    """
    moves: List[Dict[str, Any]] = []

    for bone_name in sorted(ir.bones.keys()):
        bone_ir = ir.bones[bone_name]
        emote_bone_name = restore_player_bone_name(bone_name)
        for transform in ANIM_TRANSFORMS:
            raw_stacks = getattr(bone_ir, transform)
            stacks = split_anim_axis_for_emote_items(bone_name, transform, raw_stacks)
            axis_fields = TRANSFORM_AXES[transform]
            axes = ["x"] if transform == "bend" else ["x", "y", "z"]
            for axis_index, axis in enumerate(axes):
                if axis not in stacks:
                    continue
                field_name = axis_fields[axis_index]
                for key in sorted(stacks[axis], key=lambda k: k.tick):
                    # Skip synthetic zero-length defaults generated for animations JSON.
                    # Real t=0 non-default values must be kept.
                    default_internal = 1.0 if transform == "scale" else 0.0
                    if abs(key.tick) < 1e-9 and is_num(key.value) and abs(float(key.value) - default_internal) < 1e-9:
                        continue
                    val = convert_internal_to_emote_value(bone_name, transform, axis_index, key.value, degrees)
                    move = {
                        "tick": format_tick(key.tick),
                        "easing": easing_for_emote(key.easing),
                        "turn": 0,
                        emote_bone_name: {field_name: clean_number(val)},
                    }
                    moves.append(move)

    moves.sort(key=lambda m: (float(m.get("tick", 0)), list(m.keys())[-1], list(m[list(m.keys())[-1]].keys())[0]))

    # Choose sensible emote timing.  begin/end are metadata for emote; PAL uses
    # stopTick to lengthen PLAY_ONCE animations.
    end_tick = ir.length_ticks
    if math.isinf(end_tick):
        end_tick = 0.0
    emote_obj: Dict[str, Any] = {
        "isLoop": "true" if ir.loop else "false",
        "returnTick": int((ir.loop_tick or 0) + 1) if ir.loop else 2,
        "beginTick": 0,
        "endTick": clean_number(end_tick if ir.loop else max(0.0, end_tick - 3.0)),
        "stopTick": clean_number(end_tick),
        "degrees": bool(degrees),
        "moves": moves,
    }
    if ease_before_keyframe:
        emote_obj["easeBeforeKeyframe"] = True
    out: Dict[str, Any] = {
        "version": int(version),
        "name": name or ir.metadata.get("name") or ir.name or "animation",
        "author": author if author != "" else ir.metadata.get("author", ""),
        "description": description if description != "" else ir.metadata.get("description", ""),
        "emote": emote_obj,
    }
    return out


def compare_ir_sample_points(a: AnimationIR, b: AnimationIR, tolerance: float = 1e-6) -> Tuple[bool, List[str]]:
    """Lightweight structural comparison used by validation commands.

    It compares end ticks/value/easing per axis after dropping synthetic t=0
    default keys that are only needed by AnimationLoader to reproduce emote's
    start-from-default behavior.
    """
    errors: List[str] = []
    bones = sorted(set(a.bones) | set(b.bones))
    for bone in bones:
        ba = a.bones.get(bone)
        bb = b.bones.get(bone)
        if ba is None or bb is None:
            errors.append(f"bone mismatch: {bone}")
            continue
        for transform in ANIM_TRANSFORMS:
            sa = getattr(ba, transform)
            sb = getattr(bb, transform)
            for axis in sorted(set(sa.keys()) | set(sb.keys())):
                ka = normalize_key_list_for_compare(sa.get(axis, []), transform)
                kb = normalize_key_list_for_compare(sb.get(axis, []), transform)
                if len(ka) != len(kb):
                    errors.append(f"{bone}.{transform}.{axis}: key count {len(ka)} != {len(kb)}")
                    continue
                for i, (x, y) in enumerate(zip(ka, kb)):
                    if abs(x.tick - y.tick) > tolerance:
                        errors.append(f"{bone}.{transform}.{axis}[{i}]: tick {x.tick} != {y.tick}")
                    if is_num(x.value) and is_num(y.value):
                        if abs(float(x.value) - float(y.value)) > tolerance:
                            errors.append(f"{bone}.{transform}.{axis}[{i}]: value {x.value} != {y.value}")
                    elif x.value != y.value:
                        errors.append(f"{bone}.{transform}.{axis}[{i}]: value {x.value!r} != {y.value!r}")
                    if normalize_easing(x.easing) != normalize_easing(y.easing):
                        errors.append(f"{bone}.{transform}.{axis}[{i}]: easing {x.easing} != {y.easing}")
    return not errors, errors


def normalize_key_list_for_compare(keys: List[AxisKey], transform: str) -> List[AxisKey]:
    default = 1.0 if transform == "scale" else 0.0
    out = []
    for k in keys:
        if abs(k.tick) < 1e-9 and is_num(k.value) and abs(float(k.value) - default) < 1e-9:
            continue
        out.append(k)
    return out
