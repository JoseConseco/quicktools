import bpy
import blf
from mathutils import Vector
import math
from bgl import *
from bpy.props import IntProperty, FloatProperty
from bpy_extras import view3d_utils


# to activate type 'ar' in operator search tab



def gui_update(self,context):


    font_id = 0  # XXX, need to find out how best to get this.

    # draw some text
    blf.position(font_id, 50, 50, 0)
    blf.size(font_id, 15, 72)
    glColor3f(1,0.5,0)
    
    # ouch

    blf.draw(font_id, "ARRAY MODE: MWHEEL | R ("+self.otype+") | LMB/RMB/ESC | X/Y/Z "  )

class QUICKT_OT_nwArray(bpy.types.Operator):

    bl_idname = "nw.arr"
    bl_label = "Array [arr]"

    first_mouse_x: IntProperty()
    first_value: FloatProperty()

    def vdist(self):
      area=bpy.context.window.screen.areas[0]
      for x in bpy.context.window.screen.areas:
          if x.type=='VIEW_3D': area=x

      area.spaces[0].region_3d.view_distance
      return area.spaces[0].region_3d.view_distance
    
    def vdir(self):
        region = self.context.region
        rv3d= self.context.region_data
               
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, self.coord)
        
        ovec=Vector((1,0,0))
        if self.dir==1: ovec=Vector((0,1,0))
        elif self.dir==2: ovec=Vector((0,0,-1))

        #cr=self.type*view_vector
        cd=view_vector.dot(ovec)
        #print(cd)
        return -math.copysign(1,cd)
            
    
    def modal(self, context, event):

      
        if event.type == 'X': 
            self.dir=0
            self.type[1]=0
            self.type[2]=0
            
        elif event.type == 'Y':
            self.dir=1
            self.type[0]=0
            self.type[2]=0

        
        elif event.type =='Z':
             self.dir=2
             self.type[1]=0
             self.type[0]=0

        
        elif event.type=='R' and event.value=='PRESS':
             self.view_dir = self.vdir()


             if not bpy.context.object.modifiers[self.id].use_constant_offset:
                bpy.context.object.modifiers[self.id].use_relative_offset = False
                bpy.context.object.modifiers[self.id].use_constant_offset = True
                self.type=bpy.context.object.modifiers[self.id].constant_offset_displace
                
                bpy.context.object.modifiers[self.id].constant_offset_displace[0]=0
                bpy.context.object.modifiers[self.id].constant_offset_displace[1]=0
                bpy.context.object.modifiers[self.id].constant_offset_displace[2]=0
                self.otype="CONSTANT"

             else:
                bpy.context.object.modifiers[self.id].use_relative_offset = True
                bpy.context.object.modifiers[self.id].use_constant_offset = False

                self.type=bpy.context.object.modifiers[self.id].relative_offset_displace
                bpy.context.object.modifiers[self.id].relative_offset_displace[0]=0
                bpy.context.object.modifiers[self.id].relative_offset_displace[1]=0
                bpy.context.object.modifiers[self.id].relative_offset_displace[2]=0
                
                self.otype="RELATIVE"
                
                
             self.start=0
             return {'RUNNING_MODAL'}  

        if event.type == 'WHEELUPMOUSE':
            bpy.context.object.modifiers[self.id].count+=1
        elif event.type == 'WHEELDOWNMOUSE':
            bpy.context.object.modifiers[self.id].count-=1
        
        if event.type == 'MOUSEMOVE':
            #print(bpy.context.area.type)
            vd= self.vdir() # viewport dir
            delta= event.mouse_x-self.first_mouse_x

            rm=1 # relative multiplier
            
            #self.vdir()

            if not bpy.context.object.modifiers[self.id].use_constant_offset: rm=0.5
            self.type[self.dir] =   vd*-delta * 0.005 * self.vdist() * rm+ self.start


        elif event.type == 'LEFTMOUSE':
            bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')   
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            if event.type=='ESC' and not self.exists: bpy.ops.object.modifier_remove(modifier="NArray")

            bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')   
            context.object.location.x = self.first_value
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        
        if context.object:
       

             
            self.otype="CONSTANT"  
            
            # disable mods for accurate dimensions
            m=[False]*len(context.object.modifiers)
            for x in range(0, len(context.object.modifiers)):
              mod=context.object.modifiers[x]
              m[x]=mod.show_viewport
              mod.show_viewport=False
            
            
            # perhaps a better way to update dimensions?
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.editmode_toggle()
  
            self.size=bpy.context.object.dimensions.length 
            
            # reenable
            for x in range(0, len(context.object.modifiers)): context.object.modifiers[x].show_viewport=m[x]
            
       
            self.start=0
            
            self.dir=0
            arrID=-1
            n=-1
            
            self.exists=False #Narray
            

            
            #Lets find arrays. NARRAY takes priority
            for x in bpy.context.object.modifiers:
                n+=1
                if x.name=="NArray":
                    arrID=n
                    self.id=n
                      
                    if bpy.context.object.modifiers[self.id].use_constant_offset:
                      self.type=bpy.context.object.modifiers[self.id].constant_offset_displace
                      self.otype="CONSTANT"         
                    else:  
                      self.type=bpy.context.object.modifiers[self.id].relative_offset_displace
                      self.otype="RELATIVE" 

                    max=abs(self.type[0])
                    self.dir=0
                    if abs(self.type[1])>abs(max):
                       max=(self.type[1])
                       self.dir=1
                       
                    if abs(self.type[2])>abs(max):
                       max=(self.type[2])
                       self.dir=2
                    
                    self.start=max
                    print("max", max)
                    print("dir", self.dir)
                    
                    self.exists=True
            
            #Narray not found, lets go for other arrays        
            if not self.exists:       
              for x in bpy.context.object.modifiers:
                  n+=1
                  if x.type=='ARRAY' and 'CAr' not in x.name:
                    arrID=n
                    self.id=n
                      
                    if bpy.context.object.modifiers[self.id].use_constant_offset:
                      self.type=bpy.context.object.modifiers[self.id].constant_offset_displace
                      self.otype="CONSTANT"         
                    else:  
                      self.type=bpy.context.object.modifiers[self.id].relative_offset_displace
                      self.otype="RELATIVE" 

                    max=abs(self.type[0])
                    self.dir=0
                    if abs(self.type[1])>abs(max):
                       max=(self.type[1])
                       self.dir=1
                       
                    if abs(self.type[2])>abs(max):
                       max=(self.type[2])
                       self.dir=2
                    
                    self.start=max
                    print("max", max)
                    print("dir", self.dir)
                    
                    self.exists=True
                      
                    
            # No arrays exist, create one    
            if arrID==-1:    
                bpy.ops.object.modifier_add(type='ARRAY')
                loc = bpy.context.object.location.copy()
                self.id=len(bpy.context.object.modifiers)-1
                arrID=len(bpy.context.object.modifiers)-1
                bpy.context.object.modifiers[self.id].name = "NArray"
                               
                bpy.context.object.modifiers[self.id].use_relative_offset = False
                bpy.context.object.modifiers[self.id].use_constant_offset = True


            
            self.id=int(arrID)
            
            # lazy type detection
            if bpy.context.object.modifiers[self.id].use_constant_offset:
              self.type=bpy.context.object.modifiers[self.id].constant_offset_displace        
            else:  
              self.type=bpy.context.object.modifiers[self.id].relative_offset_displace
              
            self.context=context
            self.coord=event.mouse_x,event.mouse_y
            self.first_mouse_x = event.mouse_x
            self.first_value = context.object.location.x             

            args = (self, context)
            
            self.handle= bpy.types.SpaceView3D.draw_handler_add(gui_update, args, 'WINDOW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
            
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}

