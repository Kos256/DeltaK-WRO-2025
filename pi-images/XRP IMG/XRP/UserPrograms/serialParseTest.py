from XRPLib.defaults import *
import sys
import select
from time import sleep as wait
import re

def parseCmd(cmd: str):
    """
    Parse a serial command like "<motor: 100; servo: 90;>"
    and return a dict.
    If parsing fails, return {'unformatted': '<reason>'}.
    """
    try:
        # Trim any whitespace or stray newlines
        cmd = cmd.strip()
        if not cmd:
            return {"unformatted": "empty input"}

        # Must start and end with angle brackets
        if not (cmd.startswith("<") and cmd.endswith(">")):
            return {"unformatted": "missing angle brackets"}

        # Extract key-value pairs (e.g. motor: 100; servo: 90)
        pattern = r'(\w+)\s*:\s*([\d\-]+)'
        matches = re.findall(pattern, cmd)

        if not matches:
            return {"unformatted": "no key-value pairs found"}

        # Build dict
        data = {key: int(value) for key, value in matches}

        # Check required keys
        required = ["motor", "servo"]
        for key in required:
            if key not in data:
                return {"unformatted": f"missing key '{key}'"}

        return data

    except ValueError:
        return {"unformatted": "invalid number format"}
    except Exception as e:
        return {"unformatted": f"unexpected error: {e}"}
def parseCmdNoRegex(cmd: str):
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

print("Flushing serial input buffer, please wait...")
i = 0
while select.select([sys.stdin], [], [], 0)[0]:
    i += 1
    print(f"Clearing byte {i}...", end=' ')
    sys.stdin.read(1)
    print(f"\rcleared")
    

print("Cleared, ready!")

i = 0
while True:
    # Check if there's data waiting on USB
    if select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline()
        line = line.replace('\r', '').replace('\n', '')
        # print("Got:", line)
        sys.stdout.write(f"Recv data checked at #{i}:{line}\n")
        
        cmdInput = parseCmdNoRegex(line)
        print("RAW BYTES:", repr(line))
        if "unformatted" in cmdInput: sys.stdout.write(f"Incoming data is unformatted: {cmdInput['unformatted']}")
        else:
            sys.stdout.write(f"---\n> Parsed motor speed is {cmdInput['motor']}%\n")
            sys.stdout.write(f"> Parsed servo angle is {cmdInput['servo']}deg\n---")
                
        sys.stdout.write('\n')
            
    else:
        # Do other stuff without blocking
        # print("No data yet...")
        sys.stdout.write(f"Check #{i} yields no data...\n")
        wait(1)
    i += 1


# available variables from defaults: left_motor, right_motor, drivetrain,
#      imu, rangefinder, reflectance, servo_one, board, webserver
# Write your code Here
