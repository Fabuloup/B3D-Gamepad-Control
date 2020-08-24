import inputs

maxX = 0
minX = 0

while 1:
    events = inputs.get_gamepad()
    for event in events:
        gpd_input = ""
        gpd_value = event.state
        if event.code == "ABS_X":
            gpd_input = "Left Stick X"
        elif event.code == "ABS_Y":
            gpd_input = "Left Stick Y"
        elif event.code == "ABS_RX":
            gpd_input = "Right Stick X"
            if gpd_value > maxX :
                maxX = gpd_value
            if gpd_value < minX :
                minX = gpd_value
        elif event.code == "ABS_RY":
            gpd_input = "Right Stick Y"
        elif event.code == "ABS_Z":
            gpd_input = "Left Trigger"
        elif event.code == "ABS_RZ":
            gpd_input = "Right Trigger"

        if gpd_input != "":
            print(gpd_input, gpd_value)
        print(event.ev_type, event.code, event.state)
        print(maxX,minX)
