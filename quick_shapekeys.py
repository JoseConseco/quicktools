import bpy
from mathutils import Matrix, Vector, kdtree

class QUICKT_OT_cloneShapekeyMask(bpy.types.Operator):
    """Toggle Double Sided Option"""
    bl_label = "Clone Shapekey"
    bl_idname = "object.clone_shapekey"
    bl_description = "Clone Shapekey"

    def execute(self, context):
        obj = context.active_object
        activeShapeKey = context.active_object.active_shape_key
        newshapeKey = obj.shape_key_add(from_mix=False)
        newshapeKey.name = activeShapeKey.name+".clone"
        newshapeKey.vertex_group = activeShapeKey.vertex_group
        for vert in obj.data.vertices:
            newshapeKey.data[vert.index].co = activeShapeKey.data[vert.index].co
        return {"FINISHED"}


class QUICKT_OT_mirrorShapekeyMask(bpy.types.Operator):
    """Toggle Double Sided Option"""
    bl_label = "Mirror Shapekey"
    bl_idname = "object.mirror_shapekey"
    bl_description = "Mirror Shapekey"

    def execute(self, context):

        obj = context.active_object
        activeShapeKey = context.active_object.active_shape_key

        mesh = obj.data
        size = len(mesh.vertices)
        kd = kdtree.KDTree(size)

        for i, v in enumerate(mesh.vertices):
            kd.insert(v.co, i)

        kd.balance()

        for vert in obj.data.vertices:
            if vert.co[0] > 0:
                co, index, dist = kd.find(Vector((-vert.co[0], vert.co[1], vert.co[2])))
                if dist < 0.0001:  # delta
                    activeShapeKey.data[index].co = activeShapeKey.data[vert.index].co
                    activeShapeKey.data[index].co[0] = -activeShapeKey.data[vert.index].co[0]
        return {"FINISHED"}


class QUICKT_OT_applyShapekeyMask(bpy.types.Operator):
    bl_label = "Apply Shapekey Mask"
    bl_idname = "object.apply_shapekey_mask"
    bl_description = "Apply Shapekey Mask"
    bl_options = {"REGISTER", "UNDO"}

    invertWeight: bpy.props.BoolProperty(name="Invert Weight", description="Invert Weight", default=False)

    def execute(self, context):
        obj = context.active_object
        activeShapeKey = context.active_object.active_shape_key
        baseShapeKey = obj.data.shape_keys.key_blocks[0]  # assuming basic shapekey is first always
        vertGroupName = activeShapeKey.vertex_group
        if vertGroupName == '':
            self.report({'INFO'}, message="No vertex weight assigned to active shape kay. Cancelling!")
            return {"CANCELLED"}
        for vert in obj.data.vertices:
            if not self.invertWeight:
                try:
                    vertWeight = 1-obj.vertex_groups[vertGroupName].weight(vert.index)
                except:
                    vertWeight = 1
            else:
                try:
                    vertWeight = obj.vertex_groups[vertGroupName].weight(vert.index)
                except:
                    vertWeight = 0
            delta = (baseShapeKey.data[vert.index].co-activeShapeKey.data[vert.index].co)
            activeShapeKey.data[vert.index].co = activeShapeKey.data[vert.index].co+delta*vertWeight
        activeShapeKey.vertex_group = ''
        return {"FINISHED"}


class QUICKT_OT_correctiveShapekey(bpy.types.Operator):
    bl_label = "Corrective Shapekey"
    bl_idname = "object.corrective_shapekey"
    bl_description = "Corrective Shapekey"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        activeShapeKey = context.active_object.active_shape_key
        baseShapeKey = obj.data.shape_keys.key_blocks[0]  # assuming basic shapekey is first always
        deltas = []
        vertGroupName = activeShapeKey.vertex_group

        vg = obj.vertex_groups.get(vertGroupName)
        for vert in obj.data.vertices:
            vertWeight = 1
            if vg:
                try:
                    vertWeight = vg.weight(vert.index)
                except:
                    pass
            deltas.append(vertWeight*(activeShapeKey.data[vert.index].co-baseShapeKey.data[vert.index].co))

        for shape in obj.data.shape_keys.key_blocks:
            if shape == activeShapeKey:  # skip active shape key = corrective shape
                continue
            for vert, delta in zip(obj.data.vertices, deltas):
                shape.data[vert.index].co += delta
        return {"FINISHED"}
