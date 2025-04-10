#!/usr/bin/env python3
"""
GR(1) synthesis for the Lunar Lander FSM using TuLiP (omega backend)

We replace the env‐controlled touchdown flag with a sys‐controlled 'landed'
and ensure landing is initiated exactly once and then completed.
"""

from tulip import spec, synth

# 1) Declare variables
# Environment inputs (boolean)
env_vars = {
    'p',           # |x| <= δx (over pad)
    'q',           # |angle| <= δθ (upright)
    'r',           # |vx|<=δvx and |vy|<=δvy (low linear velocity)
    'near_ground'  # y <= δy (close to ground)
}

# System outputs (boolean, one-hot thrusters + two aux flags)
sys_vars = {
    'do_nothing',
    'fire_left',
    'fire_main',
    'fire_right',
    'landing_pending',  # auxiliary: we’ve seen stable, so must land
    'landed'           # auxiliary: we have completed the landing
}

# 2) Initial conditions
env_init = set()   # no restriction on (p,q,r,near_ground) at t=0
sys_init = set()   # MUST be empty for the omega backend

# 3) Environment safety (invariants)
env_safety = set()  # no safety assumptions beyond variable domains

# 4) System safety (invariants)
stable = 'near_ground && p && q && r'

sys_safety = {
    # (a) When we first see stable & not yet pending & not yet landed → raise pending
    f'({stable} && !landing_pending && !landed) -> X(landing_pending)',

    # (b) While pending and not yet landed → keep pending
    '(landing_pending && !landed) -> X(landing_pending)',

    # (c) Once stable & pending → perform landing (set landed)
    f'(landing_pending && {stable}) -> X(landed)',

    # (d) After landed → clear pending
    'landed -> X(!landing_pending)',

    # (e) Landed persists
    'landed -> X(landed)',

    # (f) One‐hot thruster actions
    '(do_nothing || fire_left || fire_main || fire_right)',
    '!(do_nothing && fire_left)', '!(do_nothing && fire_main)', '!(do_nothing && fire_right)',
    '!(fire_left && fire_main)',    '!(fire_left && fire_right)',
    '!(fire_main && fire_right)'
}

# 5) Environment liveness (fairness)
#    The environment will eventually offer a stable hover infinitely often.
env_prog = { stable }

# 6) System liveness (guarantee)
#    The system must eventually complete the landing.
sys_prog = { 'landed' }

# 7) Build the GR(1) spec
specs = spec.GRSpec(
    env_vars=env_vars,
    sys_vars=sys_vars,
    env_init=env_init,
    sys_init=sys_init,
    env_safety=env_safety,
    sys_safety=sys_safety,
    env_prog=env_prog,
    sys_prog=sys_prog
)

# Moore machine (outputs depend only on the current state)
specs.moore = True
# For all initial env moves, there exists an initial sys move
specs.qinit = r'\A \E'

# 8) Synthesize
controller = synth.synthesize(specs)
if controller is None:
    print("❌ Unrealizable – please check your assumptions/guarantees.")
else:
    print("✅ Controller synthesized successfully!")
    print("Number of states:", len(controller.states))
    print(controller)
