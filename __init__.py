# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Auto-select strips under the playhead",
    "author": "Tintwotin",
    "version": (1, 0),
    "blender": (2, 90, 0),
    "location": "Sequencer > Select > Auto-Select",
    "description": "Auto-selects strips under the playhead.",
    "warning": "",
    "doc_url": "",
    "category": "Sequencer",
}

from bpy.types import (
    Operator,
    PropertyGroup,
)
import bpy
import datetime
from operator import attrgetter
from bpy.props import (
    BoolProperty,
    PointerProperty,
)


class PropertyGroup(bpy.types.PropertyGroup):
    auto_select_toggle: BoolProperty(
        name="Auto Select", description="Auto-Selects Strips under Playhead"
    )


def auto_select_active_strip(scene):
    print(bpy.context.scene.auto_select_strip.auto_select_toggle)
    if bpy.context.scene.auto_select_strip.auto_select_toggle == False:
        return
    screen = bpy.context.screen
    #    # Remove # for stop selecting while playing.
    #    if screen.is_animation_playing:
    #        return
    current_frame = bpy.context.scene.frame_current
    bpy.ops.sequencer.select_all(action="DESELECT")
    strips = bpy.context.sequences
    strips = sorted(strips, key=attrgetter("channel", "frame_final_start"))
    for strip in strips:
        if (
            not strip.lock
            and strip.frame_final_end >= current_frame
            and strip.frame_final_start <= current_frame
        ):
            # Comment this part for removing handle selection.
            if (
                strip.frame_final_end >= current_frame
                and strip.frame_final_end - 8 <= current_frame
            ):
                strip.select_right_handle = True
            elif (
                strip.frame_final_start <= current_frame
                and strip.frame_final_start + 8 >= current_frame
            ):
                strip.select_left_handle = True
            strip.select = True
            bpy.context.scene.sequence_editor.active_strip = strip


def menu_auto_select(self, context):
    manager = context.scene.auto_select_strip
    self.layout.separator()
    self.layout.prop(manager, "auto_select_toggle")


classes = (PropertyGroup,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.SEQUENCER_MT_context_menu.append(menu_auto_select)
    bpy.types.SEQUENCER_MT_select.append(menu_auto_select)
    bpy.app.handlers.frame_change_post.append(auto_select_active_strip)
    bpy.types.Scene.auto_select_strip = PointerProperty(type=PropertyGroup)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.SEQUENCER_MT_context_menu.remove(menu_auto_select)
    bpy.types.SEQUENCER_MT_select.remove(menu_auto_select)
    bpy.app.handlers.frame_change_post.remove(auto_select_active_strip)


if __name__ == "__main__":
    register()
