import threading
import time
from opensourceleg.osl import OpenSourceLeg
import numpy as np
import itertools
from futek import Big100NmFutek
from time import strftime
from SimpleTimer import SimpleTimer
import os

ramping_up = False
ramp_target_current = 0.0
ramp_duration = 1.0  # seconds
ramp_start_time = None

def generate_trapezoidal_current():
    peak_currents = np.arange(2.5, 21, 2.5)  # Increasing peak values up to 20A
    time_step = 0.01  # Time resolution in seconds
    segment_times = [1, 2, 2, 2, 1, 2]  # Time for each segment [rise, hold, fall, hold, rise to 0, hold at 0]

    time_values = []
    current_values = []

    t = 0
    for peak in peak_currents:
        t_rise = np.linspace(t, t + segment_times[0], int(segment_times[0] / time_step))
        c_rise = np.linspace(0, peak, len(t_rise))

        t_hold1 = np.linspace(t_rise[-1], t_rise[-1] + segment_times[1], int(segment_times[1] / time_step))
        c_hold1 = np.full_like(t_hold1, peak)

        t_fall = np.linspace(t_hold1[-1], t_hold1[-1] + segment_times[2], int(segment_times[2] / time_step))
        c_fall = np.linspace(peak, -peak, len(t_fall))

        t_hold2 = np.linspace(t_fall[-1], t_fall[-1] + segment_times[3], int(segment_times[3] / time_step))
        c_hold2 = np.full_like(t_hold2, -peak)

        t_rise_zero = np.linspace(t_hold2[-1], t_hold2[-1] + segment_times[4], int(segment_times[4] / time_step))
        c_rise_zero = np.linspace(-peak, 0, len(t_rise_zero))

        t_hold_zero = np.linspace(t_rise_zero[-1], t_rise_zero[-1] + segment_times[5], int(segment_times[5] / time_step))
        c_hold_zero = np.full_like(t_hold_zero, 0)

        time_values.extend(t_rise)
        time_values.extend(t_hold1)
        time_values.extend(t_fall)
        time_values.extend(t_hold2)
        time_values.extend(t_rise_zero)
        time_values.extend(t_hold_zero)

        current_values.extend(c_rise)
        current_values.extend(c_hold1)
        current_values.extend(c_fall)
        current_values.extend(c_hold2)
        current_values.extend(c_rise_zero)
        current_values.extend(c_hold_zero)

        t = time_values[-1]

    return list(zip(time_values, current_values))  # Return list of (time, current)

trapezoidal_current_data = generate_trapezoidal_current()

def control_knee(osl, trapezoidal_current_data, time_step=0.01):
    global ramping_up, ramp_target_current, ramp_duration, ramp_start_time 

    test_index = 0
    total_conditions = len(trapezoidal_current_data)
    test_timer = SimpleTimer()
    TEST_DURATION_S = time_step  # Ensure same step as trapezoidal generator

    with osl:
        osl.knee.set_mode(osl.knee.control_modes.current)
        osl.knee.set_current(0.0)  # Initial current value
        osl.knee.set_current_gains(kp=40, ki=400, ff=60)  # Set current gains
        cur_current_command = 0.0
        
        cooling_down = False  # Flag to indicate cooling state

        for t in osl.clock:
            osl.update()
            torqueSensor.update()
            torqueSensor.get_torque()
            winding_temp = osl.knee.winding_temperature
            battery_voltage = 1 / 1000 * osl.knee.battery_voltage

            # Safety checks
            if winding_temp > 100:
                raise ValueError("Motor above thermal limit. Quitting!")
            if battery_voltage > 43:
                print("Knee voltage {} is greater than 43V".format(battery_voltage))
            if battery_voltage < 28:
                print("Knee voltage {}".format(battery_voltage))
                raise ValueError("Battery voltage below 32V")

            # Cooling logic: Pause when temp > 60, resume when temp ≤ 40
            if winding_temp > 60:
                cooling_down = True
                ramping_up = False  # Cancel any ramp-up in progress
                cur_current_command = 0.0
                print("Max winding temp {:.2f} C. Cooling until 40°C...".format(winding_temp), end='\r')

            if cooling_down and winding_temp <= 40:
                cooling_down = False
                ramping_up = True
                if test_index > 0:
                    ramp_target_current = trapezoidal_current_data[test_index - 1][1]  # Restore previous target current
                ramp_start_time = time.time()
                cur_current_command = 0.0  # Start ramping from 0
                print("Temperature cooled to {:.2f} C. Ramping up to {:.2f} A...".format(winding_temp, ramp_target_current))


            # Ramp-up logic (before main test logic)
            if ramping_up:
                elapsed = time.time() - ramp_start_time
                if elapsed >= ramp_duration:
                    cur_current_command = ramp_target_current
                    ramping_up = False  # Done ramping
                    print("Ramp-up complete. Resuming main test.")
                else:
                    cur_current_command = ramp_target_current * (elapsed / ramp_duration)

            # Update current command based on trapezoidal profile
            if test_timer.is_done and not cooling_down:
                if test_index >= total_conditions:
                    osl.knee.set_current(0.0)
                    osl.clock.stop()
                    print("Test complete :)")
                    break
                else:
                    # Get next current value
                    cur_current_command = trapezoidal_current_data[test_index][1]
                    test_index += 1  # Move to the next current step
                    print("Step {} of {}: Setting current to {:.2f} A.".format(test_index, total_conditions, cur_current_command))
                    test_timer.start(TEST_DURATION_S)

            # Apply current to the knee (convert A to mA)
            osl.knee.set_current(cur_current_command * 1000.0)


if __name__ == '__main__':
    start_time = time.time()

    trapezoidal_current_data = generate_trapezoidal_current()  # Generate waveform

    test_timer = SimpleTimer()
    osl = OpenSourceLeg(frequency=300, file_name='motor2_updated_ankle_current_static'+strftime("%y%m%d_%H%M%S"))
    osl.add_joint(name="knee", port=r"/dev/ttyACM0", gear_ratio=9.0)

    torqueSensor = Big100NmFutek()
    torqueSensor.calibrate_loadcell()

    actpack_vars_2_log = ["output_position", "output_velocity", "motor_position", "motor_velocity",
                          "winding_temperature", "case_temperature", "motor_current", 
                          "motor_voltage","battery_voltage","battery_current",
                          "joint_position", "joint_velocity"]
    osl.log.add_attributes(osl, ["timestamp"])
    osl.log.add_attributes(osl.knee, actpack_vars_2_log)
    osl.log.add_attributes(torqueSensor, ["torque"])
    osl.log.add_attributes(test_timer, ["is_done", "start_time", "end_time"])
    osl.log.add_attributes(locals(), ["cur_current_command", "cur_voltage_command"])



    knee_thread = threading.Thread(target=control_knee, args=(osl, trapezoidal_current_data))
    knee_thread.start()
    knee_thread.join()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total execution time: {elapsed_time:.2f} seconds")