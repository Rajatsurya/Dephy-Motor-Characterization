import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
file_path = "New_Actpack9to1_Characterization_knee_250228_024002.csv"
df = pd.read_csv(file_path)

# Extract relevant columns
current_column = "knee[DephyActpack]:motor_current" 
torque_column = "torque"  


if current_column not in df.columns or torque_column not in df.columns:
    raise ValueError("Check column names in the CSV file!")

# Get current (I) and torque (τ) values
I_mA = df[current_column].values.reshape(-1, 1)  # Reshape for matrix operations
τ_volts = df[torque_column].values  # Torque values

I = I_mA * 1e-3  

calibartion_factor = 1
τ=τ_volts*calibartion_factor

# Create matrix A = [I, 1] for regression
A = np.hstack([I, np.ones_like(I)])

# Compute least squares solution α̂ = (AᵀA)⁻¹ AᵀY
alpha_cap = np.linalg.lstsq(A, τ, rcond=None)[0]

# Extract torque constant (K_t) and bias (b)
K_t, b = alpha_cap

# Print results
print(f"Torque Constant (K_t) Knee - current controlled: {K_t:.6f} Nm/A")
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




