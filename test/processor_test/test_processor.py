from django.test import TestCase
# from choreo.processor.choreography_manager import *
from choreo.processor.recorder import *
from choreo.processor.filter import *
from choreo.processor.selector import *
from choreo.processor.factory import *
import uuid
from choreo.models import ChoreoSlice


#
# class ProcessorTest(TestCase):
#     def setUp(self) -> None:
#         print()
#
#     def test_intro_manager(self):
#         IntroManager.process()
#         self.assertEquals("", "")
#
#     def test_body_manager(self):
#         BodyManager.process()
#         self.assertEquals("")
#
#     def test_outro_manager(self):
#         OutroManager.process()
#         self.assertEquals("", "")


class RecorderTest(TestCase):
    selected_cids = []

    def setUp(self) -> None:
        # set up for user redis
        UserRedisHandler.dao.flushall()
        UserRedisHandler.dao.hmset("dk-39823n9",
                                   {"audio_id": "HYMDfMMD3fw", "start_idx": 13, "end_idx": 28, "counter": 10,
                                    "interval": 15})

        # set up for selection redis
        SelectionRedisHandler.dao.flushall()
        for i in range(0, 9):
            RecorderTest.selected_cids.append(str(uuid.uuid4()))
            print(RecorderTest.selected_cids)
            SelectionRedisHandler.add_selection_info(*["dk-39823n9", RecorderTest.selected_cids[i]])

    def test_user_recorder(self):
        UserRecorder.record(*["dk-39823n9", 10])
        self.assertEquals(10, UserRedisHandler.get_user_counter("dk-39823n9"))

    def test_selection_recorder(self):
        SelectionRecorder.record(*("dk-39823n9", "ymZGEY0OAzk"))
        print(RecorderTest.selected_cids)
        self.assertEquals(RecorderTest.selected_cids + ["ymZGEY0OAzk"],
                          list(SelectionRedisHandler.get_selection_info("dk-39823n9")))


class FilterTest(TestCase):
    # 나중에 setup으로 데이터베이스 연결시켜주기
    def test_loose_filter(self):
        expected_li = [[87189, "-xmVz8BiLRo~0", "HE5wgGCxGHcㅡ0"],
                       [135441, "4X6TsiWZtJo~0", "lN47Figg8gQㅡ0"],
                       [20885, "70dcSKN5Nx0~0", "QM8HngracYYㅡ0"],
                       [34905, "CM5VSP1QWXg~0", "tz0OzH6fHrIㅡ0"],
                       [273, "dVPexyKjj_k~0", "M3ctXZBingMㅡ0"],
                       [4373, "fVw8Eu8vG4M~0", "Pp8sHP - s87Iㅡ0"],
                       [17, "GwCiHS9_3 - Y~0", "Pu1tIIdLYKEㅡ0"],
                       [533, "HJX8X1il7Ow~0", "Cf6_oDpe6rEㅡ0"],
                       [4369, "k98iZjftvKQ~0", "2i4zg9PzXYMㅡ0"],
                       [273, "P3EgWidZthc~0", "EZk1HsQvi5Qㅡ0"],
                       [17, "PDtdyNVYvgQ~0", "k8ha7zI2P0Uㅡ0"],
                       [8465, "QwXHFKWmCgw~0", "xqMYU4_kEqkㅡ0"],
                       [17, "S8fvgFDQKvk~0", "a4AeHG4l5fQㅡ0"],
                       [41617, "yNM2DU3fkgE~0", "EKiJMxGBZi8ㅡ0"],
                       [39317, "Zx1n1R_OQs0~0", "RQTgJRwMdKQㅡ0"]]
        self.assertEquals(expected_li, PhaseFilter.filter("", "intro"))

    def test_connectivity_filter(self):
        expected_res = []
        self.assertEquals(expected_res, ConnectivityFilter.filter("outro"))


class SelectorTest(TestCase):
    filter_res = None

    def setUp(self) -> None:
        ChoreoSliceHandler.flush_all()
        uuids = [str(uuid.uuid4()) for i in range(10)]
        ChoreoSliceHandler.insert_all(*(("akskdkvnksl_31", "3,4,6,7,9", 3.28, False, True, b"010101001010010",
                                         b"10000100000010", "APVLDKEKQA", "akskdkvnksl")))
        ChoreoSliceHandler.insert_all(*(("ymZGEY0OAzkㅡ4", "2,4,6,7,1", 4.28, False, False, b"010101001010010",
                                         b"10111100000010", "EZk1HsQvi5Qㅡ15", "ymZGEY0OAzk")))
        ChoreoSliceHandler.insert_all(*("zdosfdkekㅡ1", "1,10,9,9,4", 5.24, True, False, b"010101001010010",
                                        b"10000100000010", "EZk1HsQvi5Qㅡ14", "zdosfdkek"))
        ChoreoSliceHandler.insert_all(*(("ymZGEY0OAzkㅡ4", "3,4,6,7,9", 3.28, False, False, b"010101001010010",
                                         b"10000100000010", "EZk1HsQvi5Q", "ymZGEY0OAzk")))
        ChoreoSliceHandler.insert_all(*(("ymZGEY0OAzkㅡ5", "2,4,6,7,1", 4.28, True, False, b"010101001010010",
                                         b"10111100000010", "EZk1HsQvi5Qㅡ16", "ymZGEY0OAzk")))
        ChoreoSliceHandler.insert_all(*("ymZGEY0OAzkㅡ26", "1,10,9,9,4", 5.24, False, True, b"010101001010010",
                                        b"10000100000010", "EZk1HsQvi5Qㅡ26", "ymZGEY0OAzk"))
        ChoreoSliceHandler.insert_all(*(
            uuids[0], "3,4,6,7,9", 3.28, False, False, b"010101001010010", b"10000100000010", "DDDDDDDDDDDd",
            "avv0OAzk"))
        ChoreoSliceHandler.insert_all(*(uuids[1], "2,4,6,7,1", 4.28, True, False, b"010101001010010",
                                        b"10111100000010", "EZk1HsQvi5Qㅡ16", "ymZGEY0OAzk"))
        ChoreoSliceHandler.insert_all(*(uuids[2], "0,2,9,9,4", 5.24, False, True, b"010101001010010",
                                        b"10000100000010", "EZk1HsQvi5Qㅡ26", "ymZGEY0OAzk"))
        ChoreoSliceHandler.insert_all(*(
            uuids[3], "3,4,6,7,9", 3.28, False, False, b"010101001010010", b"10000100000010", "AAAAAa",
            "ddddddddd"))
        ChoreoSliceHandler.insert_all(*(
            uuids[4], "2,4,6,7,1", 4.28, True, False, b"010101001000010", b"10111100000010", "BBBBB",
            "cccccc"))
        ChoreoSliceHandler.insert_all(*(
            uuids[5], "0,2,9,9,4", 5.24, False, True, b"010101001010010", b"10000100000010", "CCCCCCCCCCC",
            "abaababab"))
        print(ChoreoSlice.objects.all())
        SelectorTest.filter_res = PhaseFilter.filter("X", "Intro")

    def test_random_selector(self):
        print(RandomSelector.select("user_id", SelectorTest.filter_res))
        self.assertIn(RandomSelector.select("user_id", SelectorTest.filter_res))

    def test_score_based_selector(self):
        self.assertEquals(['2KBFD0aoZy8ㅡ27', '2i4zg9PzXYMㅡ14', '2r7RdcgdyB8ㅡ30', '4-TbQnONe_wㅡ14', '4h0ZEkI_onsㅡ22',
                           '5tfQPuOQbRcㅡ28'], ScoreSelector.select("a", []))
