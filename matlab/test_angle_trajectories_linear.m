function [absangle] = test_angle_trajectories_linear(timeIncrements,reps,pos_i,pos_f)
%% test_angle_trajectories_linear
% Author: Aaron Raul Poyatos Bakker
% Date: 13/06/2023
% Generates absolute angle test values between initial and final pose.
    rep_points = numel(timeIncrements)/reps;
    
    absangle_1 = linspace(pos_i, pos_f, round(rep_points/2));
    absangle_2 = linspace(pos_f, pos_i, rep_points - round(rep_points/2)+1);
    absangle = [absangle_1, absangle_2];
    
    absangle = repmat(absangle, 1, reps);
    absangle = transpose(absangle(1:numel(timeIncrements)));
    
    % Apply noise
    % absangle = absangle + 0.01 * (2*rand(size(timeIncrements)) - 1);
end
