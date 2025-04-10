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
        # thresholds for p, q, r, near_ground
        self.x_th   = 0.1
        self.ang_th = 0.1
        self.vx_th  = 0.1
        self.vy_th  = 2.0
        self.y_th   = 0.2

        # save env var names
        self.input_vars = ['p', 'q', 'r', 'near_ground']

        # build and synthesize the GR(1) spec (same as before)
        env_vars = self.input_vars[:]
        sys_vars = [
            'do_nothing','fire_left','fire_main','fire_right',
            'landing_pending','landed'
        ]
        env_init = set()
        sys_init = set()
        stable = 'near_ground && p && q && r'
        env_safe = set()
        sys_safety = {
            f'({stable} && !landing_pending && !landed) -> X(landing_pending)',
            '(landing_pending && !landed) -> X(landing_pending)',
            f'(landing_pending && {stable}) -> X(landed)',
            'landed -> X(!landing_pending)',
            'landed -> X(landed)',
            '(do_nothing || fire_left || fire_main || fire_right)',
            '!(do_nothing && fire_left)', '!(do_nothing && fire_main)', '!(do_nothing && fire_right)',
            '!(fire_left && fire_main)',    '!(fire_left && fire_right)',
            '!(fire_main && fire_right)'
        }
        env_prog = {stable}
        sys_prog = {'landed'}

        specs = spec.GRSpec(
            env_vars=env_vars,
            sys_vars=sys_vars,
            env_init=env_init,
            sys_init=sys_init,
            env_safety=env_safe,
            sys_safety=sys_safety,
            env_prog=env_prog,
            sys_prog=sys_prog
        )
        specs.moore = True
        specs.qinit = r'\A \E'
        self.controller = synth.synthesize(specs)
        if self.controller is None:
            raise RuntimeError("Unrealizable spec")
        self.current_state = 0

    def _get_atomic_propositions(self, obs):
        # obs = [x, y, vx, vy, angle, ang_vel, left_contact, right_contact]
        x, y, vx, vy, ang, ang_vel, lc, rc = obs
        p = abs(x) <= self.x_th
        q = abs(ang) <= self.ang_th
        r = abs(vx) <= self.vx_th and abs(vy) <= self.vy_th
        near_ground = y <= self.y_th
        return {'p': p, 'q': q, 'r': r, 'near_ground': near_ground}

    def control(self, observation):
        # 1) Map continuous obs → boolean props
        props = self._get_atomic_propositions(observation)

        # 2) Look up all transitions from the current discrete state
        #    MealyMachine.transitions.find(state) returns
        #    a list of (src_state, dst_state, valuation) tuples :contentReference[oaicite:0]{index=0}
        trans_list = self.controller.transitions.find(self.current_state)

        # 3) Find the transition whose env‐vars in valuation match props
        for (src, dst, valuation) in trans_list:
            if all(valuation[var] == props[var] for var in self.input_vars):
                next_state = dst
                out_vals = valuation
                break
        else:
            raise ValueError(f"No valid transition from state {self.current_state} with props {props}")

        # 4) Advance the FSM state
        self.current_state = next_state

        # 5) Decode one‑hot action from out_vals
        if out_vals['do_nothing']:
            return 0
        if out_vals['fire_left']:
            return 1
        if out_vals['fire_main']:
            return 2
        if out_vals['fire_right']:
            return 3

        raise RuntimeError("Controller produced no valid action")
