bl_info = {
    "name": "Blend2Halo2 Animation",
    "author": "General_101",
    "version": (0, 0, 5),
    "blender": (2, 80, 0),
    "location": "File > Export",
    "description": "Export animation files for Halo 2/CE",
    "wiki_url": "https://num0005.github.io/h2codez_docs/w/H2Tool/Animations.html",
    "category": "Import-Export"}

import bpy
import math

from math import ceil
from decimal import *
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty

def get_child(bone, bone_list = [], *args):
    for node in bone_list:
        if bone == node.parent:
            return node

def get_sibling(armature, bone, bone_list = [], *args):
    sibling_list = []
    for node in bone_list:
        if bone.parent == node.parent:
            sibling_list.append(node)

    if len(sibling_list) <= 1:
        return None

    else:
        sibling_node = sibling_list.index(bone)
        next_sibling_node = sibling_node + 1
        if next_sibling_node >= len(sibling_list):
            sibling = None

        else:
            sibling = armature.data.bones['%s' % sibling_list[next_sibling_node].name]

        return sibling

def export_jma(context, filepath, extension, jma_version, custom_framerate):

    file = open(filepath + extension, 'w')
    
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    object_list = list(bpy.context.scene.objects)
    node_list = []
    keyframes = []
    armature = []

    for obj in object_list:
        if obj.type == 'ARMATURE':
            armature = obj
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            node_list = list(obj.data.bones)

    keyframe_points_array = []
    fcurves = bpy.context.active_object.animation_data.action.fcurves

    for curve in fcurves:
        keyframe_points = curve.keyframe_points
        for keyframe in keyframe_points:
            keyframe_points_array.append(keyframe.co[0])

    keyframe_list = list(dict.fromkeys(keyframe_points_array))
    keyframe_list.sort()

    version = 16390 + int(jma_version)
    node_checksum = 0
    transform_count = len(keyframe_list)

    if custom_framerate:
        frame_rate = bpy.context.scene.render.fps
        
    else:
        frame_rate = 30
        
    actor_count = 1
    actor_name = 'unnamedActor'
    node_count = len(node_list)

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
        for node in node_list:
            if node.parent == None:
                parent_node = -1

            else:
                parent_node = node_list.index(node.parent)

            file.write(
                '\n%s' % (node.name) +
                '\n%s' % (parent_node)
                )

    else:
        for node in node_list:
            find_child_node = get_child(node, node_list)
            find_sibling_node = get_sibling(armature, node, node_list)
            if find_child_node == None:
                first_child_node = -1

            else:
                first_child_node = node_list.index(find_child_node)

            if find_sibling_node == None:
                first_sibling_node = -1

            else:
                first_sibling_node = node_list.index(find_sibling_node)

            file.write(
                '\n%s' % (node.name) +
                '\n%s' % (first_child_node) +
                '\n%s' % (first_sibling_node)
                )

    #write transforms
    for keys in keyframe_list:
        for node in node_list:
            pose_bone = armature.pose.bones['%s' % (node.name)]

            key_index = keyframe_list.index(keys)
            bpy.context.scene.frame_set(keyframe_list[key_index])
            
            bone_matrix = pose_bone.matrix
            if pose_bone.parent:
                bone_matrix = pose_bone.parent.matrix.inverted() @ pose_bone.matrix
            
            pos  = bone_matrix.translation
            quat = bone_matrix.to_quaternion()

            quat_i = Decimal(quat[1]).quantize(Decimal('1.000000'))
            quat_j = Decimal(quat[2]).quantize(Decimal('1.000000'))
            quat_k = Decimal(quat[3]).quantize(Decimal('1.000000'))
            quat_w = Decimal(quat[0]).quantize(Decimal('1.000000'))
            pos_x = Decimal(pos[0]).quantize(Decimal('1.000000'))
            pos_y = Decimal(pos[1]).quantize(Decimal('1.000000'))
            pos_z = Decimal(pos[2]).quantize(Decimal('1.000000'))

            transform_scale = 1

            file.write(
                '\n%0.6f\t%0.6f\t%0.6f' % (pos_x, pos_y, pos_z) +
                '\n%0.6f\t%0.6f\t%0.6f\t%0.6f' % (quat_i, quat_j, quat_k, quat_w) +
                '\n%0.6f' % (transform_scale)
                )

    file.write(
        '\n'
        )

    bpy.context.scene.frame_set(1)
    file.close()
    return {'FINISHED'}

class ExportJMA(Operator, ExportHelper):
    """Write a Halo animation file"""
    bl_idname = "export_jma.export"
    bl_label = "Export Animation"

    filename_ext = ''

    extension: EnumProperty(
        name="Extension:",
        description="What extension to use for the animation file",
        items=[ ('.jma', "JMA", ""),
                ('.jmm', "JMM", ""),
                ('.jmt', "JMT", ""),
                ('.jmr', "JMR", ""),
                ('.jrmx', "JRMX", ""),
                ('.jmz', "JMZ", ""),
                ('.jmw', "JMW", ""),
               ]
        )

    jma_version: EnumProperty(
        name="Version:",
        description="What version to use for the animation file",
        default="2",
        items=[ ('0', "16390", ""),
                ('1', "16391", ""),
                ('2', "16392", ""),
                ('3', "16393", ""),
                ('4', "16394", ""),
                ('5', "16395", ""),
               ]
        )
        
    custom_framerate: BoolProperty(
        name ="Custom Framerate",
        description = "Set the framerate this animation will run at. Having this box unchecked will write 30 by default.",
        default = False,
        )

    filter_glob: StringProperty(
            default="*.jma;*.jmm;*.jmt;*.jmo;*.jmr;*.jrmx;*.jmz;*.jmw",
            options={'HIDDEN'},
            )

    def execute(self, context):
        return export_jma(context, self.filepath, extension=self.extension, jma_version=self.jma_version, custom_framerate=self.custom_framerate)

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
