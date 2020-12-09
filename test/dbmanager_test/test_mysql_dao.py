from django.test.testcases import TestCase
from choreo.dbmanager.mysql_dao import *

# os.environ['DJANGO_SETTINGS_MODULE'] = 'choleor_choreo.settings'
# import django
# django.setup()


class ChoreoSliceHandlerTest(TestCase):
    def test_get_end_pose_type(self):
        self.assertEquals("10000100000010", ChoreoSliceHandler.get_end_pose_type("ymZGEY0OAzkㅡ4"))

    def test_get_three_list(self):
        self.assertEquals([b'010101001010010', 'ymZGEY0OAzkㅡ4', 'EZk1HsQvi5Q'],
                          ChoreoSliceHandler.get_spose_cslice_aslice_list(_filter="Body"))

    def test_get_movement_list(self):
        self.assertEquals([3, 4, 6, 7, 9], ChoreoSliceHandler.get_movement_list())

    def test_get_movement_score(self):
        self.assertEquals([3, 4, 6, 7, 9], ChoreoSliceHandler.get_movement_score("ymZGEY0OAzkㅡ4"))

    def test_insert_all(self):
        self.assertEquals(None,
                          ChoreoSliceHandler.insert_all("ymZGEY0OAzkㅡ4", "3,4,6,7,9", 3.28, False, False,
                                                        b"010101001010010",
                                                        b"10000100000010", "EZk1HsQvi5Q", "ymZGEY0OAzk")
                          )
