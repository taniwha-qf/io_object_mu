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
from mathutils import Vector, Matrix, Quaternion

def translate(d):
    """
    Translate a matrix.

    Args:
        d: (array): write your description
    """
    return Matrix.Translation(Vector(d))

def scale(s):
    """
    Return a new image by scaling.

    Args:
        s: (todo): write your description
    """
    s = Vector(s)
    return Matrix(((s.x,  0,  0, 0),
                   (  0,s.y,  0, 0),
                   (  0,  0,s.z, 0),
                   (  0,  0,  0, 1)))

def rotate(r):
    """
    Rotate a rotation matrix.

    Args:
        r: (int): write your description
    """
    return Quaternion(r).normalized().to_matrix().to_4x4()
