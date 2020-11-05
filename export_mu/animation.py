# vim:ts=4:et
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
from mathutils import Vector, Quaternion

from ..mu import MuAnimation, MuClip, MuCurve, MuKey
from ..utils import strip_nnn

from .light import light_types

def shader_animations(mat, path):
    """
    Shader animation

    Args:
        mat: (array): write your description
        path: (str): write your description
    """
    animations = {}
    if not mat.animation_data:
        return animations
    for track in mat.animation_data.nla_tracks:
        if not track.strips:
            continue
        anims = []
        strip = track.strips[0]
        for curve in strip.action.fcurves:
            dp = curve.data_path.split(".")
            if dp[0] == "mumatprop" and dp[1] in ["color", "vector", "float2", "float3"]:
                anims.append((track, path, mat))
                break
            elif dp[0] == "mumatprop" and dp[1] == "texture":
                print("don't know how to export texture anims")
        if anims:
            animations[track.name] = anims
    return animations

def object_animations(obj, path):
    """
    Return a dictionary of an object

    Args:
        obj: (todo): write your description
        path: (str): write your description
    """
    animations = {}
    typ = "obj"
    if type(obj) in light_types:
        typ = "lit"
    elif type(obj.data) == bpy.types.Armature:
        print(obj.name)
        typ = "arm"
    if obj.animation_data:
        for track in obj.animation_data.nla_tracks:
            if track.strips:
                animations[track.name] = [(track, path, typ)]
        # if nla_tracks exist, then action will be an nla track that has been
        # opened for tweaking, so export action only if there are no nla tracks
        if not animations and obj.animation_data.action:
            action = obj.animation_data.action
            animations[action.name] = [(action, path, typ)]
    return animations

def extend_animations(animations, anims):
    """
    Extend histogram with new histogram.

    Args:
        animations: (todo): write your description
        anims: (int): write your description
    """
    for a in anims:
        if a not in animations:
            animations[a] = []
        animations[a].extend(anims[a])

def collect_animations(obj, path=""):
    """
    Collect all animation.

    Args:
        obj: (todo): write your description
        path: (str): write your description
    """
    animations = {}
    if path:
        path += "/"
    path += strip_nnn(obj.name)
    extend_animations(animations, object_animations (obj, path))
    if type(obj.data) == bpy.types.Mesh:
        for mat in obj.data.materials:
            if mat: # material slot may be empty
                extend_animations(animations, shader_animations(mat, path))
    if type(obj.data) in light_types:
        extend_animations(animations, object_animations (obj.data, path))
    for o in obj.children:
        extend_animations(animations, collect_animations(o, path))
    return animations

def find_path_root(animations):
    """
    Find the root path of the given animation.

    Args:
        animations: (todo): write your description
    """
    paths = {}
    for clip in animations:
        for data in animations[clip]:
            objects = data[1].split("/")
            p = paths
            for o in objects:
                if not o in p:
                    p[o] = {}
                p = p[o]
            # flag the path as having animation data so that the first object
            # with animation data is found when all objects form a vine
            # instead of a tree
            p[None] = {}
    path_root = ""
    p = paths
    while len(p) == 1:
        o = list(p)[0]
        if o == None:
            break
        if path_root:
            path_root += "/"
        path_root += o
        p = p[o]
    return path_root

def make_key(key, mult):
    """
    Creates a new key.

    Args:
        key: (str): write your description
        mult: (todo): write your description
    """
    fps = bpy.context.scene.render.fps
    mukey = MuKey()
    x, y = key.co
    mukey.time = (x - bpy.context.scene.frame_start) / fps
    mukey.value = y * mult
    dx, dy = key.handle_left
    dx = (x - dx) / fps
    dy = (y - dy) * mult
    t1 = dy / dx
    dx, dy = key.handle_right
    dx = (dx - x) / fps
    dy = (dy - y) * mult
    t2 = dy / dx
    mukey.tangent = [t1, t2]
    mukey.tangentMode = 0
    return mukey

property_map = {
    "location":(
        ("m_LocalPosition.x", 1, 0),
        ("m_LocalPosition.z", 1, 0),
        ("m_LocalPosition.y", 1, 0),
    ),
    "rotation_quaternion":(
        ("m_LocalRotation.w", 1, 0),
        ("m_LocalRotation.x", -1, 0),
        ("m_LocalRotation.z", -1, 0),
        ("m_LocalRotation.y", -1, 0),
    ),
    "scale":(
        ("m_LocalScale.x", 1, 0),
        ("m_LocalScale.z", 1, 0),
        ("m_LocalScale.y", 1, 0),
    ),
    "color":(
        ("m_Color.r", 1, 2),
        ("m_Color.g", 1, 2),
        ("m_Color.b", 1, 2),
        ("m_Color.a", 1, 2),#probably not used
    ),
    "energy":(
        ("m_Intensity", 1, 2),
    ),
}

vector_map={
    "color": (".r", ".g", ".b", ".a"),
    "vector": (".x", ".y", ".z", ".w"),
}

def make_curve(mu, muobj, curve, path, typ):
    """
    R creates curve

    Args:
        mu: (todo): write your description
        muobj: (todo): write your description
        curve: (todo): write your description
        path: (str): write your description
        typ: (str): write your description
    """
    mucurve = MuCurve()
    mucurve.path = path
    if typ in {"obj", "lit"}:
        property, mult, ctyp = property_map[curve.data_path][curve.array_index]
    elif typ == "arm":
        if "." in curve.data_path:
            bpath, dpath = curve.data_path.rsplit(".", 1)
            bone_path = muobj.bone_paths[bpath]
            bone = mu.object_paths[bone_path]
            bone_path = bone_path[len(muobj.path):]
            if bone_path[0] == '/':
                bone_path = bone_path[1:]
            if path and path[-1:] != "/":
                path = path + "/"
            mucurve.path = path + bone_path
            print(mucurve.path)
            property, mult, ctyp  = property_map[dpath][curve.array_index]
            if not hasattr(bone, "curves"):
                bone.curves = {}
            if dpath not in bone.curves:
                bone.curves[dpath] = [None] * len(property_map[dpath])
            bone.curves[dpath][curve.array_index] = mucurve
            muobj.animated_bones.add(bone)
        else:
            dp = curve.data_path
            ai = curve.array_index
            property, mult, ctyp = property_map[dp][ai]
    elif type(typ) == bpy.types.Material:
        dp = curve.data_path.split(".")
        v = {}
        str = "v['property'] = typ.%s.name" % (".".join(dp[:-1]))
        exec (str, {}, locals())
        property = v["property"]
        mult = 1
        if dp[1] in ["color", "vector"]:
            property += vector_map[dp[1]][curve.array_index]
        ctyp = 1
    mucurve.property = property
    # 0 = transform, 1 = material, 2 = light, 3 = audio source
    mucurve.type = ctyp
    mucurve.wrapMode = (8, 8)
    mucurve.keys = []
    for key in curve.keyframe_points:
        mucurve.keys.append(make_key(key, mult))
    return mucurve

def transform_curves(muarm):
    """
    Calculate the current transformation matrix

    Args:
        muarm: (array): write your description
    """
    for bone in muarm.animated_bones:
        if "location" in bone.curves:
            location = bone.curves["location"]
            if None in location:
                print("Skipping incomplete location curve set")
            elif ((len(location[0].keys) != len(location[1].keys))
                  or (len(location[0].keys) != len(location[2].keys))):
                print("Skipping mismatched location fcurve set")
            else:
                for i in range(len(location[0].keys)):
                    xk = location[0].keys[i].value
                    yk = location[1].keys[i].value
                    zk = location[2].keys[i].value
                    loc = Vector((xk, yk, zk))
                    loc += bone.transform.localPosition
                    location[0].keys[i].value = loc.x
                    location[1].keys[i].value = loc.y
                    location[2].keys[i].value = loc.z
        if "rotation_quaternion" in bone.curves:
            rotation = bone.curves["rotation_quaternion"]
            if None in rotation:
                print("Skipping incomplete rotation fcurve set")
            elif ((len(rotation[0].keys) != len(rotation[1].keys))
                  or (len(rotation[0].keys) != len(rotation[2].keys))
                  or (len(rotation[0].keys) != len(rotation[3].keys))):
                print("Skipping mismatched rotation fcurve set")
            else:
                lrot = bone.transform.localRotation
                for i in range(len(rotation[0].keys)):
                    # the keys are already left-handled, but the array
                    # order is wxzy
                    wk = rotation[0].keys[i].value
                    xk = -rotation[1].keys[i].value
                    yk = -rotation[2].keys[i].value
                    zk = -rotation[3].keys[i].value
                    rot = Quaternion((wk, xk, yk, zk))
                    rot = lrot @ rot
                    # the keys are already left-handled, but the array
                    # order is wxzy
                    rotation[0].keys[i].value = rot.w
                    rotation[1].keys[i].value = -rot.x
                    rotation[2].keys[i].value = -rot.y
                    rotation[3].keys[i].value = -rot.z
                    for j in range(2):
                        # the keys are already left-handled, but the array
                        # order is wxzy
                        wk = rotation[0].keys[i].tangent[j]
                        xk = -rotation[1].keys[i].tangent[j]
                        yk = -rotation[2].keys[i].tangent[j]
                        zk = -rotation[3].keys[i].tangent[j]
                        tan = Quaternion((wk, xk, yk, zk))
                        tan = lrot @ tan
                        # the keys are already left-handled, but the array
                        # order is wxzy
                        rotation[0].keys[i].tangent[j] = tan.w
                        rotation[1].keys[i].tangent[j] = -tan.x
                        rotation[2].keys[i].tangent[j] = -tan.y
                        rotation[3].keys[i].tangent[j] = -tan.z

def make_animations(mu, animations, anim_root):
    """
    Creates an animation for each animation

    Args:
        mu: (todo): write your description
        animations: (todo): write your description
        anim_root: (todo): write your description
    """
    anim = MuAnimation()
    anim.clip = ""
    anim.autoPlay = False
    for clip_name in animations:
        clip = MuClip()
        if not anim.clip:   #FIXME how to select when multiple?
            anim.clip = clip_name
        clip.name = clip_name
        clip.lbCenter = (0, 0, 0)
        clip.lbSize = (0, 0, 0)
        clip.wrapMode = 0   #FIXME
        for data in animations[clip_name]:
            track, path, typ = data
            muobj = mu.object_paths[path]
            path = path[len(anim_root) + 1:]
            if type(track) is bpy.types.Action:
                action = track
            else:
                action = track.strips[0].action
            for curve in action.fcurves:
                clip.curves.append(make_curve(mu, muobj, curve, path, typ))
            if hasattr(muobj, "animated_bones"):
                transform_curves(muobj)
        anim.clips.append(clip)
    return anim
