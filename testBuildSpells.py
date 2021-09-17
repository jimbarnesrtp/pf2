import unittest
from buildSpellsV3 import BuildSpells
import os

class TestBuildSpells(unittest.TestCase):

    def setUp(self):
        unittest.TestLoader.sortTestMethodsUsing = None
        self.func = BuildSpells()

    def test(self):
        self.assertTrue(True)

    def test_load_monsters(self):
        directory_path = os.getcwd()
        print("Monsters:", self.func.pf.load_csv(directory_path+"/spellscsv/RadGridExport.csv")[0])
        self.assertGreater(len(self.func.pf.load_csv(directory_path+"/spellscsv/RadGridExport.csv")), 0)

    def test_normalize_monsters(self):
        directory_path = os.getcwd()
        raw = self.func.pf.load_csv(directory_path+"/spellscsv/RadGridExport.csv")
        print("Spell:", self.func.normalize_spell_data(raw)[0])
        self.assertGreater(len(raw), 0)

    def test_monster_details(self):
        directory_path = os.getcwd()
        raw = self.func.pf.load_csv(directory_path+"/spellscsv/RadGridExport.csv")
        spell = self.func.get_spell_details(raw[0])
        print("SpellFull:", spell)
        self.assertIsNot(spell)

    
    #def test_save_data(self):
        #self.assertIsNotNone(self.func.save_data(self.func.build_monsters()))
    

if __name__ == '__main__':
    unittest.main()
