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
from .quick_focus import HistoryEpochCollection
from .utils.general_utils import get_addon_preferences
##########################         Addon Prefernedces                ###############################################


class QuickToolPreferences(bpy.types.AddonPreferences):
    def switch_focus(self, context):
        if self.use_focus:
            enable_focus()
        else:
            disable_focus()

    bl_idname = 'quicktools'
    use_focus: bpy.props.BoolProperty(name="Focus", description="Enable focus", default=False, update = switch_focus)

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, "use_focus")


addon_keymaps = []
def enable_focus():
    prefs = get_addon_preferences()
    if prefs.use_focus:
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.addon

        km = kc.keymaps.new(name='3D View', space_type="VIEW_3D")
        kmi1 = km.keymap_items.new('object.focus', 'NUMPAD_SLASH', 'PRESS')
        kmi1.properties.hide_selected = False
        addon_keymaps.append((km, kmi1))

        kmi2 = km.keymap_items.new('object.focus', 'NUMPAD_SLASH', 'PRESS', alt=True)
        kmi2.properties.hide_selected = True
        addon_keymaps.append((km, kmi2))

        bpy.types.Scene.quick_focus_history = bpy.props.CollectionProperty(type=HistoryEpochCollection)


def disable_focus():
    prefs = get_addon_preferences()
    if prefs.use_focus:
        del bpy.types.Scene.quick_focus_history
        # remove the add-on keymaps
        for km, kmi in addon_keymaps:
            # km.keymap_items.remove(kmi)
            for kmi in km.keymap_items:
                km.keymap_items.remove(kmi)
        addon_keymaps.clear()
