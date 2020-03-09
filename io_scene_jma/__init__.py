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

bl_info = {
    "name": "Blend2Halo2 JMA",
    "author": "General_101",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "File > Export",
    "description": "Export Halo 2/CE Jointed Model Animation File (.jma)",
    "warning": "",
    "wiki_url": "https://num0005.github.io/h2codez_docs/w/H2Tool/Animations.html",
    "support": 'COMMUNITY',
    "category": "Import-Export"}

import bpy
import sys
import argparse
import io_scene_jma.export_jma as halo

from bpy_extras.io_utils import (
        ExportHelper,
        )

from bpy.types import (
        Operator,
        )

from bpy.props import (
        BoolProperty,
        EnumProperty,
        IntProperty,
        StringProperty,
        )

class ExportJMA(Operator, ExportHelper):
    """Write a JMA file"""
    bl_idname = "export_jma.export"
    bl_label = "Export Animation"

    filename_ext = ''

    encoding: EnumProperty(
        name="Encoding:",
        description="What encoding to use for the animation file",
        default="UTF-16LE",        
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
        default="16395",
        items=[ ('16390', "16390", "CE/H2 Non-functional"),
                ('16391', "16391", "CE/H2 Non-functional"),
                ('16392', "16392", "CE/H2"),
                ('16393', "16393", "H2"),
                ('16394', "16394", "H2"),
                ('16395', "16395", "H2"),
               ]
        )

    game_version: EnumProperty(
        name="Game:",
        description="What game will the model file be used for",
        default="halo2",
        items=[ ('haloce', "Halo CE", "Export a JMA intended for Halo CE"),
                ('halo2', "Halo 2", "Export a JMA intended for Halo 2"),
               ]
        )

    custom_frame_rate: EnumProperty(
        name="Framerate:",
        description="Set the framerate this animation will run at.",
        default="30",
        items=[ ('24', "24", ""),
                ('25', "25", ""),
                ('30', "30", ""),
                ('50', "50", ""),
                ('60', "60", ""),
                ('CUSTOM', "CUSTOM", ""),
               ]
        )

    frame_rate_float: IntProperty(
        name="Custom Framerate",
        description="Set your own framerate.",
        default=30,
        min=0,
    )

    biped_controller: BoolProperty(
        name ="Biped Controller",
        description = "For Testing",
        default = False,
        options={'HIDDEN'},
        )

    filter_glob: StringProperty(
        default="*.jma;*.jmm;*.jmt;*.jmo;*.jmr;*.jrmx;*.jmh;*.jmz;*.jmw",
        options={'HIDDEN'},
        )

    def execute(self, context):
        if '--' in sys.argv:
            argv = sys.argv[sys.argv.index('--') + 1:]
            parser = argparse.ArgumentParser()
            parser.add_argument('-arg1', '--filepath', dest='filepath', metavar='FILE', required = True)
            parser.add_argument('-arg2', '--encoding', dest='encoding', type=str, default="UTF-16LE")
            parser.add_argument('-arg3', '--extension', dest='extension', type=str, default=".JMA")
            parser.add_argument('-arg4', '--jma_version', dest='jma_version', type=str, default="16392")
            parser.add_argument('-arg5', '--game_version', dest='game_version', type=str, default="halo2")
            parser.add_argument('-arg6', '--custom_frame_rate', dest='custom_frame_rate', type=str, default="30")
            parser.add_argument('-arg7', '--frame_rate_float', dest='frame_rate_float', type=str, default=30)
            parser.add_argument('-arg8', '--biped_controller', dest='biped_controller', action='store_true')
            args = parser.parse_known_args(argv)[0]
            # print parameters
            print('filepath: ', args.filepath)
            print('encoding: ', args.encoding)
            print('extension: ', args.extension)
            print('jma_version: ', args.jma_version)
            print('custom_frame_rate: ', args.custom_frame_rate)
            print('frame_rate_float: ', args.frame_rate_float)
            print('biped_controller: ', args.biped_controller)

        if len(self.filepath) == 0:
            self.filepath = args.filepath
            self.encoding = args.encoding
            self.extension = args.extension
            self.jma_version = args.jma_version
            self.game_version = args.game_version
            self.custom_frame_rate = args.custom_frame_rate
            self.frame_rate_float = args.frame_rate_float
            self.biped_controller = args.biped_controller

        return halo.export_jma(context, self.filepath, self.report, self.encoding, self.extension, self.jma_version, self.game_version, self.custom_frame_rate, self.frame_rate_float, self.biped_controller)

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
