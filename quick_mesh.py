#### simple uv &gt; co
import bpy
from mathutils import Vector

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


