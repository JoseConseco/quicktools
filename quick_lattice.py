'''
Copyright (C) 2017 JOSECONSCO
Created by JOSECONSCO

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import bpy
import numpy as np
from mathutils import Vector, Matrix

def get_scale_mat(vec_scale):
    mat_scale = Matrix.Identity(4)
    mat_scale[0][0] = vec_scale.x
    mat_scale[1][1] = vec_scale.y
    mat_scale[2][2] = vec_scale.z
    return mat_scale


def set_lattice_transformation(selected_objs):
    ''' return (center, sizex, sizey, sizez) '''
    patter_count = len(selected_objs)
    mode = bpy.context.active_object.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    if patter_count == 1:  # get local space cos we will align lattice to it anyway
        points = [vert.co for vert in selected_objs[0].data.vertices] if mode == 'OBJECT' else  [vert.co for vert in selected_objs[0].data.vertices if vert.select] 
        if mode == 'EDIT' and len(points)>0:
            if 'QuickLatticeMask' in selected_objs[0].vertex_groups.keys():
                vg = selected_objs[0].vertex_groups["QuickLatticeMask"]
            else:
                vg = selected_objs[0].vertex_groups.new(name="QuickLatticeMask")
            vg.add([vert.index for vert in selected_objs[0].data.vertices if vert.select] , 1, "ADD")
    else:
        points = []
        for obj in selected_objs:
            verts_co = [obj.matrix_world@vert.co for vert in obj.data.vertices] if mode == 'OBJECT' else [obj.matrix_world@vert.co for vert in obj.data.vertices if vert.select]
            points.extend(verts_co)
            if mode == 'EDIT' and len(verts_co)>0:
                if 'QuickLatticeMask' in obj.vertex_groups.keys():
                    vg = obj.vertex_groups["QuickLatticeMask"]
                else:
                    vg = obj.vertex_groups.new(name="QuickLatticeMask")
                vg.add([vert.index for vert in obj.data.vertices if vert.select] , 1, "ADD")

    np_points = np.array(points)
    max_x = np.max(np_points[:, 0])
    max_y = np.max(np_points[:, 1])
    max_z = np.max(np_points[:, 2])
    min_x = np.min(np_points[:, 0])
    min_y = np.min(np_points[:, 1])
    min_z = np.min(np_points[:, 2])

    # center = Vector((max_x+min_x, max_y+min_y, max_z+min_z)) * 0.5
    vec_scale = Vector((max(max_x-min_x, 0.1), max(max_y-min_y, 0.1), max(max_z-min_z, 0.1))) 

    mat_loc = Matrix.Translation(((max_x+min_x)/2, (max_y+min_y)/2, (max_z+min_z)/2))
    mat_sca = get_scale_mat(vec_scale)
    # mat_rot = selected_objs[0].matrix_world.to_quaternion().to_matrix().to_4x4()

    if patter_count == 1:
        out_mat = selected_objs[0].matrix_world  @ mat_loc  @ mat_sca
    else:
        out_mat = mat_loc @ mat_sca

    return out_mat


def set_lattice(context, name, target_objs):
    lattice = bpy.data.lattices.new(name)
    lattice.points_u = 2
    lattice.points_v = 2
    lattice.points_w = 2
    lattice_ob = bpy.data.objects.new(name, lattice)
    context.scene.collection.objects.link(lattice_ob)

    # lattice_ob.rotation_euler = align_obj.rotation_euler
    new_mat_transform = set_lattice_transformation(target_objs)
    lattice_ob.matrix_world = new_mat_transform
    return lattice_ob


def setup_modifiers(context, mod_name):
    mode = context.active_object.mode
    selected_objects = [obj for obj in context.selected_objects]
    mod_target_obj = set_lattice(context, name=mod_name, target_objs=selected_objects)
    for obj in selected_objects:
        lat_modifier = obj.modifiers.new(name=mod_name, type='LATTICE')
        lat_modifier.object = mod_target_obj
        if mode == 'EDIT':
            lat_modifier.vertex_group = 'QuickLatticeMask'
    context.view_layer.objects.active = mod_target_obj
    return


class QUICKT_OT_QuickLattice(bpy.types.Operator):
    bl_idname = "object.quick_lattice_add"
    bl_label = "Quick Lattice"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        setup_modifiers(context, 'Quick_Lattice')
        return {'FINISHED'}

class QUICKT_OT_QuickLatticeApply(bpy.types.Operator):
    bl_idname = "object.quick_lattice_apply"
    bl_label = "Quick Lattice Apply"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        lattice = context.active_object
        if lattice.type != 'LATTICE':
            return {'CANCELLED'}
        backup_active_obj = context.view_layer.objects.active
        for obj in context.view_layer.objects:
            if 'Quick_Lattice' in obj.modifiers.keys():
                context.view_layer.objects.active = obj
                bpy.ops.object.modifier_apply(modifier="Quick_Lattice")
                if "QuickLatticeMask" in obj.vertex_groups.keys():
                    obj.vertex_groups.remove(obj.vertex_groups["QuickLatticeMask"])
        context.view_layer.objects.active = backup_active_obj
        return {'FINISHED'}
