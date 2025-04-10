from .controller import BaseController


class DeepSeekController(BaseController):
    def __init__(self, env):
        super().__init__(env)
        # Initialize any additional variables or parameters here
        self.prev_altitude = 0.0
        self.prev_velocity = 0.0

    def control(self, observation):
        """
        Basic control logic for the Lunar Lander environment.
        :param observation: The current state of the environment.
            Typically contains information like position, velocity, etc.
        :return: Action to take (e.g., apply thrust or not)
        """
        # Observation typically includes:
        # [x_position, y_position, x_velocity, y_velocity, angle, angular_velocity, left_leg_ground_contact, right_leg_ground_contact]

        # Example observation structure from LunarLander v2
        x_pos, y_pos, x_vel, y_vel, angle, ang_vel, leg_left, leg_right = observation

        # Simple safety checks and control logic
        action = 0  # Default action (no thrust)

        # LTL specification: Safety conditions
        # 1. Avoid crashing (ensure y_velocity is not too negative when close to ground)
        if y_pos < 0.2 and y_vel < -0.5:
            action = 1  # Apply thrust to prevent crash

        # 2. Maintain stable descent
        if abs(y_vel) > 5.0:
            action = 1  # Apply thrust if descending too quickly

        # 3. Avoid excessive angular velocity
        if abs(ang_vel) > 3.0:
            action = 1  # Apply thrust to stabilize rotation

        return action

    def is_safe(self, observation):
        """
        Check if the current state meets safety conditions.
        :param observation: The current state of the environment.
        :return: True if safe, False otherwise
        """
        x_pos, y_pos, _, y_vel, _, ang_vel, _, _ = observation

        # Safety condition 1: Not touching the ground except for landing
        if (y_pos < 0.1 and abs(y_vel) > 0.5):
            return False

        # Safety condition 2: Not exceeding maximum angular velocity
        if abs(ang_vel) > 4.0:
            return False

        # Additional safety conditions can be added here

        return True

    def reset(self):
        """
        Reset controller state when the episode is reset.
        """
        self.prev_altitude = 0.0
        self.prev_velocity = 0.0
