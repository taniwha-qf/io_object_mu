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
from bpy.props import BoolProperty, FloatProperty, StringProperty, EnumProperty
from bpy.props import PointerProperty
from bpy.props import FloatVectorProperty, IntProperty

class MuSpringProp(bpy.types.PropertyGroup):
    spring: FloatProperty(name = "Spring")
    damper: FloatProperty(name = "Damper")
    targetPosition: FloatProperty(name = "Target")

    def draw(self, context, layout):
        """
        Draws the layout

        Args:
            self: (todo): write your description
            context: (dict): write your description
            layout: (str): write your description
        """
        row = layout.row()
        col = row.column()
        col.prop(self, "spring")
        col.prop(self, "damper")
        col.prop(self, "targetPosition")

class MuFrictionProp(bpy.types.PropertyGroup):
    extremumSlip: FloatProperty(name = "Slip")
    extremumValue: FloatProperty(name = "Value")
    asymptoteSlip: FloatProperty(name = "Slip")
    asymptoteValue: FloatProperty(name = "Value")
    stiffness: FloatProperty(name = "Stiffness")

    def draw(self, context, layout):
        """
        Draws the layout

        Args:
            self: (todo): write your description
            context: (dict): write your description
            layout: (str): write your description
        """
        row = layout.row()
        col = row.column()
        col.label(text="Extremum")
        col.prop(self, "extremumSlip")
        col.prop(self, "extremumValue")
        col.label(text="Asymptote")
        col.prop(self, "asymptoteSlip")
        col.prop(self, "asymptoteValue")
        col.separator()
        col.prop(self, "stiffness")

dir_map = {
    'MU_X':0,
    'MU_Y':2,   # unity is LHS, blender is RHS
    'MU_Z':1,   # unity is LHS, blender is RHS
    0:'MU_X',
    2:'MU_Y',   # unity is LHS, blender is RHS
    1:'MU_Z',   # unity is LHS, blender is RHS
}

dir_items = (
    ('MU_X', "X", ""),
    ('MU_Y', "Y", ""),
    ('MU_Z', "Z", ""),
)

modelType_items = (
    ('NONE', "None", "Nothing is assumed about the object and its descendants unless specified otherwise by an ancestral object."),
    ('PART', "Part", "The object and its descendants form a KSP part model. Only the first \"Internal Space\" descendant object is special."),
    ('PROP', "Prop", "The object and its descendants form a KSP prop model. No descendant objects are special."),
    ('INTERNAL', "Internal Space", "The object and its descendants form a KSP internal space model. Only \"Prop\" descendant objects are special."),
    ('STATIC', "KK Static", "The object and its descendants form a Kerbal Konstructs static model. No descendant objects are special."),
    ('VOLUME', "Volume", "The object and its descendants are used for volume calcuations and are NOT exported. Use Tag to specify the volume group (may be any name, not limited to valid KSP tags) which can then be accessed in cfg template expressions."),
)
collider_items = (
    ('MU_COL_NONE', "", ""),
    ('MU_COL_MESH', "Mesh", ""),
    ('MU_COL_SPHERE', "Sphere", ""),
    ('MU_COL_CAPSULE', "Capsule", ""),
    ('MU_COL_BOX', "Box", ""),
    ('MU_COL_WHEEL', "Wheel", ""),
)
method_items = (
    ('FIXED_JOINT', "Fixed Joint", ""),
    ('HINGE_JOINT', "Hinge Joint", ""),
    ('LOCKED_JOINT', "Locked Joint", ""),
    ('MERGED_PHYSICS', "Merged Physics", ""),
    ('NO_PHYSICS', "No Physics", ""),
    ('NONE', "None", ""),
)

def SetPropMask(prop, mask):
    """
    Sets the bit mask.

    Args:
        prop: (str): write your description
        mask: (array): write your description
    """
    for i in range(32):
       prop[i] = (mask & (1 << i)) and True or False

def GetPropMask(prop):
    """
    Returns the bit mask of the given bit mask.

    Args:
        prop: (str): write your description
    """
    mask = 0
    for i in range(32):
        mask |= int(prop[i]) << i;
    return mask

def collider_update(self, context):
    """
    Collider the context.

    Args:
        self: (todo): write your description
        context: (todo): write your description
    """
    #FIXME
    from ..collider import update_collider
    obj = context.active_object
    update_collider(obj)

class MuProperties(bpy.types.PropertyGroup):
    modelType: EnumProperty(items = modelType_items, name = "Model Type")
    nodeSize: IntProperty(name = "Size", default = 1)
    nodeMethod: EnumProperty(items = method_items, name = "Method")
    nodeCrossfeed: BoolProperty(name = "Crossfeed", default = True)
    nodeRigid: BoolProperty(name = "Rigid", default = False)

    tag: StringProperty(name = "Tag", default="Untagged")
    layer: IntProperty(name = "Layer")

    castShadows: BoolProperty(name = "Cast Shadows", default = True)
    receiveShadows: BoolProperty(name = "Receive Shadows", default = True)

    collider: EnumProperty(items = collider_items, name = "Collider")
    isTrigger: BoolProperty(name = "Trigger")
    separate: BoolProperty(name = "Separate", description = "Force the collider to be on a separate game object when exporting")
    center: FloatVectorProperty(name = "Center", subtype = 'XYZ', update=collider_update)
    radius: FloatProperty(name = "Radius", update=collider_update)
    height: FloatProperty(name = "Height", update=collider_update)
    direction: EnumProperty(items = dir_items, name = "Direction", update=collider_update)
    size: FloatVectorProperty(name = "Size", subtype = 'XYZ', update=collider_update)

    mass: FloatProperty(name = "Mass")
    suspensionDistance: FloatProperty(name = "Distance")
    suspensionSpring: PointerProperty(type=MuSpringProp, name = "Spring")
    forwardFriction: PointerProperty(type=MuFrictionProp, name = "Forward")
    sideFriction: PointerProperty(type=MuFrictionProp, name = "Sideways")

class MuModelProperties(bpy.types.PropertyGroup):
    name: StringProperty(name = "Name", default="")
    type: StringProperty(name = "Type", default="")
    config: StringProperty(name = "Config", default="")

class MuSceneProperties(bpy.types.PropertyGroup):
    modelType: EnumProperty(items = modelType_items[1:], name = "Model Type",
        description="Type of exported models when unspecified by root object.")
    internal: PointerProperty(name="Internal root",
        description="Root object of the KSP internal model. Used for prop placement.",
        type = bpy.types.Object)

class OBJECT_PT_MuScenePropertyPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    bl_label = "Mu Scene"

    def draw(self, context):
        """
        Draw the layout

        Args:
            self: (todo): write your description
            context: (dict): write your description
        """
        layout = self.layout
        scene = context.scene
        muprops = scene.musceneprops

        col = layout.column()
        col.prop(muprops, "modelType")
        col.prop(muprops, "internal")

class VIEW3D_PT_MuScenePanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "View"
    bl_label = "Mu Scene"

    def draw(self, context):
        """
        Draw the layout

        Args:
            self: (todo): write your description
            context: (dict): write your description
        """
        layout = self.layout
        scene = context.scene
        muprops = scene.musceneprops

        col = layout.column()
        col.prop(muprops, "modelType")
        col.prop(muprops, "internal")

class OBJECT_PT_MuAttachNodePanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_label = 'Attach Node'

    @classmethod
    def poll(cls, context):
        """
        Returns the current object.

        Args:
            cls: (todo): write your description
            context: (dict): write your description
        """
        obj = context.object
        return obj and obj.type == 'EMPTY' and obj.name[:5] == "node_"

    def draw(self, context):
        """
        Draw layout

        Args:
            self: (todo): write your description
            context: (dict): write your description
        """
        layout = self.layout
        muprops = context.active_object.muproperties
        row = layout.row()
        col = row.column()
        col.prop(muprops, "nodeSize")
        col.prop(muprops, "nodeMethod")
        col.prop(muprops, "nodeCrossfeed")
        col.prop(muprops, "nodeRigid")

class OBJECT_PT_MuPropertiesPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_label = 'Mu Properties'

    @classmethod
    def poll(cls, context):
        """
        Poll for the given context.

        Args:
            cls: (todo): write your description
            context: (dict): write your description
        """
        return True

    def draw(self, context):
        """
        Draw layout

        Args:
            self: (todo): write your description
            context: (dict): write your description
        """
        layout = self.layout
        muprops = context.active_object.muproperties
        row = layout.row()
        col = row.column()
        col.prop(muprops, "modelType")
        col.prop(muprops, "tag")
        col.prop(muprops, "layer")
        col.prop(muprops, "castShadows")
        col.prop(muprops, "receiveShadows")

classes_to_register = (
    MuSpringProp,
    MuFrictionProp,
    MuProperties,
    MuModelProperties,
    MuSceneProperties,
    OBJECT_PT_MuScenePropertyPanel,
    VIEW3D_PT_MuScenePanel,
    OBJECT_PT_MuAttachNodePanel,
    OBJECT_PT_MuPropertiesPanel,
)
custom_properties_to_register = (
    (bpy.types.Object, "muproperties", MuProperties),
    (bpy.types.Collection, "mumodelprops", MuModelProperties),
    (bpy.types.Scene, "musceneprops", MuSceneProperties),
)
