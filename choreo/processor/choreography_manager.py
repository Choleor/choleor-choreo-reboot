from .recorder import *
from .filter import *
from .selector import *
from .factory import *
from choreo.dbmanager.redis_dao import *
import abc
import sys


class ChoreographyManager(metaclass=ABCMeta):
    @abc.abstractmethod
    def __init__(self, *args):
        """
        :param args: user_id, selected_choreo_id, counter
        """
        self.info = list(args)
        self.recorder_lists = None
        self.filter = None
        self.selector = None
        self.factory = None

    def process(self):
        try:
            # Recorder를 통해 redis에 정보 업데이트
            for idx, recorder in enumerate(self.recorder_lists):
                recorder.record(self.info[idx])

            # User redis에서 필요한 정보 추출
            user_cache_info = UserRedisHandler.get_user_audio(self.info[0])  # get audio_id, start_idx
            user_audio_slice_id = user_cache_info[0] + str(int(user_cache_info[1]) + self.info[2])

            # final 6개의 choreography 후보들을 추출
            # audio 길이에 맞춰 최종적으로 선택된 6개의 춤 영상을 오디오와 합침
            self.factory.produce(self.info[0], self.info[2], user_audio_slice_id,
                                 self.selector.select(user_audio_slice_id,
                                                      self.filter.filter(self.info[1])))
        except Exception as e:
            print("Processing failure ", e, sys.stderr)


class IntroManager(ChoreographyManager):
    def __init__(self, *args):
        super().__init__(args)
        self.recorder_lists = [UserRecorder()]
        self.filter = LooseFilter()
        self.selector = RandomSelector()
        self.factory = Factory()


class BodyManager(ChoreographyManager):
    def __init__(self, *args):
        super().__init__(*args)
        self.recorder_lists = [UserRecorder(), SelectionRecorder()]
        self.filter = ConnectivityFilter()
        self.selector = ScoreBasedSelector()
        self.factory = Factory()


class OutroManager(ChoreographyManager):
    def __init__(self, *args):
        super().__init__(*args)
        self.recorder_lists = [UserRecorder(), SelectionRecorder()]
        self.filter = ConnectivityFilter()
        self.selector = RandomSelector()
        self.factory = Factory()
        # progress 계산해 rabbitmq를 통해 통신
