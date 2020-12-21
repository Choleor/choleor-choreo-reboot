from abc import ABC, abstractmethod
import random
from choreo.dbmanager.mysql_dao import ChoreoSliceHandler
from choreo.services.status_manager import *
from choreo.services.filter_manager import *
from choreo.services.select_manager import *


class ChoreographyManager:
    def __init__(self, strategy):
        self.strategy = strategy

    def run_stgy(self):
        return self.strategy.run_strategy()


class PhaseStrategy(ABC):
    def __init__(self, *args):
        self.info = [self.user_id, self.selected_choreo_id, self.counter] = args
        self.status_manager = StatusManager(*args)
        self.filtered = None
        self.selected = None

    @property
    @abstractmethod
    def phase(self):
        """return phase"""

    @property
    @abstractmethod
    def filter_manager(self):
        """return filter manager"""

    @property
    @abstractmethod
    def select_manager(self):
        """return select manager"""

    def run_strategy(self):
        # record & report information of user
        print("=============managing status===============")
        self.status_manager.manage_status()

        print("\n\n=============filter==============")
        # filter
        self.filtered = self.filter_manager.filter(self.selected_choreo_id, self.phase)
        print(self.filtered)
        print("HEY THIS IS FILTER MF!!!")
        print("\n")
        # selector
        partition = int(UserRedisHandler.dao.hget(self.user_id, "partition").decode())
        print(partition)
        audio_slice_id = UserRedisHandler.get_user_audio_slice_id(self.user_id)
        print(audio_slice_id)
        print("\n\n=============selection start!==============")
        self.selected = self.select_manager.select(self.filtered, partition, audio_slice_id)
        print(self.selected)
        # notify the selection result to other process and thumbnail
        UserRedisHandler.set_process_result(self.user_id, self.selected)

        return self.selected


class IntroStrategy(PhaseStrategy):
    phase = "intro"
    filter_manager = PhaseFilter()
    select_manager = RandomSelector()


class BodyStrategy(PhaseStrategy):
    phase = None
    filter_manager = PoseFilter()
    select_manager = ScoreSelector()


class OutroStrategy(PhaseStrategy):
    phase = "outro"
    filter_manager = PoseFilter()
    select_manager = RandomSelector()
