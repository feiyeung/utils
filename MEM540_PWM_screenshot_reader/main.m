% main
[FILENAME, PATHNAME, FILTERINDEX] = ...
    uigetfile('*.*', 'select pics', 'MultiSelect','on');
if FILTERINDEX > 0
    results = [];    close all;
    if ~iscell(FILENAME)
        FILENAME = {FILENAME};
    end
    for name = sort(FILENAME)
        r = read_pwm_from_screenshot([PATHNAME, name{1}]);
        results = [results; r];
    end
end

%%
close all;