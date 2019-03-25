import bpy
from copy import deepcopy
from mathutils import Vector, Matrix
from math import radians


class QUICKT_OT_RadialArrayModal(bpy.types.Operator):
    bl_idname = "object.radial_clone"
    bl_label = "Radial Instances "
    bl_options = {'REGISTER', 'UNDO'}

    numberOfClones: bpy.props.IntProperty(name="numberOfClones", description="", default=8, min=1, max=50)
    axis: bpy.props.EnumProperty(name="Flip Axis", description="", default="Z",
                                  items=(("X", "X", ""),
                                         ("Y", "Y", ""),
                                         ("Z", "Z", "")
                                         ))
    Radius: bpy.props.FloatProperty(name="Radius", description="", default=0.4, min=0.01, max=100)
    objList = []
    MatWorldBackup = None

    Yaw: bpy.props.FloatProperty(default=0.0, name="X", unit='ROTATION')
    Pitch: bpy.props.FloatProperty(default=0.0, name="Y", unit='ROTATION')
    Roll: bpy.props.FloatProperty(default=0.0, name="Z", unit='ROTATION')
    scale: bpy.props.FloatProperty \
            (
            name="Scale",
            description="Object Scale",
            default=1.0,
            min=0.001,
            unit='LENGTH',
        )

    def computeRadialArray(self, angle, radius):
        yawMatrix = Matrix.Rotation(self.Yaw, 4, 'X')
        pitchMatrix = Matrix.Rotation(self.Pitch, 4, 'Y')
        rollMatrix = Matrix.Rotation(self.Roll, 4, 'Z')
        if self.axis == "Z":
            RadiusOffsetMatrix = Matrix.Translation(Vector((radius, 0.0, 0.0)))
        elif self.axis == 'Y':
            RadiusOffsetMatrix = Matrix.Translation(Vector((0.0, 0.0, radius)))
        else:
            RadiusOffsetMatrix = Matrix.Translation(Vector((0.0, 0.0, radius)))
        for i, obj in enumerate(self.objList):
            RotMatrix = Matrix.Rotation(radians(angle * i), 4, self.axis)
            obj.matrix_world = self.MatWorldBackup @ RotMatrix @ RadiusOffsetMatrix @ yawMatrix @ pitchMatrix @ rollMatrix
            obj.scale *= self.scale

    def execute(self, context):
        if context.object:
            context.active_object.select_set(True)
            self.MatWorldBackup = deepcopy(context.active_object.matrix_world)
            for i in range(self.numberOfClones):
                cloned = context.active_object.copy()
                self.objList.append(cloned)
                context.scene.collection.objects.link(cloned)
                cloned.select_set(True)
            angle = 360 / self.numberOfClones
            self.computeRadialArray(angle, self.Radius)
            self.objList.clear()
            return {'FINISHED'}
        else:
            return {'CANCELLED'}
