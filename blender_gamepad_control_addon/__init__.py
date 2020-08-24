bl_info = {
    "name": "Gamepad Control",
    "description": "Allows you to control the camera with your gamepad.",
    "author": "Fabien RICHARD",
    "version": (1, 0),
    "blender": (2, 80, 0),
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
    bl_label = "Gamepad Control"

    _timer = None
    
    move = {
        'x':0,
        'y':0,
        'z':0
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
                        self.move['x'] = (float(gpd_value)/32768.0)*0.1
                    elif event.code == "ABS_Y":
                        gpd_input = "Left Stick Y"
                        if abs(gpd_value) < 3000 :
                            gpd_value = 0
                        self.move['y'] = (float(gpd_value)/32768.0)*0.1
                    elif event.code == "ABS_RX":
                        gpd_input = "Right Stick X"
                        if abs(gpd_value) < 3000 :
                            gpd_value = 0
                        self.move['rz'] = -(float(gpd_value)/32768.0)*0.3
                    elif event.code == "ABS_RY":
                        gpd_input = "Right Stick Y"
                        if abs(gpd_value) < 3000 :
                            gpd_value = 0
                        self.move['rx'] = -(float(gpd_value)/32768.0)*0.25
                    elif event.code == "ABS_Z":
                        gpd_input = "Left Trigger"
                        self.move['z'] = -(float(gpd_value)/255.0)*0.1
                    elif event.code == "ABS_RZ":
                        gpd_input = "Right Trigger"
                        self.move['z'] = (float(gpd_value)/255.0)*0.1
                events.pop(0)

            bpy.data.objects['Camera'].rotation_mode = 'XYZ'
            bpy.data.objects['Camera'].rotation_euler[0] += self.move['rx']*(math.pi / 180.0)
            bpy.data.objects['Camera'].rotation_euler[2] += self.move['rz']*(math.pi / 180.0)

            theta = bpy.data.objects['Camera'].rotation_euler[2]

            bpy.data.objects['Camera'].location.x += self.move['x']*math.cos(theta)-self.move['y']*math.sin(theta)
            bpy.data.objects['Camera'].location.y += self.move['x']*math.sin(theta)+self.move['y']*math.cos(theta)
            bpy.data.objects['Camera'].location.z += self.move['z']

        return {'PASS_THROUGH'}

def register():
    bpy.utils.register_class(GamepadControl)


def unregister():
    bpy.utils.unregister_class(GamepadControl)
