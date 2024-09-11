import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

# Generate synthetic data based on theoretical model
angles = np.linspace(0, 2 * np.pi, 100)
lift_coefficients = np.sin(angles)

# Add zeros at 0, pi/2, pi, 3pi/2, and 2pi to enforce symmetry
symmetric_angles = np.array([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi])
symmetric_lift_coefficients = np.sin(symmetric_angles)

# Combine the synthetic data with the symmetry points
combined_angles = np.concatenate((angles, symmetric_angles))
combined_lift_coefficients = np.concatenate((lift_coefficients, symmetric_lift_coefficients))

# Sort the data to ensure increasing order of angles
sorted_indices = np.argsort(combined_angles)
combined_angles = combined_angles[sorted_indices]
combined_lift_coefficients = combined_lift_coefficients[sorted_indices]

# Interpolation using cubic splines
spline = CubicSpline(combined_angles, combined_lift_coefficients)

# New angles from 0 to 2*pi
new_angles = np.linspace(0, 2 * np.pi, 200)
new_lift_coefficients = spline(new_angles)

# Plotting the results
plt.figure(figsize=(10, 6))
plt.plot(angles, lift_coefficients, 'o', label='Synthetic Data Points')
plt.plot(new_angles, new_lift_coefficients, '-', label='Spline Interpolated Data')
plt.xlabel('Angle (radians)')
plt.ylabel('Lift Coefficient')
plt.title('Synthetic Data for Lift Coefficient over 0 to 2π Radians')
plt.legend()
plt.grid(True)
plt.show()
