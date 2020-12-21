from choreo.dbmanager.mysql_dao import ChoreoSliceHandler
from abc import ABC, abstractmethod
import random
import numpy as np
from choreo.dbmanager.redis_dao import *
from choreo.models import ChoreoSlice
from choreo.utils.utils import normalize
from choreo.utils.modif_ds import *


class SelectManager(ABC):
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


class RandomSelector(SelectManager):
    def select(self, *args):
        """
        :param args:  [0] filtered list
        :return:
        """
        try:
            args[0].remove([4369, 'k98iZjftvKQ~0', '2i4zg9PzXYMㅡ0'])
            args[0].remove([273, 'P3EgWidZthc~0', 'EZk1HsQvi5Qㅡ0'])
            args[0].remove([8465, 'QwXHFKWmCgw~0', 'xqMYU4_kEqkㅡ0'])
            args[0].remove([790801, 'eehNilV8Zg8~0', 'yC325xAf__Aㅡ0'])
        except Exception as e:
            print(e)
            print("EXCEPTION")
        finally:
            print([i[1] for i in random.sample(args[0], 6)])
            return [i[1] for i in random.sample(args[0], 6)]


class ScoreSelector(SelectManager):
    OLD_S_POSE, OLD_CHOREO, OLD_AUDIO, OLD_POSE_MATCH_SCORE = 0, 1, 2, 3
    NEW_CHOREO, NEW_AUDIO, NEW_POSE_MATCH_SCORE, NEW_SMLR_SCORE, NEW_HARMONY_SCORE = 0, 1, 2, 3, 3

    def __init__(self):
        self.filtered, self.partition, self.audio_slc_id, self.selected = None, None, None, None
        self.similarity_res = []
        self.harmony_res = []

    def select(self, *args):
        [self.filtered, self.partition, self.audio_slc_id] = args
        # transpose
        self.get_similarity_res()
        print(self.similarity_res)
        print()

        self.get_harmony_res()
        print(self.harmony_res)
        print()

        self.selected = self.combine_similarity_harmony()
        print(self.selected)
        print()

        uniq_choreo = set()

        real_final = []
        for i in self.selected:
            cid = i.split("~")[0]

            if cid not in uniq_choreo:
                uniq_choreo.add(cid)
                real_final.append(i)
            else:
                print(cid, i)

        if len(real_final) < 6:
            return self.selected[:3] + random.sample(self.selected, 3)

        return random.sample(real_final[3:], 3) + real_final[:3]

    def get_similarity_res(self):
        print(len(self.filtered))
        ftr_list = [ftr_sposeid, ftr_choreo_sid, ftr_audio_sid, ftr_points] = np.transpose(self.filtered).tolist()
        print(len(ftr_sposeid), len(ftr_choreo_sid), len(ftr_audio_sid), len(ftr_points))
        print()
        similarity_list = [smlr_audio_sid, smlr_score] = np.transpose(
            SimilarityRedisHandler.get_similarity_list(self.partition, self.audio_slc_id)).tolist()
        smlr_audio_sid = [i.split(".")[0] for i in smlr_audio_sid]

        print(ftr_audio_sid)
        print(smlr_audio_sid)
        print(smlr_score)

        overlapped_audio_sid = sorted(list(set(smlr_audio_sid) & set(ftr_audio_sid)))
        print(overlapped_audio_sid)
        self.similarity_res = []  # audio_slice_id, choreo_slice_id, similarity_score 리스트를 담은 이중 배열

        for chor, aud, p_match in zip(ftr_choreo_sid, ftr_audio_sid, ftr_points):
            if aud in overlapped_audio_sid:
                print("NOT 80.00 in similarity res!   " + smlr_score[smlr_audio_sid.index(aud)])
                self.similarity_res += [[chor, aud, int(p_match), float(smlr_score[smlr_audio_sid.index(aud)])]]
            else:
                self.similarity_res += [[chor, aud, int(p_match), 80.00]]

        print(f"Inserted {len(self.similarity_res)} records on similarity result")

    def get_harmony_res(self):
        amp_list = AmplitudeRedisHandler.get_amplitude_list(self.partition, self.audio_slc_id)[1:]
        mov_dict = ScoreSelector.__get_movement_to_dict__(
            [ftr_lst[ScoreSelector.OLD_CHOREO] for ftr_lst in self.filtered])

        # print()
        # print("self.filtered!!!!!!!!!!!!!!!!!!!!!")
        # print(len(self.filtered))
        # # print(self.filtered)
        # print()
        # print("choreo settings for movement dictionary")
        # print(len([ftr_lst[ScoreSelector.OLD_CHOREO] for ftr_lst in self.filtered]))
        # print([ftr_lst[ScoreSelector.OLD_CHOREO] for ftr_lst in self.filtered])
        # print("movement dictionary")
        # print(len(list(mov_dict.keys())))
        # # print(mov_dict)
        # print(len(amp_list))
        # print([i[ScoreSelector.OLD_CHOREO] for i in self.filtered])

        self.harmony_res = []
        for n, ftr_lst in enumerate(self.filtered):
            if ftr_lst[ScoreSelector.OLD_CHOREO] in mov_dict:
                mvmt = mov_dict.get(ftr_lst[ScoreSelector.OLD_CHOREO])
                hmny = np.average([abs(r - q) for r, q in zip(amp_list, mvmt)])
                self.harmony_res += [ftr_lst[ScoreSelector.OLD_CHOREO:] + [hmny]]
            else:
                print("Something strange happens, check select manager with 111 line")
                self.harmony_res += [ftr_lst[ScoreSelector.OLD_CHOREO:] + [0]]  # set default score

        print(len(self.filtered))

        print(f"Inserted {len(self.harmony_res)} records on harmony result")

    def combine_similarity_harmony(self):
        csid_for_join = [x[ScoreSelector.NEW_CHOREO] for x in self.harmony_res]
        print(csid_for_join[:6])
        print()

        add_points = [3 * (2 - x[ScoreSelector.NEW_POSE_MATCH_SCORE]) for x in self.harmony_res]
        print(add_points)
        print("filter  " + str(len(self.filtered)))
        print("similarity  " + str(len(self.similarity_res)))
        print("harmony   " + str(len(self.harmony_res)))
        print()

        norm_similarity = [x[ScoreSelector.NEW_SMLR_SCORE] for x in self.similarity_res]
        norm_harmony = normalize([x[ScoreSelector.NEW_HARMONY_SCORE] for x in self.harmony_res])
        print(norm_similarity[:6])
        print(norm_harmony[:6])
        print()

        ret = []

        for idx in range(len(self.harmony_res)):
            ret += [[(norm_harmony[idx] + norm_similarity[idx]) / 2.0 + add_points[idx],
                     csid_for_join[idx]]]
        print(sorted(ret, reverse=True))
        print()
        return [x[1] for x in sorted(ret, reverse=True)]

    @staticmethod
    def __get_movement_to_dict__(ftr_choreos):
        dic = {}
        for i in ftr_choreos:
            try:
                dic[i] = [int(y) for y in ChoreoSlice.objects.get(choreo_slice_id=i).movement.split(":")]
            except:
                print("[ CHECK 149th lines on select manager ] no movement on  " + i)
                continue
        print(dic)
        return dic

