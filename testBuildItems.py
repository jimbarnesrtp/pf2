# -*- coding: utf-8 -*-

import unittest
from buildItems import ItemBuilder
import os

class TestBuildItems(unittest.TestCase):
    
    line_break = "++++++++++++++++++++++++++++++++++"
    data = []
    norm_data = []

    def load_items(self) -> list:
        if len(self.data) < 1:
            self.data = self.func.load_all_items()
        return self.data

    def get_normalized_data(self) -> list:

        if len(self.norm_data) < 1:
            self.norm_data = self.func.normalize_data(self.load_items(), self.func.item_keywords)
            #print("Length of Norm Data:", len(self.norm_data))
        return self.norm_data

    def setUp(self):
        unittest.TestLoader.sortTestMethodsUsing = None
        self.func = ItemBuilder()

    def test(self):
        self.assertTrue(True)

    def test_load_items(self):
        print(self.line_break)
        directory_path = os.getcwd()
        data = self.func.pf.load_csv(directory_path+"/itemcsv/RadGridExport-1.csv")
        #print("Items:", data[1])
        self.assertGreater(len(data), 0)

    def test_load_all_items(self):
        print(self.line_break)
        #print("Item:", self.load_items()[4])
        self.assertGreater(len(self.load_items()), 0)
    
    def test_normalize_all_items464(self):
        print(self.line_break)
        data = self.get_normalized_data()
        print("Norm_data:", data[464])
        self.assertGreater(len(data), 0)
    
    def test_populate_item464(self):
        print(self.line_break)
        item = self.func.populate_data(self.get_normalized_data()[464])
        print("Populated Item:", item)
        self.assertIsNotNone(item)

    def test_normalize_all_items465(self):
        print(self.line_break)
        data = self.get_normalized_data()
        print("Norm_data:", data[465])
        self.assertGreater(len(data), 0)
    
    def test_populate_item465(self):
        print(self.line_break)
        item = self.func.populate_data(self.get_normalized_data()[465])
        print("Populated Item:", item)
        self.assertIsNotNone(item)

    def test_normalize_all_items1(self):
        print(self.line_break)
        data = self.get_normalized_data()
        print("Norm_data:", data[1])
        self.assertGreater(len(data), 0)
    
    def test_populate_item1(self):
        print(self.line_break)
        item = self.func.populate_data(self.get_normalized_data()[1])
        print("Populated Item:", item)
        self.assertIsNotNone(item)

    def test_normalize_all_items595(self):
        print(self.line_break)
        data = self.get_normalized_data()
        print("Norm_data:", data[595])
        self.assertGreater(len(data), 0)
    
    def test_populate_item595(self):
        print(self.line_break)
        item = self.func.populate_data(self.get_normalized_data()[595])
        print("Populated Item:", item)
        self.assertIsNotNone(item)

 
if __name__ == '__main__':
    unittest.main()