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
from mathutils import Matrix, Vector
from math import sqrt

from .. import properties
from ..quickhull.convex_hull import quickhull
from ..utils.solver import solve_cubic
from .seb import smalest_enclosing_ball

def _swap_rows(mat, r1, r2):
    """
    Swap the rows of the matrix.

    Args:
        mat: (array): write your description
        r1: (array): write your description
        r2: (todo): write your description
    """
    mat[r1], mat[r2] = Vector(mat[r2]), Vector(mat[r1])

def _canonicalize_matrix(mat):
    """ Ensure the matrix is in X Y Z order and that the axes are all +ve"""
    # mat is (assumted to be) a rotation matrix, so while the signs are not
    # symmetric, the magnitudes are, thus finding the correct row order can be
    # done by sorting on column 0 to get X YZ or X ZY, then sort on column 1
    # to ensure X Y Z
    if abs(mat[0][0]) < abs(mat[1][0]):
        _swap_rows(mat, 0, 1)
    if abs(mat[1][0]) < abs(mat[2][0]):
        _swap_rows(mat, 1, 2)
    if abs(mat[0][0]) < abs(mat[1][0]):
        _swap_rows(mat, 0, 1)
    if abs(mat[1][1]) < abs(mat[2][1]):
        _swap_rows(mat, 1, 2)
    # ensure all vectors are cannonical (aligned with +ve axis)
    if mat[0][0] < 0:
        mat[0] = -mat[0]
    if mat[1][1] < 0:
        mat[1] = -mat[1]
    if mat[2][2] < 0:
        mat[2] = -mat[2]

def _eigen_vectors(mat):
    """Return the eigen vectors as a rotation matrix.
    Note that mat is assumed to be symmetric
    """
    a = -1
    b = mat[0][0] + mat[1][1] + mat[2][2]
    c = (mat[0][1]**2 + mat[0][2]**2 + mat[1][2]**2
         - mat[0][0] * mat[2][2] - mat[0][0] * mat[1][1]
         - mat[1][1] * mat[2][2])
    d = (mat[0][0] * mat[1][1] * mat[2][2]
         + 2 * mat[0][1] * mat[0][2] * mat[1][2]
         - mat[0][0] * mat[1][2]**2 - mat[1][1] * mat[0][2]**2
         - mat[2][2] * mat[0][1]**2)
    L = solve_cubic(a, b, c, d)
    L = [l.real for l in L]
    # Use Cayley-Hamilton to find the eigenvectors
    I = Matrix.Identity(3)
    Aa = mat - L[0] * I
    Ab = mat - L[1] * I
    Ac = mat - L[2] * I
    Q = Matrix((max(Aa @ Ab).normalized(),
                max(Aa @ Ac).normalized(),
                max(Ab @ Ac).normalized()))
    _canonicalize_matrix(Q)
    return Q

def _linear_regression(verts):
    """
    Return the linear regression of a linear regression.

    Args:
        verts: (todo): write your description
    """
    # Note that this is the centroid of the points, NOT the center of mass,
    # so it is not directly usable
    centroid = sum(verts, start=Vector((0, 0, 0))) / len(verts)
    A = Matrix(((0, 0, 0),)*3)
    for vert in verts:
        v = vert - centroid
        A += Matrix(((v.x * v.x, v.x * v.y, v.x * v.z),
                     (v.x * v.y, v.y * v.y, v.y * v.z),
                     (v.x * v.z, v.y * v.z, v.z * v.z)))
    Q = _eigen_vectors(A)
    # The rotation is never more than 45 degrees as higher angles simply
    # change the principle axes
    print(Q)
    rotation = Q.inverted().to_quaternion()
    # Note that this is not the actual axis moments, but their
    # contributions: that is, for Ixx, add moment.y and moment.z. However,
    # the size of the equivalent box edge length can be found from
    # sqrt(m/2). More importantly, it is the moments of the point masses
    # rather than of the solid object.
    moment = Q @ A @ Q.inverted() @ Vector((1,1,1))
    return centroid, rotation, moment, Q

def _calc_p(x, frame):
    """ Find properties of each point
    Distance along the primary axis
    Distance squared from the primary axis
    Projection onto the primary plane (secondary axes) for SEB
    """
    n, s, t = frame
    u = x @ s
    v = x @ t
    w = x @ n
    return w, u**2 + v**2, (u * s, v * t)

def _key_u(uv2):
    """
    Return the value of the uv2.

    Args:
        uv2: (todo): write your description
    """
    return uv2[0]

def _key_v2(uv2):
    """
    Returns the key corresponding to use in - place.

    Args:
        uv2: (todo): write your description
    """
    return uv2[1]

class Points:
    def __init__(self):
        """
        Initialize the instance

        Args:
            self: (todo): write your description
        """
        self.verts = []

    @property
    def valid(self):
        """
        Returns true if the length of the maximum number.

        Args:
            self: (todo): write your description
        """
        return len(self.verts) > 0

    def add_verts(self, verts, xform, selected=False):
        """
        Add vertices

        Args:
            self: (todo): write your description
            verts: (array): write your description
            xform: (todo): write your description
            selected: (todo): write your description
        """
        if selected:
            verts = [v for v in verts if v.select]
        base = len(self.verts)
        self.verts = self.verts + [None] * len(verts)
        for i, v in enumerate(verts):
            self.verts[base + i] = (xform @ v.co).freeze()

    def calc_box(self):
        """
        Calculate the bounding box of the image.

        Args:
            self: (todo): write your description
        """
        if not self.verts:
            return Vector((0, 0, 0)), Vector((0, 0, 0))
        mins = Vector(self.verts[0])
        maxs = Vector(self.verts[0])
        for v in self.verts:
            mins.x = min(mins.x, v.x)
            mins.y = min(mins.y, v.y)
            mins.z = min(mins.z, v.z)
            maxs.x = max(maxs.x, v.x)
            maxs.y = max(maxs.y, v.y)
            maxs.z = max(maxs.z, v.z)
        size = (maxs - mins)
        center = (maxs + mins) / 2
        return size, center

    def calc_sphere(self):
        """
        Calculate the spherical coordinates.

        Args:
            self: (todo): write your description
        """
        return smalest_enclosing_ball(self.verts)

    def calc_hull(self):
        """
        Calculate hullh hull

        Args:
            self: (todo): write your description
        """
        return quickhull(self)

    def calc_capsule(self):
        """
        Calculate the raiduleule angle.

        Args:
            self: (todo): write your description
        """
        loc, rot, mom, Q = _linear_regression(self.verts)
        m = list(mom)
        l = max(m)
        i = m.index(l)
        axis = properties.dir_items[i][0]
        del m[i]
        r = max(m)
        # pick a frame (n, s, t) such that n is the primary axis and s,t are
        # the secondary axes of the capsule
        frame = Q[i], Q[(i + 1) % 3], Q[(i + 2) % 3]
        p = [_calc_p(x - loc, frame) for x in self.verts]
        mi, ma = min(p, key=_key_u)[0], max(p, key=_key_u)[0]
        r2 = max(p, key=_key_v2)[1]
        mi = min([p[0] + sqrt(r2 - p[1]) for p in p if (p[0] - mi)**2 < r2])
        ma = max([p[0] - sqrt(r2 - p[1]) for p in p if (p[0] - ma)**2 < r2])
        print (mi, ma)
        r = sqrt(r2)
        length = (ma - mi) + 2 * r
        return loc, rot, axis, length, r
