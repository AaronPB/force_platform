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
data = readtable('../ensayos_2023_06_30/EnsayoRapida.csv', 'Delimiter', ',');

% Transform timestamp to seconds
timestamps = data.timestamp;
timeIncrements = timestamps/1000 - timestamps(1)/1000;

%% LOADCELLS PLATFORM 1
figure (1);

% P1_LoadCell_Z
if ismember('P1_LoadCell_Z_1', data.Properties.VariableNames) && ...
   ismember('P1_LoadCell_Z_2', data.Properties.VariableNames) && ...
   ismember('P1_LoadCell_Z_3', data.Properties.VariableNames) && ...
   ismember('P1_LoadCell_Z_4', data.Properties.VariableNames)

    loadCell_Z1 = [data.P1_LoadCell_Z_1, data.P1_LoadCell_Z_2, data.P1_LoadCell_Z_3, data.P1_LoadCell_Z_4];
    resultant_Z1 = data.P1_LoadCell_Z_1 + data.P1_LoadCell_Z_2 + data.P1_LoadCell_Z_3 + data.P1_LoadCell_Z_4;

    subplot(3, 1, 1);
    hold on;
    plot(timeIncrements, loadCell_Z1(:, 1), 'r-', 'LineWidth', 1.5);
    plot(timeIncrements, loadCell_Z1(:, 2), 'r--', 'LineWidth', 1.5);
    plot(timeIncrements, loadCell_Z1(:, 3), 'b-', 'LineWidth', 1.5);
    plot(timeIncrements, loadCell_Z1(:, 4), 'b--', 'LineWidth', 1.5);
    plot(timeIncrements, resultant_Z1, 'k-', 'LineWidth', 2.5);
    hold off;
    grid on;
    xlabel('Time (s)');
    ylabel('Weight (kg)');
    title('P1\_LoadCell\_Z');
    legend('P1\_LoadCell\_Z\_1', 'P1\_LoadCell\_Z\_2', 'P1\_LoadCell\_Z\_3', 'P1\_LoadCell\_Z\_4', 'RESULTANTE');
else
    disp('Los datos de Plataforma 1 - Eje Z no se encuentran disponibles. Ignorando figura.');
end

% P1_LoadCell_X
if ismember('P1_LoadCell_X_1', data.Properties.VariableNames) && ...
   ismember('P1_LoadCell_X_2', data.Properties.VariableNames) && ...
   ismember('P1_LoadCell_X_3', data.Properties.VariableNames) && ...
   ismember('P1_LoadCell_X_4', data.Properties.VariableNames)

    loadCell_X1 = [-data.P1_LoadCell_X_1, data.P1_LoadCell_X_2, data.P1_LoadCell_X_3, - data.P1_LoadCell_X_4];
    resultant_X1 = -data.P1_LoadCell_X_1 + data.P1_LoadCell_X_2 + data.P1_LoadCell_X_3 - data.P1_LoadCell_X_4;

    subplot(3, 1, 2);
    hold on;
    plot(timeIncrements, loadCell_X1(:, 1), 'r-', 'LineWidth', 1.5);
    plot(timeIncrements, loadCell_X1(:, 2), 'r--', 'LineWidth', 1.5);
    plot(timeIncrements, loadCell_X1(:, 3), 'b-', 'LineWidth', 1.5);
    plot(timeIncrements, loadCell_X1(:, 4), 'b--', 'LineWidth', 1.5);
    plot(timeIncrements, resultant_X1, 'k-', 'LineWidth', 2.5);
    hold off;
    grid on;
    xlabel('Time (s)');
    ylabel('Weight (kg)');
    title('P1\_LoadCell\_X');
    legend('P1\_LoadCell\_X\_1', 'P1\_LoadCell\_X\_2', 'P1\_LoadCell\_X\_3', 'P1\_LoadCell\_X\_4', 'RESULTANTE');
    
else
    disp('Los datos de Plataforma 1 - Eje X no se encuentran disponibles. Ignorando figura.');
end

% P1_LoadCell_Y
if ismember('P1_LoadCell_Y_1', data.Properties.VariableNames) && ...
   ismember('P1_LoadCell_Y_2', data.Properties.VariableNames) && ...
   ismember('P1_LoadCell_Y_3', data.Properties.VariableNames) && ...
   ismember('P1_LoadCell_Y_4', data.Properties.VariableNames)

    loadCell_Y1 = [-data.P1_LoadCell_Y_1, - data.P1_LoadCell_Y_2, data.P1_LoadCell_Y_3, data.P1_LoadCell_Y_4];
    resultant_Y1 = -data.P1_LoadCell_Y_1 - data.P1_LoadCell_Y_2 + data.P1_LoadCell_Y_3 + data.P1_LoadCell_Y_4;
    
    subplot(3, 1, 3);
    hold on;
    plot(timeIncrements, loadCell_Y1(:, 1), 'r-', 'LineWidth', 1.5);
    plot(timeIncrements, loadCell_Y1(:, 2), 'r--', 'LineWidth', 1.5);
    plot(timeIncrements, loadCell_Y1(:, 3), 'b-', 'LineWidth', 1.5);
    plot(timeIncrements, loadCell_Y1(:, 4), 'b--', 'LineWidth', 1.5);
    plot(timeIncrements, resultant_Y1, 'k-', 'LineWidth', 2.5);
    hold off;
    grid on;
    xlabel('Time (s)');
    ylabel('Weight (kg)');
    title('P1\_LoadCell\_Y');
    legend('P1\_LoadCell\_Y\_1', 'P1\_LoadCell\_Y\_2', 'P1\_LoadCell\_Y\_3', 'P1\_LoadCell\_Y\_4', 'RESULTANTE');
else
    disp('Los datos de Plataforma 1 - Eje Y no se encuentran disponibles. Ignorando figura.');
end

%% LOADCELLS PLATFORM 2
figure (2);

% P2_LoadCell_Z
if ismember('P2_LoadCell_Z_1', data.Properties.VariableNames) && ...
   ismember('P2_LoadCell_Z_2', data.Properties.VariableNames) && ...
   ismember('P2_LoadCell_Z_3', data.Properties.VariableNames) && ...
   ismember('P2_LoadCell_Z_4', data.Properties.VariableNames)

    loadCell_Z2 = [data.P2_LoadCell_Z_1, data.P2_LoadCell_Z_2, data.P2_LoadCell_Z_3, data.P2_LoadCell_Z_4];
    resultant_Z2 = data.P2_LoadCell_Z_1 + data.P2_LoadCell_Z_2 + data.P2_LoadCell_Z_3 + data.P2_LoadCell_Z_4;

    subplot(3, 1, 1);
    hold on;
    plot(timeIncrements, loadCell_Z2(:, 1), 'r-', 'LineWidth', 1.5);
    plot(timeIncrements, loadCell_Z2(:, 2), 'r--', 'LineWidth', 1.5);
    plot(timeIncrements, loadCell_Z2(:, 3), 'b-', 'LineWidth', 1.5);
    plot(timeIncrements, loadCell_Z2(:, 4), 'b--', 'LineWidth', 1.5);
    plot(timeIncrements, resultant_Z2, 'k-', 'LineWidth', 2.5);
    hold off;
    grid on;
    xlabel('Time (s)');
    ylabel('Weight (kg)');
    title('P2\_LoadCell\_Z');
    legend('P2\_LoadCell\_Z\_1', 'P2\_LoadCell\_Z\_2', 'P2\_LoadCell\_Z\_3', 'P2\_LoadCell\_Z\_4','RESULTANTE');
else
    disp('Los datos de Plataforma 2 - Eje Z no se encuentran disponibles. Ignorando figura.');
end

% P2_LoadCell_X
if ismember('P2_LoadCell_X_1', data.Properties.VariableNames) && ...
   ismember('P2_LoadCell_X_2', data.Properties.VariableNames) && ...
   ismember('P2_LoadCell_X_3', data.Properties.VariableNames) && ...
   ismember('P2_LoadCell_X_4', data.Properties.VariableNames)

    loadCell_X2 = [-data.P2_LoadCell_X_1, data.P2_LoadCell_X_2, data.P2_LoadCell_X_3, -data.P2_LoadCell_X_4];
    resultant_X2 = -data.P2_LoadCell_X_1 + data.P2_LoadCell_X_2 + data.P2_LoadCell_X_3 - data.P2_LoadCell_X_4;

    subplot(3, 1, 2);
    hold on;
    plot(timeIncrements, loadCell_X2(:, 1), 'r-', 'LineWidth', 1.5);
    plot(timeIncrements, loadCell_X2(:, 2), 'r--', 'LineWidth', 1.5);
    plot(timeIncrements, loadCell_X2(:, 3), 'b-', 'LineWidth', 1.5);
    plot(timeIncrements, loadCell_X2(:, 4), 'b--', 'LineWidth', 1.5);
    plot(timeIncrements, resultant_X2, 'k-', 'LineWidth', 2.5);
    hold off;
    grid on;
    xlabel('Time (s)');
    ylabel('Weight (kg)');
    title('P2\_LoadCell\_X');
    legend('P2\_LoadCell\_X\_1', 'P2\_LoadCell\_X\_2', 'P2\_LoadCell\_X\_3', 'P2\_LoadCell\_X\_4','RESULTANTE');
else
    disp('Los datos de Plataforma 2 - Eje X no se encuentran disponibles. Ignorando figura.');
end

% P2_LoadCell_Y
if ismember('P2_LoadCell_Y_1', data.Properties.VariableNames) && ...
   ismember('P2_LoadCell_Y_2', data.Properties.VariableNames) && ...
   ismember('P2_LoadCell_Y_3', data.Properties.VariableNames) && ...
   ismember('P2_LoadCell_Y_4', data.Properties.VariableNames)

    loadCell_Y2 = [-data.P2_LoadCell_Y_1, -data.P2_LoadCell_Y_2, data.P2_LoadCell_Y_3, data.P2_LoadCell_Y_4];
    resultant_Y2 = -data.P2_LoadCell_Y_1 - data.P2_LoadCell_Y_2 + data.P2_LoadCell_Y_3 + data.P2_LoadCell_Y_4;
    
    subplot(3, 1, 3);
    hold on;
    plot(timeIncrements, loadCell_Y2(:, 1), 'r-', 'LineWidth', 1.5);
    plot(timeIncrements, loadCell_Y2(:, 2), 'r--', 'LineWidth', 1.5);
    plot(timeIncrements, loadCell_Y2(:, 3), 'b-', 'LineWidth', 1.5);
    plot(timeIncrements, loadCell_Y2(:, 4), 'b--', 'LineWidth', 1.5);
    plot(timeIncrements, resultant_Y2, 'k-', 'LineWidth', 2.5);
    hold off;
    grid on;
    xlabel('Time (s)');
    ylabel('Weight (kg)');
    title('P2\_LoadCell\_Y');
    legend('P2\_LoadCell\_Y\_1', 'P2\_LoadCell\_Y\_2', 'P2\_LoadCell\_Y\_3', 'P2\_LoadCell\_Y\_4','RESULTANTE');

else
    disp('Los datos de Plataforma 2 - Eje Y no se encuentran disponibles. Ignorando figura.');
end

%% ENCODERS
figure (3);
if ismember('Encoder_Z_1', data.Properties.VariableNames) && ...
   ismember('Encoder_Z_2', data.Properties.VariableNames)

    encoders = [data.Encoder_Z_1, data.Encoder_Z_2];

    hold on;
    plot(timeIncrements, encoders(:, 1), 'r-', 'LineWidth', 1.5);
    plot(timeIncrements, encoders(:, 2), 'b-', 'LineWidth', 1.5);
    hold off;

    % plot(timeIncrements, encoders, 'LineWidth', 1.5);
    grid on;
    xlabel('Time (s)');
    ylabel('Distance (mm)');
    title('Encoders');
    legend('Encoder\_Z1', 'Encoder\_Z2');
else
    disp('Faltan uno o ambos Encoders 1 y 2. Ignorando figura.');
end

%% IMUS ANGLES
figure (4);

% IMU 1
if ismember('IMU_Leg_Right_qw', data.Properties.VariableNames) && ...
   ismember('IMU_Leg_Right_qx', data.Properties.VariableNames) && ...
   ismember('IMU_Leg_Right_qy', data.Properties.VariableNames) && ...
   ismember('IMU_Leg_Right_qz', data.Properties.VariableNames)

    imu_1_q = [data.IMU_Leg_Right_qw, data.IMU_Leg_Right_qx, data.IMU_Leg_Right_qy, data.IMU_Leg_Right_qz];

    imu_1_eul = quat2eul(imu_1_q, 'XYZ');
    imu_1_eul_deg = rad2deg(imu_1_eul);
    
    subplot(3, 1, 1);
    hold on;
    plot(timeIncrements, imu_1_eul_deg(:, 1), 'r--', 'LineWidth', 1.5);
    plot(timeIncrements, imu_1_eul_deg(:, 2), 'b--', 'LineWidth', 1.5);
    plot(timeIncrements, imu_1_eul_deg(:, 3), 'k-', 'LineWidth', 1.5);
    hold off;
    % plot(timeIncrements, imu_1_eul_deg, 'LineWidth', 1.5);
    xlabel('Time (s)');
    ylabel('Angle (º)');
    title('IMU\_1');
    legend('IMU\_X', 'IMU\_Y', 'IMU\_Z');
else
    disp('Los datos de IMU 1 - Quaterniones no se encuentran disponibles. Ignorando figura.');
end

% IMU 2
if ismember('IMU_Thigh_Right_qw', data.Properties.VariableNames) && ...
   ismember('IMU_Thigh_Right_qx', data.Properties.VariableNames) && ...
   ismember('IMU_Thigh_Right_qy', data.Properties.VariableNames) && ...
   ismember('IMU_Thigh_Right_qz', data.Properties.VariableNames)

    imu_2_q = [data.IMU_Thigh_Right_qw, data.IMU_Thigh_Right_qx, data.IMU_Thigh_Right_qy, data.IMU_Thigh_Right_qz];

    imu_2_eul = quat2eul(imu_2_q, 'XYZ');
    imu_2_eul_deg = rad2deg(imu_2_eul);
    
    subplot(3, 1, 2);
    hold on;
    plot(timeIncrements, imu_2_eul_deg(:, 1), 'r--', 'LineWidth', 1.5);
    plot(timeIncrements, imu_2_eul_deg(:, 2), 'b--', 'LineWidth', 1.5);
    plot(timeIncrements, imu_2_eul_deg(:, 3), 'k-', 'LineWidth', 1.5);
    hold off;
    % plot(timeIncrements, imu_2_eul_deg, 'LineWidth', 1.5);
    xlabel('Time (s)');
    ylabel('Angle (º)');
    title('IMU\_2');
    legend('IMU\_X', 'IMU\_Y', 'IMU\_Z');
else
    disp('Los datos de IMU 2 - Quaterniones no se encuentran disponibles. Ignorando figura.');
end

% IMU 3
if ismember('IMU_UpperTrunk_Right_qw', data.Properties.VariableNames) && ...
   ismember('IMU_UpperTrunk_Right_qx', data.Properties.VariableNames) && ...
   ismember('IMU_UpperTrunk_Right_qy', data.Properties.VariableNames) && ...
   ismember('IMU_UpperTrunk_Right_qz', data.Properties.VariableNames)

    imu_3_q = [data.IMU_UpperTrunk_Right_qw, data.IMU_UpperTrunk_Right_qx, data.IMU_UpperTrunk_Right_qy, data.IMU_UpperTrunk_Right_qz];

    imu_3_eul = quat2eul(imu_3_q, 'XYZ');
    imu_3_eul_deg = rad2deg(imu_3_eul);
    
    subplot(3, 1, 3);
    hold on;
    plot(timeIncrements, imu_3_eul_deg(:, 1), 'r--', 'LineWidth', 1.5);
    plot(timeIncrements, imu_3_eul_deg(:, 2), 'b-', 'LineWidth', 1.5);
    plot(timeIncrements, imu_3_eul_deg(:, 3), 'k--', 'LineWidth', 1.5);
    hold off;
    % plot(timeIncrements, imu_3_eul_deg, 'LineWidth', 1.5);
    xlabel('Time (s)');
    ylabel('Angle (º)');
    title('IMU\_3');
    legend('IMU\_X', 'IMU\_Y', 'IMU\_Z');
else
    disp('Los datos de IMU 3 - Quaterniones no se encuentran disponibles. Ignorando figura.');
end

%% IMUS ANGULAR VELOCITY
figure (5);

% IMU 1
if ismember('IMU_Leg_Right_wx', data.Properties.VariableNames) && ...
   ismember('IMU_Leg_Right_wy', data.Properties.VariableNames) && ...
   ismember('IMU_Leg_Right_wz', data.Properties.VariableNames)

    imu_1_w = [data.IMU_Leg_Right_wx, data.IMU_Leg_Right_wy, data.IMU_Leg_Right_wz];

    subplot(3, 1, 1);
    hold on;
    plot(timeIncrements, imu_1_w(:, 1), 'r-', 'LineWidth', 1.5);
    plot(timeIncrements, imu_1_w(:, 2), 'b-', 'LineWidth', 1.5);
    plot(timeIncrements, imu_1_w(:, 3), 'k-', 'LineWidth', 1.5);
    hold off;
    % plot(timeIncrements, imu_1_w, 'LineWidth', 1.5);
    xlabel('Time (s)');
    ylabel('Angular velocity (rad/s)');
    title('IMU\_1');
    legend('IMU\_X', 'IMU\_Y', 'IMU\_Z');
else
    disp('Los datos de IMU 1 - Velocidades angulares no se encuentran disponibles. Ignorando figura.');
end

% IMU 2
if ismember('IMU_Thigh_Right_wx', data.Properties.VariableNames) && ...
   ismember('IMU_Thigh_Right_wy', data.Properties.VariableNames) && ...
   ismember('IMU_Thigh_Right_wz', data.Properties.VariableNames)

    imu_2_w = [data.IMU_Thigh_Right_wx, data.IMU_Thigh_Right_wy, data.IMU_Thigh_Right_wz];

    subplot(3, 1, 2);
    hold on;
    plot(timeIncrements, imu_2_w(:, 1), 'r-', 'LineWidth', 1.5);
    plot(timeIncrements, imu_2_w(:, 2), 'b-', 'LineWidth', 1.5);
    plot(timeIncrements, imu_2_w(:, 3), 'k-', 'LineWidth', 1.5);
    hold off;
    % plot(timeIncrements, imu_2_w, 'LineWidth', 1.5);
    xlabel('Time (s)');
    ylabel('Angular velocity (rad/s)');
    title('IMU\_2');
    legend('IMU\_X', 'IMU\_Y', 'IMU\_Z');
else
    disp('Los datos de IMU 2 - Velocidades angulares no se encuentran disponibles. Ignorando figura.');
end

% IMU 3
if ismember('IMU_UpperTrunk_Right_wx', data.Properties.VariableNames) && ...
   ismember('IMU_UpperTrunk_Right_wy', data.Properties.VariableNames) && ...
   ismember('IMU_UpperTrunk_Right_wz', data.Properties.VariableNames)

    imu_3_w = [data.IMU_UpperTrunk_Right_wx, data.IMU_UpperTrunk_Right_wy, data.IMU_UpperTrunk_Right_wz];

    subplot(3, 1, 3);
    hold on;
    plot(timeIncrements, imu_3_w(:, 1), 'r-', 'LineWidth', 1.5);
    plot(timeIncrements, imu_3_w(:, 2), 'b-', 'LineWidth', 1.5);
    plot(timeIncrements, imu_3_w(:, 3), 'k-', 'LineWidth', 1.5);
    hold off;
    % plot(timeIncrements, imu_3_w, 'LineWidth', 1.5);
    xlabel('Time (s)');
    ylabel('Angular velocity (rad/s)');
    title('IMU\_3');
    legend('IMU\_X', 'IMU\_Y', 'IMU\_Z');
else
    disp('Los datos de IMU 3 - Velocidades angulares no se encuentran disponibles. Ignorando figura.');
end