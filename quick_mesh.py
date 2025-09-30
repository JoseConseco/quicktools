#### simple uv &gt; co
import bpy
from mathutils import Vector
import bmesh

class QUICKT_OT_UVShapekey(bpy.types.Operator):
    bl_label = "UV to Shapekey"
    bl_idname = "object.uv_to_shapekey"
    bl_description = "Uv to Shapekey"

    def execute(self, context):
        obj = context.active_object
        if not obj.data.shape_keys:
            obj.shape_key_add(from_mix=False) #base
        newshapeKey = obj.shape_key_add(from_mix=False)
        newshapeKey.name += "_UV_flatten"
        me = bpy.context.object.data
        uv_layer = me.uv_layers.active.data
        for loop in me.loops:
            co = uv_layer[loop.index].uv
            newshapeKey.data[loop.vertex_index].co = Vector((co[0], co[1], 0))
        return {"FINISHED"}



class MESH_OT_select_similar_face_set(bpy.types.Operator):
    """Select faces with similar face sets to the selected face"""
    bl_idname = "mesh.select_similar_face_set"
    bl_label = "Select Similar Face Set"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.mode == 'EDIT_MESH')

    def execute(self, context):
        obj = context.object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)

        # Get selected faces
        selected_faces = [f for f in bm.faces if f.select]
        if not selected_faces:
            self.report({'WARNING'}, "No faces selected")
            return {'CANCELLED'}

        # Check if face set data exists
        face_set_layer = None
        if ".sculpt_face_set" in bm.faces.layers.int:
            face_set_layer = bm.faces.layers.int[".sculpt_face_set"]

        if not face_set_layer:
            self.report({'WARNING'}, "No face set data found. Use Sculpt mode to create face sets first.")
            return {'CANCELLED'}
        else:
            # Get face sets from bmesh layer
            face_sets = set()
            for face in selected_faces:
                face_sets.add(face[face_set_layer])

            if not face_sets:
                self.report({'WARNING'}, "Selected faces have no face set data")
                return {'CANCELLED'}

            # Select all faces with matching face sets
            for face in bm.faces:
                if face[face_set_layer] in face_sets:
                    face.select = True

        bmesh.update_edit_mesh(mesh)
        return {'FINISHED'}


def menu_func_select_similar(self, context):
    self.layout.operator(MESH_OT_select_similar_face_set.bl_idname, text="Face Set")

def register():
    bpy.types.VIEW3D_MT_edit_mesh_select_similar.append(menu_func_select_similar)

def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_select_similar.remove(menu_func_select_similar)

