from XRPLib.defaults import *
from time import sleep

def drive_distance(5):
    while drivetrain.get_left_encoder_position() < distance_to_drive:
        drivetrain.set_speed(5, 5)
        time.sleep(0.01)
    drivetrain.stop()