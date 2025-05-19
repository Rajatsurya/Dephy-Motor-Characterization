import threading
import time
from opensourceleg.osl import OpenSourceLeg
import numpy as np
import itertools
from futek import Big100NmFutek
from time import strftime
from SimpleTimer import SimpleTimer
import os

def check_knee_temperature():
    prev_status = None  # Store previous status to avoid unnecessary writes
    while True:
        temp_knee = osl.knee.winding_temperature  # Read from ankle motor
        motor_knee_below_thresh = temp_knee <= 40

        # Get the current working directory
        current_directory = os.getcwd()

        # Define the file path in the current directory
        file_path = os.path.join(current_directory, "knee_motor_status.txt")

        # Determine current status
        current_status = "STOP" if not motor_knee_below_thresh else "GO"

        # Write status only if it changes
        if current_status != prev_status:
            with open(file_path, "w") as f:
                f.write(current_status)  # Update status in the file
            prev_status = current_status  # Update the previous status

        time.sleep(1/300)  # Check every second


def check_ankle_status():
    # Get the current working directory
    current_directory = os.getcwd()
    
    # Define the file path in the current directory
    file_path = os.path.join(current_directory, "ankle_motor_status.txt")

    try:
        # Read status directly from the file
        with open(file_path, "r") as f:
            status = f.read().strip()  # Read status (either "GO" or "STOP")
        return status == "STOP"  # Return True if status is "STOP", False if "GO"
    except FileNotFoundError:
        print(f"Ankle motor status file not found at {file_path}!")
        return False


def control_knee(osl, test_conditions):
    test_index = 0  # Start with the first current points
    total_conditions = len(test_conditions)
    test_timer = SimpleTimer() 
    TEST_DURATION_S = 5  

    with osl:
        osl.knee.set_mode(osl.knee.control_modes.current)
        osl.knee.set_current(0.0)  # Initial current value
        osl.knee.set_current_gains(kp=40, ki=400, ff=60)  # Set current gains
        cur_current_command = 0.0
        for t in osl.clock:
            osl.update()  # Update the system for each clock cycle
            torqueSensor.update()
            torqueSensor.get_torque()
            winding_temp = osl.knee.winding_temperature
            battery_voltage = 1/1000 * osl.knee.battery_voltage
            motor_below_temp_thresh = winding_temp <=40
            if winding_temp > 100:
                 raise ValueError("Motor above thermal limit. Quitting!")
            if battery_voltage > 43:
                print (" Knee voltage {} is greater than 43v".format(1/1000*osl.knee.battery_voltage))
            if battery_voltage < 28:
                print ("Knee voltage {}".format(1/1000 *osl.knee.battery_voltage ))
                raise ValueError("Battery voltage below 32 V")
            
            # Check if it's time to change the current (2 seconds passed)
            if test_timer.is_done:
                if len(test_conditions) == 0:
                    osl.knee.set_current(0.0)
                    osl.clock.stop()
                    print("Test complete :)")
                elif check_ankle_status():
                    cur_current_command = 0.0
                    print("waiting for ankle_motor to cool down")
                elif not motor_below_temp_thresh:
                    cur_current_command = 0.0
                    print("Max winding temp {:.2f} C. Cooling...".format(winding_temp),end='\r')

                else:
                    active_test_conditions = test_conditions.pop(0)
                    cur_current_command = active_test_conditions[1]
                    test_index += 1  # Move to the next current point
                    print("Starting test {} of {} with {} amps.".format(test_index, total_conditions,cur_current_command))
                    test_timer.start(TEST_DURATION_S)
            else:
                pass
            osl.knee.set_current(cur_current_command*1000.0) 
            # osl.log.info(f"{cur_current_command*1000}, {osl.knee.motor_current}")   
        
if __name__ == '__main__':

    start_time = time.time()
    #current_points = [1, 2, 3, 4, 5]  # List of current points
    current_setpoints = np.linspace(0, 5, 5)  # Example current setpoints (0A to 5A)
    voltage_setpoints = np.linspace(0, 10, 5)  # Example voltage setpoints (0V to 20V)

    # Generate unique (voltage, current) pairs (both positive and negative)
    test_conditions = list(set(itertools.product(
        np.concatenate([voltage_setpoints, -voltage_setpoints]), 
        np.concatenate([current_setpoints, -current_setpoints])
        )))
    
    test_timer = SimpleTimer()
    osl = OpenSourceLeg(frequency=300, file_name='New_Actpack9to1_Characterization_knee_'+strftime("%y%m%d_%H%M%S"))
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

    temp_thread = threading.Thread(target=check_knee_temperature, daemon=True)
    temp_thread.start()

    knee_thread = threading.Thread(target=control_knee, args=(osl, test_conditions))
    knee_thread.start()
    knee_thread.join()
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Print the elapsed time
    print(f"Total execution time: {elapsed_time:.2f} seconds")
