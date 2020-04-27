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
    valstr = valstr.strip()
    if valstr in {"False", "false"}:
        return False
    if valstr in {"True", "true"}:
        return True
    if not valstr or valstr[0].isalpha() or valstr[0] in ["_"]:
        return valstr
    return eval(valstr)

def build_nodes(matname, node_tree, ntcfg):
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
            if a == "parent":
                refs.append((sn, a, v))
                continue
            elif a == "node_tree":
                sn.node_tree = bpy.data.node_groups[v]
            else:
                setattr(sn, a, parse_value(v))
        if sndata.HasNode("inputs"):
            for i,ip in enumerate(sndata.GetNode("inputs").GetNodes("input")):
                if ip.HasValue("default_value"):
                    print(sn.name)
                    value = ip.GetValue("default_value")
                    sn.inputs[i].default_value = parse_value(value)
        if sndata.HasNode("outputs"):
            for i,op in enumerate(sndata.GetNode("outputs").GetNodes("output")):
                if op.HasValue("default_value"):
                    print(sn.name)
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

def set_tex(mu, dst, src):
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

def make_shader_prop(muprop, blendprop):
    for k in muprop:
        item = blendprop.add()
        item.name = k
        item.value = muprop[k]

def make_shader_tex_prop(mu, muprop, blendprop):
    for k in muprop:
        item = blendprop.add()
        item.name = k
        set_tex(mu, item, muprop[k])

def create_nodes(mat):
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

def make_shader4(mumat, mu):
    mat = bpy.data.materials.new(mumat.name)
    matprops = mat.mumatprop
    matprops.shaderName = mumat.shaderName
    make_shader_prop(mumat.colorProperties, matprops.color.properties)
    make_shader_prop(mumat.vectorProperties, matprops.vector.properties)
    make_shader_prop(mumat.floatProperties2, matprops.float2.properties)
    make_shader_prop(mumat.floatProperties3, matprops.float3.properties)
    make_shader_tex_prop(mu, mumat.textureProperties, matprops.texture.properties)
    create_nodes(mat)
    return mat

def make_shader(mumat, mu):
    return make_shader4(mumat, mu)
