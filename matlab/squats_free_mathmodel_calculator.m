%% FORCES AND MOMENTUM VALUES CALCULATOR
% Author: Aaron Raul Poyatos Bakker
% Date: 13/06/2023
% With the angle information, obtain all unknown forces and momentums for
% the squats free model.

%% IMPORT DATA
% Change path to desired csv file
data = readtable('../pruebas/EnsayoGiros.csv', 'Delimiter', ',');

% Data
timestamps = data.timestamp;
imu_1_q = [data.IMU_Leg_Right_qw, data.IMU_Leg_Right_qx, data.IMU_Leg_Right_qy, data.IMU_Leg_Right_qz];
imu_1_w = [data.IMU_Leg_Right_wx, data.IMU_Leg_Right_wy, data.IMU_Leg_Right_wz];
imu_2_q = [data.IMU_Thigh_Right_qw, data.IMU_Thigh_Right_qx, data.IMU_Thigh_Right_qy, data.IMU_Thigh_Right_qz];
imu_2_w = [data.IMU_Thigh_Right_wx, data.IMU_Thigh_Right_wy, data.IMU_Thigh_Right_wz];
imu_3_q = [data.IMU_UpperTrunk_Right_qw, data.IMU_UpperTrunk_Right_qx, data.IMU_UpperTrunk_Right_qy, data.IMU_UpperTrunk_Right_qz];
imu_3_w = [data.IMU_UpperTrunk_Right_wx, data.IMU_UpperTrunk_Right_wy, data.IMU_UpperTrunk_Right_wz];

% Transform timestamp to seconds
timeIncrements = timestamps/1000 - timestamps(1)/1000;

% Transform quaternions values to Euler angles
imu_1_eul = quat2eul(imu_1_q, 'XYZ');
imu_2_eul = quat2eul(imu_2_q, 'XYZ');
imu_3_eul = quat2eul(imu_3_q, 'XYZ');

% Extract absolute angles
% TODO CHECK REAL DATA VALUES TO TRANSFORM IN ABS ANGLES
absangle_A = imu_1_eul(:, 3); % Leg Z angle
absangle_B = imu_2_eul(:, 3); % Thigh Z angle
absangle_C = imu_3_eul(:, 1); % Trunk Y angle

size(absangle_A)

%% EXAMPLES WITH VIRTUAL ANGLES
% % Comment/delete this section if you want to use imported data from csv
% timeIncrements = 0:0.01:4;
% % absangle_A = transpose(linspace(pi/2, pi/4, numel(timeIncrements)));
% % absangle_B = transpose(linspace(pi/2, pi/1.2, numel(timeIncrements)));
% % absangle_C = transpose(linspace(pi/2, pi/5, numel(timeIncrements)));
% pos_i = pi/2;
% pos_f_A = pi/4;
% pos_f_B = pi/1.2;
% pos_f_C = pi/5;
% reps = 2;
% 
% absangle_A = test_angle_trajectories_linear(timeIncrements,reps,pos_i,pos_f_A);
% absangle_B = test_angle_trajectories_parabolic(timeIncrements,reps,pos_i,pos_f_B);
% absangle_C = test_angle_trajectories_linear(timeIncrements,reps,pos_i,pos_f_C);

%% MODEL PARAMETERS
% General values
g           = 9.81; % m/s2
m_body      = 90;   % Body total weight (kg)
h_body      = 170;  % Body total height (cm)
m_barbell   = 100;  % Barbell total weight (kg)
% Limbs lengths and CM offsets (m)
L_leg       = 0.231*h_body/100;
L_thigh     = 0.237*h_body/100;
L_hat       = (0.303+1-0.814)*h_body/100;
L_uppertrunk= 0.303*h_body/100;
Lp_leg      = 0.433*L_leg;
Ld_leg      = 0.567*L_leg;
Lp_thigh    = 0.433*L_thigh;
Ld_thigh    = 0.567*L_thigh;
Lp_hat      = 0.626*L_hat;
Ld_hat      = 0.374*L_hat;
% Limbs weights and partial weights (kg)
m_leg       = 0.0465*m_body;
m_thigh     = 0.1000*m_body;
m_hat       = 0.6780*m_body;

% Limb turning radios (for inertia)
r_cg_leg    = 0.302*L_leg;
r_cg_thigh  = 0.323*L_thigh;
r_cg_hat  = 0.503*L_hat;

%% OBTAIN MATRIX VALUES
% Inertia values: I = m*R2
I_leg = m_leg*r_cg_leg*r_cg_leg;
I_thigh = m_thigh*r_cg_thigh*r_cg_thigh;
I_hat = m_hat*r_cg_hat*r_cg_hat;
d = L_uppertrunk - Ld_hat;
I_barbell = m_barbell*d*d;

% --- Absolute angles management
% Sines and cosines of absolute angles
absangle_A_sin = sin(absangle_A);
absangle_A_cos = cos(absangle_A);
absangle_B_sin = sin(absangle_B);
absangle_B_cos = cos(absangle_B);
absangle_C_sin = sin(absangle_C);
absangle_C_cos = cos(absangle_C);

% Get first and second absolute angle derivates
dt = timeIncrements(2) - timeIncrements(1);
absangle_A_diff = diff(absangle_A,1) ./ dt;
absangle_B_diff = diff(absangle_B,1) ./ dt;
absangle_C_diff = diff(absangle_C,1) ./ dt;
absangle_A_diff2 = diff(absangle_A,2) ./ dt;
absangle_B_diff2 = diff(absangle_B,2) ./ dt;
absangle_C_diff2 = diff(absangle_C,2) ./ dt;
% Add initial ceros to match lengths
absangle_A_diff = [zeros(1, 1); absangle_A_diff];
absangle_B_diff = [zeros(1, 1); absangle_B_diff];
absangle_C_diff = [zeros(1, 1); absangle_C_diff];
absangle_A_diff2 = [zeros(2, 1); absangle_A_diff2];
absangle_B_diff2 = [zeros(2, 1); absangle_B_diff2];
absangle_C_diff2 = [zeros(2, 1); absangle_C_diff2];

% --- Limb accelerations
% Leg COG accelerations
a_leg_x = absangle_A_diff2.*Lp_leg.*(-absangle_A_sin)-Lp_leg.*absangle_A_diff.*absangle_A_diff.*absangle_A_cos;
a_leg_z = absangle_A_diff2.*Lp_leg.*(absangle_A_cos)-Lp_leg.*absangle_A_diff.*absangle_A_diff.*absangle_A_sin;
% Thigh COG accelerations
a_thigh_leg_x = absangle_A_diff2.*L_leg.*(-absangle_A_sin)-L_leg.*absangle_A_diff.*absangle_A_diff.*absangle_A_cos;
a_thigh_leg_z = absangle_A_diff2.*L_leg.*(absangle_A_cos)-L_leg.*absangle_A_diff.*absangle_A_diff.*absangle_A_sin;
a_thigh_x = a_thigh_leg_x + absangle_B_diff2.*Lp_thigh.*(-absangle_B_sin)-Lp_thigh.*absangle_B_diff.*absangle_B_diff.*absangle_B_cos;
a_thigh_z = a_thigh_leg_z + absangle_B_diff2.*Lp_thigh.*(absangle_B_cos)-Lp_thigh.*absangle_B_diff.*absangle_B_diff.*absangle_B_sin;
% Trunk COG accelerations
a_hat_thigh_x = a_thigh_leg_x + absangle_B_diff2.*L_thigh.*(-absangle_B_sin)-L_thigh.*absangle_B_diff.*absangle_B_diff.*absangle_B_cos;
a_hat_thigh_z = a_thigh_leg_z + absangle_B_diff2.*L_thigh.*(absangle_B_cos)-L_thigh.*absangle_B_diff.*absangle_B_diff.*absangle_B_sin;
a_hat_x = a_hat_thigh_x + absangle_C_diff2.*Lp_hat.*(-absangle_C_sin)-Lp_hat.*absangle_C_diff.*absangle_C_diff.*absangle_C_cos;
a_hat_z = a_hat_thigh_z + absangle_C_diff2.*Lp_hat.*(absangle_C_cos)-Lp_hat.*absangle_C_diff.*absangle_C_diff.*absangle_C_sin;
% Barbell COG accelerations
a_barbell_x = a_hat_thigh_x + absangle_C_diff2.*L_uppertrunk.*(-absangle_C_sin)-L_uppertrunk.*absangle_C_diff.*absangle_C_diff.*absangle_C_cos;
a_barbell_z = a_hat_thigh_z + absangle_C_diff2.*L_uppertrunk.*(absangle_C_cos)-L_uppertrunk.*absangle_C_diff.*absangle_C_diff.*absangle_C_sin;

%% BUILD A AND B MATRIX
% Ax = b -> x = A(-1)*b

iter = length(timeIncrements);
x_cell = cell(iter, 1);
offset = 3; % Avoid initial acceleration peaks

for k = 1+offset:iter
    A = [
        1, 0, -1, 0, 0, 0, 0, 0, 0;
        0, 1, 0, -1, 0, 0, 0, 0, 0;
        Ld_leg*absangle_A_sin(k,1), -Ld_leg*absangle_A_cos(k,1), Lp_leg*absangle_A_sin(k,1), -Lp_leg*absangle_A_cos(k,1), 0, 0, 1, -1, 0;
        0, 0, 1, 0, -1, 0, 0, 0, 0;
        0, 0, 0, 1, 0, -1, 0, 0, 0;
        0, 0, Ld_thigh*absangle_B_sin(k,1), Ld_thigh*absangle_B_cos(k,1), Lp_thigh*absangle_B_sin(k,1), Lp_thigh*absangle_B_cos(k,1), 0, 1, -1;
        0, 0, 0, 0, 1, 0, 0, 0, 0;
        0, 0, 0, 0, 0, 1, 0, 0, 0;
        0, 0, 0, 0, Ld_hat*absangle_C_sin(k,1), -Ld_hat*absangle_C_cos(k,1), 0, 0, 1;
    ];

    b = [
        m_leg*a_leg_x(k,1);
        m_leg*a_leg_z(k,1) + m_leg*g;
        I_leg*absangle_A_diff2(k,1);
        m_thigh*a_thigh_x(k,1);
        m_thigh*a_thigh_z(k,1) + m_thigh*g;
        I_thigh*absangle_B_diff2(k,1);
        m_hat*a_hat_x(k,1) + m_barbell*a_barbell_x(k,1);
        m_hat*a_hat_z(k,1) + m_hat*g + m_barbell*a_barbell_z(k,1) + m_barbell*g;
        m_barbell*g*Lp_hat*absangle_C_cos(k,1) + (I_hat+I_barbell)*absangle_C_diff2(k,1) - m_barbell*a_barbell_x(k,1)*d*absangle_C_sin(k,1) + m_barbell*a_barbell_z(k,1).*d*absangle_C_cos(k,1);
    ];

    x = A\b;
    x_cell{k} = x;
end

% Each cell contains the force and momentum values in the following order:
% x: [F12x;F12z;F23x;F23z;F34x;F34z;Ma;Mk;Mh]
size(x_cell)

%% PLOT RESULTS
% Get momentum vectors (ankle, knee and hip)
m1 = zeros(length(timeIncrements), 1);
m2 = zeros(length(timeIncrements), 1);
m3 = zeros(length(timeIncrements), 1);
for k = 1+offset:iter
    current_cell = x_cell{k};
    current_m1 = current_cell(7,1);
    current_m2 = current_cell(8,1);
    current_m3 = current_cell(9,1);
    m1(k) = current_m1;
    m2(k) = current_m2;
    m3(k) = current_m3;
end

% Plot absolute angles and momentums
figure (1);
subplot(3, 1, 1);
plot(timeIncrements, [rad2deg(absangle_A),rad2deg(absangle_B),rad2deg(absangle_C)], 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('Angle (º)');
title('Absolute angles');
legend('Ankle (Z axis)', 'Knee (Z axis)', 'Hip (Y axis)');

subplot(3, 1, 2);
plot(timeIncrements, [a_leg_z,a_thigh_z,a_hat_z], 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('Acc (m/s2)');
title('Accel Z axis');
legend('Leg', 'Thigh', 'Trunk');

subplot(3, 1, 3);
plot(timeIncrements, [m1,m2,m3], 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('Momentum (Nm)');
title('Momentums');
legend('Ankle', 'Knee', 'Hip');

% Plot only absolute angles
figure (2);
subplot(3, 1, 1);
plot(timeIncrements, [rad2deg(imu_1_eul(:, 1)),rad2deg(imu_2_eul(:, 1)),rad2deg(imu_3_eul(:, 1))], 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('Angle (º)');
title('Absolute angles X axis');
legend('Ankle', 'Knee', 'Hip');

subplot(3, 1, 2);
plot(timeIncrements, [rad2deg(imu_1_eul(:, 2)),rad2deg(imu_2_eul(:, 2)),rad2deg(imu_3_eul(:, 2))], 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('Angle (º)');
title('Absolute angles Y axis');
legend('Ankle', 'Knee', 'Hip');

subplot(3, 1, 3);
plot(timeIncrements, [rad2deg(imu_1_eul(:, 3)),rad2deg(imu_2_eul(:, 3)),rad2deg(imu_3_eul(:, 3))], 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('Angle (º)');
title('Absolute angles Z axis');
legend('Ankle', 'Knee', 'Hip');
