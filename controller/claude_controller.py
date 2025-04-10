from abc import ABC, abstractmethod

import numpy as np

from .controller import BaseController


class ClaudeController(BaseController):
    def __init__(self, env):
        """
        Controller for the Lunar Lander environment guided by LTL specifications.

        LTL Specifications:
        1. G(altitude > 0) - Always maintain positive altitude until landing
        2. G(|angle| < π/6) - Always keep the lander's angle within safe bounds
        3. G(|velocity| < vmax) - Always keep velocity magnitude below maximum threshold
        4. F(landing_pad ∧ |velocity| < 0.5) - Eventually reach landing pad with safe velocity
        5. G(fuel > 0 → F(landing_pad)) - If fuel remains, eventually reach landing pad

        :param env: Lunar Lander environment
        """
        super().__init__(env)

        # Safety parameters
        self.max_angle = np.pi / 6  # Maximum safe angle (30 degrees)
        self.max_velocity = 1.0     # Maximum safe velocity
        self.safe_landing_velocity = 0.5  # Safe landing velocity

        # Control parameters
        self.altitude_gain = 1.0
        self.angle_gain = 5.0
        self.velocity_gain = 1.5
        self.position_gain = 0.8

    def control(self, observation):
        """
        Computes control action based on LTL specifications.

        Observation vector:
        [0] x position
        [1] y position (altitude)
        [2] x velocity
        [3] y velocity
        [4] angle
        [5] angular velocity
        [6] left leg contact
        [7] right leg contact

        Actions:
        0: Do nothing
        1: Fire left engine
        2: Fire main engine
        3: Fire right engine

        :param observation: Current state observation
        :return: Action to take (0-3)
        """
        # Extract relevant state variables
        x_pos = observation[0]
        altitude = observation[1]
        x_vel = observation[2]
        y_vel = observation[3]
        angle = observation[4]
        angular_vel = observation[5]
        left_contact = observation[6]
        right_contact = observation[7]

        # Check if we've landed (both legs in contact)
        landed = left_contact and right_contact
        if landed:
            return 0  # Do nothing if landed

        # Calculate control errors
        # For altitude: keep positive but aim to reach 0
        altitude_error = max(0.1 - altitude, 0) if altitude < 0.2 else 0

        # For horizontal position: aim for landing pad (x=0)
        position_error = -x_pos

        # For velocity: aim to slow down when approaching landing
        x_vel_error = -x_vel
        y_vel_error = min(0, -y_vel - self.safe_landing_velocity)

        # For angle: aim to keep upright
        angle_error = -angle

        # Determine action based on the most critical specification violation
        if altitude < 0.1 and y_vel < -0.5:
            # Specification 1 & 3: Altitude too low and falling too fast
            return 2  # Fire main engine

        elif abs(angle) > self.max_angle:
            # Specification 2: Angle too large
            if angle > 0:
                return 1  # Fire left engine to rotate counterclockwise
            else:
                return 3  # Fire right engine to rotate clockwise

        elif abs(x_vel) > self.max_velocity or abs(y_vel) > self.max_velocity:
            # Specification 3: Velocity too high
            if abs(x_vel) > abs(y_vel):
                # Horizontal velocity is the main concern
                if x_vel > 0:
                    return 1  # Fire left engine to slow down
                else:
                    return 3  # Fire right engine to slow down
            else:
                # Vertical velocity is the main concern
                if y_vel < -self.max_velocity:
                    return 2  # Fire main engine to slow descent

        # Handle approach to landing pad (Specification 4)
        if abs(x_pos) < 0.3:
            # Close to landing pad horizontally, focus on vertical descent
            if y_vel < -self.safe_landing_velocity:
                return 2  # Fire main engine to ensure soft landing
            else:
                return 0  # Let it descend naturally
        else:
            # Need to move horizontally to landing pad
            if x_pos > 0:
                return 1  # Fire left engine to move right to left
            else:
                return 3  # Fire right engine to move left to right

        # Default action
        return 0        # Default action
        return 0