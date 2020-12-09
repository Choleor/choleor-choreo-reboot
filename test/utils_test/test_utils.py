from django.test import TestCase
from choreo.utils.modif_ds import *


class UtilsTest(TestCase):
    def test_dictlist_to_listdict(self):
        expected_res = {"col1": [12, 334, 555, 66], "col2": ["ab", "cc"], "col3": [3333.00],
                        "col4": [1, "a", "bc", 33.0, 66, "66"]}
        test_res = dictlist_to_listdict(
            [{'col1': 12, 'col2': 'ab', 'col3': 3333.0, 'col4': 1}, {'col1': 334, 'col2': 'cc', 'col4': 'a'},
             {'col1': 555, 'col4': 'bc'}, {'col1': 66, 'col4': 33.0}, {'col4': 66}, {'col4': '66'}])
        self.assertEquals(test_res, expected_res)

    def test_listdict_to_dictlist(self):
        input_dict = {"col1": [12, 334, 555, 66], "col2": ["ab", "cc"], "col3": [3333.00],
                      "col4": [1, "a", "bc", 33.0, 66, "66"]}
        compact_res = [{'col1': 12, 'col2': 'ab', 'col3': 3333.0, 'col4': 1},
                       {'col1': 334, 'col2': 'cc', 'col4': 'a'},
                       {'col1': 555, 'col4': 'bc'}, {'col1': 66, 'col4': 33.0}, {'col4': 66}, {'col4': '66'}]
        extended_res = [{'col1': 12, 'col2': 'ab', 'col3': 3333.0, 'col4': 1},
                        {'col1': 334, 'col2': 'cc', 'col3': '', 'col4': 'a'},
                        {'col1': 555, 'col2': '', 'col3': '', 'col4': 'bc'},
                        {'col1': 66, 'col2': '', 'col3': '', 'col4': 33.0},
                        {'col1': '', 'col2': '', 'col3': '', 'col4': 66},
                        {'col1': '', 'col2': '', 'col3': '', 'col4': '66'}]
        self.assertRaisesMessage(Exception, "No such an option", listdict_to_dictlist, input_dict, "eded")
        self.assertEquals(compact_res, listdict_to_dictlist(input_dict, "compact"))
        self.assertEquals(extended_res, listdict_to_dictlist(input_dict, "extended"))

    def test_reader(self):
        self.assertEquals("", "")

    def test_writer(self):
        self.assertEquals("", "")