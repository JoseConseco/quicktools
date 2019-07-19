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
    importlib.reload(quick_object)
    importlib.reload(quick_select)
    importlib.reload(quick_shapekeys)
    importlib.reload(quick_focus)
    importlib.reload(quick_armature)
    importlib.reload(quick_lattice)
    importlib.reload(radial_instances)
else:
    from . import quick_object
    from . import quick_select
    from . import quick_shapekeys
    from . import quick_focus
    from . import quick_armature
    from . import quick_lattice
    from . import radial_instances

import bpy


# load and reload submodules
##################################
from . import auto_load

auto_load.init()

from .quick_focus import HistoryEpochCollection
import traceback

addon_keymaps = []
def register():
    try:
        auto_load.register()
    except: traceback.print_exc()

    wm = bpy.context.window_manager
    kc = bpy.context.window_manager.keyconfigs.addon

    km = kc.keymaps.new(name='3D View', space_type="VIEW_3D")
    kmi1 = km.keymap_items.new('object.focus', 'NUMPAD_SLASH', 'PRESS')
    kmi1.properties.hide_selected = False
    addon_keymaps.append((km, kmi1))

    kmi2 = km.keymap_items.new('object.focus', 'NUMPAD_SLASH', 'PRESS', alt=True)
    kmi2.properties.hide_selected = True
    addon_keymaps.append((km, kmi2))

    bpy.types.Scene.quick_focus_history = bpy.props.CollectionProperty(type=HistoryEpochCollection)

def unregister():
    try:
        auto_load.unregister()
    except: traceback.print_exc()
    

    print("Unregistered {}".format(bl_info["name"]))
    del bpy.types.Scene.quick_focus_history
    # remove the add-on keymaps
    for km, kmi in addon_keymaps:
        # km.keymap_items.remove(kmi)
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()

