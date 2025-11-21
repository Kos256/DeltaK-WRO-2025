from XRPLib.defaults import *
from XRPLib.encoded_motor import EncodedMotor
from XRPLib.servo import Servo
from time import sleep as wait
from time import ticks_ms as millis
# import pySerial
from machine import UART, Pin

# available variables from defaults: left_motor, right_motor, drivetrain,
#      imu, rangefinder, reflectance, servo_one, board, webserver
# Write your code Here

millisStart = millis()
def programTimeElapsedMs(): return millis() - millisStart

m = EncodedMotor.get_default_encoded_motor(2)
s = Servo(16)


imu.calibrate(0.3)

while programTimeElapsedMs() < 15000:
    print(input())

# for i in range(5):
#     s.set_angle(0)
#     wait(1)
#     s.set_angle(180)
#     wait(1)

# while programTimeElapsedMs() < 30000:
#     print(f"Ydeg: {imu.get_heading()}\nxv: {imu.get_acc_x()}\nzv: {imu.get_acc_z()}\n-----")
#     wait(0.1)
    

# while 1:
    # print(rangefinder.distance())
