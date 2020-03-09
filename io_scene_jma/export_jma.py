# ##### BEGIN MIT LICENSE BLOCK #####
#
# MIT License
#
# Copyright (c) 2020 Steven Garcia
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# ##### END MIT LICENSE BLOCK #####

import bpy

from math import ceil
from decimal import *

def unhide_all_collections():
    for collection_viewport in bpy.context.view_layer.layer_collection.children:
        collection_viewport.hide_viewport = False

    for collection_hide in bpy.data.collections:
        collection_hide.hide_select = False
        collection_hide.hide_viewport = False
        collection_hide.hide_render = False

def unhide_all_objects():
    for obj in bpy.context.view_layer.objects:
        obj.hide_set(False)
        obj.hide_select = False
        obj.hide_viewport = False
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

def export_jma(context, filepath, report, encoding, extension, jma_version, game_version, custom_frame_rate, frame_rate_float, biped_controller):
    unhide_all_collections()
    unhide_all_objects()

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
    armature = []
    armature_count = 0

    first_frame = bpy.context.scene.frame_start
    last_frame = bpy.context.scene.frame_end + 1
    total_frame_count = bpy.context.scene.frame_end - first_frame + 1

    if len(object_list) == 0:
        report({'ERROR'}, "No objects in scene.")
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


    version = int(jma_version)
    node_checksum = 0
    transform_count = total_frame_count

    if custom_frame_rate == 'CUSTOM':
        frame_rate_value = frame_rate_float

    else:
        frame_rate_value = int(custom_frame_rate)

    frame_rate = frame_rate_value

    #actor related items are hardcoded due to them being an unused feature in tool. Do not attempt to do anything to write this out as it is a waste of time and will get you nothing.
    actor_count = 1
    actor_name = 'unnamedActor'
    node_count = len(node_list)

    if armature_count >= 2:
        report({'ERROR'}, "More than one armature object. Please delete all but one.")
        return {'CANCELLED'}

    if len(node_list) == 0:
        report({'ERROR'}, 'No bones in the current scene. Add an armature.')
        return {'CANCELLED'}

    if version >= 16393 and game_version == 'haloce':
        report({'ERROR'}, 'This version is not supported for Halo CE. Choose from 16390-16392 if you wish to export for Halo CE.')
        return {'CANCELLED'}

    if encoding == 'UTF-16LE' and game_version == 'haloce':
        report({'ERROR'}, 'This encoding is not supported for Halo CE. Choose UTF-8 if you wish to export for Halo CE.')
        return {'CANCELLED'}

    if encoding == 'utf_8' and game_version == 'halo2':
        report({'ERROR'}, 'This encoding is not supported for Halo 2. Choose UTF-16 if you wish to export for Halo 2.')
        return {'CANCELLED'}

    if extension == '.JMRX' and game_version == 'haloce':
        report({'ERROR'}, 'This extension is not used in Halo CE')
        return {'CANCELLED'}

    file = open(filepath + extension, 'w', encoding='%s' % encoding)

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
            parent_node = -1
            if not node.parent == None:
                parent_node = joined_list.index(node.parent)

            file.write(
                '\n%s' % (node.name) +
                '\n%s' % (parent_node)
                )

    else:
        for node in joined_list:
            find_child_node = get_child(node, reversed_joined_list)
            find_sibling_node = get_sibling(armature, node, reversed_joined_list)
            first_child_node = -1
            first_sibling_node = -1
            if not find_child_node == None:
                first_child_node = joined_list.index(find_child_node)

            if not find_sibling_node == None:
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
            quat = bone_matrix.to_quaternion()
            scale = pose_bone.scale
            if version >= 16394:
                quat = bone_matrix.to_quaternion().inverted()

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

if __name__ == '__main__':
    bpy.ops.export_jma.export()
