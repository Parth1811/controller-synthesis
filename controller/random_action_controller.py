from .controller import BaseController


class RandomActionController(BaseController):

    def control(self, observation):
        """
        Control the environment by taking a random action.
        :return: The action taken.
        """
        action = self.env.action_space.sample()
        return action