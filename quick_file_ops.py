import bpy
import os

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
