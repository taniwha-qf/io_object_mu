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

import sys, traceback
from struct import unpack
from pprint import pprint

import bpy
from mathutils import Vector
from bpy.props import BoolProperty, StringProperty
from bpy.props import CollectionProperty
from bpy.props import FloatVectorProperty, IntProperty

def texture_update_mapping(self, context):
    """
    Update the texture mapping

    Args:
        self: (todo): write your description
        context: (todo): write your description
    """
    if not hasattr(context, "material") or not context.material:
        return
    mat = context.material
    #sel_name = "%s.%s:select" % (mat.name, self.name)
    nodes = mat.node_tree.nodes
    scale = Vector(self.scale)
    offset = Vector(self.offset)
    if self.name in nodes:
        if self.tex in bpy.data.images:
            img = bpy.data.images[self.tex]
            if img.muimageprop.invertY:
                scale.y *= -1
                offset.y = 1 - offset.y
        nodes[self.name].texture_mapping.translation.xy = offset
        nodes[self.name].texture_mapping.scale.xy = scale
    #if sel_name in nodes:
    #    nodes[sel_name].inputs[0].default_value = float(self.rgbNorm)

def texture_update_tex(self, context):
    """
    Updates a texture

    Args:
        self: (todo): write your description
        context: (todo): write your description
    """
    if not hasattr(context, "material") or not context.material:
        return
    mat = context.material
    nodes = mat.node_tree.nodes
    if self.name in nodes and self.tex in bpy.data.images:
        nodes[self.name].image = bpy.data.images[self.tex]
        nodes[self.name].image.colorspace_settings.is_data = self.type

class MuTextureProperties(bpy.types.PropertyGroup):
    tex: StringProperty(name="tex", update=texture_update_tex)
    type: BoolProperty(name="type", description="Texture is a normal map", default = False, update=texture_update_tex)
    rgbNorm: BoolProperty(name="RGB Normal", description="Texture is RGB rather than GA (blender shader control, not exported)", update=texture_update_mapping)
    scale: FloatVectorProperty(name="scale", size = 2, subtype='XYZ', default = (1.0, 1.0), update=texture_update_mapping)
    offset: FloatVectorProperty(name="offset", size = 2, subtype='XYZ', default = (0.0, 0.0), update=texture_update_mapping)

class MuMaterialTexturePropertySet(bpy.types.PropertyGroup):
    bl_label = "Textures"
    properties: CollectionProperty(type=MuTextureProperties, name="Textures")
    index: IntProperty()
    expanded: BoolProperty()

    def draw_item(self, layout):
        """
        Draw the item

        Args:
            self: (todo): write your description
            layout: (str): write your description
        """
        item = self.properties[self.index]
        row = layout.row()
        col = row.column()
        col.prop(item, "name", text="Name")
        r = col.row()
        r.prop(item, "tex", text="")
        r.prop(item, "type", text="")
        r.prop(item, "rgbNorm", text="")
        col.prop(item, "scale", text="")
        col.prop(item, "offset", text="")

classes_to_register = (
    MuTextureProperties,
    MuMaterialTexturePropertySet,
)
