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
from .quickhull import get_convex_hull

def quickhull_op(self, context):
    operator = self
    undo = bpy.context.user_preferences.edit.use_global_undo
    bpy.context.user_preferences.edit.use_global_undo = False

    for obj in bpy.context.scene.objects:
        if not obj.select_get():
            continue
        obj.select_set('DESELECT')
        mesh = obj.to_mesh(context.scene, True, 'PREVIEW')
        if not mesh or not mesh.vertices:
            continue
        mesh = quickhull(mesh)
        hullobj = bpy.data.objects.new("ConvexHull", mesh)
        bpy.context.scene.collection.objects.link(hullobj)
        hullobj.select_set('SELECT')
        hullobj.location = obj.location
        bpy.context.view_layer.objects.active = hullobj

    bpy.context.user_preferences.edit.use_global_undo = undo
    return {'FINISHED'}

class KSPMU_OT_QuickHull(bpy.types.Operator):
    '''Create a convex hull from an object.'''
    bl_idname = "mesh.quickhull"
    bl_label = "Convex Hull"
    bl_description = """Create a convex hull from an object."""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        keywords = self.as_keywords ()
        return quickhull_op(self, context, **keywords)

classes_to_register = (
    KSPMU_OT_QuickHull,
)
