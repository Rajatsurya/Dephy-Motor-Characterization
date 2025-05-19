import numpy as np
import pandas as pd

# Step 1: Load CSV
csv_file = 'motor2_updated_ankle_current_static250407_053556.csv'
data = pd.read_csv(csv_file)


# Step 3: Define Index Ranges
regions = [
    (11250, 13750),
    (36250, 38750),
    (65850, 68350),
    (91250, 93750),
    (120250, 122750),
    (148375, 151125),
    (179250, 181750),
    (203250, 205750)
]

# Step 4: Compute Averages
I_avg = []
τ_avg = []

for start, end in regions:
    I_avg.append(np.mean(I[start:end]))
    τ_avg.append(np.mean(τ[start:end]))

I_avg = np.array(I_avg)
τ_avg = np.array(τ_avg)

# Step 5: Display Results
print("Average Currents (A):", I_avg)
print("Average Torques (Nm):", τ_avg)
