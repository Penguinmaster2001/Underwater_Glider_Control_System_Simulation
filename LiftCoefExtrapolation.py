
import sys
import SimMath
import json

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d, CubicSpline




wing_data: dict
angles: np.ndarray
coefficients_of_lift: np.ndarray
coefficients_of_drag: np.ndarray



def sample_angle(angle: float) -> tuple[float, float]:
    global coefficients_of_lift, coefficients_of_drag

    angle %= 2.0 * np.pi

    return (0.0, 0.0)



def load_wing_data() -> None:
    global wing_data, angles, coefficients_of_lift, coefficients_of_drag

    config = SimMath.load_config()
    wing_data_path = config["glider"]["hydrofoil"]["data_path"]
    with open(wing_data_path, 'r') as file:
        wing_data = json.load(file)

    angles = np.array([angle * SimMath.deg_to_rad for angle in reversed(wing_data["angles"])])
    coefficients_of_lift = np.array([c for c in reversed(wing_data["coefficients_of_lift"])])
    coefficients_of_drag = np.array([c for c in reversed(wing_data["coefficients_of_drag"])])



def extrapolate_wing_data() -> None:
    '''
    Extrapolate the data from [0, pi / 2] to [-pi, pi]
    '''
    global wing_data, angles, coefficients_of_lift, coefficients_of_drag

    angles = np.linspace(-np.pi, np.pi, (9 * 4) + 1)
    coefficients_of_drag = np.array([c for c in coefficients_of_drag]
                                  + [c for c in reversed(coefficients_of_drag)][1:]
                                  + [c for c in coefficients_of_drag][1:]
                                  + [c for c in reversed(coefficients_of_drag)][1:])
    
    '''
    drag_list = [c for c in coefficients_of_drag]
    drag_list.extend([c for c in reversed(coefficients_of_lift)][1:])
    drag_list.extend([c for c in coefficients_of_drag][1:])
    drag_list.extend([c for c in reversed(coefficients_of_lift)][1:])
    coefficients_of_drag = np.array(drag_list)
    '''






'''
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
'''


def plot_extrapolation(num: int) -> None:
    global wing_data, angles, coefficients_of_lift, coefficients_of_drag

    interp_angles = np.linspace(-np.pi, np.pi, num)

    lin_interp = interp1d(angles, coefficients_of_drag)
    lin_drag = lin_interp(interp_angles)

    cub_interp = CubicSpline(angles, coefficients_of_drag)
    cub_drag = cub_interp(interp_angles)
    
    plt.figure(figsize = (10, 6))
    # plt.plot(angles, coefficients_of_lift, 'o', label='Lift Coefs')
    plt.plot(angles, coefficients_of_drag, '-', label='Drag Coefs')
    plt.plot(interp_angles, lin_drag, '-', label='Drag Coefs Lin Interp')
    plt.plot(interp_angles, cub_drag, '-', label='Drag Coefs Cub Interp')
    plt.xlabel('Angle (radians)')
    plt.ylabel('Drag Coefficients Interpolations')
    plt.title('Extrapolated Data for Lift Coefficient over -π to π Radians')
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    
    print(f"{sys.argv[0]} run directly")

    load_wing_data()

    extrapolate_wing_data()

    plot_extrapolation(500)


