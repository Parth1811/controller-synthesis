from abc import ABC, abstractmethod


class BaseController(ABC):

    def __init__(self, env):
        """
        Base class for all controllers.
        :param env: The environment to control.
        """
        self.env = env

    @abstractmethod
    def control(self, observation):
        pass