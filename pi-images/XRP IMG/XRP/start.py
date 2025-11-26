from XRPLib.defaults import *
import os

# available variables from defaults: left_motor, right_motor, drivetrain,
#      imu, rangefinder, reflectance, servo_one, board, webserver
# Write your code Here


def copy(src, dst, chunk_size=512):
    """Copy a file from src to dst using only os and open()"""
    with open(src, 'rb') as fsrc:
        with open(dst, 'wb') as fdst:
            while True:
                buf = fsrc.read(chunk_size)
                if not buf:
                    break
                fdst.write(buf)
    
print("copy() method created successfully!")

def runProg(fileName):
    code = ""
    filePath = f"UserPrograms/{fileName}.py"
    with open(filePath) as f:
        code = f.read()
    exec(code)
    
print("runProg() method created successfully!")
print("Programs:")
print(os.listdir("UserPrograms"))

