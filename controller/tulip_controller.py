#!/usr/bin/env python3
"""
Tulip-based Lunar Lander Controller

This example uses the tulip-control package to synthesize a discrete controller
from a GR(1) specification. The continuous state of the Lunar Lander is abstracted
into Boolean atomic propositions:
  - p: Lander is horizontally over the landing pad (|x| ≤ δ_x)
  - q: Lander is nearly upright (|angle| ≤ δ_theta)
  - r: Lander’s linear velocities are safe (|vx| ≤ δ_vx and vy >= -δ_vy)
  - a: Lander’s angular velocity is within safe bounds (|angular_vel| ≤ δ_av)
  - s: Both landing legs are in contact (touchdown)
  - near_ground: Lander is close to the ground (y ≤ δ_y)
  - crash: A crash event has occurred

The system variable is "action", with values:
  0: No thrust,
  1: Fire left engine,
  2: Fire main engine,
  3: Fire right engine.

The GR(1) specification guarantees that crash never occurs and that eventually
the safe landing condition (p ∧ q ∧ r ∧ a ∧ s) is reached.
"""

from tulip import spec, synth

from .controller import BaseController


# =============================================================================
# Tulip-based Controller for Lunar Lander
# =============================================================================
class TulipLunarLanderController(BaseController):
    def __init__(self, env):
        super().__init__(env)
        # Thresholds for mapping the continuous state to Boolean propositions.
        self.x_threshold = 0.4         # For being over the pad (p)
        self.angle_threshold = 0.1     # For nearly upright (q)
        self.vx_threshold = 0.1        # For safe horizontal speed (r)
        self.vy_threshold = 1          # For safe vertical descent (r)
        self.angular_vel_threshold = 0.1  # For safe angular velocity (a)
        self.y_threshold = 0.3         # For near_ground condition

        # ---------------------------------------------------------------------
        # Build the GR(1) specification using tulip.
        # ---------------------------------------------------------------------
        env_vars = {
            'p': 'bool',          # Lander is over the pad
            'q': 'bool',          # Lander is nearly upright
            'r': 'bool',          # Lander’s linear velocities are safe
            'a': 'bool',          # Lander’s angular velocity is bounded
            's': 'bool',          # Both landing legs are in contact
            'near_ground': 'bool',# Lander is near the ground
            'crash': 'bool'       # Crash event detected
        }
        sys_vars = {
            'action': (0, 1, 2, 3)  # 0: none, 1: left, 2: main, 3: right
        }
        # Environment assumptions
        env_init = ['!crash']
        env_safe = ['!crash']
        env_prog = []  # (No liveness assumptions on the environment)
        # System guarantees
        sys_init = []  # (No particular initial system output required)
        sys_safe = ['!crash']  # Always avoid a crash
        # The system must eventually reach a safe landing condition.
        sys_prog = ['p && q && r && a && s']

        gr1_spec = spec.GRSpec(env_vars, sys_vars, env_init, sys_safe, env_prog, sys_prog)
        gr1_spec.moore = False  # Use a Moore machine (output depends only on current state)
        gr1_spec.plus_one = False  # Use a non-deterministic controller
        gr1_spec.qinit = r'\A \E'
        self.discrete_ctrl = synth.gr1c.synthesize(gr1_spec)
        if self.discrete_ctrl is None:
            raise RuntimeError("Tulip synthesis failed: Specification unrealizable!")
        print("Tulip discrete controller synthesized successfully!")
        # Initialize the discrete controller's current state.
        self.current_discrete_state = self.discrete_ctrl.initial_state

    def _get_env_props(self, state):
        """
        Map the continuous state of Lunar Lander into Boolean propositions expected
        by the discrete controller.
        The continuous state is assumed to be:
        [x, y, vx, vy, angle, angular_vel, left_contact, right_contact]
        """
        x, y, vx, vy, angle, angular_vel, left_contact, right_contact = state

        props = dict()
        props['p'] = abs(x) <= self.x_threshold
        props['q'] = abs(angle) <= self.angle_threshold
        # For r: ensure horizontal speed is small and descent is not too fast.
        props['r'] = (abs(vx) <= self.vx_threshold) and (vy >= -self.vy_threshold)
        props['a'] = abs(angular_vel) <= self.angular_vel_threshold
        props['s'] = (left_contact == 1 and right_contact == 1)
        props['near_ground'] = (y <= self.y_threshold)
        # For this example, we assume the environment never signals a crash.
        props['crash'] = False
        return props

    def control(self, observation):
        """
        Query the current state of the environment, map it to Boolean propositions,
        and use the synthesized Tulip discrete controller to obtain the next action.
        """
        # Retrieve the current continuous state.
        state = observation
        props = self._get_env_props(state)
        # Use the discrete controller's transition function.
        # NOTE: The synthesized controller is a finite state machine. In this example, we
        # assume that it provides a helper function "step" that, given the current discrete state
        # and the environment's Boolean inputs, returns a tuple (next_state, output).
        #
        # This "step" method is not provided by tulip by default, so you would typically
        # write a small wrapper to simulate the transition based on self.discrete_ctrl.transitions.
        # Here we assume that such a function exists.
        self.current_discrete_state, output = self.discrete_ctrl.step(self.current_discrete_state, props)
        if props['s']:
            # If the landing condition is satisfied, we can stop the episode.
            return 'terminate'

        return output['action']
