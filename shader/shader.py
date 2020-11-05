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

import bpy
from mathutils import Vector

from .shader_config import shader_configs

typemap = {
    'VALUE': "NodeSocketFloat",
    'RGBA': "NodeSocketColor",
    'SHADER': "NodeSocketShader",
}

def parse_value(valstr):
    """
    Parses a value to a boolean.

    Args:
        valstr: (str): write your description
    """
    valstr = valstr.strip()
    if valstr in {"False", "false"}:
        return False
    if valstr in {"True", "true"}:
        return True
    if not valstr or valstr[0].isalpha() or valstr[0] in ["_"]:
        return valstr
    return eval(valstr)

def build_nodes(matname, node_tree, ntcfg):
    """
    Builds a list of nodes

    Args:
        matname: (str): write your description
        node_tree: (str): write your description
        ntcfg: (todo): write your description
    """
    for value in ntcfg.values:
        attr, val, line = value
        if attr == "name":
            continue
        setattr(node_tree, attr, parse_value(val))
    if ntcfg.HasNode("inputs"):
        inputs = ntcfg.GetNode("inputs")
        for ip in inputs.GetNodes("input"):
            type = typemap[ip.GetValue("type")]
            name = ip.GetValue("name")
            input = node_tree.inputs.new(type, name)
            if ip.HasValue("min_value"):
                input.min_value = parse_value(ip.GetValue("min_value"))
            if ip.HasValue("max_value"):
                input.max_value = parse_value(ip.GetValue("max_value"))
    if ntcfg.HasNode("outputs"):
        outputs = ntcfg.GetNode("outputs")
        for op in outputs.GetNodes("output"):
            type = typemap[op.GetValue("type")]
            name = op.GetValue("name")
            node_tree.outputs.new(type, name)
    if not ntcfg.HasNode("nodes"):
        return
    refs = []
    nodes = node_tree.nodes
    for n in ntcfg.GetNode("nodes").nodes:
        sntype, sndata, line = n
        sn = nodes.new(sntype)
        for snvalue in sndata.values:
            a, v, l = snvalue
            v = v.strip()
            if a == "parent":
                refs.append((sn, a, v))
                continue
            elif a == "node_tree":
                sn.node_tree = bpy.data.node_groups[v]
            else:
                setattr(sn, a, parse_value(v))
        if sndata.HasNode("inputs"):
            input_nodes = sndata.GetNode("inputs").GetNodes("input")
            if sntype == "ShaderNodeVectorMath":
                # blender 2.82 has only 2 vector and 1 float input nodes
                # but blender 2.90 (2.83?) has 3 vector inputs
                # fortunately, the affects only the wrap operation which
                # none of the shaders use
                if len(sn.inputs) < 4:
                    del input_nodes[2]
            for i,ip in enumerate(input_nodes):
                if ip.HasValue("default_value"):
                    value = ip.GetValue("default_value")
                    sn.inputs[i].default_value = parse_value(value)
        if sndata.HasNode("outputs"):
            for i,op in enumerate(sndata.GetNode("outputs").GetNodes("output")):
                if op.HasValue("default_value"):
                    value = op.GetValue("default_value")
                    sn.outputs[i].default_value = parse_value(value)
    for r in refs:
        if r[1] == "parent" and r[2] in nodes:
            setattr(r[0], r[1], nodes[r[2]])
    if not ntcfg.HasNode("links"):
        return
    links = node_tree.links
    linknodes = ntcfg.GetNode("links")
    for ln in linknodes.GetNodes("link"):
        from_node = nodes[ln.GetValue("from_node")]
        to_node = nodes[ln.GetValue("to_node")]
        from_socket = from_node.outputs[int(ln.GetValue("from_socket"))]
        to_socket = to_node.inputs[int(ln.GetValue("to_socket"))]
        links.new(from_socket, to_socket)

def set_tex(mu, dst, src, context):
    """
    Set a single vertex in place

    Args:
        mu: (todo): write your description
        dst: (todo): write your description
        src: (todo): write your description
        context: (dict): write your description
    """
    try:
        tex = mu.textures[src.index]
        if tex.name[-4:] in [".dds", ".png", ".tga", ".mbm"]:
            dst.tex = tex.name[:-4]
        else:
            dst.tex = tex.name
        dst.type = tex.type
    except IndexError:
        pass
    if dst.tex in bpy.data.images:
        dst.rgbNorm = not bpy.data.images[dst.tex].muimageprop.convertNorm
    dst.scale = src.scale
    dst.offset = src.offset
    if context.material.node_tree:
        dst.__annotations__["tex"][1]["update"](dst, context)
        #other properties are all updated in the one updater
        dst.__annotations__["rgbNorm"][1]["update"](dst, context)

def make_shader_prop(muprop, blendprop, context):
    """
    Creates the shader property

    Args:
        muprop: (todo): write your description
        blendprop: (todo): write your description
        context: (todo): write your description
    """
    for k in muprop:
        item = blendprop.add()
        item.name = k
        item.value = muprop[k]
        if context.material.node_tree:
            item.__annotations__["value"][1]["update"](item, context)

def make_shader_tex_prop(mu, muprop, blendprop, context):
    """
    Creates a set of the given property.

    Args:
        mu: (todo): write your description
        muprop: (todo): write your description
        blendprop: (todo): write your description
        context: (todo): write your description
    """
    for k in muprop:
        item = blendprop.add()
        item.name = k
        set_tex(mu, item, muprop[k], context)

def create_nodes(mat):
    """
    Creates a list of nodes.

    Args:
        mat: (str): write your description
    """
    shaderName = mat.mumatprop.shaderName
    if shaderName in shader_configs:
        cfg = shader_configs[shaderName]
        for extra in cfg.GetNodes("node_tree"):
            ntname = extra.GetValue("name")
            if not ntname in bpy.data.node_groups:
                node_tree = bpy.data.node_groups.new(ntname, "ShaderNodeTree")
                build_nodes(mat.name, node_tree, extra)
        matcfg = cfg.GetNode("Material")
        for value in matcfg.values:
            name, val, line = value
            setattr(mat, name, parse_value(val))
        if mat.use_nodes:
            links = mat.node_tree.links
            nodes = mat.node_tree.nodes
            while len(links):
                links.remove(links[0])
            while len(nodes):
                nodes.remove(nodes[0])
        if mat.use_nodes and matcfg.HasNode("node_tree"):
            build_nodes(mat.name, mat.node_tree, matcfg.GetNode("node_tree"))
    else:
        print(f"WARNING: unknown shader: {shaderName}")

def make_shader4(mumat, mu):
    """
    Creates a matrix.

    Args:
        mumat: (todo): write your description
        mu: (todo): write your description
    """
    mat = bpy.data.materials.new(mumat.name)
    matprops = mat.mumatprop
    matprops.shaderName = mumat.shaderName
    create_nodes(mat)
    class Context:
        pass
    ctx = Context()
    ctx.material = mat
    make_shader_prop(mumat.colorProperties, matprops.color.properties, ctx)
    make_shader_prop(mumat.vectorProperties, matprops.vector.properties, ctx)
    make_shader_prop(mumat.floatProperties2, matprops.float2.properties, ctx)
    make_shader_prop(mumat.floatProperties3, matprops.float3.properties, ctx)
    make_shader_tex_prop(mu, mumat.textureProperties, matprops.texture.properties, ctx)
    return mat

def make_shader(mumat, mu):
    """
    Creates a gaussian.

    Args:
        mumat: (todo): write your description
        mu: (todo): write your description
    """
    return make_shader4(mumat, mu)
