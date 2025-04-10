from gymnasium.wrappers import RecordVideo


class ContinuousRecordVideo(RecordVideo):

    def reset(self, **kwargs):
        return super().reset(**kwargs)

    def step(self, action):
        """Steps through the environment using action, recording observations if :attr:`self.recording`."""
        (
            observations,
            rewards,
            terminateds,
            truncateds,
            infos,
        ) = self.env.step(action)

        return observations, rewards, terminateds, truncateds, infos
