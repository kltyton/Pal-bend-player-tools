import bpy
from bpy_extras import anim_utils
import os

emoteName = "name"
emoteDescription = "description"
author = "Your name"

#You can set here the emote's parameters
#SAVE before edit! Blender can crash



#Looping: Don't use capitals
isLoop = "false"
returnTick = "2"


#DON'T EDIT THE SCRIPT BELOW
#unless you know, what are you doing











class static:
    movesText = ''
    first = True

#This is a debug function. is not used.
def Key_Frame_Points(): #Gets the key-frame values as an array.
    KEYFRAME_POINTS_ARRAY = []
    fcurves = anim_utils.action_get_channelbag_for_slot(bpy.context.active_object.animation_data.action, "Legacy Slot").fcurves

    for curve in fcurves:
        keyframePoints = curve.keyframe_points
        for keyframe in keyframePoints:
            print('KEY FRAME POINTS ARE frame:{} value:{}'.format(keyframe.co[0],keyframe.co[1]))
            KEYFRAME_POINTS_ARRAY.append(keyframe.co[1])
            


def getPartData(name: str, isItem: bool = False):
    obj = bpy.data.objects.get(name)
    if obj is None:
        print("[WARN] Missing object: {}".format(name))
        return

    fcurves = getObjectFCurves(obj)

    for fcurve in fcurves:
        isLocation = fcurve.data_path == 'location'
        if not isLocation and fcurve.data_path != 'rotation_euler':
            continue

        if isLocation:
            if fcurve.array_index == 0:
                typ = 'x'
            elif (fcurve.array_index == 1) != isItem:
                typ = 'z'  # Blender 里 Z 是向上，MC 里 Y 是向上
            else:
                typ = 'y'
        else:
            if fcurve.array_index == 0:
                typ = 'pitch'
            elif (fcurve.array_index == 1) != isItem:
                typ = 'roll'
            else:
                typ = 'yaw'

        for keyframe in fcurve.keyframe_points:
            if int(keyframe.co[0]) == 0:
                continue

            if static.first:
                static.movesText = getTickData(name, typ, keyframe, isLocation, isItem)
                static.first = False
            else:
                static.movesText = '{},{}'.format(
                    static.movesText,
                    getTickData(name, typ, keyframe, isLocation, isItem)
                )

    if name == "head" or name == "leftItem" or name == "rightItem":
        return  # Don't read bend from the head/items

    bend_name = name + "_bend"
    bend_obj = bpy.data.objects.get(bend_name)
    if bend_obj is None:
        return

    bend_fcurves = getObjectFCurves(bend_obj)

    for fcurve in bend_fcurves:
        if fcurve.data_path == 'rotation_euler' and fcurve.array_index == 0:
            for keyframe in fcurve.keyframe_points:
                if int(keyframe.co[0]) == 0:
                    continue

                if static.first:
                    static.movesText = getTickData(name, "bend", keyframe, False)
                    static.first = False
                else:
                    static.movesText = '{},{}'.format(
                        static.movesText,
                        getTickData(name, "bend", keyframe, False)
                    )
                    
    
def getObjectFCurves(obj):
    if obj is None:
        return []

    anim_data = obj.animation_data
    if anim_data is None:
        return []

    action = anim_data.action
    if action is None:
        return []

    # Blender <= 4.3 / 部分 4.4 兼容旧 API
    legacy_fcurves = getattr(action, "fcurves", None)
    if legacy_fcurves is not None:
        return legacy_fcurves

    # Blender 4.4+ / 5.0 新 API：Action Slot -> Channelbag -> FCurves
    action_slot = getattr(anim_data, "action_slot", None)

    if action_slot is None:
        slots = getattr(action, "slots", None)
        if slots is not None and len(slots) == 1:
            action_slot = slots[0]
        else:
            print("[WARN] Object '{}' has no action_slot, cannot read slotted Action '{}'".format(
                obj.name, action.name
            ))
            return []

    # 优先使用 Blender 提供的工具函数
    try:
        from bpy_extras import anim_utils
        getter = getattr(anim_utils, "action_get_channelbag_for_slot", None)
        if getter is not None:
            channelbag = getter(action, action_slot)
            if channelbag is not None:
                return channelbag.fcurves
    except Exception:
        pass

    # 手动兼容路径：action.layers -> strips -> channelbag(slot) -> fcurves
    layers = getattr(action, "layers", [])
    for layer in layers:
        for strip in getattr(layer, "strips", []):
            if not hasattr(strip, "channelbag"):
                continue

            channelbag = None
            try:
                channelbag = strip.channelbag(action_slot)
            except TypeError:
                try:
                    channelbag = strip.channelbag(action_slot, ensure=False)
                except Exception:
                    channelbag = None
            except Exception:
                channelbag = None

            if channelbag is not None:
                return channelbag.fcurves

    return []
    
def getTickData(name:str, typ:str, keyframe, isL:bool, endTick:list[int], isItem:bool = False):
    turn = 0
    tick = int(keyframe.co[0])
    value = keyframe.co[1] #calculate correct
    if (tick > endTick[0]):
        endTick[0] = tick

    ## Find easing
    if(keyframe.easing == "AUTO"):
        easing = "EASEINOUT"
    else:
        easing = ''.join(keyframe.easing.split('_'))
    if(keyframe.interpolation == "BEZIER"):
        easing = easing + "QUAD"
    else:
        if(not (keyframe.interpolation == 'CONSTANT' or keyframe.interpolation == 'LINEAR')):
            easing = easing + str(keyframe.interpolation)
        else:
            easing = str(keyframe.interpolation)
       
    ## Location correction 
    #Head y correction
    if(name == 'head' and typ == 'y'):
        value -= 3
    
    if(isL):
        if(not name == 'torso'):
            value = value * 4
            if (not isItem):
                value = value * -1
        else:
            value = value * 0.25
            if(typ == 'z'):
                value = value * -1
    elif isItem:
        pass
    elif(not (name == 'torso' and not (typ == 'roll' or typ == 'bend'))) and not "scale" in typ: # rotation correction (*-1) except for torzo roll/bend
        value = value * -1
    
    if(typ == 'y'):
        if(name == "rightLeg" or name == "leftLeg"):
            value += 12
    if(typ == 'z' or typ == 'x'):
        if(name == "rightLeg"):
            value += 0.1
        elif(name == "leftLeg"):
            value -= 0.1
    
    if(name == 'rightArm' or name == 'leftArm'):
        if typ == 'y':
            value += 12
    
    text = '''
            {{
                "tick":{:d},
                "easing": "{}",
                "turn": {:d},
                "{}":{{
                    "{}":{}
                }}
            }}'''.format(tick, easing, turn, name, typ, value)
    return text

endTick = [0]

getPartData("head", endTick)
getPartData("torso", endTick)
getPartData("rightArm", endTick)
getPartData("leftArm", endTick)
getPartData("rightLeg", endTick)
getPartData("leftLeg", endTick)
getPartData("rightItem", endTick, True)
getPartData("leftItem", endTick, True)

emoteString = '''{{
    "name": "{}",
    "author": "{}",
    "description": "{}",
    "emote":{{
        "isLoop": "{}",
        "returnTick": {},
        "beginTick":{},
        "endTick":{},
        "stopTick":{},
        "degrees":false,
        "moves":[
            {}
        ]
    }}
}}'''.format(emoteName, author, emoteDescription, isLoop, returnTick, bpy.context.scene.frame_start, endTick[0], bpy.context.scene.frame_end + 1, static.movesText)

x = open(os.path.join(os.path.dirname(bpy.data.filepath), "emote.json"), "w")
x.write(emoteString)
x.close()
 