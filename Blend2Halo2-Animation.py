bl_info = {
    "name": "Blend2Halo2 Animation",
    "author": "General_101",
    "version": (0, 0, 1),
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

def get_child(bone, boneslist = [], *args):
    for node in boneslist:
        if bone == node.parent:
            child = node
            return child

def get_sibling(bone2, boneslist2 = [], *args):
    siblinglist = []
    for node in boneslist2:
        if bone2.parent == node.parent:
            siblinglist.append(node)

    if len(siblinglist) <= 1:
        return None

    else:
        sibling_node = siblinglist.index(bone2)
        test = sibling_node + 1
        if test >= len(siblinglist):
            child = None

        else:
            child = bpy.data.armatures['Armature'].bones['%s' % siblinglist[test].name]

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

    keyframelist = list(dict.fromkeys(KEYFRAME_POINTS_ARRAY))
    keyframelist.sort()

    SelectedVersion = bpy.context.scene.anim.HaloVersionType

    version = 16390 + int(SelectedVersion)
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
    for keys in keyframelist:
        for node in nodeslist:
            arm = context.scene.objects['Armature']
            pose_bone = arm.pose.bones['%s' % (node.name)]
            
            print(keyframelist.index(keys))
            keyindex = keyframelist.index(keys)
            bpy.context.scene.frame_set(keyframelist[keyindex])
            
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
                '\n%0.8f\t%0.8f\t%0.8f' % (pos_x, pos_y, pos_z) +
                '\n%0.8f\t%0.8f\t%0.8f\t%0.8f' % (quat_i, quat_j, quat_k, quat_w) +
                '\n%0.1f' % (transform_scale)
                )

    bpy.context.scene.frame_set(1)
    file.close()
    return {'FINISHED'}

class FilePanel(bpy.types.Panel):
    bl_label = "Halo Animation"
    bl_idname = "HALO_PT_AnimationPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Animation"

    def draw(self, context):
        layout = self.layout

        scn = context.scene
        anim = scn.anim

        row = layout.row()
        row.label(text="Set extension and version")

        row = layout.row()
        row.prop(anim, "HaloExtensionType")

        row = layout.row()
        row.prop(anim, "HaloVersionType")

class Animation_OptionDropdown(PropertyGroup):

    HaloExtensionType: EnumProperty(
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

    HaloVersionType: EnumProperty(
        name="Version:",
        description="What version to use for the animation file",
        items=[ ('0', "16390", ""),
                ('1', "16391", ""),
                ('2', "16392", ""),
                ('3', "16393", ""),
                ('4', "16394", ""),
                ('5', "16395", ""),
               ]
        )

class ExportJMA(Operator, ExportHelper):
    """Write a Halo animation file"""
    bl_idname = "export_jma.export"
    bl_label = "Export Animation"

    Extension = 0

    if Extension == 0:
        filename_ext = ".jma"

    elif Extension == 1:
        filename_ext = ".jmm"

    elif Extension == 2:
        filename_ext = ".jmt"

    elif Extension == 3:
        filename_ext = ".jmr" 

    elif Extension == 4:
        filename_ext = ".jrmx"

    elif Extension == 5:
        filename_ext = ".jmz"

    elif Extension == 6:
        filename_ext = ".jmw" 

    filter_glob: StringProperty(
            default="*.jma;*.jmm;*.jmt;*.jmo;*.jmr;*.jrmx;*.jmz;*.jmw",
            options={'HIDDEN'},
            )

    def execute(self, context):
        return export_jma(context, self.filepath)

classes = (
    ExportJMA,
    FilePanel,
    Animation_OptionDropdown
)

def menu_func_export(self, context):
    self.layout.operator(ExportJMA.bl_idname, text="Halo Animation file (.jma)")

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.Scene.anim = PointerProperty(type=Animation_OptionDropdown, name="Halo Animation Properties", description="Halo Animation Properties")

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    del bpy.types.Scene.anim

if __name__ == '__main__':
    register()
