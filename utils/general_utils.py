
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
import gpu
import bgl
from math import sqrt
from mathutils import Matrix, Vector
from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils
import blf
import bpy
import math
from mathutils.bvhtree import BVHTree


def obj_ray_cast(obj, ray_origin, ray_target, depsgraph=None):
    # get the ray relative to the object
    ray_direction = ray_target - ray_origin
    sourceTri_BVHT = get_obj_mesh_bvht(obj, depsgraph=None)  # [0,1,2] - polygon == vert indices list
    # location, normal, index, dist =
    return sourceTri_BVHT.ray_cast(ray_origin, ray_direction, 600)


def view_obj_raycast(context, obj, event, applyModifiers=True, depsgraph=None, world_space=True):
    ''' Return index of pin closest to mouse'''
    """Run this function on left mouse, execute the ray cast"""
    region = context.region
    rv3d = context.region_data
    coord = event.mouse_region_x, event.mouse_region_y
    # coord = mouse_coordinates

    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

    sourceTri_BVHT = get_obj_mesh_bvht(obj, applyModifiers=applyModifiers, depsgraph=depsgraph, world_space=False)  # do not transform worldspace for performance

    matrix_inv = obj.matrix_world.inverted()  # faster than transforming whole mesh
    ray_origin_obj = matrix_inv @ ray_origin
    view_vector_obj = matrix_inv @ Vector(view_vector.xyz[:]+(0,))
    hit_local, normal, index, dist = sourceTri_BVHT.ray_cast(ray_origin_obj, view_vector_obj.xyz)
    # get the ray relative to the object
    if hit_local and world_space:  # cos we always hit in local space, for performance
        location = obj.matrix_world @ hit_local
    else:
        location = hit_local

    return location, normal, index, dist


def get_weights(ob, vgroup):
    group_index = vgroup.index
    return [[g.weight for g in vert.groups if g.group == group_index] for vert in ob.data.vertices]


def set_weights(obj, weights, vgroup):
    g_id = vgroup.index
    if not weights:
        obj.vertex_groups[g_id].remove([i for i in range(len(obj.data.vertices))])

    for v_id, weight in enumerate(weights):
        if weight:
            obj.vertex_groups[g_id].add([v_id], weight[0], "REPLACE")
        else:
            obj.vertex_groups[g_id].remove([v_id])


def get_obj_mesh_bvht(obj, depsgraph=None, applyModifiers=True, world_space=True):
    if applyModifiers:
        if world_space:
            # faster 4x  than:
            # obj.update_tag()
            # bpy.context.view_layer.update()
            depsgraph.objects[obj.name].data.transform(obj.matrix_world)
            bvh = BVHTree.FromObject(obj, depsgraph)
            depsgraph.objects[obj.name].data.transform(obj.matrix_world.inverted())

            return bvh
        else:
            return BVHTree.FromObject(obj, depsgraph)
    else:
        if world_space:
            # 4 times slower than data.transform
            #bvh1 =  BVHTree.FromPolygons([obj.matrix_world @ v.co for v in obj.data.vertices], [p.vertices for p in obj.data.polygons])
            obj.data.transform(obj.matrix_world)
            bvh = BVHTree.FromPolygons([v.co for v in obj.data.vertices], [p.vertices for p in obj.data.polygons])
            obj.data.transform(obj.matrix_world.inverted())
            return bvh
        else:
            return BVHTree.FromPolygons([v.co for v in obj.data.vertices], [p.vertices for p in obj.data.polygons])


def assign_material(obj, material_name, clear_materials=True):
    '''Add material to obj. If clear_material is True - reomve all slots except first.'''
    if material_name not in bpy.data.materials.keys():
        print('Material %s dosen\'t exist!' % (material_name))
        return
    mat = bpy.data.materials[material_name]
    if clear_materials is True:
        while len(obj.material_slots) > 1:
            obj.data.materials.pop()
    if len(obj.material_slots) == 0:  # make sure first slot is assigned
        obj.data.materials.append(mat)
    else:
        obj.material_slots[0].material = mat


def unlink_from_scene(obj):
    for col in obj.users_collection:
        col.objects.unlink(obj)
    if obj.name in bpy.context.scene.collection.objects.keys():
        bpy.context.scene.collection.objects.unlink(obj)
    obj.use_fake_user = True


def link_child_to_collection(parent_obj, clone):
    ''' Link clone to collection where parent_obj is located '''
    if parent_obj.users_collection:
        if clone.name not in parent_obj.users_collection[0].objects.keys():
            parent_obj.users_collection[0].objects.link(clone)
        else:
            return
    else:
        if clone.name not in bpy.context.scene.collection.objects.keys():
            bpy.context.scene.collection.objects.link(clone)
        else:
            return


def add_driver(source, target, prop, dataPath, index=-1, negative=False, func=''):
    ''' Add driver to source prop (at index), driven by target dataPath '''

    if index != -1:
        d = source.driver_add(prop, index).driver
    else:
        d = source.driver_add(prop).driver

    v = d.variables.new()
    v.name = prop
    v.targets[0].id = target
    v.targets[0].data_path = dataPath

    d.expression = func + "(" + v.name + ")" if func else v.name
    d.expression = d.expression if not negative else "-1 * " + d.expression


def angle_signed(vA, vB, vN):
    '''angle betwen a - b, is vN space '''
    a = vA.normalized()
    b = vB.normalized()
    adotb = a.dot(b)  # not sure why but cos(x) goes above 1, and below -1   if a= -b
    if a.dot(b) > 1:
        adotb = 1
    elif a.dot(b) < -1:
        adotb = -1
    angle = math.acos(adotb)
    cross = a.cross(b)
    if vN.dot(cross) < 0:  # // Or > 0
        angle = -angle
    return angle


def frange(x, y, jump):
    while x < y:
        yield x
        x += jump


def get_scale_mat(vec_scale):
    mat_scale = Matrix.Identity(4)
    mat_scale[0][0] = vec_scale.x
    mat_scale[1][1] = vec_scale.y
    mat_scale[2][2] = vec_scale.z
    return mat_scale


LEFT = ('l', 'L', 'left', 'Left', 'LEFT')
RIGHT = ('r', 'R', 'right', 'Right', 'RIGHT')


def is_name_r_l(name):
    return name.endswith(LEFT) or name.endswith(RIGHT)


def get_mirrored_name(name):
    for i, l_suffx in enumerate(LEFT):
        if name.endswith('.'+l_suffx) or name.endswith('_'+l_suffx):
            return name[:-1*len(l_suffx)] + RIGHT[i]
    for i, r_suffx in enumerate(RIGHT):
        if name.endswith('.'+r_suffx) or name.endswith('_'+r_suffx):
            return name[:-1*len(r_suffx)] + LEFT[i]
    return ''


LEFT_MARGIN = 80
TOP_POSITION = 250
BOX_WIDTH = 395


def draw_text_line(lines):
    line_height_h1 = 35
    line_height_p = 28
    font_id = 0
    current_line_pos = TOP_POSITION
    blf.color(font_id, 1.0, 1.0, 1.0, 0.87)
    for line in lines:
        text, line_type = line
        font_size = 24 if line_type == 'H1' else 20
        blf.size(font_id, font_size, 60)
        blf.position(font_id, LEFT_MARGIN, current_line_pos, 0)
        blf.draw(font_id, text)
        if line_type == 'H1':
            current_line_pos -= line_height_h1
        else:
            current_line_pos -= line_height_p
    draw_background_box(width=BOX_WIDTH, height=TOP_POSITION +
                        line_height_h1, x0=LEFT_MARGIN-20, y0=current_line_pos)


shader2d = gpu.shader.from_builtin('2D_UNIFORM_COLOR')


def draw_background_box(width, height, x0, y0):
    # draw box
    x1 = width
    y1 = height
    positions = [[x0, y0], [x0, y1], [x1, y1], [x1, y0]]

    vertices = (
        (x0, y0), (width, y0),
        (x0, height), (width, height))
    indices = ((0, 1, 2), (2, 1, 3))
    bgl.glEnable(bgl.GL_BLEND)
    batch = batch_for_shader(shader2d, 'TRIS', {"pos": vertices}, indices=indices)

    shader2d.bind()
    shader2d.uniform_float("color", (0., 0., 0., 0.3))
    batch.draw(shader2d)
    bgl.glDisable(bgl.GL_BLEND)


def get_addon_name():
    return __package__.split(".")[0]


def addon_name_lowercase():
    return get_addon_name().lower()


def get_addon_preferences():
    return bpy.context.preferences.addons[get_addon_name()].preferences


def get_mat_world_obj(obj):
    obj.matrix_basis == (Matrix.Translation(obj.location) @ obj.rotation_quaternion.to_matrix().to_4x4() @ get_scale_mat(obj.scale))
    # replace rotation_quaternion with rotation_euler if you are using Euler mode
    matrix_local = obj.matrix_parent_inverse @ obj.matrix_basis
    matrix_world = matrix_local if obj.parent is None else obj.parent.matrix_word @ matrix_local
    return matrix_world


def create_obj_copy(obj, instance=False):
    'create object copy, non instance'
    clone = obj.copy()  # copy object
    clone.data = obj.data.copy()  # and its data
    clone.matrix_world = obj.matrix_world
    link_to_collection_sibling(obj, clone)
    if instance:
        clone.name = obj.name+'.l'
        obj.name = obj.name+'.r'
    return clone


def get_new_mat_parent_inv(old_parent_m_w, new_parent_m_w, old_obj_m_p_inv):
    ''' cos: old_m_w == new_m_w'''
    ''' so:  old_parent_m_w @ obj.m_p_inv1 @ obj.m_basis  ==  new_parent_m_w @ obj.m_p_inv2 @ obj.m_basis'''
    ''' so:  old_parent_m_w @ obj.m_p_inv1 @ new_parent_m_w.inv()   ==   obj.m_p_inv2'''
    return old_parent_m_w @ old_obj_m_p_inv @ new_parent_m_w.inverted()


def clear_parent(obj):
    parent = obj.parent
    if parent:
        obj.matrix_basis = parent.matrix_world @ obj.matrix_parent_inverse @ obj.matrix_basis
        obj.parent = None


def set_parent(obj, new_parent):
    if obj.parent:  # if there is old parent
        old_parent_m_w = obj.parent.matrix_world
        new_m_p_inv = old_parent_m_w @ obj.matrix_parent_inverse @ new_parent.matrix_world.inverted()
        obj.matrix_parent_inverse = new_m_p_inv
    else:
        obj.matrix_parent_inverse = new_parent.matrix_world.inverted()
    obj.parent = new_parent


def link_to_collection_sibling(source_obj, clone):
    ''' Link clone to collection where source_obj is located '''
    if source_obj.users_collection:
        for obj_coll in source_obj.users_collection:
            if clone.name not in obj_coll.objects.keys():
                obj_coll.objects.link(clone)
    else:
        if clone.name not in bpy.context.scene.collection.objects.keys():
            bpy.context.scene.collection.objects.link(clone)


def get_all_subcollections(current_coll):
    '''Get all sub collections (including nested) for searched collection'''
    child_colls = []
    for coll in current_coll.children:
        child_colls.extend(get_all_subcollections(coll))
    return child_colls + current_coll.children[:]


def find_create_collection(parent_col, searched_col_name):
    ''' Try to find searched collection name in parent childrens. If not found create it and link it to master'''
    def find_coll(p_coll, search_col):
        if search_col == p_coll.name:
            return True
        if search_col in p_coll.children.keys():
            return True
        else:
            for child_col in p_coll.children:
                if find_coll(child_col, search_col):
                    return True
        return False

    if find_coll(parent_col, searched_col_name):
        collection = bpy.data.collections[searched_col_name]
    else:
        if searched_col_name in bpy.data.collections.keys():
            collection = bpy.data.collections[searched_col_name]
        else:
            collection = bpy.data.collections.new(searched_col_name)
        parent_col.children.link(collection)
    return collection

