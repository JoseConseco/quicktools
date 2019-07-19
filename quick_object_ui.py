import bpy


class QUICKT_MT_QuickObjectTools(bpy.types.Menu):
    bl_label = "Quick Object Tools"
    bl_idname = "QUICKT_MT_QuickObjectTools"

    def draw(self, context):
        layout = self.layout
        layout.menu(QUICKT_MT_SmartModifiers.bl_idname, "Add Smart Modifier", icon='MODIFIER')

        layout.operator_menu_enum("object.modifier_add", "type", icon='MODIFIER')
        layout.operator("object.apply_modifiers")
        layout.operator("object.modifier_remove_all", "Remove All Modifiers")

        try:
            layout.separator()
            if bpy.context.scene.pivot_pro_enabled:
                layout.prop(context.scene, "pivot_pro_enabled", text='Disable PivotPro', icon='OUTLINER_OB_EMPTY')
                layout.operator("object.pivot_snap")
            else:
                layout.prop(context.scene, "pivot_pro_enabled", text='Enable PivotPro', icon='OUTLINER_OB_EMPTY')
        except:
            pass
        layout.separator()
        layout.menu(QUICKT_MT_SetShapeKeys.bl_idname, "ShapeKeys")

        layout.separator()
        xLay = layout.operator("object.mesh_halve", "Halve in X and Mirror")
        xLay.yAxis = False
        xLay.zAxis = False
        layout.separator()



class QUICKT_MT_SetShapeKeys(bpy.types.Menu):
    bl_idname = "QUICKT_MT_SetShapeKeys"
    bl_label = "Quick Shape Keys"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.clone_shapekey")
        layout.operator("object.mirror_shapekey")
        layout.operator("object.apply_shapekey_mask")
        layout.operator("object.corrective_shapekey")


class QUICKT_MT_SmartModifiers(bpy.types.Menu):
    bl_idname = "QUICKT_MT_SmartModifiers"
    bl_label = "Smart Modifiers"

    def draw(self, context):
        from mathutils import Vector
        layout = self.layout
        radClone = layout.operator("object.radial_clone", icon='MOD_ARRAY')
        if context.active_object.type == "EMPTY" and context.active_object.dupli_group:
            bBoxCoordList = list(context.active_object.dupli_group.BBoxVertsList)
            width = Vector((bBoxCoordList[3], bBoxCoordList[4], bBoxCoordList[5]))-Vector((bBoxCoordList[0], bBoxCoordList[1], bBoxCoordList[2]))
            length = width.length
            radClone.Radius = length*1.5
        else:
            radClone.Radius = context.active_object.dimensions.length
        layout.operator("object.bend_array", icon='MOD_ARRAY')
        layout.separator()
        layout.operator("object.empty_add_unactive", "Add Target", icon='CURSOR')

        bevel = layout.operator("object.quickbevel", "Bevel", icon='MOD_BEVEL')
        hasBevel = False
        bname = ''
        for mod in context.active_object.modifiers:
            if mod.type == "BEVEL":
                hasBevel = True
                bname = mod.name
        if hasBevel:
            bevel.bevel_width = context.active_object.modifiers[bname].width
            bevel.segments = context.active_object.modifiers[bname].segments
            bevel.Type = context.active_object.modifiers[bname].limit_method
            if bevel.Type == 'ANGLE':
                bevel.angle = context.active_object.modifiers[bname].angle_limit

            bevel.profile = context.active_object.modifiers[bname].profile
            bevel.clamp = context.active_object.modifiers[bname].use_clamp_overlap

        solidify = layout.operator("nw.solidify", "Thickness", icon='MOD_SOLIDIFY')
        hasSolidify = False
        bname = ''
        for mod in context.active_object.modifiers:
            if mod.type == "SOLIDIFY":
                hasSolidify = True
                bname = mod.name
        if hasSolidify:
            solidify.thickness = context.active_object.modifiers[bname].thickness
            solidify.offset = context.active_object.modifiers[bname].offset

        layout.operator("object.add_array", "Array", icon='MOD_ARRAY')
        layout.operator("object.add_boolean", "Boolean", icon='MOD_BOOLEAN')
        layout.operator("object.add_cast", "Cast", icon='MOD_CAST')
        layout.operator("object.add_mirror", "Mirror", icon='MOD_MIRROR')
        layout.operator("object.add_lattice", "Lattice", icon='MOD_LATTICE')
        layout.operator("object.add_screw", "Screw", icon='MOD_SCREW')
