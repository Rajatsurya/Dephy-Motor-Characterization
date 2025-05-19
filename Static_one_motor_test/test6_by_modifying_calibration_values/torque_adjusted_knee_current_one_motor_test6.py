import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
file_path = "adjusted_torque_output.csv"
df = pd.read_csv(file_path)

# Extract relevant columns
current_column = "knee[DephyActpack]:motor_current"  # Motor current (Iq)
torque_column = "torque_adjusted"  # Torque adjusted(τ)


# Ensure columns exist
if current_column not in df.columns or torque_column not in df.columns:
    raise ValueError("Check column names in the CSV file!")

# Extract data from columns
I_mA = df[current_column].values  # Motor current in milliamps
torque = df[torque_column].values  # Torque in volts (or Nm if calibrated)



# Convert motor current from mA to A
I = I_mA * 1e-3  # Convert milliamps to amps


# Convert torque from voltage to Nm (if necessary)
CALIBRATION_FACTOR = 1  # Update calibration factor if needed
GEAR_RATIO = 9 # Gear ratio for actuator setup
τ = (torque * CALIBRATION_FACTOR) / GEAR_RATIO

A = I.reshape(-1, 1)

K_t, _, _, _ = np.linalg.lstsq(A, τ, rcond=None)
K_t = K_t[0]  # Extract scalar

print(f"Torque Constant (K_t): {K_t:.6f} Nm/A")

# Validate model performance with metrics
τ_predicted = I * K_t  # Predicted torque values using regression model

# Residuals and variance accounted for (R^2)
residuals = τ - τ_predicted
SS_res = np.sum(residuals**2)  # Residual sum of squares
SS_tot = np.sum((τ - np.mean(τ))**2)  # Total sum of squares
R_squared = 1 - (SS_res / SS_tot)

# RMS residual as percentage of peak torque
RMS_residual = np.sqrt(np.mean(residuals**2))
peak_torque = np.max(np.abs(τ))
RMS_residual_percent = (RMS_residual / peak_torque) * 100

print(f"Variance Accounted For (R^2): {R_squared:.3f}")
print(f"RMS Residual: {RMS_residual:.3f} Nm ({RMS_residual_percent:.2f}% of peak torque)")

# Plot measured vs predicted torque
plt.figure(figsize=(10, 6))
plt.scatter(I, τ, label="Measured Data", color="blue", alpha=0.7)
plt.plot(I, τ_predicted, color="red", label="Regression Model")
plt.xlabel("Motor Current (A)")
plt.ylabel("Torque (Nm)")
plt.title("Torque vs Current (Regression Model)")
plt.legend()
plt.grid()
plt.show()

plt.figure(figsize=(10, 6))
plt.scatter(time, τ, label="Measured Data", color="blue", alpha=0.5, s=10, edgecolors='black')
plt.xlabel("Time (s)")
plt.ylabel("Torque (Nm)")
plt.title("Torque vs Time")
plt.legend()
plt.grid()
plt.show()

# Residual plot for further analysis
plt.figure(figsize=(10, 6))
plt.scatter(τ_predicted, residuals, color="purple", alpha=0.7)
plt.axhline(0, color="black", linestyle="--")
plt.xlabel("Predicted Torque (Nm)")
plt.ylabel("Residuals (Nm)")
plt.title("Residual Plot")
plt.grid()
plt.show()
