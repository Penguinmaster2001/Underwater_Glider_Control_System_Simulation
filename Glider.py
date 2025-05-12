
from abc import ABC, abstractmethod
from typing import List

from ControlSystem import ControlSystem

import SimMath
from SimMath import Vector

import Inlet

import numpy as np



# TODO: Use interfaces or abandon OOP

class GliderComponent(ABC):

    @abstractmethod
    def compute_drag_force(self, local_flow: Vector) -> Vector:
        return Vector()

    @abstractmethod
    def compute_lift_force(self, local_flow: Vector) -> Vector:
        return Vector()



    @property
    def mass(self) -> float:
        return self._mass
    

    @mass.setter
    def mass(self, value: float) -> None:
        self._mass = value



    @property
    def buoyancy_volume(self) -> float:
        return self._buoyancy_volume
    
    
    @buoyancy_volume.setter
    def buoyancy_volume(self, value: float) -> None:
        self._buoyancy_volume = value
    


    @property
    def position(self) -> Vector:
        return self._position
    
    
    @position.setter
    def position(self, value: Vector) -> None:
        self._position = value





class GliderBody(GliderComponent):
    """
    Represents the body of a glider. It is a capsule.

    Attributes:
        mass (float): The mass of the glider body.
        volume (float): The volume of the glider body.
        drag_multiplier (float): The drag coefficient of the glider body.
        max_force (float): The maximum force that can be applied to the glider body.

    Methods:
        compute_acceleration(applied_force: Vector) -> Vector:
            Computes the acceleration of the glider body based on the applied force.
        compute_drag_force(velocity: Vector) -> Vector:
            Computes the drag force acting on the glider body based on its velocity.
        compute_buoyancy_force() -> Vector:
            Computes the buoyancy force acting on the glider body.
        compute_gravity_force() -> Vector:
            Computes the gravity force acting on the glider body.
    """

    def __init__(self, mass: float, length: float, radius: float, drag_multiplier: float) -> None:
        
        self._mass: float = mass
        self._position: Vector = Vector()

        self.length: float = length
        self.radius: float = radius

        # Volume of the cylinder + volume of the two hemispheres
        self.volume: float = (SimMath.pi * length * radius * radius)\
                           + ((4.0 / 3.0) * SimMath.pi * radius * radius * radius)
        
        self._buoyancy_volume: float = self.volume
        

        self.drag_multiplier: float = drag_multiplier


        self.front_area: float = SimMath.pi * self.radius * self.radius
        self.side_area: float = 2.0 * self.radius * self.length


        self.front_drag_coefficient = 0.4
        self.side_drag_coefficient = 1.2



    def compute_drag_force(self, local_flow: Vector) -> Vector:
        """
        Computes the drag force acting on the glider body based on its velocity.

        Args:
            velocity (Vector): The velocity of the glider body.

        Returns:
            Vector: The drag force acting on the glider body.
        """

        # Calculate drag in each direction
        # The glider's top and side are the same
        # The sign term is important because squaring the velocity removes direction
        front_drag = SimMath.sign(local_flow.x()) * self.front_area * self.front_drag_coefficient * (local_flow.x() ** 2)
        side_drag = SimMath.sign(local_flow.y()) * self.side_area * self.side_drag_coefficient * (local_flow.y() ** 2)
        top_drag = SimMath.sign(local_flow.z()) * self.side_area * self.side_drag_coefficient * (local_flow.z() ** 2)

        # Drag equation
        local_drag = Vector(front_drag, side_drag, top_drag) * (0.5 * Inlet.density)
        
        return local_drag * self.drag_multiplier
    


    def compute_lift_force(self, local_flow: Vector) -> Vector:
        return super().compute_lift_force(local_flow)





class BuoyancyEngine(GliderComponent):
    """
    The BuoyancyEngine class represents an engine that calculates buoyancy and gravity forces for a tank.

    Attributes:
        tank_volume (float): The volume of the tank.
        pump_rate (float): The rate at which the tank is being pumped.
        proportion_full (float): The proportion of the tank that is filled.

    Methods:
        compute_tank_change(time_step: float) -> None:
            Computes the change in tank proportion based on the pump rate and time step.

        compute_buoyancy_force() -> Vector:
            Computes the buoyancy force based on the tank volume and proportion full.

        compute_gravity_force() -> Vector:
            Computes the gravity force based on the tank volume and proportion full.
    """

    def __init__(self, tank_volume: float, initial_proportion_full: float,
                  initial_pump_rate: float, max_pump_rate: float,
                  position: dict) -> None:
    
        self.tank_volume: float = tank_volume
        self.proportion_full: float = initial_proportion_full
        self.ballast_volume: float = self.tank_volume * self.proportion_full
        self._buoyancy_volume: float = self.tank_volume - self.ballast_volume

        self.pump_rate: float = initial_pump_rate
        self.max_pump_rate: float = max_pump_rate

        self._position: Vector = Vector(**position)
        self._mass: float = 0.0



    def compute_tank_change(self, time_step: float) -> None:
        """
        Computes the change in tank proportion based on the pump rate and time step.

        Args:
            time_step (float): The time step for the computation.
        """

        self.pump_rate = SimMath.clamp_mag(self.pump_rate, self.max_pump_rate)
        
        self.proportion_full = SimMath.clamp(self.proportion_full + (self.pump_rate * time_step), 0, 1)

        self.mass = self.proportion_full * self.tank_volume * Inlet.density

        self.ballast_volume = self.tank_volume * self.proportion_full
        self.buoyancy_volume = self.tank_volume - self.ballast_volume



    def compute_drag_force(self, local_flow: Vector) -> Vector:
        return super().compute_drag_force(local_flow)
    

    def compute_lift_force(self, local_flow: Vector) -> Vector:
        return super().compute_lift_force(local_flow)





class Hydrofoil(GliderComponent):

    def __init__(self, reference_area: float, lift_multiplier: float,
                 lift_curve_slope: float, stall_angle: float,
                 position: dict,
                 drag_multiplier: float, mass: float) -> None:
        
        self.reference_area: float = reference_area

        self.lift_multiplier: float = lift_multiplier

        self.lift_curve_slope: float = lift_curve_slope

        self.stall_angle: float = stall_angle

        self._position: Vector = Vector(**position)
        self._mass: float = mass

        self.drag_multiplier = drag_multiplier

        # The drag on the front and side is negligible
        self.front_area: float = 0.0
        self.side_area: float = 0.0
        self.top_area: float = reference_area


        self.front_drag_coefficient = 0.04
        self.side_drag_coefficient = 1.2

        self._buoyancy_volume = 0.0



    def compute_drag_force(self, local_flow: Vector) -> Vector:
        """
        Computes the drag force acting on the glider body based on its velocity.

        Args:
            velocity (Vector): The velocity of the glider body.

        Returns:
            Vector: The drag force acting on the glider body.
        """

        # Calculate drag in each direction
        # The glider's top and side are the same
        # The sign term is important because squaring the velocity removes direction
        front_drag = SimMath.sign(local_flow.x()) * self.front_area * self.front_drag_coefficient * (local_flow.x() ** 2)
        side_drag = SimMath.sign(local_flow.y()) * self.side_area * self.side_drag_coefficient * (local_flow.y() ** 2)
        top_drag = SimMath.sign(local_flow.z()) * self.side_area * self.side_drag_coefficient * (local_flow.z() ** 2)

        # Drag equation
        local_drag = Vector(front_drag, side_drag, top_drag) * (0.5 * Inlet.density)
        
        return local_drag * self.drag_multiplier

    

    def compute_lift_coefficient(self, angle_of_attack: float) -> float:

        lift_coefficient = 0.0

        angle = abs(angle_of_attack)

        if angle < self.stall_angle:
            lift_coefficient = self.lift_curve_slope * angle
        
        elif angle < 0.7854: # pi / 4
            lift_coefficient = SimMath.lerp(self.lift_curve_slope * self.stall_angle, 0.0, angle - self.stall_angle)
        
        return SimMath.sign(angle_of_attack) * lift_coefficient
    


    def compute_lift_force(self, local_flow: Vector) -> Vector:

        dynamic_pressure = 0.5 * Inlet.density * local_flow.dot(local_flow)

        angle_of_attack = np.arctan2(local_flow.z(), -local_flow.x())

        lift_coefficient = self.compute_lift_coefficient(angle_of_attack)

        local_lift = Vector(z = lift_coefficient * dynamic_pressure * self.reference_area)

        return local_lift * self.lift_multiplier






class Glider:
    """
    Represents a glider object.

    Attributes:
        body (GliderBody): The body of the glider.
        buoyancy_engine (BuoyancyEngine): The buoyancy engine of the glider.
        control_system (ControlSystem): The control system of the glider.
        position (Vector): The position of the glider.
        velocity (Vector): The velocity of the glider.
        acceleration (Vector): The acceleration of the glider.
        orientation (Vector): The direction the glider is pointing.
        time (float): The current time of the glider simulation.

    Methods:
        integrate_forces(time_step: float) -> None:
            Integrates the forces acting on the glider over a given time step.

        sim_timestep(time: float) -> None:
            Simulates a time step for the glider.

    """

    def __init__(self, body: GliderBody, buoyancy_engine: BuoyancyEngine, hydrofoil: Hydrofoil,
                 control_system: ControlSystem,
                 initial_position: Vector, initial_velocity: Vector, initial_acceleration: Vector,
                 initial_orientation: Vector, initial_angular_velocity: Vector, initial_angular_acceleration: Vector
                 ) -> None:
        """
        Initializes a glider object.

        Args:
            body (GliderBody): The body of the glider.
            buoyancy_engine (BuoyancyEngine): The buoyancy engine of the glider.
            control_system (ControlSystem): The control system of the glider.
            initial_position (Vector): The initial position of the glider.
            initial_velocity (Vector): The initial velocity of the glider.
            initial_acceleration (Vector): The initial acceleration of the glider.
        """
        
        self.body: GliderBody = body
        self.buoyancy_engine: BuoyancyEngine = buoyancy_engine
        self.hydrofoil: Hydrofoil = hydrofoil

        self.body.buoyancy_volume -= self.buoyancy_engine.tank_volume

        self.components: List[GliderComponent] = [self.body, self.buoyancy_engine, self.hydrofoil]

        self.control_system: ControlSystem = control_system

        self.position: Vector = initial_position
        self.velocity: Vector = initial_velocity
        self.acceleration: Vector = initial_acceleration
        
        # Euler angles
        self.orientation: Vector = initial_orientation
        self.angular_velocity: Vector = initial_angular_velocity
        self.angular_acceleration: Vector = initial_angular_acceleration

        # TODO: This should be a component-wise computation
        self.moment_of_inertia: Vector = Vector(0.5 * self.body.radius ** 2,
                                               (1.0 / 12.0) * ((3.0 * self.body.radius ** 2) + (self.body.length ** 2)),
                                               (1.0 / 12.0) * ((3.0 * self.body.radius ** 2) + (self.body.length ** 2)))

        self.time: float = 0.0



    def integrate_forces(self, time_step: float) -> None:
        """
        Integrates the forces acting on the glider over a given time step.

        Args:
            time_step (float): The time step for the integration.
        """

        # Calculate everything in the glider's local frame of reference
        rotation_matrix = SimMath.euler_to_rotation_matrix(self.orientation)

        # Local acceleration due to gravity
        local_gravity = Vector()
        local_gravity.vec = np.dot(rotation_matrix.T, Inlet.gravity.vec)

        # Flow of water over the glider
        local_flow = Vector()
        local_flow.vec = -np.dot(rotation_matrix.T, self.velocity.vec)


        # Forces
        center_of_linear_drag = Vector()
        total_linear_drag = Vector()
        total_linear_drag_magnitude = 0.0

        center_of_lift = Vector()
        total_lift = Vector()
        total_lift_magnitude = 0.0

        center_of_mass = Vector()
        total_mass = 0.0

        center_of_volume = Vector()
        total_volume = 0.0


        for component in self.components:

            # Vector quantities
            component_drag = component.compute_drag_force(local_flow)
            center_of_linear_drag += component.position * component_drag.magnitude()
            total_linear_drag += component_drag
            total_linear_drag_magnitude += component_drag.magnitude()

            component_lift = component.compute_lift_force(local_flow)
            center_of_lift += component.position * component_lift.magnitude()
            total_lift += component_lift
            total_lift_magnitude += component_lift.magnitude()

            # Scalar quantities
            center_of_mass += component.position * component.mass
            total_mass += component.mass

            center_of_volume += component.position * component.buoyancy_volume
            total_volume += component.buoyancy_volume


        if total_linear_drag_magnitude > 0.0:
            center_of_linear_drag /= total_linear_drag_magnitude

        if total_lift_magnitude > 0.0:
            center_of_lift /= total_lift_magnitude

        if total_mass > 0.0:
            center_of_mass /= total_mass

        if total_volume > 0.0:
            center_of_volume /= total_volume


        total_gravity = local_gravity * total_mass

        total_buoyancy = local_gravity * (-1.0 * Inlet.density * total_volume)

        total_lift = self.hydrofoil.compute_lift_force(local_flow)

        total_force = total_buoyancy + total_linear_drag + total_gravity + total_lift


        world_force = Vector()
        world_force.vec = np.dot(rotation_matrix, total_force.vec)
        

        self.acceleration = world_force / total_mass
        self.velocity += self.acceleration * time_step
        self.position += self.velocity * time_step


        # Torques

        # Center of mass is the pivot point


        # Buoyancy
        buoyancy_torque = (center_of_volume - center_of_mass).cross(total_buoyancy)


        # Drag
        drag_torque = (center_of_linear_drag - center_of_mass).cross(total_linear_drag)

        # Simplified model TODO: Make more accurate
        angular_drag_torque = self.angular_velocity * (-1 * 2.0)


        # Lift
        center_of_lift = self.hydrofoil.position

        lift_torque = (center_of_lift - center_of_mass).cross(total_lift)


        total_torque = buoyancy_torque + drag_torque + angular_drag_torque + lift_torque


        mass_moment = self.moment_of_inertia * total_mass

        # Parallel axis theorem TODO: Component-wise computation
        moment = Vector(mass_moment.x() + total_mass * center_of_mass.x() ** 2,
                        mass_moment.y() + total_mass * center_of_mass.y() ** 2,
                        mass_moment.z() + total_mass * center_of_mass.z() ** 2)

        self.angular_acceleration = Vector(total_torque.x() / moment.x(),
                                           total_torque.y() / moment.y(),
                                           total_torque.z() / moment.z())
        
        self.angular_velocity += self.angular_acceleration * time_step

        ### HARD CODE TO KEEP PITCH AT ZERO
        #  Keep pitch at zero
        self.orientation.y(0.0)
        self.angular_velocity.y(0.0)
        self.angular_acceleration.y(0.0)

        self.orientation = (self.orientation + (self.angular_velocity * time_step)).loop(-SimMath.pi, SimMath.pi)




    
    
    def sim_timestep(self, time: float) -> None:
        """
        Simulates a time step for the glider.

        Args:
            time (float): The time for the simulation.
        """

        time_step = time - self.time

        self.time = time

        command = self.control_system.calc_acc(self.position, self.velocity, self.acceleration,
                                               self.buoyancy_engine.proportion_full, time,
                                               [self.orientation.x(), self.orientation.y(), self.orientation.z(),
                                                self.angular_velocity, self.angular_acceleration])

        self.buoyancy_engine.pump_rate = command

        self.buoyancy_engine.compute_tank_change(time_step)

        self.integrate_forces(time_step)

        # The Glider cannot leave the water
        if self.position.z() > 0:
            self.position.z(-0.1)

            if self.velocity.z() > 0:
                self.velocity.z(0)
            
            if self.acceleration.z() > 0:
                self.acceleration.z(0)

        # It cannot go too deep either
        if self.position.z() < -200:
            self.position.z(-199.9)

            if self.velocity.z() < 0:
                self.velocity.z(0)
            
            if self.acceleration.z() < 0:
                self.acceleration.z(0)
