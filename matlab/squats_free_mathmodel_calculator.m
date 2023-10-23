%% FORCES AND MOMENTUM VALUES CALCULATOR
% Author: Aaron Raul Poyatos Bakker
% Date: 09/08/2023
% With the angle information, obtain all unknown forces and torques for
% the squats free model.
clearvars;
close all;
clc;

%% IMPORT DATA
% Change path to desired csv file
data = readtable('../ensayos/ensayos_2023_06_30/EnsayoLento.csv', 'Delimiter', ',');

idx1 = 1059;
idx2 = 2234;

% Data
timestamps = data.timestamp;
imu_1_q = [data.IMU_Leg_Right_qw, data.IMU_Leg_Right_qx, data.IMU_Leg_Right_qy, data.IMU_Leg_Right_qz];
imu_1_w = [data.IMU_Leg_Right_wx, data.IMU_Leg_Right_wy, data.IMU_Leg_Right_wz];
imu_2_q = [data.IMU_Thigh_Right_qw, data.IMU_Thigh_Right_qx, data.IMU_Thigh_Right_qy, data.IMU_Thigh_Right_qz];
imu_2_w = [data.IMU_Thigh_Right_wx, data.IMU_Thigh_Right_wy, data.IMU_Thigh_Right_wz];
imu_3_q = [data.IMU_UpperTrunk_Right_qw, data.IMU_UpperTrunk_Right_qx, data.IMU_UpperTrunk_Right_qy, data.IMU_UpperTrunk_Right_qz];
imu_3_w = [data.IMU_UpperTrunk_Right_wx, data.IMU_UpperTrunk_Right_wy, data.IMU_UpperTrunk_Right_wz];

% Cut data
timestamps = timestamps(idx1:idx2);
imu_1_q = imu_1_q(idx1:idx2,:);
imu_1_w = imu_1_w(idx1:idx2,:);
imu_2_q = imu_2_q(idx1:idx2,:);
imu_2_w = imu_2_w(idx1:idx2,:);
imu_3_q = imu_3_q(idx1:idx2,:);
imu_3_w = imu_3_w(idx1:idx2,:);

% Transform timestamp to seconds
timeIncrements = timestamps/1000 - timestamps(1)/1000;

% Transform quaternions values to Euler angles
imu_1_eul = quat2eul(imu_1_q, 'XYZ');
imu_2_eul = quat2eul(imu_2_q, 'XYZ');
imu_3_eul = quat2eul(imu_3_q, 'XYZ');

% Extract absolute angles
% TODO CHECK REAL DATA VALUES TO TRANSFORM IN ABS ANGLES
absangle_A = pi - imu_1_eul(:, 3) ; % Leg Z angle
absangle_B = pi - imu_2_eul(:, 3); % Thigh Z angle
absangle_C = imu_3_eul(:, 2) + deg2rad(20); % Trunk Y angle

%% EXAMPLES WITH VIRTUAL ANGLES
% % Comment/delete this section if you want to use imported data from csv
% timeIncrements = 0:0.01:4;
% pos_i = pi/2;
% pos_f_A = pi/4;
% pos_f_B = pi/1.2;
% pos_f_C = pi/5;
% reps = 2;
% absangle_A = test_angle_trajectories_linear(timeIncrements,reps,pos_i,pos_f_A);
% absangle_B = test_angle_trajectories_parabolic(timeIncrements,reps,pos_i,pos_f_B);
% absangle_C = test_angle_trajectories_linear(timeIncrements,reps,pos_i,pos_f_C);

%% MODEL PARAMETERS
% General values
g           = 9.81; % m/s2
m_body      = 70*0.911266;   % Body total weight (kg)
h_body      = 1.73;  % Body total height (cm)
m_barbell   = 40;  % Barbell total weight (kg)
% Limbs lengths and CM offsets (m)
L_leg       = 0.231*h_body;
L_thigh     = 0.237*h_body;
L_hat       = (0.303+1-0.814)*h_body;
L_uppertrunk= 0.303*h_body;
Lp_leg      = 0.433*L_leg;
Ld_leg      = 0.567*L_leg;
Lp_thigh    = 0.433*L_thigh;
Ld_thigh    = 0.567*L_thigh;
Lp_hat      = 0.626*L_hat;
Ld_hat      = 0.374*L_hat;
% Lp_hat      = 0.374*L_hat;
% Ld_hat      = 0.626*L_hat;
d = abs(L_uppertrunk-Ld_hat);
% Limbs partial weights (kg)
m_leg       = 2*0.0465*m_body;
m_thigh     = 2*0.1000*m_body;
m_hat       = 0.6780*m_body; % 0.6780
m_foot      = m_body - m_leg - m_thigh - m_hat;

% Limb turning radios (for inertia)
r_cg_leg    = 0.302*L_leg;
r_cg_thigh  = 0.323*L_thigh;
r_cg_hat  = 0.503*L_hat;
r_cg_barbell = 35/2000;

%% OBTAIN MATRIX VALUES
% Inertia values: I = m*R2
I_leg = m_leg*r_cg_leg*r_cg_leg;
I_thigh = m_thigh*r_cg_thigh*r_cg_thigh;
I_hat = m_hat*r_cg_hat*r_cg_hat;
I_barbell = 0.5*12*r_cg_barbell*r_cg_barbell;

% --- Absolute angles management

% % Get first and second absolute angle derivatives (applying butterworth)
FS = 100;
FC = 5;

[b,a] = butter(6,FC/(FS/2));

absangle_A_diff = filtfilt(b,a,-imu_1_w(:,3));
absangle_B_diff = filtfilt(b,a,-imu_2_w(:,3));
absangle_C_diff = filtfilt(b,a,-imu_3_w(:,2));
absangle_A_diff2 = [(-absangle_A_diff(3)+4*absangle_A_diff(2)-3*absangle_A_diff(1))*FS/2;diff(absangle_A_diff)*FS];
absangle_B_diff2 = [(-absangle_B_diff(3)+4*absangle_B_diff(2)-3*absangle_B_diff(1))*FS/2;diff(absangle_B_diff)*FS];
absangle_C_diff2 = [(-absangle_C_diff(3)+4*absangle_C_diff(2)-3*absangle_C_diff(1))*FS/2;diff(absangle_C_diff)*FS];

N = length(timeIncrements);

wzle = absangle_A_diff-mean(absangle_A_diff);
wzth = absangle_B_diff-mean(absangle_B_diff);
wytr = absangle_C_diff-mean(absangle_C_diff);
for i = 2:N
        absangle_A(i) = absangle_A(i-1) + (1/2)*(timeIncrements(i)-timeIncrements(i-1))*(wzle(i)+wzle(i-1));
        absangle_B(i) = absangle_B(i-1) + (1/2)*(timeIncrements(i)-timeIncrements(i-1))*(wzth(i)+wzth(i-1));
        absangle_C(i) = absangle_C(i-1) + (1/2)*(timeIncrements(i)-timeIncrements(i-1))*(wytr(i)+wytr(i-1));
end

% Sines and cosines of absolute angles
absangle_A_sin = sin(absangle_A);
absangle_A_cos = cos(absangle_A);
absangle_B_sin = sin(absangle_B);
absangle_B_cos = cos(absangle_B);
absangle_B_sin_M = sin(pi - absangle_B); % For torque values
absangle_B_cos_M = cos(pi - absangle_B); % For torque values
absangle_C_sin = sin(absangle_C);
absangle_C_cos = cos(absangle_C);

% --- Limb accelerations
% Leg COG accelerations
a_leg_x = absangle_A_diff2.*Ld_leg.*(-absangle_A_sin)-Ld_leg.*absangle_A_diff.*absangle_A_diff.*absangle_A_cos;
a_leg_z = absangle_A_diff2.*Ld_leg.*(absangle_A_cos)-Ld_leg.*absangle_A_diff.*absangle_A_diff.*absangle_A_sin;
% Thigh COG accelerations
a_knee_x = absangle_A_diff2.*L_leg.*(-absangle_A_sin)-L_leg.*absangle_A_diff.*absangle_A_diff.*absangle_A_cos;
a_knee_z = absangle_A_diff2.*L_leg.*(absangle_A_cos)-L_leg.*absangle_A_diff.*absangle_A_diff.*absangle_A_sin;
a_thigh_x = a_knee_x + absangle_B_diff2.*Ld_thigh.*(-absangle_B_sin)-Ld_thigh.*absangle_B_diff.*absangle_B_diff.*absangle_B_cos;
a_thigh_z = a_knee_z + absangle_B_diff2.*Ld_thigh.*(absangle_B_cos)-Ld_thigh.*absangle_B_diff.*absangle_B_diff.*absangle_B_sin;
% Trunk COG accelerations
a_hip_x = a_knee_x + absangle_B_diff2.*L_thigh.*(-absangle_B_sin)-L_thigh.*absangle_B_diff.*absangle_B_diff.*absangle_B_cos;
a_hip_z = a_knee_z + absangle_B_diff2.*L_thigh.*(absangle_B_cos)-L_thigh.*absangle_B_diff.*absangle_B_diff.*absangle_B_sin;
a_hat_x = a_hip_x + absangle_C_diff2.*Ld_hat.*(-absangle_C_sin)-Ld_hat.*absangle_C_diff.*absangle_C_diff.*absangle_C_cos;
a_hat_z = a_hip_z + absangle_C_diff2.*Ld_hat.*(absangle_C_cos)-Ld_hat.*absangle_C_diff.*absangle_C_diff.*absangle_C_sin;
% Barbell COG accelerations
a_barbell_x = a_hip_x + absangle_C_diff2.*L_uppertrunk.*(-absangle_C_sin)-L_uppertrunk.*absangle_C_diff.*absangle_C_diff.*absangle_C_cos;
a_barbell_z = a_hip_z + absangle_C_diff2.*L_uppertrunk.*(absangle_C_cos)-L_uppertrunk.*absangle_C_diff.*absangle_C_diff.*absangle_C_sin;

% To ignore dynamics
% a_leg_x = zeros(length(timeIncrements),1);
% a_leg_z = zeros(length(timeIncrements),1);
% a_thigh_x = zeros(length(timeIncrements),1);
% a_thigh_z = zeros(length(timeIncrements),1);
% a_hat_x = zeros(length(timeIncrements),1);
% a_hat_z = zeros(length(timeIncrements),1);
% a_barbell_x = zeros(length(timeIncrements),1);
% a_barbell_z = zeros(length(timeIncrements),1);
% I_leg = 0;
% I_thigh = 0;
% I_hat = 0;

%% BUILD A AND B MATRIX
% Ax = b -> x = A(-1)*b

iter = length(timeIncrements);
x_cell = cell(iter, 1);

for k = 1:iter
    A = [
        1, 0, -1, 0, 0, 0, 0, 0, 0;
        0, 1, 0, -1, 0, 0, 0, 0, 0;
        Ld_leg*absangle_A_sin(k,1), -Ld_leg*absangle_A_cos(k,1), Lp_leg*absangle_A_sin(k,1), -Lp_leg*absangle_A_cos(k,1), 0, 0, 1, -1, 0;
        0, 0, 1, 0, -1, 0, 0, 0, 0;
        0, 0, 0, 1, 0, -1, 0, 0, 0;
        0, 0, Ld_thigh*absangle_B_sin_M(k,1), Ld_thigh*absangle_B_cos_M(k,1), Lp_thigh*absangle_B_sin_M(k,1), Lp_thigh*absangle_B_cos_M(k,1), 0, 1, -1;
        0, 0, 0, 0, 1, 0, 0, 0, 0;
        0, 0, 0, 0, 0, 1, 0, 0, 0;
        0, 0, 0, 0, Ld_hat*absangle_C_sin(k,1), -Ld_hat*absangle_C_cos(k,1), 0, 0, 1;
    ];

    b = [
        m_leg*a_leg_x(k,1);
        m_leg*a_leg_z(k,1) + m_leg*g + m_foot*g;
        I_leg*absangle_A_diff2(k,1) + m_foot*g*Ld_leg*absangle_A_cos(k,1);
        m_thigh*a_thigh_x(k,1);
        m_thigh*a_thigh_z(k,1) + m_thigh*g;
        I_thigh*absangle_B_diff2(k,1);
        m_hat*a_hat_x(k,1) + m_barbell*a_barbell_x(k,1);
        m_hat*a_hat_z(k,1) + m_hat*g + m_barbell*a_barbell_z(k,1) + m_barbell*g;
        m_barbell*g*d*absangle_C_cos(k,1) + (I_hat+I_barbell)*absangle_C_diff2(k,1) - m_barbell*a_barbell_x(k,1)*d*absangle_C_sin(k,1) + m_barbell*a_barbell_z(k,1).*d*absangle_C_cos(k,1);
    ];

    x = A\b;
    x_cell{k} = x;
end

% Each cell contains the force and momentum values in the following order:
% x: [F12x;F12z;F23x;F23z;F34x;F34z;Ma;Mk;Mh]
size(x_cell)

%% PLOT RESULTS
% Get torque vectors (ankle, knee and hip)
m1 = zeros(length(timeIncrements), 1);
m2 = zeros(length(timeIncrements), 1);
m3 = zeros(length(timeIncrements), 1);
for k = 1:iter
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
% plot(timeIncrements, [rad2deg(absangle_A),rad2deg(absangle_B),rad2deg(absangle_C)], 'LineWidth', 1.5);
hold on;
plot(timeIncrements, rad2deg(absangle_A), 'r-', 'LineWidth', 1.5);
plot(timeIncrements, rad2deg(absangle_B), 'b-', 'LineWidth', 1.5);
plot(timeIncrements, rad2deg(absangle_C), 'k-', 'LineWidth', 1.5);
hold off;
grid on;
xlabel('Time (s)');
ylabel('Angle (º)');
title('Absolute angles');
legend('Ankle (Z axis)', 'Knee (Z axis)', 'Hip (Y axis)');

subplot(3, 1, 2);
% plot(timeIncrements, [a_leg_z,a_thigh_z,a_hat_z], 'LineWidth', 1.5);
hold on;
plot(timeIncrements, a_leg_z, 'r-', 'LineWidth', 1.5);
plot(timeIncrements, a_thigh_z, 'b-', 'LineWidth', 1.5);
plot(timeIncrements, a_hat_z, 'k-', 'LineWidth', 1.5);
hold off;
grid on;
xlabel('Time (s)');
ylabel('Acc (m/s2)');
ylim([-5,5]);
title('Accel Z axis');
legend('Leg', 'Thigh', 'HAT');

subplot(3, 1, 3);
% plot(timeIncrements, [m1,m2,m3], 'LineWidth', 1.5);
hold on;
plot(timeIncrements, m1, 'r-', 'LineWidth', 1.5);
plot(timeIncrements, m2, 'b-', 'LineWidth', 1.5);
plot(timeIncrements, m3, 'k-', 'LineWidth', 1.5);
hold off;
grid on;
xlabel('Time (s)');
ylabel('Torque (Nm)');
title('Torques');
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

% Plot derivatives
subplot(3, 1, 1);
plot(timeIncrements, [absangle_A,absangle_B,absangle_C], 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('Angle (rad)');
title('Absolute angles');
legend('Ankle', 'Knee', 'Hip');

subplot(3, 1, 2);
plot(timeIncrements, [absangle_A_diff,absangle_B_diff,absangle_C_diff], 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('Angle (rad/s)');
ylim([-5,5]);
title('Absolute angles velocity');
legend('Ankle', 'Knee', 'Hip');

subplot(3, 1, 3);
plot(timeIncrements, [absangle_A_diff2,absangle_B_diff2,absangle_C_diff2], 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('Angle (rad/s2)');
ylim([-30,40]);
title('Absolute angles acceleration');
legend('Ankle', 'Knee', 'Hip');

%% Compare ground forces with platform readings
% Get ground f12x and f12z vectors
f12x = zeros(length(timeIncrements), 1);
f12z = zeros(length(timeIncrements), 1);
for k = 1:iter
    current_cell = x_cell{k};
    current_f12x = current_cell(1,1);
    current_f12z = current_cell(2,1);
    f12x(k) = current_f12x;
    f12z(k) = current_f12z;
end
% Get forces from platfom
p_f12x = - data.P1_LoadCell_X_1 + data.P1_LoadCell_X_2 + data.P1_LoadCell_X_3 - data.P1_LoadCell_X_4 + ...
    - data.P2_LoadCell_X_1 + data.P2_LoadCell_X_2 + data.P2_LoadCell_X_3 - data.P2_LoadCell_X_4;
p_f12z = data.P1_LoadCell_Z_1 + data.P1_LoadCell_Z_2 + data.P1_LoadCell_Z_3 + data.P1_LoadCell_Z_4 +...
    data.P2_LoadCell_Z_1 + data.P2_LoadCell_Z_2 + data.P2_LoadCell_Z_3 + data.P2_LoadCell_Z_4;
p_f12x = p_f12x(idx1:idx2) * g;
p_f12z = p_f12z(idx1:idx2) * g;
% Plot
figure(4);
% plot(timeIncrements, [f12x,f12z,p_f12x,p_f12z], 'LineWidth', 1.5);
hold on;
plot(timeIncrements, f12x, 'r--', 'LineWidth', 1.5);
plot(timeIncrements, f12z, 'r-', 'LineWidth', 1.5);
plot(timeIncrements, p_f12x, 'b--', 'LineWidth', 1.5);
plot(timeIncrements, p_f12z, 'b-', 'LineWidth', 1.5);
hold off;
grid on;
xlabel('Time (s)');
ylabel('Force (N)');
ylim([-500,2000]);
title('Comparison between platform and model total forces');
legend('Math model horizontal force', 'Math model vertical force', 'Platform horizontal force', 'Platform vertical force');

disp('Mass ratio diff')
mean(p_f12z)/mean(f12z)

%% Plot checks
% Angles, Forces, COG Accelerations
figure (5);
subplot(3, 1, 1);
% plot(timeIncrements, [rad2deg(absangle_A),rad2deg(absangle_B),rad2deg(absangle_C)], 'LineWidth', 1.5);
hold on;
plot(timeIncrements, rad2deg(absangle_A), 'r-', 'LineWidth', 1.5);
plot(timeIncrements, rad2deg(absangle_B), 'b-', 'LineWidth', 1.5);
plot(timeIncrements, rad2deg(absangle_C), 'k-', 'LineWidth', 1.5);
hold off;
grid on;
xlabel('Time (s)');
ylabel('Angle (º)');
title('Absolute angles');
legend('Ankle (Z axis)', 'Knee (Z axis)', 'Hip (Y axis)');

subplot(3, 1, 2);
hold on;
plot(timeIncrements, f12z, 'r-', 'LineWidth', 1.5);
plot(timeIncrements, p_f12z, 'b-', 'LineWidth', 1.5);
hold off;
grid on;
xlabel('Time (s)');
ylabel('Force (N)');
ylim([-500,1700]);
title('Comparison between platform and model total forces');
legend('Model vertical force', 'Platform vertical force');

subplot(3, 1, 3);
% plot(timeIncrements, [a_leg_z,a_thigh_z,a_hat_z], 'LineWidth', 1.5);
hold on;
plot(timeIncrements, a_leg_z, 'r-', 'LineWidth', 1.5);
plot(timeIncrements, a_thigh_z, 'b-', 'LineWidth', 1.5);
plot(timeIncrements, a_hat_z, 'k-', 'LineWidth', 1.5);
hold off;
grid on;
xlabel('Time (s)');
ylabel('Acc (m/s2)');
ylim([-5,5]);
title('Accel Z axis');
legend('Leg', 'Thigh', 'HAT');

% Thigh angle and forces
figure (6);
f12z = f12z(725:size(timeIncrements));
p_f12z = p_f12z(725:size(timeIncrements));
hold on;
plot(timeIncrements(725:end), f12z - mean(f12z), 'r-', 'LineWidth', 1.5);
plot(timeIncrements(725:end), p_f12z - mean(p_f12z), 'b-', 'LineWidth', 1.5);
hold off;
grid on;
xlabel('Time (s)');
ylabel('Force (N)');
% ylim([500,1700]);
% yyaxis right
% plot(timeIncrements, rad2deg(absangle_B), 'k-', 'LineWidth', 1.5);
% ylabel('Angle (º)');
% legend('Model vertical force', 'Platform vertical force','Knee absolute angle');
% title('Comparison between platform and model total forces');

% Frequency
figure (7);
signal = f12z - mean(f12z);
time = timeIncrements(725:end);
L = length(signal);
Y = fft(signal);
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
f = FS*(0:(L/2))/L;
plot(f,P1)
% amplitude = abs(Y);
% freqs = (-FS/2):(FS/L):(FS/2-FS/L);
% plot(freqs,fftshift(amplitude));
grid on;
xlabel('f (Hz)');
ylabel('|P1(f)|');
title('Single-Sided Amplitude Spectrum of Model Force signal');
% xlim([0,15]);


%% Pose animation
% Determine poses
pos_A_x = zeros(size(timeIncrements));
pos_A_z = zeros(size(timeIncrements));
pos_B_x = pos_A_x + L_leg .* absangle_A_cos;
pos_B_z = pos_A_z + L_leg .* absangle_A_sin;
pos_C_x = pos_B_x + L_thigh .* absangle_B_cos;
pos_C_z = pos_B_z + L_thigh .* absangle_B_sin;
pos_D_x = pos_C_x + L_uppertrunk .* absangle_C_cos;
pos_D_z = pos_C_z + L_uppertrunk .* absangle_C_sin;
pos_E_x = pos_C_x + L_hat .* absangle_C_cos;
pos_E_z = pos_C_z + L_hat .* absangle_C_sin;

% Plot D position
figure (8);
plot(timeIncrements,(data.Encoder_Z_1(idx1:idx2) + data.Encoder_Z_2(idx1:idx2))/2, 'r-', 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('L (mm)');
yyaxis right
plot(timeIncrements, pos_D_z*1000, 'b-', 'LineWidth', 1.5);
ylabel('L (mm)');
ylim([800, 1400]);
yticks(800:100:1400);
set(gca, 'YDir', 'reverse');
legend('Encoder','Model');
% title('Single-Sided Amplitude Spectrum of Model Force signal');

return;

fig = figure(10);
axis([-1 1 0 2]);
xlabel('X (m)');
ylabel('Z (m)');
title('Animacion del cuerpo');

% Body
joint(1) = line(pos_A_x(1),pos_A_z(1),'Marker','o','Color','r','MarkerSize', 10);
joint(2) = line([pos_A_x(1), pos_B_x(1)],[pos_A_z(1), pos_B_z(1)], 'Color', 'b', 'LineWidth', 2);
joint(3) = line([pos_B_x(1), pos_C_x(1)],[pos_B_z(1), pos_C_z(1)], 'Color', 'b', 'LineWidth', 2);
joint(4) = line([pos_C_x(1), pos_E_x(1)],[pos_C_z(1), pos_E_z(1)], 'Color', 'b', 'LineWidth', 2);
joint(5) = line(pos_D_x(1),pos_D_z(1),'Marker','o','Color','r','MarkerSize', 5, 'LineWidth', 3);
joint(6) = line(pos_E_x(1),pos_E_z(1),'Marker','o','Color','b','MarkerSize', 20);

for frame = 2:size(timeIncrements)
    cla;
    joint(1) = line(pos_A_x(frame),pos_A_z(frame),'Marker','o','Color','k','MarkerSize', 10);
    joint(2) = line([pos_A_x(frame), pos_B_x(frame)],[pos_A_z(frame), pos_B_z(frame)], 'Color', 'b', 'LineWidth', 2);
    joint(3) = line([pos_B_x(frame), pos_C_x(frame)],[pos_B_z(frame), pos_C_z(frame)], 'Color', 'b', 'LineWidth', 2);
    joint(4) = line([pos_C_x(frame), pos_E_x(frame)],[pos_C_z(frame), pos_E_z(frame)], 'Color', 'b', 'LineWidth', 2);
    joint(5) = line(pos_D_x(frame),pos_D_z(frame),'Marker','o','Color','r','MarkerSize', 5, 'LineWidth', 3);
    joint(6) = line(pos_E_x(frame),pos_E_z(frame),'Marker','o','Color','b','MarkerSize', 20);
    pause(0.01);
end
