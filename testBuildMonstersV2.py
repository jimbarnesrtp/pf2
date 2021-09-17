import unittest
from buildMonstersV2 import BuildMonsters
import os

class TestBuildMonstersVs(unittest.TestCase):

    def setUp(self):
        unittest.TestLoader.sortTestMethodsUsing = None
        self.func = BuildMonsters()

    def test(self):
        self.assertTrue(True)

    def test_load_monsters(self):
        directory_path = os.getcwd()
        print("Monsters:", self.func.pf.load_csv(directory_path+"/monstercsv/RadGridExport.csv")[2])
        self.assertGreater(len(self.func.pf.load_csv(directory_path+"/monstercsv/RadGridExport.csv")), 0)
    
    def test_normalize_monsters(self):
        directory_path = os.getcwd()
        raw = self.func.pf.load_csv(directory_path+"/monstercsv/RadGridExport.csv")
        print("Monsters:", self.func.normalize_monster_data(raw)[0])
        self.assertGreater(len(raw), 0)

    def test_monster_details(self):
        directory_path = os.getcwd()
        raw = self.func.pf.load_csv(directory_path+"/monstercsv/RadGridExport.csv")

    
    def test_save_data(self):
        self.assertIsNotNone(self.func.save_data(self.func.build_monsters()))
    

if __name__ == '__main__':
    unittest.main()
