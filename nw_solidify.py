import bpy
      
class QUICKT_OT_nwSolidify(bpy.types.Operator):
    bl_idname = "nw.solidify"
    bl_label = "nw Solidify Crease"
    bl_options = {"REGISTER","UNDO"}

    thickness: bpy.props.FloatProperty(name="Thickness", description="", default=0.01, min = 0, max = 10)
    offset: bpy.props.FloatProperty(name="Offset", description="", default=-1, min = -1, max = 1)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):

        for obj in context.selected_objects:
            hasBevel = False

            bname = ""
            self.newlyCreated = False
            for mod in obj.modifiers:
                if mod.type == "SOLIDIFY":
                    hasBevel = True
                    bname = mod.name

            if not hasBevel:
                context.view_layer.objects.active=obj
                bpy.ops.object.modifier_add(type='SOLIDIFY')

                obj.modifiers[len(bpy.context.object.modifiers) - 1].thickness = self.thickness
                obj.modifiers[len(bpy.context.object.modifiers) - 1].offset = self.offset
                obj.modifiers[len(bpy.context.object.modifiers) - 1].use_even_offset = True
                obj.modifiers[len(bpy.context.object.modifiers) - 1].use_quality_normals = True
            else:
                obj.modifiers[bname].thickness = self.thickness
                obj.modifiers[bname].offset = self.offset
                obj.modifiers[bname].use_even_offset = True
                obj.modifiers[bname].use_quality_normals = True
            # bpy.context.object.modifiers[bname].limit_method

        return {'FINISHED'}

    def check(self, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_popup(self, event)


    
    
