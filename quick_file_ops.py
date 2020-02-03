import bpy
import os


def addons_list(self, context):
    return [(name, name, name ) for name in sorted(context.preferences.addons.keys())]

class QF_OT_ReloadScript(bpy.types.Operator):
    bl_idname = "script.reload_my_addon"
    bl_label = "reload script"
    bl_description = "Reload addon by name"
    bl_options = {"REGISTER"}
    bl_property = 'addon_name'

    addon_name: bpy.props.EnumProperty(name='addon name', description='', items=addons_list)
    # mod_name: bpy.props.StringProperty(name='mod name', description='', default='')

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, 'addon_name')

    def execute(self, context):
        # import garment_tool
        import importlib
        mod = __import__(self.addon_name)
        importlib.reload(mod) #this unregisters but wont call reg?
        mod.unregister() 
        mod.register() 
        bpy.ops.preferences.addon_enable(module=self.addon_name)
        return {"FINISHED"}



class BLEND_OT_DeleteBlend(bpy.types.Operator):
    bl_idname = "object.delete_blend_file"
    bl_label = "Delete Remove blend file"
    bl_description = "Delete current blend file from HDrive"
    bl_options = {"REGISTER","UNDO"}


    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
        # else:
        #     return self.execute(context)

    def draw(self, context):
        layout = self.layout
        layout.label(text=f'Remove file: {bpy.data.filepath}?')

    def execute(self, context):
        bpy.ops.object.delete()
        current_blend = bpy.data.filepath
        if os.path.isfile(bpy.data.filepath):
            os.remove(bpy.data.filepath)
            self.report({'INFO'}, f'Removed: {bpy.data.filepath}')
        else:
            self.report({'INFO'}, f'File: {bpy.data.filepath} does not exist! Cancelling')
            return {'CANCELLED'}

        blend1 = current_blend+'1'
        if os.path.isfile(blend1):
            os.remove(blend1)
            self.report({'INFO'}, f'Removed: {blend1}')
            
        blend2 = current_blend+'2'
        if os.path.isfile(blend2):
            os.remove(blend2)
            self.report({'INFO'}, f'Removed: {blend2}')

        return {"FINISHED"}
