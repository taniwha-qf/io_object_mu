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
import os
from math import pi

import bpy
from mathutils import Vector, Quaternion

from ..import_mu import import_mu
from ..cfgnode import parse_vector
from ..utils import util_collection

def compile_model(db, path, type, name, cfg, collection):
    """
    Compile a model.

    Args:
        db: (todo): write your description
        path: (str): write your description
        type: (str): write your description
        name: (str): write your description
        cfg: (todo): write your description
        collection: (str): write your description
    """
    nodes = cfg.GetNodes("MODEL")
    model = bpy.data.collections.new(f"{name}:{type}model")
    if nodes:
        root = bpy.data.objects.new(name+":model", None)
        model.objects.link(root)
        for n in nodes:
            submodelname = n.GetValue("model")
            position = Vector((0, 0, 0))
            rotation = Vector((0, 0, 0))
            scale = Vector((1, 1, 1))
            if n.HasValue("position"):
                position = parse_vector(n.GetValue("position"))
            if n.HasValue("rotation"):
                rotation = parse_vector(n.GetValue("rotation"))
            if n.HasValue("scale"):
                scale = parse_vector(n.GetValue("scale"))
            mdl = db.model(submodelname)
            obj = mdl.instantiate(f"{name}:submodel", position, rotation, scale)
            model.objects.link(obj)
            obj.parent = root
    else:
        mesh = db.model_by_path[path][0]
        url = '/'.join((path, mesh))
        submodel = db.model(url)
        position = Vector((0, 0, 0))
        rotation = Vector((0, 0, 0))
        scale = Vector((1, 1, 1))
        root = submodel.instantiate(f"{name}:submodel", position, rotation, scale)
        model.objects.link(root)
    collection.children.link(model)
    model.mumodelprops.name = name
    model.mumodelprops.type = type
    return model

def loaded_models_collection():
    """
    Return a list of all models.

    Args:
    """
    return util_collection("loaded_models")

def instantiate_model(model, name, loc, rot, scale):
    """
    Create a new quaternion

    Args:
        model: (todo): write your description
        name: (str): write your description
        loc: (todo): write your description
        rot: (todo): write your description
        scale: (float): write your description
    """
    obj = bpy.data.objects.new(name, None)
    obj.instance_type = 'COLLECTION'
    obj.instance_collection = model
    obj.location = loc
    obj.scale = scale
    if type(rot) == Vector:
        # blender is right-handed, KSP is left-handed
        # FIXME: it might be better to convert the given euler rotation
        # to a quaternion (for consistency)
        # this assumes the rot vector came straight from a ksp cfg file
        # Unity's rotation order is ZXY, which makes it YXZ for blender
        obj.rotation_mode = 'YXZ'
        obj.rotation_euler = -rot.xzy * pi / 180
    else:
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = rot
    return obj

class Model:
    @classmethod
    def Preloaded(cls):
        """
        Return a dictionary of pre - registered pre - pre - pre - preloaded.

        Args:
            cls: (todo): write your description
        """
        preloaded = {}
        for g in bpy.data.collections:
            if g.name[:6] == "model:":
                url = g.name[6:]
                preloaded[url] = Model(None, url)
        return preloaded
    def __init__(self, path, url):
        """
        Initialize a quaternion.

        Args:
            self: (todo): write your description
            path: (str): write your description
            url: (str): write your description
        """
        modelname = "model:" + url
        print(modelname)
        loaded_models = loaded_models_collection()
        if modelname in loaded_models:
            model = loaded_models[modelname]
        else:
            model = bpy.data.collections.new(modelname)
            loaded_models.children.link(model)
            obj, mu = import_mu(model, path, False, False)
            obj.location = Vector((0, 0, 0))
            obj.rotation_quaternion = Quaternion((1,0,0,0))
            obj.scale = Vector((1,1,1))
        self.model = model
    def instantiate(self, name, loc, rot, scale):
        """
        Instantiates a model from the model.

        Args:
            self: (todo): write your description
            name: (str): write your description
            loc: (todo): write your description
            rot: (todo): write your description
            scale: (float): write your description
        """
        return instantiate_model(self.model, name, loc, rot, scale)
