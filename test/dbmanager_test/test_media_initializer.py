from django.test.testcases import TestCase
from choreo.dbmanager.initializer import *
from configuration.config import *
import os


class MediaInitializerTest(TestCase):
    def test_initialize(self):
        Initializer().initialize()
        self.assertEquals(30, next(os.walk(F_ORG))[2])  # for only file numbers
        self.assertEquals(30, next(os.walk(F_SLICE))[1])  # for only directory numbers
