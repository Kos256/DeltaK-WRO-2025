% --- 1. Input Parameters (Modify these values) ---
M = 1;      % Total mass of the robot (kg)
r = 0.03175;    % Wheel radius (m) - 35 mm radius (70 mm diameter)
N_w = 1;      % Number of driving motors/wheels
RPM = 100;    % Desired motor output speed (RPM)
mu_r = 0.01;  % Coefficient of rolling resistance
a_max = 3.2;  % Maximum desired linear acceleration (m/s^2)
eta_g = 0.8; % Drivetrain efficiency (0.85 = 85%)
g = 9.81;     % Acceleration due to gravity (m/s^2)

% --- 2. Calculate Theoretical Linear Speed (v_max) at 120 RPM ---
v_max = (RPM * 2 * pi / 60) * r;

% --- 3. Calculate Required Force Components (Maximum Force for Acceleration) ---
% Force to overcome Rolling Resistance (Fr):
Fr = mu_r * M * g;

% Force for Acceleration (Fa):
Fa = M * a_max;

% Total Force (F_total) required from all motors:
F_total = Fr + Fa;

% --- 4. Calculate Minimum Required Torque Per Motor ---
% Total Required Torque: Tau_total = F_total * r
Tau_total = F_total * r;

% Minimum Torque Per Motor (accounting for number of motors and efficiency):
% Tau_motor = (Tau_total / N_w) / eta_g
Tau_motor = (Tau_total / N_w) / eta_g;

% --- 5. Display Results ---
fprintf('--- WRO Car Motor Calculation ---\n');
fprintf('Robot Mass: %.2f kg | Wheel Radius: %.3f m\n', M, r);
fprintf('-------------------------------------------\n');
fprintf('Theoretical Max Speed at %d RPM: %.2f m/s (%.1f cm/s)\n', RPM, v_max, v_max*100);
fprintf('Total Force Required for %.1f m/s^2 accel: %.2f N\n', a_max, F_total);
fprintf('Minimum Torque Required Per Motor (Tau_motor): %.4f Nm\n', Tau_motor);

% Recommended Design Torque with a safety factor
Safety_Factor = 1.5;
Tau_design = Tau_motor * Safety_Factor;
fprintf('Recommended Design Torque (with 1.5 Safety Factor): %.4f Nm\n', Tau_design);