import subprocess
import signal
import sys

# Running both scripts in parallel

process1 = subprocess.Popen(['python', '/home/pi/MBLUE_PEA_based_on_osl_v3_testbed/control_ankle_voltage_main.py'])
process2 = subprocess.Popen(['python', '/home/pi/MBLUE_PEA_based_on_osl_v3_testbed/control_knee_current_main.py'])

# Define a signal handler to catch Ctrl+C (KeyboardInterrupt)
def terminate_processes(signal, frame):
    print("Terminating both scripts...")
    process1.terminate()  # Terminate the first script
    process2.terminate()  # Terminate the second script
    sys.exit(0)

# Set up the signal handler for Ctrl+C
signal.signal(signal.SIGINT, terminate_processes)

# Keep the program running until Ctrl+C is pressed
print("Both scripts are running. Press Ctrl+C to stop them.")
signal.pause()  # Wait for signals (like Ctrl+C)

