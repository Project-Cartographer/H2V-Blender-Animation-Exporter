bl_info = {
    "name": "Blend2Halo2 JMA",
    "author": "Not General_101",
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Export JMA files for Halo 2",
    "warning": "",
    "category": "Import-Export"}

import bpy
import math

from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty
from bpy.types import Operator
from math import ceil
from decimal import *

def get_child(bone, boneslist = [], *args):
    for node in boneslist:
        if bone == node.parent:
            child = node
            print(child)                
            return child
            
def get_sibling(bone2, boneslist2 = [], *args):
    for node in boneslist2:
        if bone2.parent == node.parent:
            child = node
            if child == bone2:
                return None
            else:
                print(child)                
                return child            
    
def export_jma(context, filepath):

    file = open(filepath, 'w', encoding='utf_16')
    
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
        
    objectslist = list(bpy.context.scene.objects)
    nodeslist = []
    keyframes = []
    
    for obj in objectslist:
        if (obj.name[0:2].lower() == 'b_' or obj.name[0:5].lower() == "bone_" or obj.name[0:6].lower() == "bip01_" or obj.name[0:6].lower() == "frame_" or obj.name.lower() == "armature"):
            if obj.type == 'ARMATURE':
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                nodeslist = list(obj.data.bones)    
                
    KEYFRAME_POINTS_ARRAY = []
    fcurves = bpy.context.active_object.animation_data.action.fcurves

    for curve in fcurves:
        keyframePoints = curve.keyframe_points
        for keyframe in keyframePoints:
            KEYFRAME_POINTS_ARRAY.append(keyframe.co[0])  

    keyframelist = list( dict.fromkeys(KEYFRAME_POINTS_ARRAY) )
    keyframelist.sort()
    
    version = 16392
    node_checksum = 0
    transform_count = len(keyframelist)
    frame_rate = 30
    actor_count = 1
    actor_name = 'unnamedActor'
    node_count = len(nodeslist)
    
    #write header 
    if version >= 16394:    
        file.write(
            '%s' % (version) +
            '\n%s' % (node_checksum) +        
            '\n%s' % (transform_count) +
            '\n%s' % (frame_rate) +
            '\n%s' % (actor_count) +
            '\n%s' % (actor_name) +
            '\n%s' % (node_count)    
            )
    else:
        file.write(
            '%s' % (version) +      
            '\n%s' % (transform_count) +
            '\n%s' % (frame_rate) +
            '\n%s' % (actor_count) +
            '\n%s' % (actor_name) +
            '\n%s' % (node_count) +   
            '\n%s' % (node_checksum)            
            )        
    #write nodes
    if version >= 16394:
        for node in nodeslist:
            parent_node = -1 
            if node.parent == None:
                parent_node = -1
            else:
                parent_node = nodeslist.index(node.parent)
                
            file.write(
                '\n%s' % (node.name) +
                '\n%s' % (parent_node)  
                )
    else:
        for node in nodeslist:
            findchildnode = get_child(node, nodeslist)       
            findsiblingnode = get_sibling(node, nodeslist)
            if findchildnode == None:
                first_child_node = -1
            else:
                first_child_node = nodeslist.index(findchildnode)
            if findsiblingnode == None:
                sibling_node = -1
            else:
                sibling_node = nodeslist.index(findsiblingnode)                

            file.write(
                '\n%s' % (node.name) +
                '\n%s' % (first_child_node) +
                '\n%s' % (sibling_node)                 
                )    

    #write transforms
    for node in nodeslist:
        a = 0 
        arm = context.scene.objects['Armature']
        bone = arm.pose.bones['%s' % (node.name)]             
        for keys in keyframelist:
            bpy.context.scene.frame_set(keyframelist[a])
            
            pos  = bone.location
            quat = bone.matrix.to_quaternion()
            
            quat_i = Decimal(quat[1]).quantize(Decimal('1.000000'))
            quat_j = Decimal(quat[2]).quantize(Decimal('1.000000'))
            quat_k = Decimal(quat[3]).quantize(Decimal('1.000000'))
            quat_w = Decimal(quat[0]).quantize(Decimal('1.000000'))
            pos_x = Decimal(pos[0]).quantize(Decimal('1.000000'))
            pos_y = Decimal(pos[1]).quantize(Decimal('1.000000'))
            pos_z = Decimal(pos[2]).quantize(Decimal('1.000000'))
            
            transform_scale = 1  
            
            file.write(
                '\n%0.8f\t%0.8f\t%0.8f' % (pos_x, pos_y, pos_z) +
                '\n%0.8f\t%0.8f\t%0.8f\t%0.8f' % (quat_i, quat_j, quat_k, quat_w) +       
                '\n%0.1f' % (transform_scale)
                )  
            a = a + 1    
            
    bpy.context.scene.frame_set(1)
    file.close()
    return {'FINISHED'}        

class ExportJMA(Operator, ExportHelper):
    """Write a Halo animation file"""
    bl_idname = "export_jma.export"
    bl_label = "Export Animation"
    
    Halo_Animation_Type: EnumProperty(
        name="Extension:",
        description="What extension to use for the animation file",
        items=[ ('0', "JMA", ""),
                ('1', "JMM", ""),
                ('2', "JMT", ""),
                ('3', "JMR", ""),
                ('4', "JRMX", ""),
                ('5', "JMZ", ""),
                ('6', "JMW", ""),
               ]
        )
        
    filename_ext = ".jma"
#    if props.Halo_Animation_Type == 0:
#        filename_ext = ".jma"
#    elif props.Halo_Animation_Type == 1:
#        filename_ext = ".jmm"       
#    elif props.Halo_Animation_Type == 2:
#        filename_ext = ".jmt"          
#    elif props.Halo_Animation_Type == 3:
#        filename_ext = ".jmr" 
#    elif props.Halo_Animation_Type == 4:
#        filename_ext = ".jrmx"      
#    elif props.Halo_Animation_Type == 5:
#        filename_ext = ".jmz"              
#    elif props.Halo_Animation_Type == 6:
#        filename_ext = ".jmw" 
       
    filter_glob: StringProperty(
            default="*.jma;*.jmm;*.jmt;*.jmo;*.jmr;*.jrmx;*.jmz;*.jmw",
            options={'HIDDEN'},
            )

    def execute(self, context):             
        return export_jma(context, self.filepath)

def menu_func_export(self, context):
    self.layout.operator(ExportJMA.bl_idname, text="Halo Animation file (.jma)")

def register():
    bpy.utils.register_class(ExportJMA)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ExportJMA)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    
if __name__ == '__main__':
    register()