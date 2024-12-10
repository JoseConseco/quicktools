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


import bpy
# import rna_keymap_ui
# from .quick_focus import HistoryEpochCollection
from .utils.general_utils import get_addon_preferences
import rna_keymap_ui

##########################         Addon Prefernedces                ###############################################


class QuickToolPreferences(bpy.types.AddonPreferences):
    def switch_focus(self, context):
        if self.use_focus:
            enable_focus()
        else:
            disable_focus()

    bl_idname = 'quicktools'
    use_focus: bpy.props.BoolProperty(name="Focus", description="Enable focus", default=False, update = switch_focus)


    def draw_key_item(self, layout, description, kc, km, oper_bl_name, prop_name=None, prop_value=None):
        kmi = get_hotkey_entry_item(km, oper_bl_name, prop_name, prop_value)
        if kmi:
            layout.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, layout, 0)
        else:
            layout.label(text=description)


    def draw(self, context):

        def compare_kmi_props(addon_kmi, user_kmi):
            for prop in dir(addon_kmi.properties):
                if not prop.startswith('__'):
                    if getattr(addon_kmi.properties, prop) != getattr(user_kmi.properties, prop):
                        return False
            return True

        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, "use_focus")

        col = layout.column()
        col.label(text="Keymap List:",icon="KEYINGSET")

        wm = context.window_manager
        old_km_name = ""
        found_addon_kmi = [] # list of tuples (exist, (km, kmi))
        for i,(km_add, kmi_add) in enumerate(addon_keymaps):
            for user_km in wm.keyconfigs.user.keymaps:
                if km_add.name == user_km.name:
                    km = user_km
                    break
            got_kmi = False
            for kmi in km.keymap_items:
                if kmi_add.idname == kmi.idname and kmi_add.name == kmi.name and compare_kmi_props(kmi_add, kmi):
                    found_addon_kmi.append((True,(km,kmi)))
                    got_kmi = True
            if not got_kmi:
                found_addon_kmi.append((False,(km_add,kmi_add)))


        # found_addon_kmi = sorted(set(found_addon_kmi), key=found_addon_kmi.index)

        kc = wm.keyconfigs.user
        for i, (exist, (km, kmi)) in enumerate(found_addon_kmi):
            if not km.name == old_km_name:
                col.label(text=str(km.name),icon="DOT")
            if exist:   # user keymap
                col.context_pointer_set("keymap", km)
                rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
                col.separator()
            else: # else holds addon keymap - that is missing in user keymap
                split = col.split(factor=0.1)
                split.label(text='   ')
                op = split.operator(GP_OT_ReregisterUserKeym.bl_idname, text=f"Restore '{kmi.name}' hotkey" , icon="DISCLOSURE_TRI_RIGHT")
                op.index = i
                col.separator()

            old_km_name = km.name

        col.operator(QT_OT_Add_Hotkey.bl_idname, text="Reset Group Pro Hotkeys")


addon_keymaps = []
def enable_focus():
    prefs = get_addon_preferences()
    if prefs.use_focus:
        bpy.types.Scene.quick_focus_history = bpy.props.CollectionProperty(type=HistoryEpochCollection)


def disable_focus():
    del bpy.types.Scene.quick_focus_history
    prefs = get_addon_preferences()
    # if prefs.use_focus:
    #     # remove the add-on keymaps
    #     for km, kmi in addon_keymaps:
    #         # km.keymap_items.remove(kmi)
    #         for kmi in km.keymap_items:
    #             km.keymap_items.remove(kmi)
    #     addon_keymaps.clear()



def new_keymap_items(kc):
    '''AFAIK this is overridden later by user set hotkey in keyconfigs.user.
    keyconfig.addon - is always there, but if entry is missing in keyconfig.user , then GroupPro hotkey won't work

    addon_km = wm.keyconfigs.addon   # always has gpro hotkey (and other addons)
    user_km = wm.keyconfigs.user # default (active) + addons. Final keyconfig, can be customized by user.  Fix: if gpro menu is missing here, ctrl+X wont work.
    active_km = wm.keyconfigs.active # same as default?
    default_km = wm.keyconfigs.default #same as active?
    '''
    new_keymaps = []

    km = kc.keymaps.new(name='3D View', space_type="VIEW_3D")
    # if not km:
    #     km = kc.keymaps.new(name='3D View', space_type="VIEW_3D")
    # kmi1 = km.keymap_items.new('object.focus', 'NUMPAD_SLASH', 'PRESS')
    # kmi1.properties.hide_selected = False
    # new_keymaps.append((km, kmi1))
    #
    # kmi2 = km.keymap_items.new('object.focus', 'NUMPAD_SLASH', 'PRESS', alt=True)
    # kmi2.properties.hide_selected = True
    # new_keymaps.append((km, kmi2))

    # add hoteky for 'QUICKT_MT_SplitAreaPie' pie menu (ctrl+shift+q)


    km = kc.keymaps.new(name='Window', space_type="EMPTY")
    kmi = km.keymap_items.new('wm.call_menu_pie', value= 'PRESS', type='Q', ctrl=True, shift=True)
    kmi.properties.name = 'QUICKT_MT_SplitAreaPie'
    kmi.active = True
    new_keymaps.append((km, kmi))

    bpy.types.Scene.quick_focus_history = bpy.props.CollectionProperty(type=HistoryEpochCollection)

    return new_keymaps


addon_keymaps = []

def get_hotkey_entry_item(km, kmi_name, prop_key=None, prop_val=None):
    '''
    returns hotkey of specific type, with specific properties.name (keymap is not a dict, so referencing by keys is not enough
    if there are multiple hotkeys!)
    '''
    for i, km_item in enumerate(km.keymap_items):
        if km.keymap_items.keys()[i] == kmi_name:
            if prop_key:  # usually for wm.call_menu_pie
                if getattr(km.keymap_items[i].properties,prop_key) == prop_val: # eg. 'mode' == 'TILT'
                    return km_item  #TODO: maybe this should return multiple keymaps...
            else: #for operators
                return km_item

    return None



def register_keymap():
    wm = bpy.context.window_manager

    addon_keyconfig = wm.keyconfigs.addon   # always has gpro hotkey (and other addons)
    user_keyconfig = wm.keyconfigs.user # default (active) + addons. Final keyconfig, can be customized by user.  Fix: if gpro menu is missing here, ctrl+X wont work.
    active_keyconfig = wm.keyconfigs.active # same as default?
    default_km = wm.keyconfigs.default #same as active?

    registered_km_items = new_keymap_items(addon_keyconfig)
    global addon_keymaps
    for km, kmi in registered_km_items:
        addon_keymaps.append((km, kmi))

    km3 = wm.keyconfigs.default.keymaps['3D View']
    if 'view3d.pastebuffer' in km3.keymap_items.keys():  # won't be there on blender start ( is there better workaround?)
        km3.keymap_items['view3d.pastebuffer'].active = False

    km2 = wm.keyconfigs.default.keymaps['Object Mode']
    # kmi2 = km2.keymap_items.new('object.duplicate_group_override', 'D', 'PRESS', shift=True)
    if 'object.duplicate_move' in km2.keymap_items.keys():  # disable default hotkey if exist
        kmi2 = km2.keymap_items['object.duplicate_move'].active = False

    if 'object.join' in km2.keymap_items.keys():  # disable default hotkey if exist
        kmi2 = km2.keymap_items['object.join'].active = False


class QT_OT_Add_Hotkey(bpy.types.Operator):
    ''' Add hotkey entry '''
    bl_idname = "quick_tool.add_hotkey"
    bl_label = "Quick Tool Init Hotkey"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        wm = bpy.context.window_manager
        # wm.keyconfigs.user # addon + active (or default?) # is user removed Gpro ctrl+X key, then this will add it back
        registered_km_items = new_keymap_items(wm.keyconfigs.user)

        self.report({'INFO'}, "Restored Group Pro Hotkeys in User Preferences -> Input -> 3D view")
        return {'FINISHED'}


# operator GP_OT_ReregisterUserKeym, that will re-register user keymap from addon keymap item
class GP_OT_ReregisterUserKeym(bpy.types.Operator):
    bl_idname = "groupro.reregister_user_keym"
    bl_label = "Restore GroupPro Hotkey"
    bl_description = "Restore missing GroupPro hotkey entry"
    bl_options = {'REGISTER', 'INTERNAL'}

    index: bpy.props.IntProperty()

    def execute(self, context):
        (km_add,kmi_add) = addon_keymaps[self.index]
        wm = bpy.context.window_manager
        user_keyconfig = wm.keyconfigs.user
        km = user_keyconfig.keymaps.get(km_add.name)
        if not km:
            km = user_keyconfig.keymaps.new(name=km_add.name, space_type=km_add.space_type)
        kmi = km.keymap_items.new(kmi_add.idname, kmi_add.type, kmi_add.value, ctrl=kmi_add.ctrl, shift=kmi_add.shift, alt=kmi_add.alt, oskey=kmi_add.oskey)
        if hasattr(kmi_add.properties, 'name'):
            kmi.properties.name = kmi_add.properties.name
        self.report({'INFO'}, "Restored Group Pro Hotkeys in User Preferences -> Input -> 3D view")
        return {'FINISHED'}


def unregister_keymap():
    global addon_keymaps
    wm = bpy.context.window_manager
    for km, kmi in addon_keymaps:
        if len(km.keymap_items) > 0:  # why this is empty/broken of F8 scripts.reload?
            try:
                km.keymap_items.remove(kmi)
            except Exception as e:
                print(e)
        # if km in wm.keyconfigs.addon.keymaps.values():
        #     wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()

    # stuff from gpro
    # wm = bpy.context.window_manager
    # km = wm.keyconfigs.default.keymaps['3D View']  # activate back defautl ctrl+v and shift+d hotkeys
    # if 'view3d.pastebuffer' in km.keymap_items.keys():  # won't be there on blender start ( is there better workaround?)
    #     km.keymap_items['view3d.pastebuffer'].active = True
    #
    # km = wm.keyconfigs.default.keymaps['Object Mode']  # activate back defautl ctrl+v and shift+d hotkeys XXX: enablinig this break 3d view nav...
    # if 'object.duplicate_move' in km.keymap_items.keys():  # won't be there on blender start ( is there better workaround?)
    #     km.keymap_items['object.duplicate_move'].active = True
    # if 'object.join' in km.keymap_items.keys():  # won't be there on blender start ( is there better workaround?)
    #     km.keymap_items['object.join'].active = True

