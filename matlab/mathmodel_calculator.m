%% FORCES AND MOMENTUM VALUES CALCULATOR
% Autor: Aaron Raul Poyatos Bakker
% Fecha: 13/06/2023
% With the angle information, obtain all the forces and momentums

%% IMPORT DATA
% Change path to desired csv file
data = readmatrix('../pruebas/EnsayoTODO.csv', 'Delimiter', ',');

% Data
timestamps = data(:, 1);
imu_1_q = data(:, 28:31); % x,y,z,w
imu_1_w = data(:, 32:34); % x,y,z
imu_2_q = data(:, 35:38); % x,y,z,w
imu_2_w = data(:, 39:41); % x,y,z
imu_3_q = data(:, 42:45); % x,y,z,w
imu_3_w = data(:, 46:48); % x,y,z

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
absangle_C = imu_3_eul(:, 2); % Trunk Y angle

%% MODEL PARAMETERS
% General values
g           = 9.81; % m/s2
m_body      = 90;   % Body total weight (kg)
m_barbell   = 100;  % Barbell total weight (kg)
% Limbs lengths and CM offsets (m)
L_leg       = 0.231;
L_thigh     = 0.237;
L_trunk     = 0.303;
Lp_leg      = 0.433*L_leg;
Ld_leg      = 0.567*L_leg;
Lp_thigh    = 0.433*L_thigh;
Ld_thigh    = 0.567*L_thigh;
Lp_trunk    = 0.500*L_trunk;
Ld_trunk    = 0.500*L_trunk;
% Limbs weights and partial weights (kg)
m_leg       = 0.0465*m_body;
m_thigh     = 0.1000*m_body;
m_trunk     = 0.4970*m_body;

% Limb turning radios (for inertia)
r_cg_leg    = 0.302*L_leg;
r_cg_thigh  = 0.323*L_thigh;
r_cg_trunk  = 0.503*L_trunk;

%% OBTAIN MATRIX VALUES
% Inertia values: I = m*R2
I_leg = m_leg*r_cg_leg*r_cg_leg;
I_thigh = m_thigh*r_cg_thigh*r_cg_thigh;
I_trunk = m_trunk*r_cg_trunk*r_cg_trunk;

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
a_trunk_thigh_x = a_thigh_leg_x + absangle_B_diff2.*L_thigh.*(-absangle_B_sin)-L_thigh.*absangle_B_diff.*absangle_B_diff.*absangle_B_cos;
a_trunk_thigh_z = a_thigh_leg_z + absangle_B_diff2.*L_thigh.*(absangle_B_cos)-L_thigh.*absangle_B_diff.*absangle_B_diff.*absangle_B_sin;
a_trunk_x = a_trunk_thigh_x + absangle_C_diff2.*Lp_trunk.*(-absangle_C_sin)-Lp_trunk.*absangle_C_diff.*absangle_C_diff.*absangle_C_cos;
a_trunk_z = a_trunk_thigh_z + absangle_C_diff2.*Lp_trunk.*(absangle_C_cos)-Lp_trunk.*absangle_C_diff.*absangle_C_diff.*absangle_C_sin;
% Barbell COG accelerations
a_barbell_x = a_trunk_thigh_x + absangle_C_diff2.*L_trunk.*(-absangle_C_sin)-L_trunk.*absangle_C_diff.*absangle_C_diff.*absangle_C_cos;
a_barbell_z = a_trunk_thigh_z + absangle_C_diff2.*L_trunk.*(absangle_C_cos)-L_trunk.*absangle_C_diff.*absangle_C_diff.*absangle_C_sin;

%% BUILD A AND B MATRIX
% Ax = b -> x = A(-1)*b

iter = length(timeIncrements);
x_cell = cell(iter, 1);

for k = 1:iter
    A = [
        1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0;
        0, 1, 0, -1, 0, 0, 0, 0, 0, 0, 0;
        Lp_leg*absangle_A_sin(k,1), -Lp_leg*absangle_A_cos(k,1), Ld_leg*absangle_A_sin(k,1), -Ld_leg*absangle_A_cos(k,1), 0, 0, 0, 0, 1, -1, 0;
        0, 0, 1, 0, -1, 0, 0, 0, 0, 0, 0;
        0, 0, 0, 1, 0, -1, 0, 0, 0, 0, 0;
        0, 0, Lp_thigh*absangle_B_sin(k,1), Lp_thigh*absangle_B_cos(k,1), Ld_thigh*absangle_B_sin(k,1), Ld_thigh*absangle_B_cos(k,1), 0, 0, 0, 1, -1;
        0, 0, 0, 0, 1, 0, -1, 0, 0, 0, 0;
        0, 0, 0, 0, 0, 1, 0, -1, 0, 0, 0;
        0, 0, 0, 0, Lp_trunk*absangle_C_sin(k,1), -Lp_trunk*absangle_C_cos(k,1), Ld_trunk*absangle_C_sin(k,1), -Ld_trunk*absangle_C_cos(k,1), 0, 0, 1;
        0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0;
        0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0;
    ];

    b = [
        m_leg*a_leg_x(k,1);
        m_leg*a_leg_z(k,1) + m_leg*g;
        I_leg*absangle_A_diff2(k,1);
        m_thigh*a_thigh_x(k,1);
        m_thigh*a_thigh_z(k,1) + m_thigh*g;
        I_thigh*absangle_B_diff2(k,1);
        m_trunk*a_trunk_x(k,1) + m_barbell*a_barbell_x(k,1);
        m_trunk*a_trunk_z(k,1) + m_trunk*g + m_barbell*a_barbell_z(k,1);
        I_trunk*absangle_C_diff2(k,1) - m_barbell*a_barbell_x(k,1)*Ld_trunk*absangle_C_sin(k,1) + m_barbell*a_barbell_z(k,1).*Ld_trunk*absangle_C_cos(k,1);
        0;
        m_barbell*g;
    ];

    x = inv(A) * b;
    x_cell{k} = x;
end

% Each cell contains the force and momentum values in the following order:
% x: [F12x;F12z;F23x;F23z;F34x;F34z;Fx;Fz;Ma;Mk;Mh]
size(x_cell)

%% PLOT RESULTS
% Get momentum vectors (ankle, knee and hip)
m1 = zeros(7636, 1);
m2 = zeros(7636, 1);
m3 = zeros(7636, 1);
for k = 1:iter
    current_cell = x_cell{k};
    current_m1 = current_cell(9,1);
    current_m2 = current_cell(10,1);
    current_m3 = current_cell(11,1);
    m1(k) = current_m1;
    m2(k) = current_m2;
    m3(k) = current_m3;
end

% Plot absolute angles and momentums
figure;
subplot(2, 1, 1);
plot(timeIncrements, [rad2deg(absangle_A),rad2deg(absangle_B),rad2deg(absangle_C)], 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('Angle (º)');
title('Absolute angles');
legend('Absolute angle A Z', 'Absolute angle B Z', 'Absolute angle C Y');

subplot(2, 1, 2);
plot(timeIncrements, [m1,m2,m3], 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('Momentum (Nm)');
title('Momentums');
legend('Ankle', 'Knee', 'Hip');

