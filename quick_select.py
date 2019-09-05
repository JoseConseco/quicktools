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
import bmesh
from mathutils import Vector, Matrix


def other_not_selected_edges(vert, edge):
    for ed in vert.link_edges:
        if ed != edge and not ed.select:
            yield ed


class MESH_OT_GrowLoop(bpy.types.Operator):
    bl_idname = "mesh.grow_loop"
    bl_label = "Grow Loop"
    bl_description = "Grow loop"
    bl_options = {"REGISTER","UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        obj = context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        selected_edges = [e for e in bm.edges if e.select]
        edges_to_select = []
        for e in selected_edges:
            for vert in e.verts:
                e_link_faces = set(e.link_faces)
                if len(vert.link_edges) == 4:
                    for other_edge in other_not_selected_edges(vert, e):
                        if not e_link_faces & set(other_edge.link_faces):
                            edges_to_select.append(other_edge)
                            break
                elif len(vert.link_edges) == 2:
                    for other_edge  in other_not_selected_edges(vert, e):
                        e_vec = vert.co - e.other_vert(vert).co #from A -> Vert
                        other_e_vec = other_edge.other_vert(vert).co - vert.co # from vert  -> B
                        if e_vec.dot(other_e_vec) < - 3.14 * (2/3):
                            edges_to_select.append(other_edge)

                elif len(vert.link_edges) == 3:
                    for other_edge in other_not_selected_edges(vert, e):
                        common_face = e_link_faces & set(other_edge.link_faces)
                        if not common_face:
                            edges_to_select.append(other_edge)
                        elif common_face and len(common_face.pop().edges) > 4:
                            edges_to_select.append(other_edge)
        for e in edges_to_select:  # may contain duplicates but whatever
            e.select = True
                        
        bmesh.update_edit_mesh(me, True)
        return {"FINISHED"}


class MESH_OT_ShrinkLoop(bpy.types.Operator):
    bl_idname = "mesh.shrink_loop"
    bl_label = "Shrink Loop"
    bl_description = "Shrink loop"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        obj = context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        selected_edges = [e for e in bm.edges if e.select]
        deselect_border_edges = []
        for e in selected_edges:
            e_link_faces = set(e.link_faces)
            for vert in e.verts:
                other_nonsel_e = list(other_not_selected_edges(vert, e))
                other_nonsel_e_count = len(other_nonsel_e)
                if len(vert.link_edges) == 4 and other_nonsel_e_count == 3:  # vert is the end of loop. So mark it for deselect
                    deselect_border_edges.append(e)
                elif len(vert.link_edges) == 2 and other_nonsel_e_count == 1:
                    deselect_border_edges.append(e)

                elif len(vert.link_edges) == 3 and other_nonsel_e_count == 2:
                    deselect_border_edges.append(e)
        for e in deselect_border_edges:#may contain duplicates but whatever
            e.select = False
        bmesh.update_edit_mesh(me, True)
        return {"FINISHED"}


class MESH_OT_LoopToRing(bpy.types.Operator):
    bl_idname = "mesh.loops_to_rigns"
    bl_label = "Loops to rings"
    bl_description = "Loops to rings"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        obj = context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        selected_faces = [f for f in bm.faces if all([v.select for v in f.verts]) ]
        edges_to_select = []
        for f in selected_faces:
            for e in f.edges:
                if not e.select:
                    edges_to_select.append(e)
        for e in bm.edges:
            e.select = False
        e = None
        for e in set(edges_to_select):
            e.select = True
        bm.select_history.clear()
        if e:
            bm.select_history.add(e) #make active
        bmesh.update_edit_mesh(me, True)
        return {"FINISHED"}

class MESH_OT_GrowRing(bpy.types.Operator):
    bl_idname = "mesh.grow_ring"
    bl_label = "Grow Ring"
    bl_description = "Grow ring"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        obj = context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        selected_edges = [e for e in bm.edges if e.select]
        edges_to_select = []
        for e in selected_edges:
            for loop in e.link_loops:
                if len(loop.face.edges) == 4:
                    edges_to_select.append(loop.link_loop_next.link_loop_next.edge)
        for e in edges_to_select:
            e.select = True
        bmesh.update_edit_mesh(me, True)
        return {"FINISHED"}


class MESH_OT_ShrinkRing(bpy.types.Operator):
    bl_idname = "mesh.shrink_ring"
    bl_label = "Shrink Ring"
    bl_description = "Shrink ring"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        obj = context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        selected_edges = [e for e in bm.edges if e.select]
        edges_to_deselect = []
        for e in selected_edges:
            for loop in e.link_loops: #? two loops if edge has 2 faces. What if not....
                if len(loop.face.edges) == 4 and not loop.link_loop_next.link_loop_next.edge.select:
                    edges_to_deselect.append(e)
                    break
        e = None
        for e in edges_to_deselect:
            e.select = False
        bm.select_history.clear()
        if e:
            bm.select_history.add(e)  # make active
        bmesh.update_edit_mesh(me, True)
        return {"FINISHED"}


def my_get_sorted_loops2(self, bm):
    remaining_edges_ids = [e.index for e in bm.edges if e.select]
    edge_strips = []
    vert_strips = []

    while remaining_edges_ids:
        current_edge_loop = []
        current_vert_loop = []
        current_edge = bm.edges[remaining_edges_ids.pop()]
        current_edge_loop.append(current_edge)

        def follow_edge_loop(curr_edge, old_vert, add_right):
            while True:  # go vert0 way, till no lined edges (line stops)
                next_vert = curr_edge.other_vert(old_vert)
                next_edges = [link_e for link_e in next_vert.link_edges if link_e.select and link_e != curr_edge]
                if add_right:
                    current_vert_loop.append(next_vert)
                else:
                    current_vert_loop.insert(0, next_vert)
                if next_edges and next_edges[0] not in current_edge_loop:  # just ignore if there are more linked edges selected. Maybe give error - bad selection
                    if add_right:
                        current_edge_loop.append(next_edges[0])
                        # current_vert_loop.append(next_vert)
                    else:
                        current_edge_loop.insert(0, next_edges[0])
                        # current_vert_loop.insert(0,next_vert)
                    remaining_edges_ids.remove(next_edges[0].index)
                    curr_edge = next_edges[0]
                    old_vert = next_vert  # right vert becomes left
                else:
                    break
        follow_edge_loop(current_edge, current_edge.verts[0], True)  # go in direction of vert 1
        follow_edge_loop(current_edge, current_edge.verts[1], False)  # go in direction of vert 0

        edge_strips.append(current_edge_loop)
        vert_strips.append(current_vert_loop)

    #TODO: maybe sort verts.
    # first_vert = vert_strips[0][0]
    # for i, edge_strip in enumerate(edge_strips):
    #     edge = edge_strip[0]
    #     ring_edges = [e_loop.link_loop_next.link_loop_next.edge for e_loop in edge.link_loops if len(e_loop.face.verts) == 4]
    #     if vert_loop[0] == first_vert and

    return vert_strips, edge_strips
