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
from bpy.props import BoolProperty, FloatProperty
from bpy.props import CollectionProperty
from bpy.props import IntProperty

def float3_update(self, context):
    """
    Update the graph3 output.

    Args:
        self: (todo): write your description
        context: (todo): write your description
    """
    if not hasattr(context, "material") or not context.material:
        return
    mat = context.material
    nodes = mat.node_tree.nodes
    if self.name in nodes:
        nodes[self.name].outputs[0].default_value = self.value

class MuFloat3Prop(bpy.types.PropertyGroup):
    value: FloatProperty(name="", update=float3_update)

class MuMaterialFloat3PropertySet(bpy.types.PropertyGroup):
    bl_label = "Float3"
    properties: CollectionProperty(type=MuFloat3Prop, name="Float3")
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
    MuFloat3Prop,
    MuMaterialFloat3PropertySet,
)
