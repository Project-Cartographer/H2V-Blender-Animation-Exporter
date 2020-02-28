bl_info = {
    "name": "Blend2Halo2 JMA",
    "author": "General_101",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "File > Export",
    "description": "Import-Export Halo 2/CE Jointed Model Animation File (.jma)",
    "wiki_url": "https://num0005.github.io/h2codez_docs/w/H2Tool/Animations.html",
    "category": "Import-Export"}

import bpy
import math

from math import ceil
from decimal import *
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty

def unhide_all_collections():
    for collection_viewport in bpy.context.view_layer.layer_collection.children:
        collection_viewport.hide_viewport = False

    for collection_hide in bpy.data.collections:
        collection_hide.hide_select = False
        collection_hide.hide_viewport = False
        collection_hide.hide_render = False

def unhide_all_objects():
    context = bpy.context
    for obj in context.view_layer.objects:
        if obj.hide_set:
            obj.hide_set(False)

        if obj.hide_select:
            obj.hide_select = False

        if obj.hide_viewport:
            obj.hide_viewport = False

        if obj.hide_render:
            obj.hide_render = False

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

def export_jma(context, filepath, report, encoding, extension, jma_version, custom_framerate):

    unhide_all_collections()
    unhide_all_objects()
    file = open(filepath + extension, 'w', encoding='%s' % encoding)

    object_list = list(bpy.context.scene.objects)
    node_list = []
    layer_count = []
    root_list = []
    children_list = []
    reversed_children_list = []
    joined_list = []
    reversed_joined_list = []
    sort_list = []
    reversed_sort_list = []
    keyframes = []
    armature = []
    armature_count = 0

    first_frame = bpy.context.scene.frame_start
    last_frame = bpy.context.scene.frame_end + 1
    total_frame_count = bpy.context.scene.frame_end - first_frame + 1

    if len(object_list) == 0:
        report({'ERROR'}, "No objects in scene.")
        file.close()
        return {'CANCELLED'}

    bpy.context.view_layer.objects.active = object_list[0]
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    for obj in object_list:
        if obj.type == 'ARMATURE':
            armature_count += 1
            armature = obj
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            node_list = list(obj.data.bones)

        if armature_count >= 2:
            report({'ERROR'}, "More than one armature object. Please delete all but one.")
            file.close()
            return {'CANCELLED'}

    if armature_count == 0:
        report({'ERROR'}, "No armature object.")
        file.close()
        return {'CANCELLED'}

    for node in node_list:
        if node.parent == None:
            layer_count.append(None)

        else:
            if not node.parent.name in layer_count:
                layer_count.append(node.parent.name)

    for layer in layer_count:
        joined_list = root_list + children_list
        reversed_joined_list = root_list + reversed_children_list
        layer_index = layer_count.index(layer)
        if layer_index == 0:
            root_list.append(armature.data.bones[0])

        else:
            for node in node_list:
                if node.parent != None:
                    if armature.data.bones['%s' % node.parent.name] in joined_list and not node in children_list:
                        sort_list.append(node.name)
                        reversed_sort_list.append(node.name)

            sort_list.sort()
            reversed_sort_list.sort()
            reversed_sort_list.reverse()
            for sort in sort_list:
                if not armature.data.bones['%s' % sort] in children_list:
                    children_list.append(armature.data.bones['%s' % sort])

            for sort in reversed_sort_list:
                if not armature.data.bones['%s' % sort] in reversed_children_list:
                    reversed_children_list.append(armature.data.bones['%s' % sort])

        joined_list = root_list + children_list
        reversed_joined_list = root_list + reversed_children_list


    version = 16390 + int(jma_version)
    node_checksum = 0
    transform_count = total_frame_count

    if custom_framerate:
        frame_rate = bpy.context.scene.render.fps

    else:
        frame_rate = 30

    #actor related items are hardcoded due to them being an unused feature in tool. Do not attempt to do anything to write this out as it is a waste of time and will get you nothing.
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
        for node in joined_list:
            if node.parent == None:
                parent_node = -1

            else:
                parent_node = joined_list.index(node.parent)

            file.write(
                '\n%s' % (node.name) +
                '\n%s' % (parent_node)
                )

    else:
        for node in joined_list:
            find_child_node = get_child(node, reversed_joined_list)
            find_sibling_node = get_sibling(armature, node, reversed_joined_list)
            if find_child_node == None:
                first_child_node = -1

            else:
                first_child_node = joined_list.index(find_child_node)

            if find_sibling_node == None:
                first_sibling_node = -1

            else:
                first_sibling_node = joined_list.index(find_sibling_node)

            file.write(
                '\n%s' % (node.name) +
                '\n%s' % (first_child_node) +
                '\n%s' % (first_sibling_node)
                )

    #write transforms
    for frame in range(first_frame, last_frame):
        for node in joined_list:
            pose_bone = armature.pose.bones['%s' % (node.name)]

            bpy.context.scene.frame_set(frame)

            bone_matrix = pose_bone.matrix
            if pose_bone.parent and not version >= 16394:
                bone_matrix = pose_bone.parent.matrix.inverted() @ pose_bone.matrix

            pos  = bone_matrix.translation
            if version >= 16394:
                quat = bone_matrix.to_quaternion()

            else:
                quat = bone_matrix.to_quaternion().inverted()

            scale = pose_bone.scale

            quat_i = Decimal(quat[1]).quantize(Decimal('1.000000'))
            quat_j = Decimal(quat[2]).quantize(Decimal('1.000000'))
            quat_k = Decimal(quat[3]).quantize(Decimal('1.000000'))
            quat_w = Decimal(quat[0]).quantize(Decimal('1.000000'))
            pos_x = Decimal(pos[0]).quantize(Decimal('1.000000'))
            pos_y = Decimal(pos[1]).quantize(Decimal('1.000000'))
            pos_z = Decimal(pos[2]).quantize(Decimal('1.000000'))
            scale_x = Decimal(scale[0]).quantize(Decimal('1.000000'))
            scale_y = Decimal(scale[1]).quantize(Decimal('1.000000'))
            scale_z = Decimal(scale[2]).quantize(Decimal('1.000000'))

            if not scale_x == scale_y == scale_z:
                report({'WARNING'}, "Scale for bone %s is not uniform at frame %s. Resolve this or understand that what shows up ingame may be different from your scene." % (node.name, frame))

            transform_scale = scale_x

            file.write(
                '\n%0.6f\t%0.6f\t%0.6f' % (pos_x, pos_y, pos_z) +
                '\n%0.6f\t%0.6f\t%0.6f\t%0.6f' % (quat_i, quat_j, quat_k, quat_w) +
                '\n%0.6f' % (transform_scale)
                )

    #H2 specific biped controller data bool value.
    if version > 16394:
        biped_controller = false
        biped_controller_attached = 0
        if biped_controller:
            biped_controller_attached = 1

        file.write(
            '\n%s' % (biped_controller_attached)
            )

        #Explanation for this found in closed issue #15 on the Git. Seems to do nothing in our toolset so no way to test this to properly port.
        if biped_controller:
            for i in range(transform_count):
                file.write(
                    '\n%0.6f\t%0.6f\t%0.6f' % (0, 0, 0) +
                    '\n%0.6f\t%0.6f\t%0.6f\t%0.6f' % (0, 0, 0, 1) +
                    '\n%0.6f' % (1)
                    )

    file.write(
        '\n'
        )

    bpy.context.scene.frame_set(1)
    file.close()
    return {'FINISHED'}

class ExportJMA(Operator, ExportHelper):
    """Write a JMA file"""
    bl_idname = "export_jma.export"
    bl_label = "Export Animation"

    filename_ext = ''

    encoding: EnumProperty(
        name="Encoding:",
        description="What encoding to use for the animation file",
        items=[ ('utf_8', "UTF-8", "For CE/H2"),
                ('UTF-16LE', "UTF-16", "For H2"),
               ]
        )

    extension: EnumProperty(
        name="Extension:",
        description="What extension to use for the animation file",
        items=[ ('.JMA', "JMA", "Jointed Model Animation CE/H2"),
                ('.JMM', "JMM", "Jointed Model Moving CE/H2"),
                ('.JMT', "JMT", "Jointed Model Turning CE/H2"),
                ('.JMO', "JMO", "Jointed Model Overlay CE/H2"),
                ('.JMR', "JMR", "Jointed Model Replacement CE/H2"),
                ('.JMRX', "JMRX", "Jointed Model Replacement Extended H2"),
                ('.JMH', "JMH", "Jointed Model Havok H2"),
                ('.JMZ', "JMZ", "Jointed Model Height CE/H2"),
                ('.JMW', "JMW", "Jointed Model World CE/H2"),
               ]
        )

    jma_version: EnumProperty(
        name="Version:",
        description="What version to use for the animation file",
        default="2",
        items=[ ('0', "16390", "CE/H2 Non-functional"),
                ('1', "16391", "CE/H2 Non-functional"),
                ('2', "16392", "CE/H2"),
                ('3', "16393", "H2"),
                ('4', "16394", "H2"),
                ('5', "16395", "H2"),
               ]
        )

    custom_framerate: BoolProperty(
        name ="Custom Framerate",
        description = "Set the framerate this animation will run at. Having this box unchecked will write 30 by default.",
        default = False,
        )

#    biped_controller: BoolProperty(
#        name ="Biped Controller",
#        description = "For Testing",
#        default = False,
#        )

    filter_glob: StringProperty(
        default="*.jma;*.jmm;*.jmt;*.jmo;*.jmr;*.jrmx;*.jmh;*.jmz;*.jmw",
        options={'HIDDEN'},
        )

    def execute(self, context):
        return export_jma(context, self.filepath, self.report, self.encoding, self.extension, self.jma_version, self.custom_framerate)

def menu_func_export(self, context):
    self.layout.operator(ExportJMA.bl_idname, text="Halo Jointed Model Animation (.jma)")

def register():
    bpy.utils.register_class(ExportJMA)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ExportJMA)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == '__main__':
    register()
