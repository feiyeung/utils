function results = read_pwm_from_screenshot( path_to_pic )

% clear; clc; close all;
% A = imread('C:\Users\Feiyang\Google Drive\MEM540\Week3 Lab\5D12\50.PNG');
A = imread(path_to_pic);
A3 = imread('anchor.png');
B_blue =  [0.58 0.80 1.00]; % in hsv space
B_white =  [0.00 0.00 1.00]; % in hsv space
n_colors = 10; % number of colors for comparison
offset_from_anchor = [706 ,286];
Fs = 627 / 0.002 ; % num_pixels / timespan
gpu = false;
plot1 = true; % raw pic
plot2 = false; % intermediate pics
th_anchor = 2; % threshold for finding anchor. euclidean distance in RGB space, 0-255.
th_voltage = 0.02; % threshold for finding each voltage/color in HSV space, 0-1.

[pathstr,name,ext] = fileparts(path_to_pic);
fprintf('%s%s\n', name, ext);
% tic;
[X, map] = rgb2ind(A3, n_colors, 'nodither');
count = 0; ACropColor = {}; AColor = {};
for color = (map * 255)'
    count = count + 1; ACropCh = {}; ACh = {};
    for ch = [1:3]
        ACropCh{ch} = abs( A3(:,:,ch) - color(ch) ) < th_anchor;
        ACh{ch} = abs( A(:,:,ch) - color(ch) ) < th_anchor;
    end
    ACropColor{count} = uint32( ACropCh{1} .* ACropCh{2} .* ACropCh{3});
    AColor{count} = uint32( ACh{1} .* ACh{2} .* ACh{3} );
end

if gpu
    for i = 1:length(AColor)
        ACropColor{i} = gpuArray(ACropColor{i});
        AColor{i} = gpuArray(AColor{i});
    end
end

AConvG = {};
for i = 1:length(AColor)
    AConvG{i} = conv2(AColor{i}, flipud(fliplr(ACropColor{i})));
end

AConv = gather(AConvG{1});
for i = 2:length(AConvG)
    if gpu
        AConv = AConv + gather(AConvG{i});
    else
        AConv = AConv + AConvG{i};
    end
end
% toc;
[x,y] = find( AConv == max(max(AConv)) );
anchor = flip( [x, y-size(A3,2)+1] );



B_raw = imcrop(A, [anchor, offset_from_anchor]);
if plot1
    figure; imshow(B_raw, 'InitialMagnification',100);
    title([name,ext]);
end

% anchor: (70, 540)
% cornor 1: (66, 558)  [213 213 213]
% cornor 2: (772, 844)  [71 71 71]

% c1 to anchor: [-4    18]
% c2 to anchor: [702   304]

% imcrop( I, [xmin ymin width height] )
% [706   286]


B = rgb2hsv(B_raw);
results = [];
sig = {}; itp = {}; bin_pic = {};
for color = {B_blue, B_white}
    bin_pic{end+1} = cmp_pic_to_c_3d( B, color{1}, th_voltage);  
    [sig{end+1}, itp{end+1}] = get_sig_from_pic(bin_pic{end}, 0.25);
end
sig_lookedup = {};
[sig_lookedup{1}, sig_lookedup{2}] = xcmp(sig{1}, itp{1}, sig{2}, itp{2});

for i=[1,2]
    [sig_lookedup{i}, itp{i}] = offset_zeros(sig_lookedup{i}, itp{i});
end

i = 0;
for color = {B_blue, B_white}
    i = i + 1;
    sig = sig_lookedup{i};
    if (max(sig) - min(sig)) < 4
        disp('vertical difference is less than 5 pixels. skip');
        r = struct(); r.sig = sig; r.dc = []; r.dc_med = []; 
        r.color = color{1}; r.color_ind = length(results) + 1;
        r.pathstr = pathstr; r.name = name; r.ext = ext;
        results = [results; r];
        continue
    end
    if plot2
        figure; title(sprintf('[%.2f %.2f %.2f]',color{1})); 
        subplot(2,1,1); imshow(bin_pic{i}); 
        subplot(2,1,2); imshow(B_raw);
        figure; title(sprintf('[%.2f %.2f %.2f]',color{1})); hold on; 
        plot(sig); 
        if ~isempty(itp{i})
            plot(itp{i}(:,1), ...
                itp{i}(:,2),'.'); 
        end
        hold off; grid on;
        legend('overall signal', 'interpolated points'); axis equal;
        title(sprintf('[%.2f %.2f %.2f]',color{1}));
    end
    figure; dutycycle(sig, Fs, 'Tolerance', 5); dc = ans
    r = struct(); r.sig = sig; r.dc = dc; r.dc_med = median(dc); 
    r.color = color{1}; r.color_ind = length(results) + 1;
    % r.path = path_to_pic; 
    r.pathstr = pathstr; r.name = name; r.ext = ext;
    results = [results; r];
    title(sprintf('%s%s, color %d, DC=%.4f' , ...
        name,ext,r.color_ind, r.dc_med));
end
% toc;

% dc = [median(results(1).dc), median(results(2).dc)];

end


function bin_pic = cmp_pic_to_c_3d(pic, c, err)
% compare a picture to a color
C = {};
for ch = [1:3]
    C{ch} = abs(pic(:,:,ch) - c(ch)) < err;
end
bin_pic = C{1} .* C{2} .* C{3};
end

function [sig, itp_pts] = get_sig_from_pic(pic, th)
% find PWM signals from a binary picture
% sig: vector for signal
% itp_pts: matrix for interpolated points
[y, x] = find(pic == 1); 
y = (size(pic,1) - y + 1); % flip y
% find thresholds
thy_up = max(y) - th * (max(y) - min(y));
thy_lo = min(y) + th * (max(y) - min(y));
sig = zeros([1 size(pic, 2)]);
for this_x = min(x):max(x)
     this_y = y( x == this_x );
     if length(this_y) > 0
         if (max(this_y) > thy_up) == (min(this_y) < thy_lo)
             sig(this_x) = median( this_y );
         elseif max(this_y) > thy_up
             sig(this_x) = max( this_y );
         elseif min(this_y) < thy_lo
             sig(this_x) = min( this_y );
         end
     else
         sig(this_x) = 0;
     end
end
x_has_value = sort(find(sig>0));
fill_sig = @(xin) interp1(x_has_value, sig(x_has_value), xin);
itp_pts = [];
for missing_x = find(sig==0)
    if (min(x) < missing_x) && (missing_x < max(x))
        itp = fill_sig(missing_x);
        sig(missing_x) = itp;
        itp_pts = [itp_pts; [missing_x, itp]];
    end
end
% sig = sig(min(x):max(x)); % strip no-signals
% itp_pts(:,1) = itp_pts(:,1) - min(x) + 1; % offset to match
end

function [sig1 sig2] = xcmp(sig1, itp1, sig2, itp2)
% assume that overlapping happens when
% (x has value in sig1) XOR (x has value in sig2), 
% therefore use value from the other sign to fill in 
if ~isempty(itp1)
    itp1_x = itp1(:,1);
else
    itp1_x = [];
end
if ~isempty(itp2)
    itp2_x = itp2(:,1);
else
    itp2_x = [];
end
for x = itp1_x'
    if sum(itp2_x == x) == 0
        sig1(x) = sig2(x);
    end
end
for x = itp2_x'
    if sum(itp1_x == x) == 0
        sig2(x) = sig1(x);
    end
end 

end


function [sig itp] = offset_zeros(sig, itp)
    sig_nonzero_ind = find(sig ~= 0);
    nonzero_begin_ind = min(sig_nonzero_ind);
    nonzero_end_ind = max(sig_nonzero_ind);
    sig = sig(nonzero_begin_ind : nonzero_end_ind);
    if ~isempty(itp)
        itp(:,1) = itp(:,1) - nonzero_begin_ind + 1;
    end
end

function [pic] = get_anchor_pic()


end