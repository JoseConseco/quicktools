import bpy
from mathutils import Vector
import gpu
from gpu_extras.batch import batch_for_shader

shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
indices = ( (0, 1, 2), (1, 3, 2))


class QUICKT_OT_SplitAreaPie(bpy.types.Operator):
    bl_idname = "screen.split_area_pie"
    bl_label = "Split Area Pie"
    bl_options = {'REGISTER', 'UNDO'}

    new_area_type: bpy.props.EnumProperty(name="New Area Type", description="", default="VIEW_3D",
                                            items=(("VIEW_3D", "3D View", ""),
                                                    ("IMAGE_EDITOR", "Image Editor", ""),
                                                    ("NODE_EDITOR", "Geometry Nodes", ""),
                                                    # ("DOPESHEET_EDITOR", "Dope Sheet", ""),
                                                    # ("GRAPH_EDITOR", "Graph Editor", ""),
                                                    ("TEXT_EDITOR", "Text Editor", ""),
                                                    ("CONSOLE", "Console", ""),
                                                    ("INFO", "Info", ""),
                                                    ("OUTLINER", "Outliner", ""),
                                                    # ("PROPERTIES", "Properties", ""),
                                                    # ("FILE_BROWSER", "File Browser", ""),
                                                    # ("PREFERENCES", "Preferences", ""),
                                                    # ("EMPTY", "Empty", ""),
                                                    ("UV", "UV", ""),
                                                    # ("SEQUENCE", "Sequence", ""),
                                                ))

    def draw_callback_px(tmp, self, context):
        # draw horizontal line or vertical line through area, depending on self.mouse_x and self.mouse_y
        print('drawing')
        area = context.area

        # get the area's width and height
        width = area.width
        height = area.height

        # get the area's center
        center_x = area.x + width / 2
        center_y = area.y + height / 2

        # get the mouse position relative to the area's center
        mouse_x = self.mouse_x - center_x
        mouse_y = self.mouse_y - center_y

        # get the mouse position as a vector
        mouse_vector = Vector((mouse_x, mouse_y))

        # get the mouse position as a percentage of the area's width and height
        mouse_x_percent = mouse_x / width
        mouse_y_percent = mouse_y / height

        line_points = []
        rect_points = [] #
        if abs(mouse_x_percent) > abs(mouse_y_percent):
            line_points = [(self.mouse_x, 0), (self.mouse_x, height)]
            if mouse_x_percent > 0: # right
                rect_points = [(self.mouse_x, 0), (width, 0), (self.mouse_x, height), (width, height)]
            else: # left
                rect_points = [(0, 0), (self.mouse_x, 0), (0, height), (self.mouse_x, height)]

        else:
            line_points = [(0, self.mouse_y), (width, self.mouse_y)]
            if mouse_y_percent > 0: # top
                rect_points = [(0, self.mouse_y), (width, self.mouse_y), (0, height), (width, height)]
            else: # bottom
                rect_points = [(0, 0), (width, 0), (0, self.mouse_y), (width, self.mouse_y)]


        batch = batch_for_shader(shader, 'TRIS', {"pos": rect_points}, indices=indices)
        gpu.state.blend_set('ALPHA')
        shader.bind()
        shader.uniform_float("color", (1.0, 1.0, 1.0, 0.2))
        batch.draw(shader)

        batch = batch_for_shader(shader, 'LINES', {"pos": line_points})
        shader.bind()
        shader.uniform_float("color", (1.0, 1.0, 1.0, 1.0))
        batch.draw(shader)

        gpu.state.blend_set('NONE')


    def invoke(self, context, event):
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_callback_px, args, "WINDOW", "POST_PIXEL")

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


    def modal(self, context, event):
        if event.type == "LEFTMOUSE" and event.value == "RELEASE":
            self.mouse_x = event.mouse_x
            self.mouse_y = event.mouse_y
            return self.finish(context, event)

        elif event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_x
            self.mouse_y = event.mouse_y
            context.area.tag_redraw()

        if event.type in {"RIGHTMOUSE", "ESC"}:
            return self.cancelled(context, event)

        return {"RUNNING_MODAL"}

    def finish(self, context, event):
        area = context.area

        # get the area's width and height
        width = area.width
        height = area.height

        # get the area's center
        center_x = area.x + width / 2
        center_y = area.y + height / 2

        # get the mouse position relative to the area's center
        mouse_x = self.mouse_x - center_x
        mouse_y = self.mouse_y - center_y

        # get the mouse position as a vector
        mouse_vector = Vector((mouse_x, mouse_y))

        # get the mouse position as a percentage of the area's width and height
        mouse_x_percent = mouse_x / width
        mouse_y_percent = mouse_y / height


        if abs(mouse_x_percent) > abs(mouse_y_percent):
            if mouse_x_percent > 0:
                split = 'RIGHT'
            else:
                split = 'LEFT'
        else:
            if mouse_y_percent > 0:
                split = 'TOP'
            else:
                split = 'BOTTOM'

        print(f'mouse_x_percent: {mouse_x_percent}')
        print(f'mouse_y_percent: {mouse_y_percent}')
        print(f'split: {split}')

        if split in ('RIGHT','LEFT'):
            bpy.ops.screen.area_split( direction='VERTICAL', factor=self.mouse_x/width) # 'INVOKE_DEFAULT',
            if split == 'RIGHT':
                context.area.type = self.new_area_type
                if self.new_area_type == 'NODE_EDITOR':
                    context.area.ui_type = 'GeometryNodeTree'
            else:
                context.screen.areas[-1].type = self.new_area_type
                if self.new_area_type == 'NODE_EDITOR':
                    context.screen.areas[-1].ui_type = 'GeometryNodeTree'

        else:
            bpy.ops.screen.area_split( direction='HORIZONTAL', factor=self.mouse_y/height) #'INVOKE_DEFAULT',
            if split == 'TOP':
                context.area.type = self.new_area_type
                if self.new_area_type == 'NODE_EDITOR':
                    context.area.ui_type = 'GeometryNodeTree'
            else:
                context.screen.areas[-1].type = self.new_area_type
                if self.new_area_type == 'NODE_EDITOR':
                    context.screen.areas[-1].ui_type = 'GeometryNodeTree'

        bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
        return {"FINISHED"}

    def cancelled(self):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
        return {"CANCELLED"}


# create pie menu
class QUICKT_MT_SplitAreaPie(bpy.types.Menu):
    bl_idname = "QUICKT_MT_SplitAreaPie"
    bl_label = "Split Area Pie"

    def draw(self, context):
        layout = self.layout

        layout.operator_context = "INVOKE_DEFAULT"
        pie = layout.menu_pie()
        pie.operator("screen.split_area_pie", text='View 3D').new_area_type = 'VIEW_3D'
        pie.operator("screen.split_area_pie", text="Image Editor").new_area_type = 'IMAGE_EDITOR'
        pie.operator("screen.split_area_pie", text="Geometry Nodes").new_area_type = 'NODE_EDITOR'
        # pie.operator("screen.split_area_pie", text="VIEW_3D").new_area_type = 'DOPESHEET_EDITOR'
        # pie.operator("screen.split_area_pie", text="VIEW_3D").new_area_type = 'GRAPH_EDITOR'
        pie.operator("screen.split_area_pie", text="Text Editor").new_area_type = 'TEXT_EDITOR'
        pie.operator("screen.split_area_pie", text="Console").new_area_type = 'CONSOLE'
        pie.operator("screen.area_close", text="Close Area", icon='X')


