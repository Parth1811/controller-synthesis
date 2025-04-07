from tulip import spec, synth

# Define environment and system variables
env_vars = {'req'}               # Boolean environment variable (request signal)
sys_vars = {'grant'}             # Boolean system variable (grant signal)

# Initial conditions
env_init = {'!req'}              # Assume no request at the very start (req is False initially)
sys_init = {'!grant'}            # Require the system starts with grant output False

# Safety constraints
env_safe = set()                # No additional environment invariants (environment can toggle req freely)
sys_safe = {
    # System should never grant when there is no request:
    '(!req -> X(!grant))',
    # If a reques
    # t is present, the system must grant on the next step:
    '(req -> X(grant))'
}

# Liveness goals
env_prog = {'req'}              # Environment will issue 'req' infinitely often (never stops requesting)
sys_prog = {'grant'}            # System will produce 'grant' infinitely often

# Combine into a GR(1) specification
specs = spec.GRSpec(env_vars, sys_vars, env_init, sys_init, env_safe, sys_safe, env_prog, sys_prog)
specs.moore = True      # System is a Moore machine (doesn't read next env move in same step)
specs.qinit = r'\E \A'  # There exists a sys initial move for all env initial moves (default for Moore)

# Attempt synthesis (for demonstration purposes)
ctrl = synth.synthesize(specs)
assert ctrl is not None, "Specification is unrealizable!"
