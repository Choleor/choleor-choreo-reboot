from django.test.testcases import TestCase
from choreo.dbmanager.redis_dao import *


class UserRedisDaoTest(TestCase):
    def test_set_counter(self):
        UserRedisHandler.set_user_counter('4a785be4-6272-4c15-b2d8-4f7981c6d959', 6)  # user_id, counter
        self.assertEquals(6, int(UserRedisHandler.get_user_info('4a785be4-6272-4c15-b2d8-4f7981c6d959', "counter")))

    def test_get_audio(self):
        self.assertEquals("EZk1HsQvi5Qㅡ12",
                          UserRedisHandler.get_user_audio_slice_id('4a785be4-6272-4c15-b2d8-4f7981c6d959'))  # user_id


class SelectionRedisDaoTest(TestCase):
    def test_add_selection(self):
        self.assertEquals(None, SelectionRedisHandler.add_selection_info('4a785be4-6272-4c15-b2d8-4f7981c6d959',
                                                                         "ymZGEY0OAzkㅡ3"))  # user_id, selected_choreo_idx

    def test_get_selection(self):  # for test
        self.assertEquals("ymZGEY0OAzkㅡ3",
                          SelectionRedisHandler.get_selection_info('4a785be4-6272-4c15-b2d8-4f7981c6d959'))


class AmplitudeRedisDaoTest(TestCase):
    def test_get_ampl_list(self):
        self.assertEquals([2, 4, 5, 10, 9, 1, 3, 5],
                          AmplitudeRedisHandler.get_amplitude_list("EZk1HsQvi5Qㅡ13"))  # audio_slice_id(user)


class SimilarityRedisDaoTest(TestCase):
    def test_get_similarity_list(self):
        self.assertEquals([['나', '2'], ['다', 'c'], ['라', 'd'], ['1'], ['2'], ['가'], ['나'], ['가', '1']],
                          SimilarityRedisHandler.get_similarity_list("HYMDfMMD3fwㅡ1"))  # audio_slice_id
