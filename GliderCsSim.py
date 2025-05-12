
import matplotlib.pyplot as plt

import numpy as np

import csv

import json

import sys

import Glider
import ControlSystem
import SimMath
from SimMath import Vector





    
def load_config(file_path: str) -> dict:
    """
    Load a configuration file and return the configuration as a dictionary.

    Args:
        file_path (str): The path to the configuration file.

    Returns:
        dict: The configuration loaded from the file.
    """
    
    with open(file_path, 'r') as file:
        config = json.load(file)
    
    return config





def do_sim() -> None:
    """
    Runs the glider simulation.

    This function sets up the glider simulation by initializing the glider body, buoyancy engine,
    control system, and other necessary parameters. It then runs the simulation for a specified
    duration of time, updating the glider's position, velocity, and acceleration at each time step.
    Finally, it creates a plot of the glider's variables and displays it.

    It is one big function that does too many things
    TODO: It too big

    Args:
        None

    Returns:
        None
    """

    # Get the config path
    config_path = None
    for arg in sys.argv:
        if arg.endswith(".json"):
            config_path = arg

    if config_path is None:
        print(f"Usage: {''.join(sys.argv)} /path/to/config.json")

        while config_path is None:
            arg = input("Please enter config path: ")

            if arg.endswith(".json"):
                config_path = arg

    
    config = load_config(config_path)

    glider_config = config["glider"]


    print("Setting Up")

    glider = Glider.Glider(body = Glider.GliderBody(**glider_config["hull"]),
                           buoyancy_engine = Glider.BuoyancyEngine(**glider_config["buoyancy_engine"]),
                           hydrofoil = Glider.Hydrofoil(**glider_config["hydrofoil"]),
                           control_system = ControlSystem.ControlSystem(glider_config["control_system"]),
                           initial_position = Vector(**glider_config["initial_position"]),
                           initial_velocity = Vector(**glider_config["initial_velocity"]),
                           initial_acceleration = Vector(**glider_config["initial_acceleration"]),
                           initial_orientation = Vector(**glider_config["initial_orientation"]),
                           initial_angular_velocity = Vector(**glider_config["initial_angular_velocity"]),
                           initial_angular_acceleration = Vector(**glider_config["initial_angular_acceleration"]))
    

    sim_config = config["sim"]

    time: float = 0.0

    time_step: float = sim_config["timestep"]

    max_time: float = sim_config["end_time"]


    print("Setup Done")
    print("Running Simulation")
    while time < max_time:

        glider.sim_timestep(time)

        time += time_step

    print("Simulation Done")

    print("Creating Plot")
    
    glider_log = np.array(glider.control_system.logger.glider_log)
    control_log = np.array(glider.control_system.logger.control_log)


    # Downsample the data to 24 FPS
    sampling_rate = 100  # Original sampling rate (100 Hz)
    target_rate = 24  # Target sampling rate (24 FPS)
    downsample_factor = sampling_rate // target_rate

    glider_log_downsampled = glider_log[::downsample_factor]
    control_log_downsampled = control_log[::downsample_factor]


    # Export glider_log to CSV
    with open('animation/glider_log.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['time', 'position_x', 'position_y', 'position_z', "velocity", "acceleration", "tank*1e1", 'roll', 'pitch', 'yaw'])
        for row in glider_log_downsampled:
            writer.writerow(row)

    # Export control_log to CSV
    with open('animation/control_log.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['time', 'control_input'])
        for row in control_log_downsampled:
            writer.writerow(row)
    

    glider_time = [row[0] for row in glider_log]
    glider_x_components = [row[1] for row in glider_log]
    glider_y_components = [row[2] for row in glider_log]
    glider_z_pos = [row[3] for row in glider_log]
    glider_z_vel = [row[4].z() for row in glider_log]
    glider_z_acc = [row[5].z() for row in glider_log]

    glider_roll = [row[7] * 180.0 / SimMath.pi for row in glider_log]
    glider_pitch = [row[8] * 180.0 / SimMath.pi for row in glider_log]
    glider_yaw = [row[9] * 180.0 / SimMath.pi for row in glider_log]
    # glider_pitch_vel = [row[6].y() * 180.0 / SimMath.pi for row in glider_log]
    # glider_pitch_acc = [row[7].y() * 180.0 / SimMath.pi for row in glider_log]

    glider_tank = [row[6] for row in glider_log]  # Extracting z components

    control_time = [row[0] for row in control_log]
    control_vars = list(zip(*control_log))[1:]
    control_labels = ["target depth", "depth pid", "vel pid", "acc pid"]

    # Create a new figure for the x-y plot
    plt.figure()
    sc = plt.scatter(glider_x_components, glider_y_components, c = glider_time, cmap = "viridis")
    plt.xlabel("X Component")
    plt.ylabel("Y Component")
    plt.legend(loc="lower left")
    plt.axis('equal')  # Automatic scaling
    plt.title("X vs Y Components")
    plt.grid(True)
    plt.colorbar(sc, label="Time")
    plt.show()

    # Create subplots for the remaining plots
    fig, axs = plt.subplots(3, 1, sharex=True)

    # Plotting z components against time
    axs[1].plot(glider_time, glider_z_pos, label="pos")
    axs[1].plot(glider_time, glider_z_vel, label="vel")
    axs[1].plot(glider_time, glider_z_acc, label="acc")

    axs[0].plot(glider_time, glider_roll, label="roll")
    axs[0].plot(glider_time, glider_pitch, label="pitch")
    axs[0].plot(glider_time, glider_yaw, label="yaw")

    axs[1].plot(glider_time, glider_tank, label = "tank*1e1")
    
    axs[1].set_ylabel("Z Component")
    axs[1].legend(loc="lower left")
    axs[0].legend(loc="lower left")

    # Plotting control variables
    for i, var in enumerate(control_vars):
        axs[2].plot(control_time, var, label=control_labels[i])

    axs[2].set_ylabel("Control")
    axs[2].legend(loc="lower left")

    fig.supxlabel("Time")
    plt.title(f"Glider Dynamics")
    plt.grid(True)

    print("Plot Created")

    print("Showing Plot")
    plt.show()

    print("Plot Exited")
    print("Finished!")




if __name__ == "__main__":
    do_sim()
