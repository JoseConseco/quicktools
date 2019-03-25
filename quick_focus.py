import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty, CollectionProperty, PointerProperty, EnumProperty, FloatProperty


# COLLECTIONS
class HistoryObjectsCollection(bpy.types.PropertyGroup):
    name: StringProperty()
    obj: PointerProperty(name="History Object", type=bpy.types.Object)


class HistoryUnmirroredCollection(bpy.types.PropertyGroup):
    name: StringProperty()
    obj: PointerProperty(name="History Unmirror", type=bpy.types.Object)


class HistoryEpochCollection(bpy.types.PropertyGroup):
    name: StringProperty()
    objects: CollectionProperty(type=HistoryObjectsCollection)
    unmirrored: CollectionProperty(type=HistoryUnmirroredCollection)


class QT_OT_Focus(bpy.types.Operator):
    bl_idname = "object.focus"
    bl_label = "Focus"
    bl_description = "Hides objects with visibility queue"
    bl_options = {'REGISTER', 'UNDO'}

    view_selected: BoolProperty(name="Zoom Selcted", default=False)
    unmirror: BoolProperty(name="Un-Mirror", default=False)
    hide_selected: BoolProperty(name="Hide Selected", default=False)


    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        history = context.scene.quick_focus_history
        
        sel = context.selected_objects if not self.hide_selected else list(set(context.visible_objects) - set(context.selected_objects))
        if sel:
            self.focus(context, sel, history)
        elif history:
            self.unfocus(context, history)

        # for epoch in history:
            # print(epoch.name, ", hidden: ", [obj.name for obj in epoch.objects], ", unmirrored: ", [obj.name for obj in epoch.unmirrored])
        return {'FINISHED'}

    def focus(self, context, sel, history):
        hidden = []

        # hide objects not in the selection (and not already hidden)
        for obj in context.visible_objects:
            if obj not in sel:
                hidden.append(obj)
                obj.hide_viewport = True

        # create new epoch, if objects were hidden

        if hidden:
            epoch = history.add()
            epoch.name = "Epoch %d" % (len(history) - 1)

            # store hidden objects

            for obj in hidden:
                entry = epoch.objects.add()
                entry.obj = obj
                entry.name = obj.name

            # disable mirror mods and store these unmirrored objects

            if self.unmirror:
                for obj in sel:
                    for mod in obj.modifiers:
                        if mod.type == "MIRROR":
                            if mod.show_viewport:
                                mod.show_viewport = False

                                entry = epoch.unmirrored.add()
                                entry.obj = obj
                                entry.name = obj.name

            # view selected

            if self.view_selected:
                bpy.ops.view3d.view_selected()
        else: #notihng to hide so assure we want to run unhide
            self.unfocus(context, history)


    def unfocus(self, context, history):
        selected = []
        # for view_selected, select visible objects

        if self.view_selected:
            for obj in context.visible_objects:
                obj.select_set(True)
                selected.append(obj)

        last_epoch = history[-1]

        # restore hidden objects and select them

        for entry in last_epoch.objects:
            entry.obj.hide_viewport = False
            if self.view_selected:
                entry.obj.select_set(True)
                selected.append(entry.obj)

        # re-enbable mirror mods
        if self.unmirror:
            for entry in last_epoch.unmirrored:
                for mod in entry.obj.modifiers:
                    if mod.type == "MIRROR":
                        mod.show_viewport = True

        # delete the last epoch

        idx = history.keys().index(last_epoch.name)
        history.remove(idx)

        # view selected and deselect everythng

        if self.view_selected:
            bpy.ops.view3d.view_selected()

            for obj in selected:
                obj.select_set(False)
