clc;
clear;
close all;

pole_pairs = 14;
multichan = 0;
saveflag = 0;
datapath = 'C:\Users\Riley\OneDrive\Documents\Neurobionics\skip_char\Testbed\Data\backEMF';
testname = "backEMF__M1__CA__5rev_s";

daqreset;
dev = daqlist("ni");
assert(height(dev)==1);
disp("Reading device:");
disp(dev.Description);

dq = daq("ni");
dq.Rate = 20000;

if multichan
    [ch1,idx1] = addinput(dq, dev.DeviceID, "ai1", "Voltage");
    ch1.Range = [-5 5];
    [ch2,idx2] = addinput(dq, dev.DeviceID, "ai2", "Voltage");
    ch2.Range = [-5 5];
    [ch3,idx3] = addinput(dq, dev.DeviceID, "ai3", "Voltage");
    ch3.Range = [-5 5];
else
    [ch0,idx0] = addinput(dq, dev.DeviceID, "ai0", "Voltage");
    ch0.Range = [-5 5];
end

data = read(dq, seconds(1));

if multichan
    chan1 = getBackEMF(data.Time, data.DAQ_ScrewTerm_ai1, pole_pairs);
    chan2 = getBackEMF(data.Time, data.DAQ_ScrewTerm_ai2, pole_pairs);
    chan3 = getBackEMF(data.Time, data.DAQ_ScrewTerm_ai3, pole_pairs);
else
    chan0 = getBackEMF(data.Time, data.DAQ_ScrewTerm_ai0, pole_pairs);
end


figure(1);
plot(data.Time, data.Variables);
hold on;
if multichan
    scatter(data.Time(chan1.idxs), data.DAQ_ScrewTerm_ai1(chan1.idxs));
    scatter(data.Time(chan2.idxs), data.DAQ_ScrewTerm_ai2(chan2.idxs));
    scatter(data.Time(chan3.idxs), data.DAQ_ScrewTerm_ai3(chan3.idxs));
else
    scatter(data.Time(chan0.idxs), data.DAQ_ScrewTerm_ai0(chan0.idxs));
end
hold off;
ylabel('Voltage [V]');
xlabel('Time [s]');

figure(2);
if multichan
    subplot(1,3,1);
    plot(chan1.time_avg, chan1.cycle_avg);
    ylabel('Voltage [V]');
    xlabel('Time [s]');
    title("Channel 1: k_t^q = " + string(chan1.k_t_q));
    subplot(1,3,2);
    plot(chan2.time_avg, chan2.cycle_avg);
    ylabel('Voltage [V]');
    xlabel('Time [s]');
    title("Channel 2: k_t^q = " + string(chan2.k_t_q));
    subplot(1,3,3);
    plot(chan3.time_avg, chan3.cycle_avg);
    ylabel('Voltage [V]');
    xlabel('Time [s]');
    title("Channel 3: k_t^q = " + string(chan3.k_t_q));
else
    plot(chan0.time_avg, chan0.cycle_avg);
    title("k_t^q = " + string(chan0.k_t_q));
end
ylabel('Voltage [V]');
xlabel('Time [s]');

if saveflag
    if multichan
        save(fullfile(datapath, testname), 'chan1', 'chan2', 'chan3');
    else
        save(fullfile(datapath, testname), 'chan0');
    end
end

function chan = getBackEMF(time, voltage, pole_pairs)
    
    chan.data = voltage;
    chan.time = time;
    
    chan.idxs = [];
    for i = 2:length(time)
        if voltage(i) >= 0 && voltage(i-1) <= 0 && (voltage(i) - voltage(i-1)) >= 0
            chan.idxs = [chan.idxs i];
        end
    end

    chan.cycles = [];
    chan.periods = [];
    for i = 1:length(chan.idxs)-1
        start_idx = chan.idxs(i);
        end_idx = chan.idxs(i+1)-1;
        voltage_cyc = voltage(start_idx:end_idx);
        time_cyc = time(start_idx:end_idx);
        chan.periods = [chan.periods range(time_cyc)];
        timeq = linspace(time_cyc(1), time_cyc(end), 1000);
        voltage_interp = interp1(time_cyc, voltage_cyc, timeq)';
        chan.cycles = [chan.cycles voltage_interp];
    end
    chan.cycle_avg = mean(chan.cycles, 2);
    chan.period_avg = mean(chan.periods);
    chan.freq_avg = 1/seconds(chan.period_avg);
    chan.time_avg = linspace(0, chan.period_avg, 1000);
    chan.V_pkpk_avg = max(chan.cycle_avg) - min(chan.cycle_avg);
    chan.k_t_q = (chan.V_pkpk_avg/2)/(sqrt(2/3)*chan.freq_avg*2*pi/pole_pairs);

end