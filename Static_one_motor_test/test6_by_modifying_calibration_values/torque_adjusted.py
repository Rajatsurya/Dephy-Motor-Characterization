import pandas as pd
import numpy as np 

# Load your CSV file
df = pd.read_csv("test_updated_knee_current_static250405_070238.csv")  # Replace with your actual filename

# Make sure the column names match your CSV
# Let's assume your torque column is named 'torque' and current column is 'current'

# Define gear friction constant
fg = 0.02  # Nm/A
gear_ratio = 9
fc = 0.007

# Calculate adjusted torque
df['torque_adjusted'] = (df['torque']) - ((fg * gear_ratio )*((df['knee[DephyActpack]:motor_current']))* 1e-3) + (gear_ratio*fc)

# Optionally, save to a new CSV
df.to_csv("adjusted_torque_output.csv", index=False)

print("Adjusted torque column added and saved to 'adjusted_torque_output.csv'")
