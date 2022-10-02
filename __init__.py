# SPDX-License-Identifier: GPL-2.0-or-later

bl_info = {
    "name": "Auto-select strips under the playhead",
    "author": "Tintwotin, Samuel Bernou",
    "version": (1, 4),
    "blender": (2, 90, 0),
    "location": "Sequencer > Select > Auto-Select & Sidebar > Auto Select",
    "description": "Auto-selects strips under the playhead.",
    "warning": "",
    "doc_url": "https://github.com/tin2tin/auto_select_active_strip",
    "category": "Sequencer",
}

import bpy
from bpy.app.handlers import persistent
from operator import attrgetter
from bpy.types import (
    Panel,
    PropertyGroup,
)
from bpy.props import (
    BoolProperty,
    EnumProperty,
    IntProperty,
    PointerProperty,
)

class autoselect_property_group(PropertyGroup):
    auto_select_toggle: BoolProperty(
        name="Auto Select", description="Auto-Selects Strips under playhead"
    )

    select_mode: EnumProperty(
        name="Select",
        description="Method to select strips under cursor",
        default='ALL', options={'ANIMATABLE'},
        items=(
            ('ALL', 'All', 'Select All under playhead', 0),
            ('TOP', 'Top', 'Select only top strip under playhead', 1),   
            ('CHANNEL', 'Channel', 'Select only strip in chosen channel under playhead', 2),
            ))

    channel: IntProperty(name='Channel',
    description='Restrict selection to this channel', default=1)

    select_while_playing: BoolProperty(name='While Playing',
    description='Selection is still active during playback', default=True)

    select_handles: BoolProperty(name='Handles',
    description='Selectable handles', default=True)


@persistent
def auto_select_active_strip(scene):
    if bpy.context.scene.auto_select_strip.auto_select_toggle == False:
        return
    settings = bpy.context.scene.auto_select_strip
    screen = bpy.context.screen

    if not settings.select_while_playing and screen.is_animation_playing:
        return
    current_frame = bpy.context.scene.frame_current
    bpy.ops.sequencer.select_all(action="DESELECT")
    strips = bpy.context.sequences
    strips = sorted(strips, key=attrgetter("channel", "frame_final_start"),
        reverse=settings.select_mode == 'TOP')

    for strip in strips:
        if settings.select_mode == 'CHANNEL' and settings.channel != strip.channel:
            continue

        if (
            not strip.lock
            and strip.frame_final_end >= current_frame
            and strip.frame_final_start <= current_frame
        ):

            if settings.select_handles:
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

            if settings.select_mode == 'TOP':
                break

class SEQUENCER_PT_auto_select_ui(Panel):
    bl_label = "Auto Select"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_options = {"INSTANCED"}

    def draw_header(self, context):
        settings = context.scene.auto_select_strip
        ico = 'RESTRICT_SELECT_OFF' if settings.auto_select_toggle else 'RESTRICT_SELECT_ON'
        self.layout.prop(settings, "auto_select_toggle", text="", icon=ico)

    def draw(self, context):
        settings = context.scene.auto_select_strip
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        col = layout.column(align=True)
        col.prop(settings, 'select_mode')
        col_sub = col.column()
        col_sub.prop(settings, 'channel')
        col.prop(settings, 'select_handles')
        col.prop(settings, 'select_while_playing')
        col.enabled = context.scene.auto_select_strip.auto_select_toggle
        col_sub.enabled = (settings.select_mode == 'CHANNEL')


def menu_auto_select(self, context):
    self.layout.separator()
    self.layout.popover(panel="SEQUENCER_PT_auto_select_ui")
    # manager = context.scene.auto_select_strip
    #self.layout.prop(manager, "auto_select_toggle")


classes = (
    autoselect_property_group,
    SEQUENCER_PT_auto_select_ui,
    )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.auto_select_strip = PointerProperty(type=autoselect_property_group)
    # bpy.types.SEQUENCER_MT_context_menu.append(menu_auto_select)
    # bpy.types.SEQUENCER_MT_select.append(menu_auto_select)
    bpy.types.SEQUENCER_HT_header.append(menu_auto_select) 
    bpy.app.handlers.frame_change_post.append(auto_select_active_strip)


def unregister():

    del bpy.types.Scene.auto_select_strip
    # bpy.types.SEQUENCER_MT_context_menu.remove(menu_auto_select)
    # bpy.types.SEQUENCER_MT_select.remove(menu_auto_select)
    bpy.types.SEQUENCER_HT_header.remove(menu_auto_select)
    bpy.app.handlers.frame_change_post.remove(auto_select_active_strip)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
