import bpy
import datetime
from operator import attrgetter


def auto_select_active_strip(scene):
    current_frame = bpy.context.scene.frame_current
    sel_strips = []
    bpy.ops.sequencer.select_all(action="DESELECT")
    strips = bpy.context.sequences
    strips = sorted(strips, key=attrgetter("channel", "frame_final_start"))
    for strip in strips:
        if (
            not strip.lock
            and strip.frame_final_end >= current_frame
            and strip.frame_final_start <= current_frame
        ):
            strip.select = True
            sel_strips.append(strip)
    if sel_strips != []:
        bpy.context.scene.sequence_editor.active_strip = sel_strips[len(sel_strips)]


def register():
    bpy.app.handlers.frame_change_post.append(auto_select_active_strip)


def unregister():
    bpy.app.handlers.frame_change_post.remove(auto_select_active_strip)


if __name__ == "__main__":
    register()
