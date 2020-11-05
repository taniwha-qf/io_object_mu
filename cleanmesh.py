from mu import Mu
import sys

def check_mesh(obj, level):
    """
    Check if a mesh is a mesh.

    Args:
        obj: (todo): write your description
        level: (int): write your description
    """
    if hasattr(obj, "shared_mesh") and not hasattr(obj, "renderer"):
        print(obj.transform.name)
        obj.shared_mesh = None
        return True
    return False

def check_obj(obj, level = 0):
    """
    Check if obj is an object has changed.

    Args:
        obj: (todo): write your description
        level: (int): write your description
    """
    changed = check_mesh(obj, level)
    for o in obj.children:
       changed = check_obj(o, level + 1) or changed
    return changed

for fname in sys.argv[1:]:
    mu = Mu()
    if not mu.read(fname):
        print("could not read: " + fname)
        break
    if check_obj(mu.obj):
        mu.write(fname+".out")
