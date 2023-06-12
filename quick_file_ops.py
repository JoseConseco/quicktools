import bpy
import os

class BLEND_OT_DeleteBlend(bpy.types.Operator):
    bl_idname = "object.delete_blend_file"
    bl_label = "Delete current blend file"
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

# copy blend file path to clipboard operator
class BLEND_OT_CopyBlendPath(bpy.types.Operator):
    bl_idname = "object.copy_blend_path"
    bl_label = "Copy blend file path to clipboard"
    bl_description = "Copy blend file path to clipboard"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.context.window_manager.clipboard = bpy.data.filepath
        # use to system clipboard too
        import subprocess
        # for linux
        subprocess.run(['xclip', '-selection', 'clipboard'], input=bpy.data.filepath.encode('utf-8'))

        self.report({'INFO'}, f'Copied: {bpy.data.filepath}')
        return {"FINISHED"}


class BLEND_OT_RenameBlend(bpy.types.Operator):
    bl_idname = "object.rename_blend"
    bl_label = "Rename current blend file"
    bl_description = "Rename current file from HDrive"
    bl_options = {"REGISTER", "UNDO"}

    name: bpy.props.StringProperty(name='name', description='', default='')


    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text=f'Rename current file to:')
        layout.prop(self, 'name')

    def execute(self, context):
        current_blend = bpy.data.filepath
        current_dir = os.path.dirname(current_blend)
        self.name = self.name + '.blend' if self.name[-6:] != '.blend' else self.name
        if os.path.isfile(bpy.data.filepath):
            new_name = os.path.join(current_dir, self.name)
            # os.rename(current_blend,new_name)
            os.remove(bpy.data.filepath)
            bpy.ops.wm.save_as_mainfile(filepath=new_name, compress=True)
            bpy.ops.wm.open_mainfile(filepath=new_name)
            # bpy.data.filepath = new_name #! read only
            self.report({'INFO'}, f'Renamed: {bpy.data.filepath}')
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
