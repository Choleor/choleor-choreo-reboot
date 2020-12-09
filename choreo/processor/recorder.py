from abc import *
from choreo.dbmanager.redis_dao import *

"""
REDIS CONNECTIONS
"""


class Recorder(metaclass=ABCMeta):
    @staticmethod
    def record():
        pass


class UserRecorder(Recorder):
    """
    User Redis [HSET]
        user_id : {
        "audio_id": "",
        "start_idx": 12,
        "end_idx": 20,
        "counter": 12.
        "interval": 9 (20-12+1)
    }
    """

    @staticmethod
    def record(*args):
        """
        :param args: user_id, counter
        :return: None (only cache data access - change counter value)
        """
        try:
            UserRedisHandler.set_user_counter(args)
        except Exception as e:
            print(e)


class SelectionRecorder(Recorder):
    """
    Selection Redis [LIST]
    user_id : [ choreo_id lists ]
    """
    @staticmethod
    def record(*args):
        """
        :param args: user_id, choreo_id
        :return:
        """
        try:
            SelectionRedisHandler.add_selection_info(args)
        except Exception as e:
            print(e)
