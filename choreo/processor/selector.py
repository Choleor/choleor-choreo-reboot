from abc import *
import random
import numpy as np
from choreo.dbmanager.redis_dao import *
from choreo.models import ChoreoSlice
from choreo.utils.utils import normalize
from choreo.utils.modif_ds import *
from choreo.processor.filter import *
# from choreo.dbmanager.mysql_dao import ChoreoSliceHandler

from abc import ABC, abstractmethod


class Selector(ABC):
    def __init__(self):
        self.audio_slc_id = None
        self.filtered_li = []

    @abstractmethod
    def select(self, *args):
        """
        :param args
                user_audio_slice_id:
                filtered_list: 2D list
                    [[spose1, cslice1, aslice1],
                    [spose2, cslice2, aslice2],
                    ...]
        :return: [cslice1, cslice2, cslice3, cslice4, cslice5, cslice6]
        """
        pass


class RandomSelector(Selector):
    def select(self, *args):
        print(args[1])
        print([i[1] for i in random.sample(args[1], 6)])
        return [i[1] for i in random.sample(args[1], 6)]


class ScoreSelector(Selector):
    def select(self, *args):  # user id, filtered_list
        partition = int(UserRedisHandler.dao.hget(args[0], "partition").decode())
        print(partition)
        audio_slc_id = UserRedisHandler.get_user_audio_slice_id(args[0])
        print(audio_slc_id)

        # filtered_list를 transpose 시켜 pose, choreo_slice, audio_slice 배열로 만듦
        # for test
        # filtered_list = [[b'010101001010010', 'ymZGEY0OAzkㅡ5', '2i4zg9PzXYMㅡ14'],
        #                  [b'010101001010010', 'nlYrKGumWk', '4h0ZEkI_onsㅡ22'],
        #                  [b'100001001010010', 'eyha_YQFKWwㅡ12', '2r7RdcgdyB8ㅡ30'],
        #                  [b'100001001010010', 'zdosfdkekㅡ1', '4-TbQnONe_wㅡ14'],
        #                  [b'100001001010010', 'SyDqzqokY5Y', '62LIGmJTXRkㅡ15'],
        #                  [b'100001001010010', '62LIGmJTXRk', '7PrONon7jgㅡ19']]

        [ftr_sposeid, ftr_choreo_sid, ftr_audio_sid, ftr_points] = np.transpose(sorted(args[1])).tolist()
        print("==============================================================")
        # print(ftr_sposeid)
        # print(ftr_choreo_sid)
        # print(ftr_audio_sid)
        # print(ftr_points)

        # 같은 cluster의 음악군의 유사도 점수 - 가져와서 정렬시킨 후 transpose

        # temp_li = [('k8ha7zI2P0Uㅡ24', 99.69), ('k8ha7zI2P0Uㅡ10', 99.47), ('k8ha7zI2P0Uㅡ11', 99.39),
        #            ('k8ha7zI2P0Uㅡ26', 99.3), ('cu9q10b8UiYㅡ10', 99.3), ('9vTm96LPk5cㅡ36', 99.29),
        #            ('QM8HngracYYㅡ7', 99.28), ('RFSWbQ9JA6Qㅡ21', 99.27), ('k8ha7zI2P0Uㅡ9', 99.23),
        #            ('2i4zg9PzXYMㅡ30', 99.2), ('efLayd9pvjQㅡ11', 99.18), ('Pp8sHP-s87Iㅡ10', 99.16),
        #            ('k8ha7zI2P0Uㅡ25', 98.75), ('x-JvjkGt9e0ㅡ63', 98.75),
        #            ('2r7RdcgdyB8ㅡ0', 98.75), ('zQX2q6WCrbEㅡ25', 98.75), ('DRqdXqk4Q_cㅡ21', 98.74)]
        # si = [smlr_audio_sid, smlr_score] = np.transpose(sorted(temp_li)).tolist()

        similarity_list = [smlr_audio_sid, smlr_score] = np.transpose(
            sorted(SimilarityRedisHandler.get_similarity_list(partition, audio_slc_id))).tolist()
        print(smlr_audio_sid)
        print(smlr_score)

        # print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        overlapped_audio_sid = sorted(list(set(smlr_audio_sid) & set(ftr_audio_sid)))
        print(overlapped_audio_sid)
        # print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")

        result1 = []  # audio_slice_id, choreo_slice_id, similarity_score 리스트를 담은 이중 배열
        for i, j, m in zip(ftr_choreo_sid, ftr_audio_sid, ftr_points):
            if j in overlapped_audio_sid:
                result1 += [[i, j, int(m), float(smlr_score[smlr_audio_sid.index(j)])]]

        # Harmony 점수 연산
        # 사용자가 선택하고자 하는 음악 구간에 대한 진폭 배열 가져옴
        # 그와 같은 res_audio_id와 매핑되는 res_choreo_id의 movement 배열과 연산

        amp_list = AmplitudeRedisHandler.get_amplitude_list(partition, audio_slc_id)[1:]  # 진폭 정보를 redis로부터 가져옴
        # amp_list = [5, 4, 3, 2, 2, 1, 1, 1, 1]
        mov_dict = ScoreSelector.__get_movement_to_dict__([i[0] for i in result1])
        # print(mov_dict)
        result2 = []

        for n, i in enumerate(result1):
            if i[0] in mov_dict:
                mvmt = mov_dict.get(i[0])
                hmny = np.average([abs(r - q) for r, q in zip(amp_list, mvmt)])
                result2.append(i + [hmny])

        print("!!!!!!!!!!!!!!!!!!!!!! RESULT 1 !!!!!!!!!!!!!!!!!!!!!")
        print(result1, len(result1))
        print("!!!!!!!!!!!!!!!!!!!!!! RESULT 2 !!!!!!!!!!!!!!!!!!!!!")
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

            final_list = [x[1] for x in sorted(final_list, reverse=True)]

        else:  # harmony 생각하지 말고 --> result1 (유사도)만 고려
            norm_similarity = [x[3] for x in result1]
            choreo_id_for_join = [x[0] for x in result1]
            add_points = [0.6 * (2 - x[2]) for x in result1]

            for idx2, val2 in enumerate(result1):
                final_list += [[norm_similarity[idx2] + add_points[idx2], choreo_id_for_join[idx2]]]

            final_list = [x[1] for x in sorted(final_list, reverse=True)]

            if len(final_list) < 6:
                # remove duplicates with result 1 and added with filter score
                ftr_proc = [[x[3], x[1]] if x[3] != -1 else [10, x[1]] for x in args[1] if
                            x[1] not in [a[0] for a in result1]]  # ftr points & choreo slice id
                ftr_proc = [[52 - x[0] if x[0] != -1 else 0, x[1]] for x in
                            sorted(ftr_proc)]  # filter 점수가 낮을 수록 더 많이 매치, 가산점 대신 점수로 변환
                tp_for_final = [i[1] for i in ftr_proc if i[0] >= 50]
                pre_choiced_choreos = set([x.split("~")[0] for x in tp_for_final])
                uniq_choreos = set([x.split("~")[0] for x in tp_for_final])

                random_dct = {}

                print(ftr_proc)
                print(tp_for_final)
                print(uniq_choreos)

                if len(tp_for_final) >= 6-len(final_list):
                    final_list = sorted(tp_for_final, reverse=True)[:6]

                else: # pose filter로도 부족한 경우
                    for idx3 in range(len(ftr_proc)):
                        csid = ftr_proc[idx3][1]
                        cid = csid.split("~")[0]

                        if cid not in pre_choiced_choreos:
                            uniq_choreos.add(cid)
                            ex = random_dct.get(cid) if bool(random_dct.get(cid)) else []
                            random_dct[cid] = ex + [csid]

                    cands = []
                    for v in random_dct.values():
                        to_add = random.sample(v, 1)[0]
                        cands.append(to_add)

                    cands = random.sample(cands, 6 - len(tp_for_final))
                    tp_for_final += cands
                    print("temporary result adding for final lists")

                    final_list += tp_for_final

                    print(tp_for_final)
                    print(final_list)

        return final_list

    @staticmethod
    def __get_movement_to_dict__(filtered_list):
        dic = {}
        for i in filtered_list:
            try:
                dic[i] = [int(y) for y in ChoreoSlice.objects.get(choreo_slice_id=i).movement.split(":")]
            except:
                pass
        return dic

    # """
    # # final 6개의 choreography 후보들을 추출
    # # audio 길이에 맞춰 최종적으로 선택된 6개의 춤 영상을 오디오와 합침
    #
    # self.factory.produce(self.info[0], self.info[2], user_audio_slice_id,
    #                      self.selector.select(user_audio_slice_id,
    #                                           self.filter.filter(*(self.info[1], self.state))))
    # """
    #
    # filter_res = [[405, '70dcSKN5Nx0~11', 'QM8HngracYYㅡ11', 1], [401, '70dcSKN5Nx0~6', 'QM8HngracYYㅡ6', 2],
    #               [2453, '70dcSKN5Nx0~7', 'QM8HngracYYㅡ7', 0], [4501, 'fVw8Eu8vG4M~10', 'Pp8sHP-s87Iㅡ10', 2],
    #               [405, 'GwCiHS9_3-Y~3', 'Pu1tIIdLYKEㅡ3', 1], [405, 'HJX8X1il7Ow~6', 'Cf6_oDpe6rEㅡ6', 1],
    #               [8597, 'jWhyc6UQ9ss~6', 'HYMDfMMD3fwㅡ6', 2], [277, 'ketGpeL4gao~5', '4h0ZEkI_onsㅡ5', 2],
    #               [277, 'PDtdyNVYvgQ~10', 'k8ha7zI2P0Uㅡ10', 2], [8597, 'PDtdyNVYvgQ~11', 'k8ha7zI2P0Uㅡ11', 2],
    #               [34965, 'PDtdyNVYvgQ~8', 'k8ha7zI2P0Uㅡ8', 2], [4501, 'RHTqzSSl5qU~6', 'DycottXjONkㅡ6', 2],
    #               [401, 'S8fvgFDQKvk~9', 'a4AeHG4l5fQㅡ9', 2]]
    # outro_ftr_res = [[27153, 'fVw8Eu8vG4M~14', 'Pp8sHP-s87Iㅡ14', 2], [8725, 'GwCiHS9_3-Y~12', 'Pu1tIIdLYKEㅡ12', 1],
    # [8725, 'P3EgWidZthc~8', 'EZk1HsQvi5Qㅡ8', 1], [8721, 'PDtdyNVYvgQ~12', 'k8ha7zI2P0Uㅡ12', 0],
    # [8721, 'QwXHFKWmCgw~13', 'xqMYU4_kEqkㅡ13', 0], [17, 'UfbuINOh_pM~6', 'ZJo_M2Nh-Jwㅡ6', 2]]
    # print(RandomSelector.select("I", outro_ftr_res))
    # Recorder.record(*user_id, selected_choreo_id, counter)
    # RandomSelector.select(*ConnectivityFilter(_filter="outro").filter("I'm user", "QDqlB8M25DQ~8"))


# #
# from choreo.processor.main_manager import *
#
# if __name__ == '__main__':
#     print(MainManager(BodyStrategy("8d1eecfe-c4c7-486b-bd50-2147db89bebf", "qprWYiynxEQ~0", 2)).run_stgy())
#     print(MainManager(BodyStrategy("8d1eecfe-c4c7-486b-bd50-2147db89bebf", "CowQPxBmN6c~6", 2)).run_stgy())
#     print(MainManager(BodyStrategy("8d1eecfe-c4c7-486b-bd50-2147db89bebf", "u1CYPY61uPI~5", 3)).run_stgy())
