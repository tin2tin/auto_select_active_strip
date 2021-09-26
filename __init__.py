import bpy
import datetime
from operator import attrgetter


def auto_select_active_strip(scene):
    screen = bpy.context.screen
    if screen.is_animation_playing:
        return
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
            # Select handles.
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


def register():
    bpy.app.handlers.frame_change_post.append(auto_select_active_strip)


def unregister():
    bpy.app.handlers.frame_change_post.remove(auto_select_active_strip)


if __name__ == "__main__":
    register()
