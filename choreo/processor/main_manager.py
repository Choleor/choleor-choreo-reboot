from abc import ABC, abstractmethod
from choreo.processor.recorder import *
from choreo.processor.filter import *
from choreo.processor.selector import *
import random
import numpy as np
from choreo.utils.utils import normalize


# client class
# views.py에서 MainManager.run_strategy(Intro())
class MainManager:
    def __init__(self, strategy):
        self.strategy = strategy

    def run_stgy(self):
        return self.strategy.run_strategy()


class Strategy(ABC):
    def __init__(self, *args):
        self.info = [self.user_id, self.selected_choreo_id, self.counter] = args

    # @property
    # @abstractmethod
    # def get_type(self):
    #     """return strategy type(state)"""

    @property
    @abstractmethod
    def recorder(self):
        """return recorder from child class"""

    @property
    @abstractmethod
    def filter(self):
        """return filter from child class"""

    @property
    @abstractmethod
    def selector(self):
        """return selector from child class"""

    def run_strategy(self):
        # selected_choreo_id / user's audio_slice_id / user_id, filtered_list
        return self.selector.select(*self.filter.filter_with_phase(*self.recorder.record(*self.info)))


class IntroStrategy(Strategy):
    recorder = Recorder()
    filter = PhaseFilter(_filter="intro")
    selector = RandomSelector()


class BodyStrategy(Strategy):
    recorder = Recorder()
    filter = ConnectivityFilter(_filter=None)
    selector = ScoreSelector()


class OutroStrategy(Strategy):
    recorder = Recorder()
    filter = ConnectivityFilter(_filter="outro")
    selector = RandomSelector()
