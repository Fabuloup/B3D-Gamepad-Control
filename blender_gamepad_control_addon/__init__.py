bl_info = {
    "name": "Gamepad Control",
    "description": "Allows you to control the camera with your gamepad.",
    "author": "Fabien RICHARD",
    "version": (1, 1),
    "blender": (3, 1, 2),
    "category": "3D View",
}

import bpy
import time
import math
import threading
from .inputs import get_gamepad

events = [];
_t = None;

def worker():
    global events
    while True :
        events.append(get_gamepad())
                
class GamepadControl(bpy.types.Operator):
    """Gamepad Control"""
    bl_idname = "view3d.gamepad_control"
    bl_label = "Gamepad_control"
    bl_space_type = "View_3D"
    bl_region_type = "UI"
    bl_category = "Gamepad_control"

    _timer = None
    
    move = {
        'x':0,
        'y':0,
        'z':0
    }

    movement_speed = {
        'x':0.1,
        'y':0.1,
        'z':0.1
    }

    rotation_speed = {
        'x':1.0,
        'y':0.5
    }

    def execute(self, context):
        global _t
        if not _t :
            _t = threading.Thread(target=worker)
            _t.start()

        self.move = {
            'x':0,
            'y':0,
            'z':0,
            'rx':0,
            'rz':0
        }

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.01, window=context.window)
        wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}
	
    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    def modal(self, context, event):
        #catch gamepad input here
        global events

        cam_obj = bpy.context.scene.camera

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            #worker()
            while len(events) > 0 :
                for event in events[0]:
                    gpd_input = ""
                    gpd_value = event.state
                    if event.code == "ABS_X":
                        gpd_input = "Left Stick X"
                        if abs(gpd_value) < 3000 :
                            gpd_value = 0
                        self.move['x'] = (float(gpd_value)/32768.0)*self.movement_speed['x']
                    elif event.code == "ABS_Y":
                        gpd_input = "Left Stick Y"
                        if abs(gpd_value) < 3000 :
                            gpd_value = 0
                        self.move['y'] = (float(gpd_value)/32768.0)*self.movement_speed['y']
                    elif event.code == "ABS_RX":
                        gpd_input = "Right Stick X"
                        if abs(gpd_value) < 3000 :
                            gpd_value = 0
                        self.move['rz'] = -(float(gpd_value)/32768.0)*self.rotation_speed['x']
                    elif event.code == "ABS_RY":
                        gpd_input = "Right Stick Y"
                        if abs(gpd_value) < 3000 :
                            gpd_value = 0
                        self.move['rx'] = (float(gpd_value)/32768.0)*self.rotation_speed['y']
                    elif event.code == "ABS_Z":
                        gpd_input = "Left Trigger"
                        self.move['z'] = -(float(gpd_value)/255.0)*self.movement_speed['z']
                    elif event.code == "ABS_RZ":
                        gpd_input = "Right Trigger"
                        self.move['z'] = (float(gpd_value)/255.0)*self.movement_speed['z']
                events.pop(0)

            cam_obj.rotation_mode = 'XYZ'
            cam_obj.rotation_euler[0] += self.move['rx']*(math.pi / 180.0)
            cam_obj.rotation_euler[2] += self.move['rz']*(math.pi / 180.0)

            theta = cam_obj.rotation_euler[2]

            cam_obj.location.x += self.move['x']*math.cos(theta)-self.move['y']*math.sin(theta)
            cam_obj.location.y += self.move['x']*math.sin(theta)+self.move['y']*math.cos(theta)
            cam_obj.location.z += self.move['z']

            cam_obj.keyframe_insert(data_path="location")
            cam_obj.keyframe_insert(data_path="rotation_euler")

        return {'PASS_THROUGH'}

def menu_func(self, context):
    self.layout.operator(GamepadControl.bl_idname)

def register():
    bpy.utils.register_class(GamepadControl)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(GamepadControl)

if __name__ == "__main__":
    register()