import pandas as pd
import numpy as np

# Load the CSV
file_path = "test_updated_knee_current_static250405_070238.csv"  # Replace with your file path
df = pd.read_csv(file_path)

# Parameters
f_g = 0.008     # Nm/A
GEAR_RATIO = 9  # Gear ratio

# Column names
torque_col = "torque"
current_col = "knee[DephyActpack]:motor_current"   # in mA
velocity_col = "knee[DephyActpack]:motor_velocity"

# Convert current from mA to A
I = df[current_col].values * 1e-3  # Now in A

# Compute sign of velocity (sgn(theta_dot))
sgn_velocity = np.sign(df[velocity_col].values)

# Compute absolute current * sign of velocity
I_abs_sgn = np.abs(I) * sgn_velocity

# Compute torque adjustment
torque_adjusted = df[torque_col].values - (f_g * GEAR_RATIO) * I_abs_sgn

# Add new column to dataframe
df["torque_adjusted"] = torque_adjusted

# Save modified CSV
df.to_csv("adjusted_torque_output_2.0.csv", index=False)

print("Adjusted torque column added and saved to 'adjusted_torque_output.csv'")
