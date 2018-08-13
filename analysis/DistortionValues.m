% FOR XY orientation 
% MUST change the x input name for the following to work 

% x_iso = x_in - 119;%118; %Note: this input file name changes with every import depending on file name
% y_iso = VarName2 - 100;% 101; % Note these values will also change depending on the input image and its orientation/origin
% z_iso = VarName3 - 35; %34 

x_iso = x_in - 119;%118; %Note: this input file name changes with every import depending on file name
y_iso = VarName2 - 100;% 101; % Note these values will also change depending on the input image and its orientation/origin
z_iso = VarName3 - 35;

x = x_iso*1.195312;
y = y_iso*1.195312;
z = z_iso*3;

Dist_from_iso = sqrt(x.^2 + y.^2 + z.^2);

TotalDist = sqrt((VarName4.^2) + (VarName5.^2)+ (VarName6.^2));
MaxDist = max(TotalDist)
MeanDist = mean(TotalDist)
minDIst = min(TotalDist)
StDevDist = std(TotalDist)

% Scatter plot of the total distortion as a function of distance from iso
scatter(Dist_from_iso,TotalDist)