import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
file_path = "New_Actpack9to1_Characterization_ankle_250228_024845.csv"
df = pd.read_csv(file_path)

# Extract relevant columns
current_column = "ankle[DephyActpack]:motor_current"  # Update if needed
torque_column = "torque"  # Update if needed

# Ensure columns exist
if current_column not in df.columns or torque_column not in df.columns:
    raise ValueError("Check column names in the CSV file!")

# Get current (I) and torque (τ) values
I_mA = df[current_column].values.reshape(-1, 1)  # Reshape for matrix operations
τ = df[torque_column].values  # Torque in Nm

# Convert mA to A
I = I_mA * 1e-3  # Convert milliamps to amps

# Compute raw voltage from torque
raw_volts = (τ / 100) * 2.5 + 2.5

raw_volts_converted = (2*raw_volts)-5

conversion_factor = 1

new_τ = raw_volts_converted * conversion_factor

A = np.hstack([I, np.ones_like(I)])

# Compute (A^T A)
ATA = A.T @ A  # Matrix multiplication

# Compute (A^T Y)
ATY = A.T @ new_τ

# Compute the inverse of (A^T A)
ATA_inv = np.linalg.inv(ATA)

# Compute alpha_cap manually
alpha_cap = ATA_inv @ ATY  # Final solution


# Extract torque constant (K_t) and bias (b)
K_t, b = alpha_cap

# Print results
print(f"Torque Constant (K_t) for ankle - voltage controlled: {K_t:.6f} Nm/A")
print(f"Intercept (b): {b:.6f} Nm")

# Plot torque vs current with regression line
plt.scatter(I, τ, label="Measured Data", color="blue")
plt.plot(I, A @ alpha_cap, label=f"Fit: τ = {K_t:.4f}I + {b:.4f}", color="red")
plt.xlabel("Motor Current (A)")
plt.ylabel("Torque (Nm)")
plt.title("Torque vs Current (Linear Regression)")
plt.legend()
plt.grid()
plt.show()




