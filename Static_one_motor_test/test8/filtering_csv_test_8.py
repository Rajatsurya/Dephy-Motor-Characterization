import pandas as pd

# Load the CSV file
df = pd.read_csv("motor2_updated_ankle_current_static250407_053556.csv")

# Define peak values in milliamps with a small tolerance
important_ranges = [
 

    (11250, 13750),

    (36250, 38750),

    (65850, 68350),

    (91250, 93750),

    (120250, 122750),

    (148375, 151125),

    (179250, 181750),

    (203250, 205750)


]

important_df = pd.concat([df.iloc[start:end] for start, end in important_ranges])


# Save filtered data if needed
important_df.to_csv("filtered_motor_data_test_8.csv", index=False)

