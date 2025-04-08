from .controller import BaseController


class LTLSafeController(BaseController):
    def __init__(self, env):
        # Safety threshold constants (based on LTL specs and environment limits)
        self.MAX_TILT = 0.4        # maximum allowed tilt angle in radians (~22°) to avoid flip
        self.MAX_X   = 0.9        # maximum allowed horizontal displacement (env fails at |x| > 1)
        self.MAX_DESCENT_SPEED = 1.0   # max safe downward speed (vertical velocity) far from ground
        self.SAFE_DESCENT_SPEED = 0.5  # stricter downward speed when close to ground (for soft landing)

    def control(self, state):
        """
        Decide on a control action (0,1,2,3) based on the current state to ensure safety.
        state format: [x, y, v_x, v_y, angle, angular_velocity, leg1_contact, leg2_contact]
        """
        x, y, v_x, v_y, angle, angular_vel, leg1, leg2 = state

        # If already landed (both legs on ground) and nearly zero velocity, keep engines off (stay landed).
        if leg1 and leg2 and v_y >= -self.SAFE_DESCENT_SPEED and abs(v_x) < 1e-1:
            return 'terminate'  # Safe touchdown achieved, no further action

        # Enforce horizontal bounds (LTL: G |x| < 1).
        if x > self.MAX_X:
            # Too far to the right, fire right engine to push left (and tilt left).
            return 3  # action 3 = right orientation thruster
        if x < -self.MAX_X:
            # Too far to the left, fire left engine to push right (and tilt right).
            return 1  # action 1 = left orientation thruster

        # Enforce tilt bound (LTL: G |θ| < θ_max).
        if angle > self.MAX_TILT:
            # Lander tilted clockwise beyond limit; fire right engine to correct (rotate counter-clockwise).
            return 3  # right thruster to reduce angle
        if angle < -self.MAX_TILT:
            # Lander tilted counter-clockwise beyond limit; fire left engine to correct (rotate clockwise).
            return 1  # left thruster to reduce angle

        # Enforce controlled descent speed (LTL: G v_y > -V_max).
        if y < 0.2:
            # Near the ground – require very slow descent for soft landing.
            if v_y < -self.SAFE_DESCENT_SPEED:
                # Descending too fast when about to land; fire main engine to slow down.
                return 2  # action 2 = main engine (upward thrust)
        else:
            # Higher altitude – limit fall speed to MAX_DESCENT_SPEED.
            if v_y < -self.MAX_DESCENT_SPEED:
                # Falling too quickly; fire main engine to reduce speed.
                return 2  # main engine thrust

        # If none of the safety conditions are violated, do nothing (LTL: if safe then no thrust).
        # This conserves fuel and maintains stability.
        return 0  # action 0 = no engine fire
        return 0  # action 0 = no engine fire
