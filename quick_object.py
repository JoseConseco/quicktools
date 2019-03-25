import numpy as np

import bpy
import bgl
import bmesh
from bpy import ops
from bpy.props import BoolProperty, IntProperty
from bpy_extras import view3d_utils
from mathutils import Color, Matrix, Quaternion, Vector, kdtree

###################################################
# Halve the mesh and add a Mirror modifier
###################################################


def select_off_center(self, context):
    obj = context.active_object.data

    for verts in obj.vertices:
        if verts.co.x < -0.001:
            verts.select = True


def select_Yoff_center(self, context):
    obj = context.active_object.data

    for verts in obj.vertices:
        if verts.co.y > 0.001:
            verts.select = True


def select_Zoff_center(self, context):
    obj = context.active_object.data

    for verts in obj.vertices:
        if verts.co.z < -0.001:
            verts.select = True


class QUICKT_OT_CutMeshInHalfAndMirror(bpy.types.Operator):
    """Delete all vertices on the -X side of center"""
    bl_idname = "object.mesh_halve"
    bl_label = "Cut and mirror"
    bl_options = {'REGISTER', 'UNDO'}
    xAxis: bpy.props.BoolProperty(default=True)
    yAxis: bpy.props.BoolProperty(default=False)
    zAxis: bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):

        obj = context.active_object.data
        selected = context.selected_objects
        # Go to edit mode and ensure all vertices are deselected, preventing accidental deletions
        if context.object.mode == 'OBJECT':
            backupActive = context.view_layer.objects.active
            for obj in selected:
                if obj.type == 'MESH':
                    context.view_layer.objects.active = obj

                    ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    if self.xAxis == True:
                        bpy.ops.mesh.symmetrize(direction='POSITIVE_X')
                    if self.yAxis == True:
                        bpy.ops.mesh.symmetrize(direction='NEGATIVE_Y')
                    if self.zAxis == True:
                        bpy.ops.mesh.symmetrize(direction='POSITIVE_Z')
                    bpy.ops.mesh.select_all(action='DESELECT')
                    ops.object.mode_set(mode='OBJECT')

                    # Find verts left of center and select them
                    if self.xAxis == True:
                        select_off_center(self, context)
                    if self.yAxis == True:
                        select_Yoff_center(self, context)
                    if self.zAxis == True:
                        select_Zoff_center(self, context)
                    ops.object.mode_set(mode='EDIT')
                    ops.mesh.delete(type='VERT')

                    # Switch back to object mode and add the mirror modifier
                    ops.object.mode_set(mode='OBJECT')
                    bpy.context.object.modifiers.new(type="MIRROR", name="CutMirror")
                    bpy.context.object.modifiers["CutMirror"].use_clip = True
                    bpy.context.object.modifiers["CutMirror"].use_axis = [self.xAxis, self.yAxis, self.zAxis]
                    self.report({'INFO'}, "Mesh half removed and Mirror modifier added")
                else:
                    self.report({'INFO'}, "Only works on mesh objects")
                # move to top modifier stack
                for i, mod in enumerate(obj.modifiers):
                    if mod.name == 'CutMirror':
                        bpy.context.view_layer.objects.active = obj
                        for x in range(0, i):
                            bpy.ops.object.modifier_move_up(modifier=mod.name)
            context.view_layer.objects.active = backupActive
        return {'FINISHED'}


###################################################
# Set object origin to center of current mesh selection in edit mdoe
###################################################

class QUICKT_OT_setObjectOrigin(bpy.types.Operator):
    """Set Object Origin To Center Of Current Mesh Selection"""
    bl_idname = "mesh.origin_to_mesh_select"
    bl_label = "Origin to mesh selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mode = bpy.context.object.mode
        if mode != 'EDIT':
            self.report({'INFO'}, "Must be run in Edit Mode")
        else:
            ops.view3d.snap_cursor_to_selected()
            ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            ops.object.mode_set(mode='EDIT')

        return {"FINISHED"}


bpy.types.Scene.bevelWeight = bpy.props.FloatProperty(name="Bevel Weight", description="", default=1.0, min=0.0, max=1.0)


class QUICKT_OT_setBevelWeight(bpy.types.Operator):
    bl_idname = "mesh.set_bevel_weight"
    bl_label = "Set Bevel Weight"
    bl_options = {'REGISTER', 'UNDO'}

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def execute(self, context):
        mode = context.object.mode
        if mode != 'EDIT':
            # If user is not in object mode, don't run the operator and report reason to the Info header
            self.report({'INFO'}, "Must be run in Edit Mode")
        else:
            text = context.window_manager.clipboard
            mesh = bpy.context.active_object.data
            mesh.show_edge_bevel_weight = True
            bm = bmesh.from_edit_mesh(mesh)
            bw = bm.edges.layers.bevel_weight.verify()

            for edge in bm.edges:
                if (edge.select):
                    edge[bw] = context.scene.bevelWeight
            # trigger UI update
            bmesh.update_edit_mesh(mesh)
        return {"FINISHED"}

