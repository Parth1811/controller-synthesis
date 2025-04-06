from .controller import BaseController


class LTLSynthesizedController(BaseController):

    def __init__(self, env):
        super().__init__(env)
        # Define thresholds for the atomic propositions
        self.x_threshold = 0.1       # For being horizontally over the pad (p)
        self.angle_threshold = 0.1   # For near-upright orientation (q)
        self.vx_threshold = 0.1      # For small horizontal velocity (r)
        self.vy_threshold = 0.1      # For small vertical velocity (r)
        self.y_threshold = 0.2       # For near_ground condition

    def _get_atomic_propositions(self, state):
        """
        From the continuous state vector, compute the truth values for the atomic propositions.
        State is assumed to be: [x, y, vx, vy, angle, angular_vel, left_contact, right_contact]
        """
        x, y, vx, vy, angle, angular_vel, left_contact, right_contact = state

        # p: Lander is over the landing pad (assume pad is centered at x=0)
        p = abs(x) <= self.x_threshold
        # q: Lander is nearly upright
        q = abs(angle) <= self.angle_threshold
        # r: Lander's velocities are small
        r = (abs(vx) <= self.vx_threshold) and (abs(vy) <= self.vy_threshold)
        # s: Both landing legs are in contact
        s = (left_contact == 1 and right_contact == 1)
        # near_ground: Lander is close enough to the ground for landing maneuvers
        near_ground = y <= self.y_threshold

        return {'p': p, 'q': q, 'r': r, 's': s, 'near_ground': near_ground}

    def _get_fsm_state(self, props):
        """
        Determine the FSM state based on the atomic propositions.
        The states are:
          - 'Cruise': Not near ground.
          - 'Approach': Near ground but not aligned (p, q, r not all true).
          - 'Align': Near ground and aligned (p, q, r true) but not yet in contact.
          - 'Touchdown': Both legs are in contact (s true).
        """
        if props['s']:
            return 'Touchdown'
        elif props['near_ground']:
            if props['p'] and props['q'] and props['r']:
                return 'Align'
            else:
                return 'Approach'
        else:
            return 'Cruise'

    def control(self, observation):
        """
        Synthesize an action based on the current observation, according to the FSM.
        """
        # Get the current state from the environment.
        # Depending on the Gym version, you may need to access the state differently.
        # Here we assume that env.state is available.
        state = observation  # [x, y, vx, vy, angle, angular_vel, left_contact, right_contact]
        props = self._get_atomic_propositions(state)
        fsm_state = self._get_fsm_state(props)

        # Choose an action based on the FSM state.
        if fsm_state == 'Cruise':
            # In Cruise: adjust horizontal position.
            if state[0] > self.x_threshold:
                # Too far right: fire left engine to nudge left.
                return 1
            elif state[0] < -self.x_threshold:
                # Too far left: fire right engine to nudge right.
                return 3
            else:
                # When roughly centered, no thrust.
                return 0

        elif fsm_state == 'Approach':
            # In Approach: the lander is near the ground but not yet aligned.
            # First, correct orientation if necessary.
            if state[4] > self.angle_threshold:
                # Angle too high (tilted to the right): fire left engine to rotate counter-clockwise.
                return 1
            elif state[4] < -self.angle_threshold:
                # Angle too low (tilted to the left): fire right engine to rotate clockwise.
                return 3
            else:
                # If the vertical speed is too high, use main engine.
                if state[3] < -self.vy_threshold:
                    return 2
                else:
                    return 0

        elif fsm_state == 'Align':
            # In Align: already over the pad, upright, and with low velocities.
            # If descending too quickly, fire main engine.
            if state[3] < -self.vy_threshold:
                return 2
            else:
                # Otherwise, maintain current orientation.
                return 0

        elif fsm_state == 'Touchdown':
            # Once landed, no further action is necessary.
            return 'terminate'

    # Optional: Verification routines to validate that the synthesized controller meets the LTL specifications.
    # One simple strategy is to run a batch of simulated episodes, log the trajectories, and then verify
    # that for each episode:
    #    - Eventually, the state satisfies (p ∧ q ∧ r ∧ s) (i.e. a safe landing is achieved).
    #    - crash never occurs (which you would monitor via a crash flag if available).
    #    - When near_ground is true, the state remains within the acceptable bounds until touchdown.
    # For a more formal verification, you could export the FSM model and use a temporal logic model checker.
    #
    # For example:
    #
    # def verify_controller(self, num_episodes=100):
    #     successful_landings = 0
    #     for i in range(num_episodes):
    #         state = self.env.reset()
    #         done = False
    #         trajectory = []
    #         while not done:
    #             action = self.control()
    #             state, reward, done, info = self.env.step(action)
    #             trajectory.append(state)
    #             # Optionally, insert runtime monitors for LTL formulas here.
    #         # Analyze trajectory for satisfaction of F (p ∧ q ∧ r ∧ s) and G (¬ crash)
    #         # (This analysis would depend on how your environment indicates a crash.)
    #         if self._trajectory_satisfies_spec(trajectory):
    #             successful_landings += 1
    #     print("Successful Landings: ", successful_landings, "out of", num_episodes)
    #
    # def _trajectory_satisfies_spec(self, trajectory):
    #     # Implement the logic to verify the LTL properties on the given trajectory.
    #     # For example, check that eventually the atomic propositions p, q, r, s all become true,
    #     # and that a crash condition never occurs.
    #     return True  # Placeholder
    #     return True  # Placeholder


class LTLSynthesizedControllerV2(BaseController):
    def __init__(self, env):
        super().__init__(env)
        # Define thresholds for the atomic propositions
        self.x_threshold = 0.1       # For being horizontally over the pad (p)
        self.angle_threshold = 0.1   # For near-upright orientation (q)
        self.vx_threshold = 0.1      # For small horizontal velocity (r)
        self.vy_threshold = 0.1      # For small vertical velocity (r)
        self.y_threshold = 0.2       # For near_ground condition

    def _get_atomic_propositions(self, state):
        """
        From the continuous state vector, compute the truth values for the atomic propositions.
        State is assumed to be: [x, y, vx, vy, angle, angular_vel, left_contact, right_contact]
        """
        x, y, vx, vy, angle, angular_vel, left_contact, right_contact = state

        # p: Lander is over the landing pad (assume pad is centered at x=0)
        p = abs(x) <= self.x_threshold
        # q: Lander is nearly upright
        q = abs(angle) <= self.angle_threshold
        # r: Lander's velocities are small
        r = (abs(vx) <= self.vx_threshold) and (abs(vy) <= self.vy_threshold)
        # s: Both landing legs are in contact
        s = (left_contact == 1 and right_contact == 1)
        # near_ground: Lander is close enough to the ground for landing maneuvers
        near_ground = y <= self.y_threshold

        return {'p': p, 'q': q, 'r': r, 's': s, 'near_ground': near_ground}

    def _get_fsm_state(self, props):
        """
        Determine the FSM state based on the atomic propositions.
        The states are:
          - 'Cruise': Not near ground.
          - 'Approach': Near ground but not aligned (p, q, r not all true).
          - 'Align': Near ground and aligned (p, q, r true) but not yet in contact.
          - 'Touchdown': Both legs are in contact (s true).
        """
        if props['s']:
            return 'Touchdown'
        elif props['near_ground']:
            if props['p'] and props['q'] and props['r']:
                return 'Align'
            else:
                return 'Approach'
        else:
            return 'Cruise'

    def control(self, observation):
        """
        Synthesize an action based on the current observation, according to the FSM,
        with an added condition that the vertical speed is kept in check.
        """
        # Get the current state from the environment.
        # The state is assumed to be in the form:
        # [x, y, vx, vy, angle, angular_vel, left_contact, right_contact]
        state = observation
        props = self._get_atomic_propositions(state)
        fsm_state = self._get_fsm_state(props)

        # Additional condition: if the vertical velocity is too high (descending too quickly),
        # fire the main engine immediately.
        if state[3] < -self.vy_threshold:
            return 2

        # Choose an action based on the FSM state.
        if fsm_state == 'Cruise':
            # In Cruise: adjust horizontal position.
            if state[0] > self.x_threshold:
                # Too far right: fire left engine to nudge left.
                return 1
            elif state[0] < -self.x_threshold:
                # Too far left: fire right engine to nudge right.
                return 3
            else:
                # When roughly centered, no thrust.
                return 0

        elif fsm_state == 'Approach':
            # In Approach: near the ground but not aligned.
            # Correct orientation if necessary.
            if state[4] > self.angle_threshold:
                # Lander tilted to the right: fire left engine.
                return 1
            elif state[4] < -self.angle_threshold:
                # Lander tilted to the left: fire right engine.
                return 3
            else:
                # If vertical speed is too high, though the earlier condition should catch this.
                return 0

        elif fsm_state == 'Align':
            # In Align: already over the pad, upright, and with low velocities.
            # If descending too quickly, fire the main engine.
            if state[3] < -self.vy_threshold:
                return 2
            else:
                return 0

        elif fsm_state == 'Touchdown':
            # Once landed, no further action is necessary.
            return 0

class LTLSynthesizedControllerV3(BaseController):
    def __init__(self, env):
        super().__init__(env)
        # Define thresholds for the atomic propositions and safety bounds.
        self.x_threshold = 0.3         # For being horizontally over the pad (p)
        self.angle_threshold = 0.1     # For near-upright orientation (q)
        self.vx_threshold = 0.1        # For small horizontal velocity (r)
        self.vy_threshold = 1.0        # For small vertical velocity (r)
        self.angular_vel_threshold = 0.1  # Bound on angular velocity
        self.y_threshold = 0.3         # For near_ground condition

    def _get_atomic_propositions(self, state):
        """
        Compute truth values for atomic propositions from the continuous state vector.
        State is assumed to be: [x, y, vx, vy, angle, angular_vel, left_contact, right_contact]
        """
        x, y, vx, vy, angle, angular_vel, left_contact, right_contact = state

        # p: Lander is over the landing pad (assume pad is centered at x=0)
        p = abs(x) <= self.x_threshold
        # q: Lander is nearly upright
        q = abs(angle) <= self.angle_threshold
        # r: Lander's velocities are small
        r = (abs(vx) <= self.vx_threshold) and (abs(vy) <= self.vy_threshold)
        # s: Both landing legs are in contact
        s = (left_contact == 1 and right_contact == 1)
        # near_ground: Lander is close enough to the ground for landing maneuvers
        near_ground = y <= self.y_threshold

        return {'p': p, 'q': q, 'r': r, 's': s, 'near_ground': near_ground}

    def _get_fsm_state(self, props):
        """
        Determine the FSM state based on the atomic propositions.
        The discrete states are:
          - 'Cruise': Not near the ground.
          - 'Approach': Near the ground but not aligned (p, q, r not all true).
          - 'Align': Near the ground and aligned (p, q, r true) but not yet in contact.
          - 'Touchdown': Both legs are in contact (s true).
        """
        if props['s']:
            return 'Touchdown'
        elif props['near_ground']:
            if props['p'] and props['q'] and props['r']:
                return 'Align'
            else:
                return 'Approach'
        else:
            return 'Cruise'

    def control(self, observation):
        """
        Synthesize an action based on the current observation using the FSM,
        with added conditions to bound vertical and angular velocities.
        """
        # Retrieve the current state vector.
        # The state is assumed to be in the form:
        # [x, y, vx, vy, angle, angular_vel, left_contact, right_contact]
        state = observation
        props = self._get_atomic_propositions(state)
        fsm_state = self._get_fsm_state(props)

        # Priority 1: If vertical speed (vy) is too high (descending too fast), fire main engine.
        if state[3] < -self.vy_threshold:
            return 2

        # Priority 2: If angular velocity is too high, correct it.
        if state[5] > self.angular_vel_threshold:
            # Angular velocity is too high in the positive direction: counteract with the engine that rotates oppositely.
            return 3
        elif state[5] < -self.angular_vel_threshold:
            # Angular velocity is too high in the negative direction.
            return 1

        # Priority 3: Choose an action based on the FSM state.
        if fsm_state == 'Cruise':
            # In Cruise: adjust horizontal position.
            if state[0] > self.x_threshold:
                # Too far right: fire left engine to nudge left.
                return 1
            elif state[0] < -self.x_threshold:
                # Too far left: fire right engine to nudge right.
                return 3
            else:
                # Roughly centered: no thrust.
                return 0

        elif fsm_state == 'Approach':
            # In Approach: near the ground but not yet aligned.
            # Correct orientation if necessary.
            if state[4] > self.angle_threshold:
                return 1
            elif state[4] < -self.angle_threshold:
                return 3
            else:
                return 0

        elif fsm_state == 'Align':
            # In Align: conditions are mostly met; only adjust vertical speed if needed.
            if state[3] < -self.vy_threshold:
                return 2
            else:
                return 0

        elif fsm_state == 'Touchdown':
            # Once landed, no further action is needed.
            return 0