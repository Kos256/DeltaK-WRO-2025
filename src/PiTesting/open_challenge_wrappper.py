import threading
import serial
import time
import math
import subprocess
import numpy as np

# --- 1. CONFIGURATION ---
# Motor and Steering Settings
XRP_PORT = '/dev/ttyACM0'
XRP_BAUD = 230400

# Lidar Settings (Used only for passing arguments to the C++ binary)
LIDAR_PORT = '/dev/ttyUSB0'
LIDAR_BAUD = 256000 # Confirmed from your input

# 🟢 CUSTOMIZE: C++ Wrapper Command
# You must ensure this path and arguments correctly start your C++ binary.
# The binary is expected to print "Left_Dist_mm,Right_Dist_mm,Is_Straight_int" to stdout.
WRAPPER_COMMAND = ['./ultra_simple', LIDAR_PORT, str(LIDAR_BAUD)]

# Speed Constants (You must tune these RPM/Scale values!)
NORMAL_SPEED = 300     # ⚠️ TUNE ME: High speed for line following
SLOW_SPEED = 50        # ⚠️ TUNE ME: Slow, controlled speed for final approach
STOP_SPEED = 0         # Precise stop command

# Challenge-Specific Constants
LAP_DISTANCE_M = 15.0  # ⚠️ CRITICAL: Must be calibrated (e.g., 15.0 meters per lap)
TOTAL_LAPS_REQUIRED = 3

# --- 2. THREAD-SAFE DATA STRUCTURE ---
class SharedData:
    """Holds shared variables and a lock for thread-safe access."""
    def __init__(self):
        self.lock = threading.Lock()
        
        # Lidar data (Updated by C++ Subprocess)
        self.wall_distance_left = 5000  # Distance to left wall in mm
        self.wall_distance_right = 5000 # Distance to right wall in mm
        
        # 🟢 NEW: Lap Tracking and Encoder Data
        self.total_distance_m = 0.0     # Distance traveled since start (from XRP)
        # LiDAR geometry check: True when in a long, straight corridor (updated by C++)
        self.is_in_final_straight = False 
        self.lap_count = 0
        
        # State control
        self.stop_threads = False

# --- 3. LIDAR THREAD (THE SUBPROCESS LISTENER) ---
class LidarThread(threading.Thread):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.process = None # The handle for the C++ process
        
    def run(self):
        print(f"🟢 LIDAR LISTENER: Starting C++ binary with command: {' '.join(WRAPPER_COMMAND)}")
        
        try:
            # 1. Start the C++ process and capture its stdout
            self.process = subprocess.Popen(
                WRAPPER_COMMAND,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, 
                text=True,               
                bufsize=1                
            )
            
            # 2. Continuously read lines from the C++ process's stdout
            for line in iter(self.process.stdout.readline, ''):
                if self.data.stop_threads:
                    break
                    
                line = line.strip()
                if not line:
                    continue

                # 3. Parse the assumed CSV output: "left_dist,right_dist,is_straight"
                try:
                    parts = line.split(',')
                    if len(parts) == 3:
                        left_dist = int(parts[0])
                        right_dist = int(parts[1])
                        is_straight = bool(int(parts[2]))

                        # 4. Update the shared data structure
                        with self.data.lock:
                            self.data.wall_distance_left = left_dist
                            self.data.wall_distance_right = right_dist
                            self.data.is_in_final_straight = is_straight

                except ValueError:
                    # Ignore malformed or non-numeric output
                    # print(f"LIDAR LISTENER: Skipping unparseable line: {line}")
                    pass
            
            # Check if the process terminated on its own
            self.process.wait()

        except FileNotFoundError:
            print(f"🔴 LIDAR ERROR: C++ executable not found. Check path: {WRAPPER_COMMAND[0]}")
            # Do not set stop_threads here if you want to keep trying to connect, but for safety:
            self.data.stop_threads = True
        except Exception as e:
            print(f"🔴 UNEXPECTED LISTENER ERROR: {e}")
            self.data.stop_threads = True
            
        finally:
            if self.process and self.process.poll() is None:
                print("LIDAR: Terminating C++ process...")
                self.process.terminate()
                self.process.wait()
            print("LIDAR: Listener thread finished.")

# --- 4. XRP CONTROL THREAD (THE DECISION MAKER) ---
class XRPControlThread(threading.Thread):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.xrp = None
        self.current_speed_for_sim = 0 # For simulation only
        
    def run(self):
        try:
            self.xrp = serial.Serial(XRP_PORT, XRP_BAUD, timeout=0.1)
            print("🟢 XRP: Connected successfully.")
            
            while not self.data.stop_threads:
                
                # 1. ⚠️ PLACEHOLDER: Read Encoder Distance and Status
                # You MUST replace this with actual serial communication to get the total distance from the XRP
                current_encoder_distance_m = self._read_encoder_distance() 
                
                # 2. Update Lap Count Logic
                self._update_lap_count(current_encoder_distance_m)
                
                # 3. Read Shared Data
                with self.data.lock:
                    lap_count = self.data.lap_count
                    left_dist = self.data.wall_distance_left
                    right_dist = self.data.wall_distance_right
                    is_in_straight = self.data.is_in_final_straight

                # 4. FINAL STOP LOGIC (Highest Priority)
                if lap_count >= TOTAL_LAPS_REQUIRED:
                    self._handle_final_stop(current_encoder_distance_m, is_in_straight)
                
                # 5. NORMAL NAVIGATION LOGIC (Lower Priority)
                else:
                    self._handle_lane_following(left_dist, right_dist)

                # Control loop timing
                time.sleep(0.02) # Run the control loop at 50 Hz

        except serial.SerialException as e:
            print(f"🔴 XRP SERIAL ERROR: {e}")
            self.data.stop_threads = True
        except Exception as e:
            print(f"🔴 UNEXPECTED XRP ERROR: {e}")
            self.data.stop_threads = True
        finally:
            if self.xrp and self.xrp.is_open:
                self.xrp.close()
                print("XRP: Serial connection closed.")

    def _read_encoder_distance(self):
        """
        ⚠️ CRITICAL PLACEHOLDER: Replace this with actual serial read logic.
        This must query the XRP for the total distance traveled (in meters).
        """
        # Simulation: Increment distance over time
        with self.data.lock:
            # Simulate a speed (meters/second * time slice)
            # 100 is a scale factor for simulation to turn RPM into m/s roughly
            self.data.total_distance_m += self.current_speed_for_sim * 0.02 / 100.0 
            return self.data.total_distance_m

    def _update_lap_count(self, current_distance):
        """
        Increments lap count when total distance crosses a LAP_DISTANCE_M boundary.
        """
        current_lap = math.floor(current_distance / LAP_DISTANCE_M)
        with self.data.lock:
            if current_lap > self.data.lap_count:
                self.data.lap_count = current_lap
                print(f"🎉 XRP CONTROL: LAP {self.data.lap_count} COMPLETED!")

    def _handle_lane_following(self, left_dist, right_dist):
        """
        Uses LiDAR distances to center the car in the lane and maintain speed.
        """
        # Calculate error in distance from center
        error = left_dist - right_dist
        
        # Simple Proportional Steering Control (P-Controller)
        Kp_steer = 0.5  # ⚠️ TUNE ME: Steering gain
        target_steering_angle = int(error * Kp_steer / 10.0) # Scale down error to angle
        
        # Clamp steering angle to servo limits (e.g., -45 to 45)
        steering_angle = max(-45, min(45, target_steering_angle))
        
        # Send command (e.g., <motor: 300; servo: 5;>\n)
        self.send_xrp_command(f"<motor: {NORMAL_SPEED}; servo: {steering_angle};\n")
        self.current_speed_for_sim = NORMAL_SPEED # For simulation

    def _handle_final_stop(self, current_distance, is_in_straight):
        """
        Manages the final approach and autonomous stop sequence using encoder distance 
        and LiDAR geometry confirmation.
        """
        distance_into_lap = current_distance % LAP_DISTANCE_M
        distance_to_finish = LAP_DISTANCE_M - distance_into_lap
        
        # Define the zone where the car MUST slow down (e.g., 2 meters before the finish)
        SLOW_DOWN_ZONE_M = 2.0 
        
        # 1. Execute SLOW DOWN when close to the finish section
        if distance_to_finish < SLOW_DOWN_ZONE_M: 
            print(f"🏁 FINAL APPROACH: Distance {distance_to_finish:.2f} m. Slowing to {SLOW_SPEED} RPM.")
            self.send_xrp_command(f"<motor: {SLOW_SPEED}; servo: 0;\n")
            self.current_speed_for_sim = SLOW_SPEED # For simulation

            # 2. Check for the final stop condition (LiDAR confirmation + Encoder position)
            # The stop location is assumed to be 0.5m past the start of the final straight section.
            FINAL_STOP_POSITION_M = 0.5 # ⚠️ TUNE ME: The precise stop point in the start box
            
            if is_in_straight and distance_into_lap >= FINAL_STOP_POSITION_M:
                print("🛑 FINAL STOP: Position Reached AND LiDAR Confirmed Straight Zone. Stopping motors.")
                
                # Execute the precise, final stop (0 RPM)
                self.send_xrp_command(f"<motor: {STOP_SPEED}; servo: 0;\n")
                self.current_speed_for_sim = STOP_SPEED
                
                # Signal system shutdown (Mission complete)
                self.data.stop_threads = True 
                
        else:
             # Keep driving normally until the slow-down zone
             self.send_xrp_command(f"<motor: {NORMAL_SPEED}; servo: 0;\n")

    def send_xrp_command(self, msg):
        """Helper function to send commands to XRP."""
        try:
            self.xrp.write(msg.encode('utf-8'))
        except Exception:
            pass # Fail silently if port is temporarily busy or disconnected

# --- 5. MAIN EXECUTION ---
def main():
    print("--- WRO Open Challenge Control System (3-Lap Stop) ---")
    
    data = SharedData()
    
    # 1. Initialize and start the threads
    lidar_thread = LidarThread(data)
    xrp_thread = XRPControlThread(data)

    lidar_thread.start()
    xrp_thread.start()

    try:
        # Keep the main thread alive while waiting for the others
        while not data.stop_threads:
            # Print status periodically for monitoring
            with data.lock:
                print(f"STATUS: Lap {data.lap_count}/{TOTAL_LAPS_REQUIRED} | Dist: {data.total_distance_m:.2f} m | Lidar: L:{data.wall_distance_left} R:{data.wall_distance_right} | Straight: {data.is_in_final_straight}")
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nCtrl+C detected. Shutting down system...")
    
    finally:
        # 2. Signal all threads to stop cleanly
        data.stop_threads = True
        
        # 3. Wait for the threads to finish
        lidar_thread.join()
        xrp_thread.join()
        
        print("--- System Shutdown Complete ---")

if __name__ == "__main__":
    # Ensure subprocess can find the binary by making sure it's executable
    try:
        if WRAPPER_COMMAND[0].startswith('./') and not os.access(WRAPPER_COMMAND[0], os.X_OK):
            print(f"WARNING: Making {WRAPPER_COMMAND[0]} executable.")
            os.chmod(WRAPPER_COMMAND[0], 0o755)
    except:
        pass # Ignore if permission change fails

    main()