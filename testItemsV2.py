# -*- coding: utf-8 -*-

import unittest
from buildItemsV2 import ItemBuilder
import os

class TestBuildItemsV2(unittest.TestCase):

    def setUp(self):
        unittest.TestLoader.sortTestMethodsUsing = None
        self.func = BuildMonsters()

    def test(self):
        self.assertTrue(True)