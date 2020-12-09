from abc import *
import random
import numpy as np
from choreo.dbmanager.redis_dao import *
from choreo.dbmanager.mysql_dao import ChoreoSliceHandler
from choreo.utils.modif_ds import *
from choreo.utils.utils import normalize


class Selector(metaclass=ABCMeta):
    @staticmethod
    def select(user_audio_slice_id, filtered_list):
        """
        :param user_audio_slice_id:
        :param filtered_list: 2D list
                [[spose1, cslice1, aslice1],
                [spose2, cslice2, aslice2],
                ...]
        :return: [cslice1, cslice2, cslice3, cslice4, cslice5, cslice6]
        """
        pass


class RandomSelector(Selector):
    @staticmethod
    def select(user_audio_slice_id, filtered_list):
        return random.sample(filtered_list, 6)


class ScoreBasedSelector(Selector):
    @staticmethod
    def select(user_audio_slice_id, filtered_list):
        # 자료구조 변환
        # filtered_list를 transpose 시켜 pose, choreo_slice, audio_slice 배열로 만듦

        [ftr_sposeid, ftr_choreo_sid, ftr_audio_sid] = np.transpose(sorted(filtered_list)).tolist()
        # 같은 cluster의 음악군의 유사도 점수 - 가져와서 정렬시킨 후 transpose
        [smlr_audio_sid, smlr_score] = np.transpose(
            sorted(SimilarityRedisHandler.get_similarity_list(user_audio_slice_id))).tolist()

        overlapped_audio_sid = sorted(list(set(smlr_audio_sid) & set(ftr_audio_sid)))

        result = []  # audio_slice_id, choreo_slice_id, similarity_score 리스트를 담은 이중 배열
        for i, j in zip(ftr_choreo_sid, ftr_audio_sid):
            if i in overlapped_audio_sid:
                result += [[i, j, smlr_score[smlr_audio_sid.indexOf(i)]]]

        # Harmony 점수 연산
        # 사용자가 선택하고자 하는 음악 구간에 대한 진폭 배열 가져옴
        # 그와 같은 res_audio_id와 매핑되는 res_choreo_id의 movement 배열과 연산

        amp_list = AmplitudeRedisHandler.get_amplitude_list(user_audio_slice_id)
        harmony_list, similarity_list = [], []

        for i in result:
            i += ChoreoSliceHandler.get_movement_score(i[1])
            harmony_list += [abs(np.average([amp_list[idx] - mvmt for idx, mvmt in enumerate(i[3])]))]
            similarity_list += [i[2]]

        final_score_list = np.average(normalize(harmony_list), normalize(similarity_list))
        print(sorted(final_score_list, reverse=True))
        return sorted(final_score_list, reverse=True)[:6]
