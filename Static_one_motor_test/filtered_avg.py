import pandas as pd

# Load the CSV file
df = pd.read_csv("test_updated_knee_current_static250405_070238.csv")

# Define peak values in milliamps with a small tolerance
peak_values_milliamps = {
    '2.5A': (2400, 2600),
    '-2.5A': (-2600, -2400),
    '5A': (4900, 5100),
    '-5A': (-5100, -4900),
    '7.5A': (7400, 7600),
    '-7.5A': (-7600, -7400),
    '10.0A': (9900, 10100),
    '-10.0A': (-10100, -9900),
    '12.5A': (12400, 12600),
    '-12.5A': (-12600, -12400),
    '15.0A': (14900, 15100),
    '-15.0A': (-15100, -14900),
    '17.5A': (17400, 17600),
    '-17.5A': (-17600, -17400),
    '20.0A': (19900, 20100),
    '-20.0A': (-20100, -19900),
}

# Step 1: Filter and label data
filtered_df = pd.DataFrame()

for name, (lower, upper) in peak_values_milliamps.items():
    filtered_rows = df[(df['knee[DephyActpack]:motor_current'] >= lower) & 
                       (df['knee[DephyActpack]:motor_current'] <= upper)].copy()
    filtered_rows['peak_value'] = name
    filtered_df = pd.concat([filtered_df, filtered_rows], ignore_index=True)

# Step 2: Compute averages
avg_dict = filtered_df.groupby('peak_value')['knee[DephyActpack]:motor_current'].mean().to_dict()

# Step 3: Map the average back to each row
filtered_df['average_for_peak'] = filtered_df['peak_value'].map(avg_dict)

# Optional: Save to CSV
filtered_df.to_csv("filtered_with_peak_averages.csv", index=False)

# Display result
print(filtered_df.head())
