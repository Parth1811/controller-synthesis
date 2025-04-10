import numpy as np

from .controller import BaseController


class LlamaController(BaseController):

    def __init__(self, env):
        """
        Controller class for the Lunar Lander environment.

        :param env: The Lunar Lander environment to control.
        """
        super().__init__(env)
        self.ltl_properties = {
            "always_safe_altitude": True,
            "never_crash": True,
            "avoid_large_velocity": True
        }

    def check_ltl_properties(self, observation):
        """
        Checks the current state against the defined LTL properties.

        :param observation: The current state of the environment.
        :return: A dictionary indicating whether each property is satisfied.
        """
        # Define thresholds for safe altitude and velocity
        safe_altitude_threshold = 10.0
        large_velocity_threshold = 5.0

        self.ltl_properties["always_safe_altitude"] = observation[1] > -safe_altitude_threshold
        self.ltl_properties["never_crash"] = not (observation[1] < -0.8)
        self.ltl_properties["avoid_large_velocity"] = np.abs(observation[2]) < large_velocity_threshold

    def control(self, observation):
        """
        Compute the next action based on the current state and LTL properties.

        :param observation: The current state of the environment.
        :return: An action to take in the environment.
        """
        # Check LTL properties
        self.check_ltl_properties(observation)

        # Compute the next action (example: prioritize landing safely)
        if not self.ltl_properties["always_safe_altitude"]:
            return 3  # Thrust down to increase altitude
        elif not self.ltl_properties["never_crash"] or not self.ltl_properties["avoid_large_velocity"]:
            return 0  # Apply no thrust and try to reduce velocity

        # If all properties are satisfied, apply a gentle landing strategy
        if observation[2] > -0.5:
            return 0  # No thrust, let the lander descend slowly
        else:
            return 3  # Apply minimal thrust to control descent

    def reset(self):
        """
        Resets the controller for a new episode.

        :return: None
        """
        self.ltl_properties = {
            "always_safe_altitude": True,
            "never_crash": True,
            "avoid_large_velocity": True
        }