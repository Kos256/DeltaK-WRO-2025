%% DC Motor Speed Controller Design and Analysis
% This script models a closed-loop speed control system (using a PID controller)
% to achieve a desired output speed (RPM) with optimized stability.
%
% The script calculates:
% 1. The steady-state Input Voltage (V_ss) required to maintain the speed.
% 2. The optimized PID gains (Kp, Ki, Kd) for smooth, fast response.

% -------------------------------------------------------------------------
% --- USER INPUT: Speed & Time Parameters (The script will prompt you) ---
% -------------------------------------------------------------------------
desired_output_RPM = input('Enter the desired final output speed (in RPM): ');
% We will still ask for the desired time, but use pidtune for optimization
desired_settling_time = input('Enter the desired stabilization time (in seconds): ');

% --- USER INPUT: Load Parameters (Customize these for your setup) ---
mass_load = 1.5;            % Mass of the load (in kilograms, kg)
radius_of_load = 0.01;      % Radius at which the mass acts (in meters, m).
                            % (e.g., the radius of the pulley or wheel)
gear_ratio = 48;            % GEAR RATIO (Motor Speed:Output Speed, e.g., 48 for 1:48)
% -------------------------------------------------------------------------

% --- STEP 1: Define Physical Motor Parameters (Crucial for Accuracy) ---
% NOTE: Replace these generic values with the actual parameters 
% of your specific motor for the most accurate results.

% Electrical Constants (Armature)
R = 1.5;    % Armature Resistance (Ohms)
L = 0.003;  % Armature Inductance (Henries)
Kt = 0.01;  % Torque Constant (N*m/A)
Ke = 0.01;  % Back-EMF Constant (V*s/rad)

% Mechanical Constants (Rotor)
J_rotor = 1e-5;   % Rotor Inertia (kg*m^2)
b = 1e-6;         % Viscous Friction Coefficient (N*m*s/rad)

% --- LOAD CALCULATION ---
J_load = mass_load * (radius_of_load)^2; 
J = J_rotor + J_load; 

fprintf('--- DC Motor Model Parameters ---\n');
fprintf('Target Output Speed: %.2f RPM\n', desired_output_RPM);
fprintf('Target Settling Time (for reference): %.2f seconds\n', desired_settling_time);
fprintf('Total Inertia (J): %g kg*m^2\n', J);
fprintf('Gear Ratio: 1:%g\n\n', gear_ratio);

%% --- STEP 2: Calculate Open-Loop Transfer Function G(s) ---

% Motor Shaft Speed in rad/s (Input: Va, Output: w_motor)
Numerator = Kt;
Denominator = [(L*J), (R*J + L*b), (R*b + Kt*Ke)];
G_s = tf(Numerator, Denominator);

%% --- STEP 3: Solve for Required Steady-State Voltage (Va_required) ---

% This voltage is the ideal DC signal needed to maintain the target speed.
% 1. Convert Desired Output RPM to Motor Shaft Speed (rad/s)
desired_motor_rads = desired_output_RPM * gear_ratio * (2 * pi / 60);

% 2. Calculate the DC Gain (Steady-State gain at s=0)
dc_gain = Kt / (R*b + Kt*Ke);

% 3. Calculate Required Voltage (Va)
Va_required = desired_motor_rads / dc_gain;

fprintf('\n--- Required Control Outputs ---\n');
fprintf('Required Motor Speed (at shaft): %.2f rad/s\n', desired_motor_rads);
fprintf('1. Steady-State Input Voltage (V_ss) for speed: %.3f Volts\n', Va_required);
fprintf('   (The PID controller will automatically supply this as its steady-state output.)\n');

% Safety Check:
if Va_required > 5
    fprintf('!! WARNING: Required steady-state voltage (%.3fV) exceeds typical 5V limit. Speed is unreachable. !!\n', Va_required);
end

%% --- STEP 4: Design PID Controller for Optimal Stability and Speed ---

% Use pidtune to automatically find RECOMMENDED PID gains (Kp, Ki, Kd)
% for the plant G_s.
% pidtune optimizes for robustness (stability) and a good response time.
C_pid = pidtune(G_s, 'pid');

Kp_opt = C_pid.Kp;
Ki_opt = C_pid.Ki;
Kd_opt = C_pid.Kd;

fprintf('\n2. Recommended PID Controller Gains (Tuned for Robust Stability):\n');
fprintf('   Proportional Gain (Kp): %.3f\n', Kp_opt);
fprintf('   Integral Gain (Ki):     %.3f\n', Ki_opt);
fprintf('   Derivative Gain (Kd):   %.3f\n', Kd_opt);

% --- Manual Input for PID Gains ---
fprintf('\n--- Manual PID Input ---\n');
% Prompt user for Kp, showing the recommended value in brackets
Kp = input(sprintf('Enter Kp (Recommended: %.3f): ', Kp_opt));
% Prompt user for Ki, showing the recommended value in brackets
Ki = input(sprintf('Enter Ki (Recommended: %.3f): ', Ki_opt));
% Prompt user for Kd, showing the recommended value in brackets
Kd = input(sprintf('Enter Kd (Recommended: %.3f): ', Kd_opt));

fprintf('\nUsing manually entered gains: Kp=%.3f, Ki=%.3f, Kd=%.3f for simulation.\n', Kp, Ki, Kd);


%% --- STEP 5: Closed-Loop Simulation with PID Controller ---

% The PID Controller Transfer Function: C(s) = Kp + Ki/s + Kd*s
C_s = tf([Kd, Kp, Ki], [1, 0]); 

% The overall Open-Loop Transfer Function is C(s) * G(s)
G_ol = C_s * G_s;

% Closed-Loop System T(s) = G_ol / (1 + G_ol * H(s))
% H(s)=1 for unity feedback speed control
G_cl = feedback(G_ol, 1);

% Simulation time must be long enough for the response to settle
t_final = 20; % Use a longer time to show the stable response
t = 0:0.01:t_final;

% The closed-loop system input is the desired motor speed reference (rad/s)
u_ref = desired_motor_rads * ones(size(t));

% Simulate the response to the speed reference
[omega_motor_rads, time] = lsim(G_cl, u_ref, t);

% Convert simulated motor speed to output shaft RPM for plotting
omega_output_RPM = (omega_motor_rads * (60 / (2 * pi))) / gear_ratio;

figure('Name', 'DC Motor PID Closed-Loop Speed Response', 'NumberTitle', 'off');

% Plot the Output Shaft Speed Response (RPM)
plot(time, omega_output_RPM, 'b', 'LineWidth', 2);
hold on;
title(sprintf('PID Controlled Output Shaft Speed (Target: %.2f RPM)', desired_output_RPM));
xlabel('Time (seconds)');
ylabel('Output Shaft Speed (RPM)');
grid on;

% Add the target speed line
plot([0 max(time)], [desired_output_RPM desired_output_RPM], 'r--', 'LineWidth', 1);
legend('Simulated Output Speed', 'Desired Stable Speed', 'Location', 'southeast');
hold off;

% Extract actual settling time and overshoot from the PID controlled system
settling_info = stepinfo(G_cl);
actual_settling_time = settling_info.SettlingTime;
overshoot = settling_info.Overshoot;

fprintf('\n--- Actual Simulation Results (PID Controlled) ---\n');
fprintf('3. Actual Stabilization Time:\n');
fprintf('   The system stabilizes at the target speed in %.3f seconds.\n', actual_settling_time);
fprintf('4. Maximum Overshoot:\n');
fprintf('   The speed overshoots the target by: %.2f%%\n', overshoot);
fprintf('5. Final Achieved Speed:\n');
fprintf('   The final speed reached in the simulation is %.2f RPM.\n', omega_output_RPM(end));
