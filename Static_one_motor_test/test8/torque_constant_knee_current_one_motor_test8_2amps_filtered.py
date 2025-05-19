import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Input Data: 8-point average currents (in mA) and torques (in Nm)
I_mA = np.array([501.0752, -501.996, 1000.414, -1001.976,
                 1498.3356, -1502.49454545, 1998.6488, -1999.5648])
τ = np.array([-0.03390288, 0.04432542, -0.10980483, 0.11997644,
              -0.18901949, 0.21212171, -0.25539692, 0.24846055])

# Convert motor current from mA to A
I = I_mA * 1e-3  # mA to A

# Construct matrix A for regression model: [I, 1]
A = np.hstack((I.reshape(-1, 1), np.ones((len(I), 1))))

# Flip current sign if needed (optional based on convention)
A[:, 0] = -A[:, 0]

# Perform least squares regression to solve for α̂ = [K_t, b]
alpha_cap, _, _, _ = np.linalg.lstsq(A, τ, rcond=None)
K_t, b = alpha_cap

# Print results
print(f"Torque Constant (K_t): {K_t:.6f} Nm/A")
print(f"Bias (b): {b:.6f} Nm")

# Predicted torques using regression model
τ_predicted = A @ alpha_cap

# Residuals and metrics
residuals = τ - τ_predicted
SS_res = np.sum(residuals**2)
SS_tot = np.sum((τ - np.mean(τ))**2)
R_squared = 1 - (SS_res / SS_tot)
RMS_residual = np.sqrt(np.mean(residuals**2))
peak_torque = np.max(np.abs(τ))
RMS_residual_percent = (RMS_residual / peak_torque) * 100

print(f"Variance Accounted For (R^2): {R_squared:.3f}")
print(f"RMS Residual: {RMS_residual:.6f} Nm ({RMS_residual_percent:.2f}% of peak torque)")

# Plot measured vs predicted torque
plt.figure(figsize=(10, 6))
plt.scatter(I, τ, label="Measured Torque", color="blue", alpha=0.7)
plt.plot(I, τ_predicted, color="red", label="Fitted Line", linewidth=2)
plt.xlabel("Motor Current (A)")
plt.ylabel("Torque (Nm)")
plt.title("Torque vs Current (Linear Fit)")
plt.legend()
plt.grid()
plt.show()

# Residual plot
plt.figure(figsize=(10, 6))
plt.scatter(τ_predicted, residuals, color="purple", alpha=0.7)
plt.axhline(0, color="black", linestyle="--")
plt.xlabel("Predicted Torque (Nm)")
plt.ylabel("Residuals (Nm)")
plt.title("Residual Plot")
plt.grid()
plt.show()
