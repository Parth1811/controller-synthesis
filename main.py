import gymnasium as gym
from gym.wrappers.monitoring.video_recorder import VideoRecorder
from gymnasium.wrappers import RecordVideo

from controller import *
from utils import ContinuousRecordVideo

# Initialise the environment
env = gym.make("LunarLander-v3", render_mode="rgb_array")

NO_OF_ITER = 10
CONTROLLERS_LIST = [
    ChatGPTController,
    ClaudeController,
    DeepSeekController,
    LlamaController,
    ChatGPTExtendedPromptController,
    ChatGPTExtendedPromptControllerV2,
    ChatGPTExtendedPromptControllerV3,
    RandomActionController,
    TulipLunarLanderController
]

for CONTROLLER in CONTROLLERS_LIST:
    print("----" * 20)
    print (f"Testing controller: {CONTROLLER.__name__}")
    env = RecordVideo(env, "runs", episode_trigger=lambda x: True, name_prefix=CONTROLLER.__name__)
    # env = ContinuousRecordVideo(env, "runs", episode_trigger=lambda x: True, name_prefix=CONTROLLER.__name__)

    # recorder = VideoRecorder(env, path=f"runs/{CONTROLLER.__name__}_first_run.mp4", enabled=True)
    controller = CONTROLLER(env)
    env.start_recording("first Run")

    sucess = 0
    for i in range(NO_OF_ITER):
        print(f"Starting episode {i + 1}")
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
            # recorder.capture_frame()

            if truncated or terminated:
                print(" ==============")
                print("Terminating episode.")
                print("Final Observation: ", observation)
                print("Final Reward: ", reward)
                print(" ==============")

                if reward >= 200:
                    sucess += 1

                break

        env.stop_recording()
        # recorder.close()
        print(f"Success rate of {CONTROLLER.__name__}: {sucess / NO_OF_ITER * 100:.2f}%")