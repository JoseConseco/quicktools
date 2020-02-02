bl_info = {
    "name": "Quick Tools",
    "description": "A series of tools and menus to enhance and speed up workflow",
    "author": "Jonathan Williamson, Bartosz Styperek",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D - 'Q' key gives a menu in Object, Edit, and Sculpt modes.",
    "warning": '',  # used for warning icon and text in addons panel
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/3D_interaction/quicktools",
    "tracker_url": "https://github.com/CGCookie/script-bakery/issues",
    "category": "3D View"}


if "bpy" in locals():
    import importlib
    importlib.reload(general_utils)
    importlib.reload(quick_file_ops)
    importlib.reload(quick_object)
    importlib.reload(quick_mesh)
    importlib.reload(quick_shapekeys)
    importlib.reload(quick_focus)
    importlib.reload(quick_armature)
    importlib.reload(quick_lattice)
    importlib.reload(radial_instances)
    importlib.reload(quick_prefs)

else:
    from .utils import general_utils
    from . import quick_file_ops
    from . import quick_file_ops
    from . import quick_object
    from . import quick_mesh
    from . import quick_shapekeys
    from . import quick_focus
    from . import quick_armature
    from . import quick_lattice
    from . import radial_instances
    from . import quick_prefs

import bpy


# load and reload submodules
##################################
from . import auto_load

auto_load.init()

import traceback
from .quick_prefs import enable_focus, disable_focus
def register():
    try:
        auto_load.register()
    except: traceback.print_exc()
    enable_focus()

def unregister():
    try:
        auto_load.unregister()
    except: traceback.print_exc()
    
    print("Unregistered {}".format(bl_info["name"]))
    disable_focus()
