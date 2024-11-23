import bpy
from bpy.props import (StringProperty, IntProperty, BoolProperty,
                      CollectionProperty, PointerProperty, EnumProperty,
                      FloatProperty)

class IsolatedObjects(bpy.types.PropertyGroup):
    obj: PointerProperty( name="History Object", type=bpy.types.Object, description="Reference to the history object")

class HistoryEpochCollection(bpy.types.PropertyGroup):
    layer_objects: CollectionProperty(type=IsolatedObjects, description="Collection of hidden objects")

class QT_OT_Focus(bpy.types.Operator):
    bl_idname = "object.focus"
    bl_label = "Focus"
    bl_description = "Hides objects with visibility queue"
    bl_options = {'REGISTER', 'UNDO'}

    view_selected: BoolProperty( name="Zoom Selected", default=False, description="Zoom view to selected objects")
    hide_selected: BoolProperty( name="Hide Selected", default=False, description="Hide selected objects instead of unselected")

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.space_data.type == 'VIEW_3D'

    def execute(self, context):
        space_data = context.space_data
        if space_data.local_view:
            bpy.ops.view3d.localview(frame_selected=False)

        # Cache selected objects to avoid multiple lookups
        visible_objects = set(context.visible_objects)
        selected_objects = set(context.selected_objects)

        sel = (visible_objects - selected_objects) if self.hide_selected else selected_objects

        if sel:
            self.focus(context, list(sel))
        elif context.scene.quick_focus_history:
            self.unfocus(context)

        return {'FINISHED'}

    def focus(self, context, sel_objs):
        focus_history = context.scene.quick_focus_history
        visible_objects = set(context.visible_objects)
        hidden = [obj for obj in visible_objects if obj not in sel_objs]

        if hidden:
            # Create new focus entry
            history_item = focus_history.add()
            focus_items = len(focus_history) - 1
            # print(f"Focus depth: {focus_items}")

            # Batch hide objects
            for obj in hidden:
                obj.hide_viewport = True
                history_obj = history_item.layer_objects.add()
                history_obj.obj = obj

            # View selected objects
            if self.view_selected and sel_objs:
                bpy.ops.view3d.view_selected()
        else:
            self.unfocus(context)

    def unfocus(self, context):
        focus_history = context.scene.quick_focus_history
        if not focus_history:
            return

        selected = set()
        last_item = focus_history[-1]

        # Restore hidden objects
        for entry in last_item.layer_objects:
            if entry.obj:  # Check if object still exists
                entry.obj.hide_viewport = False
                if self.view_selected:
                    entry.obj.select_set(True)
                    selected.add(entry.obj)

        # Remove the last entry
        focus_history.remove(len(focus_history) - 1)

        # View selected and deselect everything
        if self.view_selected and selected:
            bpy.ops.view3d.view_selected()
            for obj in selected:
                obj.select_set(False)
