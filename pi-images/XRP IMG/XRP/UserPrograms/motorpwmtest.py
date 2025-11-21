from XRPLib.defaults import *
from machine import Pin, PWM
from time import sleep as wait

# available variables from defaults: left_motor, right_motor, drivetrain,
#      imu, rangefinder, reflectance, servo_one, board, webserver
# Write your code Here

# pins
# IO17 = PWM
# IO26 = FWD
# IO27 = BKD
# IO12 and 13 = encoder
# Motor R

class MotorPWM:
    def __init__(self, pwm_pin, fwd_pin, bkd_pin, freq=20000):
        self.pwm = PWM(Pin(pwm_pin))
        self.pwm.freq(freq)

        self.fwdP = Pin(fwd_pin, Pin.OUT)
        self.bkdP = Pin(bkd_pin, Pin.OUT)

        self.stop()  # ensure safe state

    def stop(self):
        self.fwdP.off()
        self.bkdP.off()
        self.pwm.duty_u16(0)
    sp = stop

    def forward(self, duty):
        if duty < 0: duty = -duty
        if duty > 65535: duty = 65535

        self.fwdP.on()
        self.bkdP.off()
        self.pwm.duty_u16(duty)
    # fwd = forward
    # fd = forward

    def backward(self, duty):
        if duty < 0: duty = -duty
        if duty > 65535: duty = 65535

        self.fwdP.off()
        self.bkdP.on()
        self.pwm.duty_u16(duty)
    # bwd = backward
    # bd = backward
    
    def set_speed(self, speed):
        """
        speed: -100 to +100 (percent)
        """
        if speed > 0:
            self.forward(int(speed * 655.35))
        elif speed < 0:
            self.backward(int(-speed * 655.35))
        else:
            self.stop()
    setSpeed = set_speed
    
m = MotorPWM(17, 26, 27)
print("Motor object created")
for i in range(100):
    m.setSpeed(i)
    print(f"\r+^ Speed: {i}%   ", end='')
for i in range(100, 0, -1):
    m.setSpeed(i)
    print(f"\r+v Speed: {i}%   ", end='')
    for i in range(100):
    m.setSpeed(-i)
    print(f"\r-v Speed: {-i}%   ", end='')
for i in range(-100, 0):
    m.setSpeed(i)
    print(f"\r-^ Speed: {i}%   ", end='')
