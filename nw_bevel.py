import bpy


class QUICKT_OT_nwBevel(bpy.types.Operator):
    bl_idname = "object.quickbevel"
    bl_label = "Quick Bevel"
    bl_options = {"REGISTER","UNDO"}

    bevel_width: bpy.props.FloatProperty(name="Bevel Width", description="", default=0.01, min = 0, max = 10)
    profile: bpy.props.FloatProperty(name="Profile", description="", default=0.5, min = 0, max = 1)
    angle: bpy.props.FloatProperty(name="angle", description="", default=0.523599, min = 0, max = 60, subtype = 'ANGLE')
    segments: bpy.props.IntProperty(name="Segments", description="", default=1, min=1, max=12)
    clamp: bpy.props.BoolProperty(name = "Clamp overlap", default = True)
    Type: bpy.props.EnumProperty(name = "Bevel Type", default = "ANGLE",
                                    items = (("NONE","NONE",""),
                                             ("ANGLE","ANGLE",""),
                                             ("WEIGHT","WEIGHT",""),
                                             ("VGROUP","VGROUP",""),
                                            ))

    @classmethod
    def poll(cls, context):
        return context.active_object is not None


    def draw(self, context):
        layout = self.layout
        layout.prop(self,'bevel_width')
        layout.prop(self,'profile')
        layout.prop(self,'segments')
        layout.prop(self,'clamp')
        layout.prop(self,'Type')
        if self.Type=='ANGLE':
            layout.prop(self,'angle')

    def execute(self, context):

        for obj in context.selected_objects:
            if obj.type!='MESH':
                continue;
            hasBevel = False

            bname = ""
            self.newlyCreated = False
            for mod in obj.modifiers:
                if mod.type == "BEVEL":
                    hasBevel = True
                    bname = mod.name


            if not hasBevel:
                context.view_layer.objects.active=obj
                bpy.ops.object.modifier_add(type='BEVEL')

                obj.modifiers[len(bpy.context.object.modifiers) - 1].limit_method = self.Type
                obj.modifiers[len(bpy.context.object.modifiers) - 1].width = self.bevel_width
                obj.modifiers[len(bpy.context.object.modifiers) - 1].segments = self.segments
                obj.modifiers[len(bpy.context.object.modifiers) - 1].profile = self.profile
                obj.modifiers[len(bpy.context.object.modifiers) - 1].use_clamp_overlap = self.clamp
                if self.Type=='ANGLE':
                    obj.modifiers[len(bpy.context.object.modifiers) - 1].angle_limit = self.angle
            else:
                obj.modifiers[bname].limit_method = self.Type
                obj.modifiers[bname].width = self.bevel_width
                obj.modifiers[bname].segments = self.segments
                obj.modifiers[bname].profile = self.profile
                obj.modifiers[bname].use_clamp_overlap = self.clamp
                if self.Type=='ANGLE':
                    obj.modifiers[bname].angle_limit = self.angle

            # bpy.context.object.modifiers[bname].limit_method

        return {'FINISHED'}

    def check(self, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_popup(self, event)

