from mu import Mu
import sys

def dump_skin(obj):
    """
    Dump a trimesh mesh.

    Args:
        obj: (todo): write your description
    """
    smr = obj.skinned_mesh_renderer
    print(smr.materials);
    print(smr.bones)
    print(smr.center);
    print(smr.size);
    print(smr.quality);
    print(smr.updateWhenOffscreen);
    mesh = smr.mesh
    for b in mesh.boneWeights:
        print(b.indices, b.weights)

def check_obj(obj):
    """
    Check if obj is a builtin object.

    Args:
        obj: (todo): write your description
    """
    if hasattr(obj, "skinned_mesh_renderer"):
        print("skin on ", obj.transform.name)
        dump_skin(obj)
    for o in obj.children:
        check_obj(o)

def find_skins(fname):
    """
    Finds skins from a file name.

    Args:
        fname: (str): write your description
    """
    mu = Mu()
    if not mu.read(fname):
        print("could not read: " + fname)
        raise
    check_obj(mu.obj)

for f in sys.argv[1:]:
    find_skins(f)
