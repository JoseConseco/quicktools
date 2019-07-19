import bpy
from bpy.props import *


### ------------ New Menus ------------ ###        

object_mode = 'OBJECT'
edit = 'EDIT'
sculpt = 'SCULPT'
vertex_paint = 'VERTEX_PAINT'
weight_paint = 'WEIGHT_PAINT'
texture_paint = 'TEXTURE_PAINT'
particle_edit = 'PARTICLE_EDIT'
pose = 'POSE'

# creates a menu for Sculpt mode tools
class QUICKT_MT_QuickSculptTools(bpy.types.Menu):

    bl_label = "Quick Sculpt Tools"
    bl_idname = "QUICKT_MT_QuickSculptTools"

    def draw(self, context):
        toolsettings = context.tool_settings
        sculpt = toolsettings.sculpt
        brush = sculpt.brush
        if context.sculpt_object and brush:
            layout = self.layout
            capabilities = brush.sculpt_capabilities

            # bpy.context.tool_settings.sculpt.brush=bpy.data.brushes['Nudge']
            layout.menu(QUICKT_MT_BrushesMenu.bl_idname, "Brush", icon_value=layout.icon(brush))
            if capabilities.has_plane_offset:
                layout.prop(brush, "plane_offset", slider=True)
            if context.sculpt_object.use_dynamic_topology_sculpting:
                layout.operator("sculpt.dynamic_topology_toggle", icon='X', text="Disable Dyntopo")
                # layout = layout.column()
                layout.prop_menu_enum(sculpt, "detail_refine_method", text="Detail refine method")
                layout.prop_menu_enum(sculpt, "detail_type_method", text="Detail type method")
                if sculpt.detail_type_method == 'CONSTANT':
                    layout.prop(sculpt, "constant_detail", slider=True)
                    layout.operator("sculpt.sample_detail_size", text="Sample detail size", icon='EYEDROPPER')
                elif sculpt.detail_type_method == 'BRUSH':
                    layout.prop(sculpt, "detail_percent", slider=True)
                else:
                    layout.prop(sculpt, "detail_size", slider=True)
                layout.separator()
                layout.prop(sculpt, "use_smooth_shading")
                layout.operator("sculpt.optimize")
                if sculpt.detail_type_method == 'CONSTANT':
                    layout.operator("sculpt.detail_flood_fill")
            else:
                layout.operator("sculpt.dynamic_topology_toggle", text="Enable Dyntopo", icon='SCULPTMODE_HLT')
            layout.separator()

            layout.prop(sculpt, "use_symmetry_x", text="Enable X symmetry", toggle=True)



class QUICKT_MT_BrushesMenu(bpy.types.Menu):
    bl_label = "Brush"
    bl_idname = "QUICKT_MT_BrushesMenu"

    def draw(self, context):
        layout = self.layout
        for brush in bpy.data.brushes:
            if brush.use_paint_sculpt:
                row = layout.row()
                props = row.operator("wm.context_set_id", text=brush.name,icon_value=row.icon(brush))
                props.data_path = "tool_settings.sculpt.brush"
                props.value = brush.name




    
