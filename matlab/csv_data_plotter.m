%% CSV DATA PLOTTER FOR CALIBRATED VALUES
% Author: Aaron Raul Poyatos Bakker
% Date: 13/06/2023
% Script that generates 5 figures with the recorded data in CSV files:
% - 3 subfigures for loadcells of platform 1
% - 3 subfigures for loadcells of platform 2
% - figure with encoders info
% - 3 subfigures for IMUs orientation data
% - 3 subfigures for IMUs angular velocity data

%% IMPORT DATA
% Change path to desired csv file
data = readmatrix('../pruebas/EnsayoTODO.csv', 'Delimiter', ',');

% Data
timestamps = data(:, 1);
loadCell_Z1 = data(:, 2:5);
loadCell_X1 = data(:, 6:9);
loadCell_Y1 = data(:, 10:13);
loadCell_Z2 = data(:, 14:17);
loadCell_X2 = data(:, 18:21);
loadCell_Y2 = data(:, 22:25);
encoders = data(:, 26:27);
imu_1_q = data(:, 28:31); % x,y,z,w
imu_1_w = data(:, 32:34); % x,y,z
imu_2_q = data(:, 35:38); % x,y,z,w
imu_2_w = data(:, 39:41); % x,y,z
imu_3_q = data(:, 42:45); % x,y,z,w
imu_3_w = data(:, 46:48); % x,y,z

% Transform timestamp to seconds
timeIncrements = timestamps/1000 - timestamps(1)/1000;

%% LOADCELLS PLATFORM 1
figure (1);

% P1_LoadCell_Z
subplot(3, 1, 1);
plot(timeIncrements, loadCell_Z1, 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('Force (N)');
title('P1\_LoadCell\_Z');
legend('P1\_LoadCell\_Z\_1', 'P1\_LoadCell\_Z\_2', 'P1\_LoadCell\_Z\_3', 'P1\_LoadCell\_Z\_4');

% P1_LoadCell_X
subplot(3, 1, 2);
plot(timeIncrements, loadCell_X1, 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('Force (N)');
title('P1\_LoadCell\_X');
legend('P1\_LoadCell\_X\_1', 'P1\_LoadCell\_X\_2', 'P1\_LoadCell\_X\_3', 'P1\_LoadCell\_X\_4');

% P1_LoadCell_Y
subplot(3, 1, 3);
plot(timeIncrements, loadCell_Y1, 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('Force (N)');
title('P1\_LoadCell\_Y');
legend('P1\_LoadCell\_Y\_1', 'P1\_LoadCell\_Y\_2', 'P1\_LoadCell\_Y\_3', 'P1\_LoadCell\_Y\_4');

%% LOADCELLS PLATFORM 2
figure (2);

% P2_LoadCell_Z
subplot(3, 1, 1);
plot(timeIncrements, loadCell_Z2, 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('Force (N)');
title('P2\_LoadCell\_Z');
legend('P2\_LoadCell\_Z\_1', 'P2\_LoadCell\_Z\_2', 'P2\_LoadCell\_Z\_3', 'P2\_LoadCell\_Z\_4');

% P2_LoadCell_X
subplot(3, 1, 2);
plot(timeIncrements, loadCell_X2, 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('Force (N)');
title('P2\_LoadCell\_X');
legend('P2\_LoadCell\_X\_1', 'P2\_LoadCell\_X\_2', 'P2\_LoadCell\_X\_3', 'P2\_LoadCell\_X\_4');

% P2_LoadCell_Y
subplot(3, 1, 3);
plot(timeIncrements, loadCell_Y2, 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('Force (N)');
title('P2\_LoadCell\_Y');
legend('P2\_LoadCell\_Y\_1', 'P2\_LoadCell\_Y\_2', 'P2\_LoadCell\_Y\_3', 'P2\_LoadCell\_Y\_4');

%% ENCODERS
figure (3);

plot(timeIncrements, encoders, 'LineWidth', 1.5);
grid on;
xlabel('Time (s)');
ylabel('Distance (mm)');
title('Encoders');
legend('Encoder\_Z1', 'Encoder\_Z2');

%% IMUS ANGLES
% Transform quaternions values to Euler angles
imu_1_eul = quat2eul(imu_1_q, 'XYZ');
imu_2_eul = quat2eul(imu_2_q, 'XYZ');
imu_3_eul = quat2eul(imu_3_q, 'XYZ');
% To degrees
imu_1_eul_deg = rad2deg(imu_1_eul);
imu_2_eul_deg = rad2deg(imu_2_eul);
imu_3_eul_deg = rad2deg(imu_3_eul);

figure (4);

% IMU 1
subplot(3, 1, 1);
plot(timeIncrements, imu_1_eul_deg, 'LineWidth', 1.5);
xlabel('Time (s)');
ylabel('Angle (º)');
title('IMU\_1');
legend('IMU\_X', 'IMU\_Y', 'IMU\_Z');

% IMU 2
subplot(3, 1, 2);
plot(timeIncrements, imu_2_eul_deg, 'LineWidth', 1.5);
xlabel('Time (s)');
ylabel('Angle (º)');
title('IMU\_2');
legend('IMU\_X', 'IMU\_Y', 'IMU\_Z');

% IMU 3
subplot(3, 1, 3);
plot(timeIncrements, imu_3_eul_deg, 'LineWidth', 1.5);
xlabel('Time (s)');
ylabel('Angle (º)');
title('IMU\_3');
legend('IMU\_X', 'IMU\_Y', 'IMU\_Z');

%% IMUS ANGULAR VELOCITY
figure (5);

% IMU 1
subplot(3, 1, 1);
plot(timeIncrements, imu_1_w, 'LineWidth', 1.5);
xlabel('Time (s)');
ylabel('Angular velocity (rad/s)');
title('IMU\_1');
legend('IMU\_X', 'IMU\_Y', 'IMU\_Z');

% IMU 2
subplot(3, 1, 2);
plot(timeIncrements, imu_2_w, 'LineWidth', 1.5);
xlabel('Time (s)');
ylabel('Angular velocity (rad/s)');
title('IMU\_2');
legend('IMU\_X', 'IMU\_Y', 'IMU\_Z');

% IMU 3
subplot(3, 1, 3);
plot(timeIncrements, imu_3_w, 'LineWidth', 1.5);
xlabel('Time (s)');
ylabel('Angular velocity (rad/s)');
title('IMU\_3');
legend('IMU\_X', 'IMU\_Y', 'IMU\_Z');