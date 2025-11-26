from XRPLib.defaults import *
from XRPLib.encoded_motor import EncodedMotor
from XRPLib.servo import Servo
from machine import Pin, time_pulse_us
import sys
import select
import time
from time import sleep as wait
import re

# program params
_PROGPARAMS = {
    'debug_text': False,
    'motor_test': False,
    'routine_rate_hz': 10
    'servo_offset_left': 80
    'servo_offset_center': 90
    'servo_offset_right': 100
}
# --------------

class Ultrasonic:
    def __init__(self, trig_pin, echo_pin, timeout_us=30000):
        self.trig = Pin(trig_pin, mode=Pin.OUT)
        self.echo = Pin(echo_pin, mode=Pin.IN)
        self.timeout_us = timeout_us

    def distance(self):
        '''Returns distance in cm.'''
        # send pulse
        self.trig.value(0)
        time.sleep_us(2)
        self.trig.value(1)
        time.sleep_us(10)
        self.trig.value(0)
        # measure echo time
        pulse_time = time_pulse_us(self.echo, 1, self.timeout_us)
        # convert to cm: sound speed ~343 m/s => ~29.1 us per cm round-trip
        distance = (pulse_time / 2) / 29.1
        return distance

# drive motor and servo motor
driveMtr = EncodedMotor.get_default_encoded_motor(2)
servoMtr = Servo(16)

# ultra sonic left and right
usLeft = Ultrasonic(28, 22)
usRight = Ultrasonic(21, 20)

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
def setSteerCorrected(steer, debug=False):
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
    softLimits = {
        'left': _PROGPARAMS['servo_offset_left'],
        'right': _PROGPARAMS['servo_offset_right'],
        'center': _PROGPARAMS['servo_offset_center']
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
        if debug: print("steer is not within range, freeing servo")
        # return (1, -1) # return error 1 and angle -1 to indicate a fail
        servoMtr.free()
        return (0, -1) # return error 0 and indicate servo is freed thru angle being -1
    servoMtr.set_angle(outAngle)

imu.calibrate()

def parseCmd(cmd: str):
    try:
        cmd = cmd.strip().replace('\r', '').replace('\n', '')

        if not cmd:
            return {"unformatted": "empty input"}

        if not (cmd.startswith("<") and cmd.endswith(">")):
            return {"unformatted": "missing angle brackets"}

        # remove angle brackets
        inside = cmd[1:-1]

        pairs = inside.split(';')
        data = {}

        for pair in pairs:
            if not pair.strip():
                continue  # skip empty from final semicolon

            if ':' not in pair:
                return {"unformatted": f"missing ':' in '{pair.strip()}'"}

            key, value = pair.split(':', 1)
            key = key.strip()
            value = value.strip()

            if not value.lstrip('-').isdigit():
                return {"unformatted": f"invalid number '{value}'"}

            data[key] = int(value)

        # Required fields enforcement
        for key in ("motor", "servo"):
            if key not in data:
                return {"unformatted": f"missing key '{key}'"}

        return data

    except Exception as e:
        return {"unformatted": f"unexpected error: {e}"}
        
        
# clear the entire serial buffer so previous data cannot interfere
print("Flushing serial input buffer, please wait...")
i = 0
while select.select([sys.stdin], [], [], 0)[0]:
    i += 1
    print(f"Clearing byte {i}...", end=' ')
    sys.stdin.read(1)
    print(f"\rcleared")
print("Cleared, ready!")

# # testing motor
# print("Testing motor FWD")
# driveMtr.set_effort(0.2)
# wait(1)
# print("Testing motor BKD")
# driveMtr.set_effort(-0.2)
# wait(1)
# driveMtr.coast()

# testing motor ramp speed
if _PROGPARAMS['motor_test']:
    for i in range(0, 100):
        print(f"\rSpeed: {i}%  ", end='')
        # print(f"\rSpeed: [", end='')
        # for j in range(round(i/10)): print('|', end='')
        # for j in range(10 - round(i/10)): print(' ', end='')
        driveMtr.set_effort(i/100.0)
        wait(0.002)
    for i in range(100, 0, -1):
        print(f"\rSpeed: {i}%  ", end='')
        driveMtr.set_effort(i/100.0)
        wait(0.002)
        
    for i in range(0, -100, -1):
        print(f"\rSpeed: {i}%  ", end='')
        driveMtr.set_effort(i/100.0)
        wait(0.002)
    for i in range(-100, 1):
        print(f"\rSpeed: {i}%  ", end='')
        driveMtr.set_effort(i/100.0)
        wait(0.002)
    driveMtr.coast()
    print()

i = 0
while True:
    # Check if there's data waiting on USB
    parseCmdSuccess = True
    if select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline()
        line = line.replace('\r', '').replace('\n', '')
        # print("Got:", line)
        if _PROGPARAMS['debug_text']: sys.stdout.write(f"Recv data checked at #{i}:{line}\n")
        
        cmdInput = parseCmd(line)
        if _PROGPARAMS['debug_text']: print("RAW BYTES:", repr(line))
        if "unformatted" in cmdInput: # this is line 122
            if _PROGPARAMS['debug_text']: sys.stdout.write(f"Incoming data is unformatted: {cmdInput['unformatted']}")
        else:
            # fetch and update motor
            mSpeed = cmdInput['motor']
            mSpeed = float(mSpeed)
            mSpeed = mSpeed / 100
            if mSpeed == 0: driveMtr.coast()
            else: driveMtr.set_effort(mSpeed)
            
            # fetch and update servo
            sAngle = cmdInput['servo']
            sAngle = int(sAngle)
            # if sAngle > -1: servoMtr.set_angle(sAngle)
            # else: servoMtr.free();
            setSteerCorrected(sAngle)
            
            if _PROGPARAMS['debug_text']: 
                sys.stdout.write(f"---\n> Parsed motor speed is {mSpeed}%\n")
                sys.stdout.write(f"> Parsed servo angle is {cmdInput['servo']}deg\n---")
            else:
                parseCmdSuccess = False
        if _PROGPARAMS['debug_text']: sys.stdout.write('\n')
            
    else:
        # Do other stuff without blocking
        # print("No data yet...")
        if _PROGPARAMS['debug_text']: sys.stdout.write(f"Check #{i} yields no data...\n")
    
    if _PROGPARAMS['routine_rate_hz'] > 0: wait(1.0 / _PROGPARAMS['routine_rate_hz'])
    # if parseCmdSuccess: sys.stdout.write(f"<i:{i};success:1;>\n\r")
    
    # send sensor output data
    outputData = {
        'i': i,
        # 'dist': rangefinder.distance(),
        # 'accel': f"{imu.get_acc_x()}, {imu.get_acc_y()}, {imu.get_acc_z()}",
        # 'gyro': f"{imu.get_roll()}, {imu.get_heading()}, {imu.get_yaw()}",
        # 'gyrorate': f"{imu.get_gyro_x_rate()}, {imu.get_gyro_y_rate()}, {imu.get_gyro_z_rate()}"
        'accel': f"{imu.get_acc_x()}, {imu.get_acc_y()}",
        'gyroHeading': imu.get_heading(),
        # 'gyroHeadingRate': imu.get_gyro_y_rate()
        'distL': usLeft.distance(),
        'distR': usRight.distance()
    }
    outputItems = []
    outputFormatted = ""
    for k, v in outputData.items():
        outputItems.append(f"{k}: {v}")
    sys.stdout.write("<" + "; ".join(outputItems) + ";>\n\r")
    # sys.stdout.flush()
    
    i += 1

# available variables from defaults: left_motor, right_motor, drivetrain,
#      imu, rangefinder, reflectance, servo_one, board, webserver
# Write your code Here

