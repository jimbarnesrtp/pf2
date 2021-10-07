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

    def test_load_items(self):
        directory_path = os.getcwd()
        data = self.func.pf.load_csv(directory_path+"/itemcsv/RadGridExport.csv")
        print("Items:", data[1])
        self.assertGreater(len(data), 0)

    #def test_load_all_items(self)