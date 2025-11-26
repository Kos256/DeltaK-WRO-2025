import threading
import serial
import time
import math
from rplidar import RPLidar, RPLidarException

# --- 1. CONFIGURATION ---
# Motor and Steering Settings
XRP_PORT = '/dev/ttyACM0'
XRP_BAUD = 230400
LIDAR_PORT = '/dev/ttyUSB0'
LIDAR_BAUD = 256000 # Confirmed from your input

# Speed Constants (You must tune these RPM/Scale values!)
NORMAL_SPEED = 300     # High speed for line following
SLOW_SPEED = 50        # Slow, controlled speed for final approach
STOP_SPEED = 0         # Precise stop command

# Challenge-Specific Constants
LAP_DISTANCE_M = 15.0  # ⚠️ CRITICAL: Must be calibrated (e.g., 15.0 meters per lap)
TOTAL_LAPS_REQUIRED = 3

# --- 2. THREAD-SAFE DATA STRUCTURE ---
class SharedData:
    """Holds shared variables and a lock for thread-safe access."""
    def __init__(self):
        self.lock = threading.Lock()
        
        # Lidar data
        self.min_front_distance = 99999 
        self.wall_distance_left = 5000  # Placeholder for lane centering distance
        self.wall_distance_right = 5000 # Placeholder for lane centering distance
        
        # 🟢 NEW: Lap Tracking and Encoder Data
        self.total_distance_m = 0.0     # Distance traveled since start
        self.is_in_final_straight = False # LiDAR check for long, straight corridor
        self.lap_count = 0
        
        # State control
        self.stop_threads = False

# --- 3. LIDAR THREAD (THE LANE SENSOR) ---
class LidarThread(threading.Thread):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.lidar = None
        
    def run(self):
        try:
            self.lidar = RPLidar(LIDAR_PORT, LIDAR_BAUD)
            print("🟢 LIDAR: Connected successfully. Starting motor...")
            self.lidar.start_motor()
            
            for scan in self.lidar.iter_scans():
                if self.data.stop_threads: break
                    
                # Process scan for lane centering and geometry
                left_dist, right_dist = self._get_wall_distances(scan)
                is_straight = self._check_straight_geometry(scan)

                with self.data.lock:
                    self.data.wall_distance_left = left_dist
                    self.data.wall_distance_right = right_dist
                    self.data.is_in_final_straight = is_straight
                
        except RPLidarException as e:
            print(f"🔴 LIDAR ERROR: {e}")
            self.data.stop_threads = True
        except Exception as e:
            print(f"🔴 UNEXPECTED LIDAR ERROR: {e}")
            self.data.stop_threads = True
        finally:
            if self.lidar:
                print("LIDAR: Stopping motor and disconnecting.")
                self.lidar.stop_motor()
                self.lidar.disconnect()

    def _get_wall_distances(self, scan):
        """Calculates average distance to the left (~90 deg) and right (~270 deg) walls."""
        left_samples = [d for q, a, d in scan if 80 < a < 100 and d > 0]
        right_samples = [d for q, a, d in scan if 260 < a < 280 and d > 0]
        
        # Return average distance (or a large number if no points are seen)
        left_dist = np.mean(left_samples) if left_samples else 5000
        right_dist = np.mean(right_samples) if right_samples else 5000
        return left_dist, right_dist

    def _check_straight_geometry(self, scan):
        """
        Conceptual check for a long, straight corridor geometry.
        This often involves checking if the points around 90/270 degrees 
        form a flat plane (minimal standard deviation).
        """
        # ⚠️ PLACEHOLDER: This logic is complex and needs tuning.
        # For simulation, we'll assume the last meter of the lap is straight.
        return self.data.total_distance_m % LAP_DISTANCE_M > (LAP_DISTANCE_M - 1.0) 

# --- 4. XRP CONTROL THREAD (THE DECISION MAKER) ---
class XRPControlThread(threading.Thread):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.xrp = None
        self.current_speed = 0
        self.last_lap_distance = 0.0 # Used for lap counting
        
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
                    is_straight = self.data.is_in_final_straight

                # 4. FINAL STOP LOGIC (Highest Priority)
                if lap_count >= TOTAL_LAPS_REQUIRED:
                    self._handle_final_stop(current_encoder_distance_m, is_straight)
                
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
        This must query the XRP and get the total distance traveled since the start.
        """
        # Simulation: Increment distance over time
        with self.data.lock:
            # Simulate a speed (meters/second * time slice)
            self.data.total_distance_m += self.current_speed * 0.02 / 100.0 
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
                
                # Logic to reset the encoder or track next lap
                self.last_lap_distance = current_distance 

    def _handle_lane_following(self, left_dist, right_dist):
        """
        Uses LiDAR distances to center the car in the lane and maintain speed.
        """
        error = left_dist - right_dist
        
        # Simple Proportional Steering Control (P-Controller)
        Kp_steer = 0.5  # TUNE ME
        target_steering_angle = int(error * Kp_steer)
        
        # Clamp steering angle to servo limits (e.g., -45 to 45)
        steering_angle = max(-45, min(45, target_steering_angle))
        
        # Send command
        self.send_xrp_command(f"<motor: {NORMAL_SPEED}; servo: {steering_angle};\n")
        self.current_speed = NORMAL_SPEED # For simulation

    def _handle_final_stop(self, current_distance, is_straight):
        """
        Manages the final approach and autonomous stop sequence.
        """
        distance_into_lap = current_distance % LAP_DISTANCE_M
        distance_to_finish = LAP_DISTANCE_M - distance_into_lap
        
        # 1. Execute SLOW DOWN when close to the finish section
        if distance_to_finish < 1.0: # Slow down 1 meter before the start point
            print(f"🏁 FINAL APPROACH: Distance {distance_to_finish:.2f} m. Slowing to {SLOW_SPEED} RPM.")
            self.send_xrp_command(f"<motor: {SLOW_SPEED}; servo: 0;\n")
            self.current_speed = SLOW_SPEED # For simulation

            # 2. Check for the final stop condition (Entering the start box)
            # This must be refined, but for simulation, we'll use a precise encoder stop:
            # Stop exactly 0.5m into the start zone
            if distance_into_lap >= 0.5: 
                print("🛑 FINAL STOP: Position Reached. Stopping motors.")
                self.send_xrp_command(f"<motor: {STOP_SPEED}; servo: 0;\n")
                self.current_speed = STOP_SPEED
                self.data.stop_threads = True
                
    def send_xrp_command(self, msg):
        """Helper function to send commands to XRP."""
        try:
            self.xrp.write(msg.encode('utf-8'))
        except Exception:
            pass # Fail silently if port is temporarily busy or disconnected

# --- 5. MAIN EXECUTION ---
def main():
    print("--- WRO Open Challenge Control System (3-Lap Stop) ---")
    
    # ⚠️ Check for numpy, required for LidarThread's calculation
    try:
        import numpy as np
    except ImportError:
        print("🔴 ERROR: numpy is required for this code. Please run: pip install numpy")
        return

    data = SharedData()
    
    # 1. Initialize and start the threads
    lidar_thread = LidarThread(data)
    xrp_thread = XRPControlThread(data)

    lidar_thread.start()
    xrp_thread.start()

    try:
        # Keep the main thread alive while waiting for the others
        while not data.stop_threads:
            time.sleep(1)
            
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
    main()