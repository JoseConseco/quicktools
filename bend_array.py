import bpy
from copy import deepcopy
from mathutils import Vector, Matrix
from math import radians
import blf
  # bgl deprecated, use blf.color for text color


def gui_update(self, context):
    font_id = 0
    blf.position(font_id, 50, 50, 0)
    blf.size(font_id, 15, 72)
    blf.color(font_id, 1.0, 0.5, 0.0, 1.0)  # RGBA
    blf.draw(font_id, "ARRAY MODE: Scroll add/remove instances | Mouse move - radius")


class QUICKT_OT_RadialArray(bpy.types.Operator):
    bl_idname = "object.bend_array"
    bl_label = "Bend array"
    bl_options = {'REGISTER', 'UNDO'}

    axis: bpy.props.EnumProperty(name="Axis", description="", default="Z",
                                    items = (("X", "X", ""),
                                            ("Y", "Y", ""),
                                            ("Z", "Z", "")
                                             ))
    # Radius:  bpy.props.FloatProperty(name="Radius", description="", default=0.4, min=0.01, max=100)
    MatWorldBackup = None

    Radius:  bpy.props.FloatProperty(name="Radius", description="", default=2, min=0.01, max=10)
    spacing:  bpy.props.FloatProperty(name="Spacing", description="", default=0, min=0.0, max=10)

    arrayCount: bpy.props.IntProperty(name="ArrayCount", description="Amount Of Clones", default=8, min = 1, max = 100)


    def invoke(self, context, event):
        obj = bpy.context.object
        self.objWidth = obj.dimensions[0]
        return self.execute(context)

    def execute(self, context):
        obj  = bpy.context.object
        arrayCount=self.arrayCount #sets array count
        obwod=self.objWidth*arrayCount+self.spacing/self.arrayCount*(arrayCount-1)  #width*count = obwod  // last spacing delta is ==0 so skip it == -1
        radius=obwod/radians(360)
        # bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        bpy.ops.object.modifier_add(type='ARRAY')
        context.object.modifiers["Array"].count = arrayCount
        context.object.modifiers["Array"].use_constant_offset = True
        context.object.modifiers["Array"].use_relative_offset = False
        bpy.context.object.modifiers["Array"].constant_offset_displace[0] = self.objWidth/obj.scale[0]+self.spacing/self.arrayCount

        bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
        #s = r * alpha => alpha = s / r       r=obw/2pi
        fixAngleSpacing = self.spacing/self.arrayCount*radians(360)/obwod  # 2*pi*alpha = len of obwod  // compensate last delta
        obj.modifiers[-1].deform_method = 'BEND' #last mod is simple deform
        obj.modifiers[-1].angle = radians(360) - fixAngleSpacing

        loc, rotQuat, scale=obj.matrix_world.decompose()
        radiusScale=Matrix.Scale(self.Radius,4)
        offsetPiR = Matrix.Translation(Vector((0.0, -radius, 0.0)))
        locMat=Matrix.Translation(loc)
        rotMatrix=rotQuat.to_matrix().to_4x4()
        scaleMatrix=Matrix.Identity(4)
        scaleMatrix[0][0]=scale[0]
        scaleMatrix[1][1]=scale[1]
        scaleMatrix[2][2]=scale[2]
        obj.matrix_world=obj.matrix_world*radiusScale*offsetPiR*scaleMatrix #matWorld*RadiusScale*offsetRadius


        return {'FINISHED'}

