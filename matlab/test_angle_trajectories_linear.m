function [absangle_A,absangle_B,absangle_C] = test_angle_trajectories_linear(timeIncrements,pos_i,pos_f_A,pos_f_B,pos_f_C,reps)
%% test_angle_trajectories_linear
% Author: Aaron Raul Poyatos Bakker
% Date: 13/06/2023
% Generates absolute angle test values between common initial pose and
% specific final pose for each angle.
    rep_points = numel(timeIncrements)/reps;
    
    absangle_A1 = linspace(pos_i, pos_f_A, round(rep_points/2));
    absangle_A2 = linspace(pos_f_A, pos_i, rep_points - round(rep_points/2)+1);
    absangle_B1 = linspace(pos_i, pos_f_B, round(rep_points/2));
    absangle_B2 = linspace(pos_f_B, pos_i, rep_points - round(rep_points/2)+1);
    absangle_C1 = linspace(pos_i, pos_f_C, round(rep_points/2));
    absangle_C2 = linspace(pos_f_C, pos_i, rep_points - round(rep_points/2)+1);
    
    absangle_A = [absangle_A1, absangle_A2];
    absangle_B = [absangle_B1, absangle_B2];
    absangle_C = [absangle_C1, absangle_C2];
    
    absangle_A = repmat(absangle_A, 1, reps);
    absangle_B = repmat(absangle_B, 1, reps);
    absangle_C = repmat(absangle_C, 1, reps);
    
    absangle_A = transpose(absangle_A(1:numel(timeIncrements)));
    absangle_B = transpose(absangle_B(1:numel(timeIncrements)));
    absangle_C = transpose(absangle_C(1:numel(timeIncrements)));
    
    % Apply noise
    % absangle_A = absangle_A + 0.01 * (2*rand(size(timeIncrements)) - 1);
    % absangle_B = absangle_B + 0.01 * (2*rand(size(timeIncrements)) - 1);
    % absangle_C = absangle_C + 0.01 * (2*rand(size(timeIncrements)) - 1);
end

