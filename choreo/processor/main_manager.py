from abc import ABC, abstractmethod
from choreo.processor.recorder import *
import random
import numpy as np
from choreo.utils.utils import normalize


class Recorder(ABC):
    @abstractmethod
    def record(self, *args):
        pass


class UserRecorder(Recorder):
    def record(self, *args):
        # args[0]
        return 0


class SelectionRecorder(UserRecorder):
    def record(self, *args):
        # args[0], args[1]
        super(SelectionRecorder, self).record(args[0])
        return 0


class Filter(ABC):
    def __init__(self, _filter):
        self.filter = _filter

    @abstractmethod
    def filter(self):
        pass


class PhaseFilter(Filter):
    def __init__(self, _filter):
        super().__init__(_filter)

    def filter(self):
        # self.filter
        return 0


class ConnectivityFilter(PhaseFilter):
    def __init__(self, _filter):
        super(ConnectivityFilter, self).__init__(_filter)

    def filter(self):
        return 0


class Selector(ABC):
    @abstractmethod
    def select(self):
        pass


class RandomSelector(Selector):
    def select(self, *args):  # user_audio_slice_id, filtered_list
        return [i[1] for i in random.sample(args[1], 6)]


class ScoreSelector(Selector):
    def select(self, *args):
        user_audio_slice_id = args[0]
        filtered_list = args[1]
        # filtered_list를 transpose 시켜 pose, choreo_slice, audio_slice 배열로 만듦
        # for test
        # filtered_list = [[b'010101001010010', 'ymZGEY0OAzkㅡ5', '2i4zg9PzXYMㅡ14'],
        #                  [b'010101001010010', 'nlYrKGumWk', '4h0ZEkI_onsㅡ22'],
        #                  [b'100001001010010', 'eyha_YQFKWwㅡ12', '2r7RdcgdyB8ㅡ30'],
        #                  [b'100001001010010', 'zdosfdkekㅡ1', '4-TbQnONe_wㅡ14'],
        #                  [b'100001001010010', 'SyDqzqokY5Y', '62LIGmJTXRkㅡ15'],
        #                  [b'100001001010010', '62LIGmJTXRk', '7PrONon7jgㅡ19']]

        [ftr_sposeid, ftr_choreo_sid, ftr_audio_sid, ftr_points] = np.transpose(sorted(filtered_list)).tolist()

        print("==============================================================")
        # print(ftr_sposeid)
        # print(ftr_choreo_sid)
        print(ftr_audio_sid)
        # print(ftr_points)
        print("==============================================================")

        # 같은 cluster의 음악군의 유사도 점수 - 가져와서 정렬시킨 후 transpose

        # temp_li = [('k8ha7zI2P0Uㅡ24', 99.69), ('k8ha7zI2P0Uㅡ10', 99.47), ('k8ha7zI2P0Uㅡ11', 99.39),
        #            ('k8ha7zI2P0Uㅡ26', 99.3), ('cu9q10b8UiYㅡ10', 99.3), ('9vTm96LPk5cㅡ36', 99.29),
        #            ('QM8HngracYYㅡ7', 99.28), ('RFSWbQ9JA6Qㅡ21', 99.27), ('k8ha7zI2P0Uㅡ9', 99.23),
        #            ('2i4zg9PzXYMㅡ30', 99.2), ('efLayd9pvjQㅡ11', 99.18), ('Pp8sHP-s87Iㅡ10', 99.16),
        #            ('k8ha7zI2P0Uㅡ25', 98.75), ('x-JvjkGt9e0ㅡ63', 98.75),
        #            ('2r7RdcgdyB8ㅡ0', 98.75), ('zQX2q6WCrbEㅡ25', 98.75), ('DRqdXqk4Q_cㅡ21', 98.74)]
        # si = [smlr_audio_sid, smlr_score] = np.transpose(sorted(temp_li)).tolist()

        similarity_list = [smlr_audio_sid, smlr_score] = np.transpose(
            sorted(SimilarityRedisHandler.get_similarity_list(user_audio_slice_id))).tolist()
        # print(smlr_audio_sid)
        # print(smlr_score)

        # print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        overlapped_audio_sid = sorted(list(set(smlr_audio_sid) & set(ftr_audio_sid)))
        # print(overlapped_audio_sid)

        result1 = []  # audio_slice_id, choreo_slice_id, similarity_score 리스트를 담은 이중 배열
        for i, j, m in zip(ftr_choreo_sid, ftr_audio_sid, ftr_points):
            if j in overlapped_audio_sid:
                result1 += [[i, j, int(m), float(smlr_score[smlr_audio_sid.index(j)])]]

        # Harmony 점수 연산
        # 사용자가 선택하고자 하는 음악 구간에 대한 진폭 배열 가져옴
        # 그와 같은 res_audio_id와 매핑되는 res_choreo_id의 movement 배열과 연산

        amp_list = AmplitudeRedisHandler.get_amplitude_list(user_audio_slice_id)  # 진폭 정보를 redis로부터 가져옴
        # amp_list = [5, 4, 3, 2, 2, 1, 1, 1, 1]
        mov_dict = ScoreSelector.__get_movement_to_dict__([i[0] for i in result1])
        print(mov_dict)
        result2 = []

        for n, i in enumerate(result1):
            if i[0] in mov_dict:
                mvmt = mov_dict.get(i[0])
                hmny = np.average([abs(r - q) for r, q in zip(amp_list, mvmt)])
                result2.append(i + [hmny])

        print(result1, len(result1))
        print(result2, len(result2))

        final_list = []

        if len(result2) >= 6:  # harmony와 similarity 함께 고려 --> result 2
            norm_similarity = [x[3] for x in result2]
            choreo_id_for_join = [x[0] for x in result2]
            norm_harmony = normalize([x[4] for x in result2])
            add_points = [0.6 * (2 - x[2]) for x in result2]  # 0 : 1.2 / 1: 0.6 / 2: 0

            for idx1 in range(len(result2)):
                final_list += [np.average(norm_harmony[idx1], norm_similarity[idx1]) + add_points[idx1],
                               choreo_id_for_join[idx1]]

        else:  # harmony 생각하지 말고 --> result1 (유사도)만 고려
            norm_similarity = [x[3] for x in result1]
            choreo_id_for_join = [x[0] for x in result1]
            add_points = [0.6 * (2 - x[2]) for x in result1]

            for idx2, val2 in enumerate(result1):
                final_list += [[norm_similarity[idx2] + add_points[idx2], choreo_id_for_join[idx2]]]

            more_n = 6 - len(final_list)

            if more_n > 0:
                # remove duplicates with result 1 and added with filter score
                ftr_proc = [[x[3], x[1]] for x in filtered_list if
                            x[1] not in [a[0] for a in result1]]  # ftr points & choreo slice id
                ftr_proc = [[52 - x[0], x[1]] for x in
                            sorted(ftr_proc)]  # filter 점수가 낮을 수록 더 많이 매치, 가산점 대신 점수로 변환

                tp_for_final = []
                for idx3 in range(more_n):  # result 1으로도 6개 채울 수 없음 > filtered_result에서 높은 순으로 필요한 개수만큼 가져오기(0-6)
                    tp_for_final += [ftr_proc[idx3]]
                # print(final_list)
                # print(tp_for_final)
                final_list += tp_for_final

        # final_list = sorted(final_list, reverse=True)
        return [x[1] for x in sorted(final_list, reverse=True)][:7]

    @staticmethod
    def __get_movement_to_dict__(filtered_list):
        dic = {}
        for i in filtered_list:
            try:
                dic[i] = [int(y) for y in ChoreoSlice.objects.get(choreo_slice_id=i).movement.split(":")]
            except:
                pass
        return dic


# client class
# views.py에서 MainManager.run_strategy(Intro())
class MainManager:
    def __init__(self, *args):
        self.info = self.user_id, self.selected_choreo_id, self.counter, self.remark = args

    def run_stgy(self, strategy):
        strategy.run_stgy(*self.info)


class Strategy(ABC):
    def __init__(self, *args):
        self.user_id, self.selected_choreo_id, self.counter, self.remark = args

    @property
    @abstractmethod
    def get_type(self):
        """return strategy type(state)"""

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
        # self.recorder.record()
        # self.filter.filter()
        # self.selector.select()
        self.selector.select(self.filter.filter(self.recorder.record()))


class IntroStrategy(Strategy):
    recorder = UserRecorder()
    filter = PhaseFilter()
    selector = RandomSelector()


class BodyStrategy(Strategy):
    recorder = SelectionRecorder()
    filter = ConnectivityFilter()
    selector = ScoreSelector()


class OutroStrategy(Strategy):
    recorder = SelectionRecorder()
    filter = ConnectivityFilter()
    selector = RandomSelector()
