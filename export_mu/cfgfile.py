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

import bpy
from mathutils import Vector

from ..cfgnode import ConfigNode, ConfigNodeError
from ..cfgnode import parse_node
from ..utils import strip_nnn, swapyz, swizzleq, vector_str

def find_template(mu, filepath):
    """
    Returns the template of a cfgin. cfgin.

    Args:
        mu: (todo): write your description
        filepath: (str): write your description
    """
    base = os.path.splitext(filepath)
    cfg = base[0] + ".cfg"

    cfgin = mu.name + ".cfg.in"
    if cfgin in bpy.data.texts:
        return cfg, ConfigNode.load(bpy.data.texts[cfgin].as_string())

    cfgin = base[0] + ".cfg.in"
    if os.path.isfile (cfgin):
        try:
            return cfg, ConfigNode.loadfile(cfgin)
        except ConfigNodeError as e:
            print("Error reading", cfgin, e.message)

    return None, None

def add_internal_node(node, internal):
    """
    Add a node to the internal node.

    Args:
        node: (todo): write your description
        internal: (str): write your description
    """
    # NOTE this assumes the internal is the direct child of the part's root
    # also, it assumes the internal is correctly oriented relative to the part
    # (FIXME?)
    inode = node.AddNewNode('INTERNAL')
    inode.AddValue("name", strip_nnn(internal.name))
    if internal.location:
        inode.AddValue("offset", vector_str(swapyz(internal.location)))
    # not really a good idea IMHO, but it's there...
    if internal.scale != Vector((1, 1, 1)):
        inode.AddValue("scale", vector_str(swapyz(internal.scale)))

def add_prop_node(node, prop):
    """
    Add a property to the node.

    Args:
        node: (todo): write your description
        prop: (todo): write your description
    """
    # NOTE this assumes the prop is the direct child of the internal's root
    pnode = node.AddNewNode('PROP')
    pnode.AddValue("name", strip_nnn(prop.name))
    pnode.AddValue("position", vector_str(swapyz(prop.location)))
    pnode.AddValue("rotation", vector_str(swizzleq(prop.rotation_quaternion)))
    pnode.AddValue("scale", vector_str(swapyz(prop.scale)))

def generate_cfg(mu, filepath):
    """
    Generate cfgn file

    Args:
        mu: (str): write your description
        filepath: (str): write your description
    """
    cfgfile, cfgnode = find_template(mu, filepath)
    if not cfgnode:
        return
    ntype = mu.type
    if ntype == 'NONE':
        ntype = bpy.context.scene.musceneprops.modelType
    node = cfgnode.GetNode(ntype)
    if not node:
        return
    parse_node(mu, cfgnode)
    if ntype == 'PART':
        if mu.CoMOffset != None:
            node.AddValue("CoMOffset", vector_str(swapyz(mu.CoMOffset)))
        if mu.CoPOffset != None:
            node.AddValue("CoPOffset", vector_str(swapyz(mu.CoPOffset)))
        if mu.CoLOffset != None:
            node.AddValue("CoLOffset", vector_str(swapyz(mu.CoLOffset)))
        if mu.internals:
            add_internal_node(node, mu.internals[0])
        mu.nodes.sort()
        for n in mu.nodes:
            n.save(node)
    elif ntype == 'INTERNAL':
        for prop in mu.props:
            add_prop_node(node, prop)
    # nothing meaningful for PROP
    of = open(cfgfile, "wt")
    for n in cfgnode.nodes:
        of.write(n[0] + " " + n[1].ToString())
