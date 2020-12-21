# from choreo.processor.recorder import *
# from choreo.processor.filter import *
# from choreo.processor.selector import *
# from choreo.processor.factory import *
# from choreo.dbmanager.redis_dao import *
# from abc import ABC
# import sys
#
#
# class ChoreographyManager(ABC):
#     def __init__(self, *args):
#         """
#         :param args: user_id, selected_choreo_id, counter, remark
#         """
#         self.info = list(args)  # [user_id, selected_choreo_id, counter] // user_id, selected_choreo_id, counter, remark, request_n
#         self.recorder_lists = None
#         self.filter = None
#         self.selector = None
#         self.factory = None
#         self.state = None
#
#     def process(self):
#         try:
#             # Recorder를 통해 redis에 정보 업데이트
#             for idx, recorder in enumerate(self.recorder_lists):
#                 recorder.record(self.info[idx])
#             # User redis에서 필요한 정보 추출
#             prev_audio_slice_id = UserRedisHandler.get_user_audio_slice_id(self.info[0])  # get audio_id, start_idx
#             current_audio_slice_id = prev_audio_slice_id.split("ㅡ")[0] + "ㅡ" + str(
#                 int(prev_audio_slice_id.split("ㅡ")[1]) + self.info[2])
#
#             # final 6개의 choreography 후보들을 추출
#             # audio 길이에 맞춰 최종적으로 선택된 6개의 춤 영상을 오디오와 합침
#             ret1 = self.filter.filter(self.info[1], self.state)
#             print(ret1, len(ret1))
#             ret2 = self.selector.select(current_audio_slice_id, ret1)
#             print(ret2, len(ret2))
#             UserRedisHandler.set_process_result(ret2)
#             # ret3 = self.factory.produce(self.info[0], self.info[2], ret2)
#             # print(ret3)
#
#             # self.factory.produce(self.info[0], self.info[2], current_audio_slice_id,
#             #                      self.selector.select(current_audio_slice_id,
#             #                                           self.filter.filter(self.info[1], self.state)))
#             return ret2
#         except Exception as e:
#             print("Processing failure ", e, sys.stderr)
#
#
# class IntroManager(ChoreographyManager):
#     def __init__(self, *args):
#         super().__init__(args)
#         self.recorder_lists = [UserRecorder()]
#         self.filter = PhaseFilter()
#         self.selector = RandomSelector()
#         # self.factory = Factory()
#         self.state = "Intro"
#
#
# class BodyManager(ChoreographyManager):
#     def __init__(self, *args):
#         super().__init__(*args)
#         self.recorder_lists = [UserRecorder(), SelectionRecorder()]
#         self.filter = ConnectivityFilter()
#         self.selector = ScoreSelector()
#         # self.factory = Factory()
#
#
# class OutroManager(ChoreographyManager):
#     def __init__(self, *args):
#         super().__init__(*args)
#         self.recorder_lists = [UserRecorder(), SelectionRecorder()]
#         self.filter = ConnectivityFilter()
#         self.selector = RandomSelector()
#         # self.factory = Factory()
#         self.state = "Outro"
#         # progress 계산해 rabbitmq를 통해 통신
#
#
# if __name__ == '__main__':
#     OutroManager.process()
