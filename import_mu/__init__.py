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

from .operators import KSPMU_OT_ImportMu
from .import_mu import import_mu
from .exception import MuImportError

from . import import_modules

def import_mu_menu_func(self, context):
    """
    Imports all the import_func

    Args:
        self: (todo): write your description
        context: (todo): write your description
    """
    self.layout.operator(KSPMU_OT_ImportMu.bl_idname, text="KSP Mu (.mu)")

classes_to_register = (
    KSPMU_OT_ImportMu,
)

menus_to_register = (
    (bpy.types.TOPBAR_MT_file_import, import_mu_menu_func),
)
