import bpy
from mathutils import Vector, Matrix
import numpy as np
from bpy_extras import view3d_utils


class QUICKT_OT_ArmatureDisableConstranits(bpy.types.Operator):
    bl_idname = "armature.toogle_constraints"
    bl_label = "Toogle Constraints"
    bl_options = {'REGISTER','UNDO'}

    mute: bpy.props.BoolProperty(name="Mute", default=False)

    @classmethod
    def poll(cls, context):
       return context.object is not None

    def execute(self, context):
        active_obj = context.active_object
        if active_obj.type=='ARMATURE' and active_obj.mode == 'POSE':
            for p_bone in active_obj.pose.bones:
                if p_bone.bone.select:
                    for constraint in p_bone.constraints:
                        constraint.mute = self.mute
        
        return {'FINISHED'}


class QUICKT_OT_SnapEmptiesToBoneTails(bpy.types.Operator):
    bl_idname = "armature.snap_empties_to_bones"
    bl_label = "Snap Empties"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
       return context.object is not None

    def execute(self, context):
        active_obj = context.active_object
        arma_obj = None
        for obj in context.selected_objects:
            if obj.type == 'ARMATURE':
                arma_obj = obj
                break
        if arma_obj is None:
            for obj in context.scene.objects:
                if obj.type == 'ARMATURE':
                    arma_obj = obj
                    break
        if arma_obj is None:
            self.report({'INFO'}, 'No armature found. Cancelling.')
            return {'CANCELLED'}

        for obj in context.selected_objects:
            if obj.type == 'EMPTY':
                if obj.name in arma_obj.pose.bones.keys():
                    obj.matrix_world.translation = arma_obj.matrix_world * arma_obj.pose.bones[obj.name].tail
        
        return {'FINISHED'}



class QUICKT_OT_StraightenBoneChain(bpy.types.Operator):
    bl_idname = "armature.straighten_bone_chain"
    bl_label = "Straighten bones chain"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
       return context.object is not None

    def execute(self, context):
        active_obj = context.active_object
        if active_obj.type == 'ARMATURE':
            selected_bones = [p_bone for p_bone in active_obj.data.edit_bones if p_bone.select]
            selected_bones_names = [p_bone.name for p_bone in active_obj.data.edit_bones if p_bone.select]

        bone_sorted = []        
        for bone in selected_bones:
            if bone.parent.name not in selected_bones_names:
                bone_sorted.append(bone)
                break

        children = bone_sorted[0].children
        while True:
            if len(children)>0:
                if children[0].name in selected_bones_names:
                    bone_sorted.append(children[0])
                    children = children[0].children
                else: 
                    break
            else: 
                break
        for b in bone_sorted:
            print(b.name)

        start_pos = bone_sorted[0].head
        end_pos = bone_sorted[-1].tail
        diff = end_pos - start_pos
        diff_normalized = diff/len(bone_sorted)
    
        for i, bone in enumerate(bone_sorted):
            bone.head = start_pos + i * diff_normalized
            bone.tail = start_pos + (i+1) * diff_normalized

        return {'FINISHED'}

