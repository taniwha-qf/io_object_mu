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
from bpy.props import BoolProperty
from bpy.props import CollectionProperty
from bpy.props import FloatVectorProperty, IntProperty

def color_update(self, context):
    """
    Updates the color matrix.

    Args:
        self: (todo): write your description
        context: (todo): write your description
    """
    if not hasattr(context, "material") or not context.material:
        return
    mat = context.material
    nodes = mat.node_tree.nodes
    if self.name in nodes:
        nodes[self.name].inputs[0].default_value = self.value
        nodes[self.name].inputs[1].default_value = self.value[3]

class MuColorProp(bpy.types.PropertyGroup):
    value: FloatVectorProperty(name="", size = 4, subtype='COLOR', min = 0.0, max = 1.0, default = (1.0, 1.0, 1.0, 1.0), update=color_update)

class MuMaterialColorPropertySet(bpy.types.PropertyGroup):
    bl_label = "Colors"
    properties: CollectionProperty(type=MuColorProp, name="Colors")
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
        col.prop(item, "value", text="")

classes_to_register = (
    MuColorProp,
    MuMaterialColorPropertySet,
)
