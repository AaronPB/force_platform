function [absangle] = test_angle_trajectories_parabolic(timeIncrements,reps,pos_i,pos_f)
%% test_angle_trajectories_parabolic
% Author: Aaron Raul Poyatos Bakker
% Date: 13/06/2023
% Generates absolute angle test values between initial and final pose.
    rep_points = numel(timeIncrements) / reps;

    x1 = linspace(0, 1, round(rep_points/2));
    x2 = linspace(0, 1, rep_points - round(rep_points/2) + 1);
    
    y1 = sqrt(x1);
    y2 = -sqrt(x2);
    
    absangle_1 = pos_i + (pos_f - pos_i) * y1;
    absangle_2 = pos_f + (-pos_i + pos_f) * y2;
    absangle = [absangle_1, absangle_2];

    absangle = repmat(absangle, 1, reps);
    absangle = transpose(absangle(1:numel(timeIncrements)));

    % Apply noise
    % absangle = absangle + 0.01 * (2*rand(size(timeIncrements)) - 1);
end
