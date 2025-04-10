import gymnasium as gym

from controller import *

# Initialise the environment
env = gym.make("LunarLander-v3", render_mode="human")


# controller = LTLSafeController(env)
# controller = LTLLunarLanderController(env)
# controller = LunarLanderController(env)
# controller = LlamaLunarLanderController(env)
# controller = LTLSynthesizedControllerV2(env)
controller = LTLSynthesizedControllerV3(env)
# controller = LTLSynthesizedController(env)
# controller = RandomActionController(env)
# controller = TulipLunarLanderController(env)
# controller = RandomActionController(env)
# controller = TulipLunarLanderController(env)



sucess = 0
NO_OF_ITER = 10
for i in range(NO_OF_ITER):
    print("----" * 20)
    print(f"Starting episode {i + 1}")

    # Reset the environment to generate the first observation
    observation, info = env.reset(seed=i)
    for iter in range(400):
        # this is where you would insert your policy
        action = controller.control(observation)

        if iter % 10 == 0:
            print(f"Iter: {iter:3d}, Action: {action}, Observation: x={' ' if observation[0] >= 0 else ''}{observation[0]:.2f}, "
                  f"y={' ' if observation[1] >= 0 else ''}{observation[1]:.2f}, "
                  f"vx={' ' if observation[2] >= 0 else ''}{observation[2]:.2f}, "
                  f"vy={' ' if observation[3] >= 0 else ''}{observation[3]:.2f}, "
                  f"ang={' ' if observation[4] >= 0 else ''}{observation[4]:.2f}, "
                  f"av={' ' if observation[5] >= 0 else ''}{observation[5]:.2f}, "
                  f"lleg={observation[6]}, rleg={observation[7]}")

        # step (transition) through the environment with the action
        # receiving the next observation, reward and if the episode has terminated or truncated
        observation, reward, terminated, truncated, info = env.step(action)

        if truncated or terminated:
            print(" ==============")
            print("Terminating episode.")
            print("Final Observation: ", observation)
            print("Final Reward: ", reward)
            print(" ==============")

            if reward >= 200:
                sucess += 1

            break

    print("Success rate: ", sucess * 10000 // NO_OF_ITER / 100 )