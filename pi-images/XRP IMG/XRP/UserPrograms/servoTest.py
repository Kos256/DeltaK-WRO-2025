from XRPLib.defaults import *
from XRPLib.servo import Servo
from time import sleep as w

# available variables from defaults: left_motor, right_motor, drivetrain,
#      imu, rangefinder, reflectance, servo_one, board, webserver
# Write your code Here

# 40 
# 100
# 160

runmode = "test"
runmode = "input"
runmode = "func"

s = Servo(16)
s.free()

w(1) # wait 1 second

print("wiggling...", end='')
for i in range(8):
    print(f"\rwiggle {i}   ", end='')
    s.set_angle(100+20)
    w(0.1)
    s.set_angle(100-20)
    w(0.1)
    
s.free()
w(1)

def mapf(v, inL, inU, outL, outU): # float linear interpolation (similar to arduino's map() function)
    return outL + (v - inL) * (outU - outL) / (inU - inL)
def isnumber(s):
    if len(s) == 0:
        return False
    if s[0] == '-':        # allow leading minus
        s = s[1:]          # strip it
        if len(s) == 0:    # "-" alone is not a number
            return False
    return all('0' <= c <= '9' for c in s)
def setSteerCorrected(steer, debug=True):
    # check type and convert to int if needed
    if isinstance(steer, str):
        if debug: print("steer is a string, attempting to convert to int")
        if not isnumber(steer):
            if debug: print("steer is not numeric or not int")
            return (2, -1) # return error 1 and angle -1 to indicate a fail
        else:
            steer = int(steer)
            if debug: print("converted")
    
    # check range and set servo angle
    # TODO: ALLOW -100 TO 100 STEERING (for accuracy) AND REMAP LEFT AND RIGHT SCALING VALUES TO MATCH HARD LIMITS
    softLimits = {
        'left': 40,
        'right': 160,
        'center': 100
    }
    if steer == 0:
        outAngle = 100
        if debug: print(f"Sterring straight ({outAngle}deg)")
    elif -100 <= steer < 0:
        outAngle = mapf(steer, -100, 0, softLimits['left'], softLimits['center'])
        outAngle = int(round(outAngle))
        if debug: print(f"Sterring left {abs(steer)}% ({outAngle}deg)")
    elif 0 < steer <= 100:
        outAngle = mapf(steer, 0, 100, softLimits['center'], softLimits['right'])
        outAngle = int(round(outAngle))
        if debug: print(f"Sterring right {steer}% ({outAngle}deg)")
    else:
        if debug: print("steer is not within range")
        return (1, -1) # return error 1 and angle -1 to indicate a fail
    s.set_angle(outAngle)
    # outAngle = 90
    # if 0 <= deg <= 180:
    #     if debug: print("deg is within range, setting...")
    #     s.set_angle(deg)
    # elif deg < 0:
    #     if debug: print("freed servo")
    #     s.free()
    # else:
    #     if debug: print("deg is not within range")
    #     return (1, -1) # return error 1 and angle -1 to indicate a fail
    
    
    return (0, outAngle) # return no error and the final angle
    # err 0 = OK
    # err 1 = deg arg is not in the range 0 <= deg <= 180
    # err 2 = deg arg is not an integer or numeric
    

if runmode == "test":
    print("90 deg")
    s.set_angle(90)
    w(1)
    print("0 deg")
    s.set_angle(0)
    w(1)
    print("90 deg")
    s.set_angle(90)
    w(1)
    print("180 deg")
    s.set_angle(180)
    w(1)
    
    print("servo free()")
    s.free()
    
if runmode == "input":
    for i in range(20):
        print(f"{20-i} input(s) remaining, ", end='')
        a = input("enter angle: ")
        try:
            a = int(a)
        except:
            print("int(a) failed")
            continue
            
        if a < 0:
            s.free()
            print("Freed servo")
        elif a >= 0 and a <= 180:
            s.set_angle(a)
            print(f"Set angle to {a}deg")
        else:
            print("Out of range!")
            
            
if runmode == "func":
    for i in range(20):
        print(f"{20-i} input(s) remaining, ", end='')
        a = input("enter value: ")
        result = setSteerCorrected(a)
        print(f"Set angle to {result[1]}deg")