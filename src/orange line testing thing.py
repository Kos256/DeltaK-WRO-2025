import time
import threading
from queue import Queue
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera

# -----------------------------
# MOTOR / SERVO QUEUE
# -----------------------------
motor_queue = Queue()

def send_motor_command(command):
    """Send command safely to XRP controller via queue"""
    motor_queue.put(command)

def motor_worker():
    """Worker thread that sends commands with small delay"""
    while True:
        cmd = motor_queue.get()
        if cmd == "STOP_THREAD":
            break
        # xrp.send(cmd)  # Replace with your XRP controller command
        print(f"Sent motor command: {cmd}")
        time.sleep(0.02)  # Small delay to avoid serial jam

# -----------------------------
# ULTRASONIC HELPER
# -----------------------------
LEFT_TRIG = 23
LEFT_ECHO = 24
RIGHT_TRIG = 27
RIGHT_ECHO = 22

def read_ultrasonic(trig_pin, echo_pin):
    """Dummy function; replace with actual GPIO ultrasonic reading"""
    distance = 20  # Replace with actual reading
    return distance

# -----------------------------
# ENCODER HELPER
# -----------------------------
class Encoder:
    def __init__(self):
        self.count = 0

    def reset(self):
        self.count = 0

    def read(self):
        # Replace with actual encoder reading
        return self.count

left_encoder = Encoder()
right_encoder = Encoder()

# -----------------------------
# NAVIGATION PARAMETERS
# -----------------------------
TARGET_LAPS = 3
lap_count = 0
ENCODER_COUNTS_PER_LAP = 1000  # Replace with your calibration
STEERING_CORRECTION_MAX = 30    # Max servo adjustment for corners
STEERING_CORRECTION_STRAIGHT = 10  # Small correction for straight sections

# Define corner positions in encoder counts (example)
CORNER_POSITIONS = [200, 500, 800]  # Replace with your calibration

# -----------------------------
# PI CAMERA SETUP
# -----------------------------
camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 30
raw_capture = PiRGBArray(camera, size=(320, 240))
time.sleep(0.5)  # warm-up

# Marker detection parameters (finish section)
LOWER_COLOR = (0, 120, 70)
UPPER_COLOR = (10, 255, 255)
MARKER_THRESHOLD = 200  # pixel count threshold

def detect_finish_marker(frame):
    """Return True if finish marker detected"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, LOWER_COLOR, UPPER_COLOR)
    mask2 = cv2.inRange(hsv, (170,120,70), (180,255,255))
    mask = mask1 + mask2
    count = cv2.countNonZero(mask)
    return count > MARKER_THRESHOLD

# -----------------------------
# MAIN LOOP WITH CORNER AND CAMERA STOP
# -----------------------------
def main_loop():
    global lap_count
    left_encoder.reset()
    right_encoder.reset()

    send_motor_command("MOTOR_FORWARD 100")  # start motors

    for frame in camera.capture_continuous(raw_capture, format="bgr",
use_video_port=True):
        image = frame.array

        # --- Ultrasonic centering ---
        left_dist = read_ultrasonic(LEFT_TRIG, LEFT_ECHO)
        right_dist = read_ultrasonic(RIGHT_TRIG, RIGHT_ECHO)

        # Determine if approaching a corner
        avg_count = (left_encoder.read() + right_encoder.read()) / 2
        near_corner = any(abs(avg_count - pos) < 50 for pos in
CORNER_POSITIONS)  # 50 counts margin

        if near_corner:
            # Sharper turn proportional to side distance difference
            error = left_dist - right_dist
            servo_value = max(-STEERING_CORRECTION_MAX,
min(STEERING_CORRECTION_MAX, error))
            send_motor_command(f"SERVO_ADJUST {servo_value}")
        else:
            # Straight section: small ultrasonic correction
            if left_dist < right_dist:
                send_motor_command(f"SERVO_ADJUST
{STEERING_CORRECTION_STRAIGHT}")
            elif right_dist < left_dist:
                send_motor_command(f"SERVO_ADJUST
{-STEERING_CORRECTION_STRAIGHT}")
            else:
                send_motor_command("SERVO_ADJUST 0")  # straight

        # --- Lap update ---
        if avg_count >= ENCODER_COUNTS_PER_LAP:
            lap_count += 1
            print(f"Completed lap {lap_count}")
            left_encoder.reset()
            right_encoder.reset()

        # --- Camera stop logic (3rd lap only) ---
        if lap_count >= TARGET_LAPS:
            if detect_finish_marker(image):
                send_motor_command("MOTOR_STOP")
                print("Robot stopped in finish section on 3rd lap!")
                break

        raw_capture.truncate(0)
        time.sleep(0.05)

# -----------------------------
# START MOTOR THREAD
# -----------------------------
motor_thread = threading.Thread(target=motor_worker, daemon=True)
motor_thread.start()

try:
    main_loop()
finally:
    motor_queue.put("STOP_THREAD")
    motor_thread.join()
    camera.close()