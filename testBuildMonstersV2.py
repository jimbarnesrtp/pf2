import unittest
from buildMonstersV2 import BuildMonsters
import os

class TestBuildMonstersVs(unittest.TestCase):

    def setUp(self):
        unittest.TestLoader.sortTestMethodsUsing = None
        self.func = BuildMonsters()

    def test(self):
        self.assertTrue(True)

    # def test_load_monsters(self):
    #     directory_path = os.getcwd()
    #     data = self.func.pf.load_csv(directory_path+"/monstercsv/RadGridExport.csv")
    #     print("Monsters:", data[2])
    #     self.assertGreater(len(data), 0)
    
    # def test_normalize_monsters(self):
    #     directory_path = os.getcwd()
    #     raw = self.func.pf.load_csv(directory_path+"/monstercsv/RadGridExport.csv")
    #     print("Monsters2:", self.func.normalize_monster_data(raw)[0])
    #     self.assertGreater(len(raw), 0)
    
    # def test_get_monster_details(self):
    #     directory_path = os.getcwd()
    #     raw = self.func.normalize_monster_data(self.func.pf.load_csv(directory_path+"/monstercsv/RadGridExport.csv"))

    #     details = self.func.get_details(raw[0])
    #     #print("Details:", details)
    #     self.assertIsNotNone(details)
    
    def test_parse_header(self):
        text = '<h1 class="title">Aapoph Serpentfolk</h1> Aapophs possess greater strength and stronger venom than their zyss kin, but they lack zyss\' intelligence and innate magic. Unlike their selfish superiors, aapophs are communal and group together to hunt, wrestle, and sleep curled together in pits. Though they\'re looked down upon and insulted by zyss, most aapophs lack the higher brain functions to recognize when they\'re being insulted, much less plan or execute a rebellion. Aapophs often have unusual physical mutations—horns, vestigial tails, or spines protruding from their scales—yet these variations have little impact on their overall combat prowess— and combat prowess is the measure by which zyss judge them. <br/> <br/> <b><u><a href="Skills.aspx?ID=5&amp;General=true">Recall Knowledge - Humanoid</a></u> (<u><a href="Skills.aspx?ID=14">Society</a></u>)</b> : DC 20 '
        raw = self.func.parse_header(text)
        print("Parsed:", raw)
        self.assertIsNotNone(raw)

    def test_parse_recall(self):
        text = 'Recall Knowledge - Humanoid ( Society ) : DC 20 Recall Knowledge - Undead (Religion) : DC 22'
        raw = self.func.parse_recall(text)
        print("Recall:", raw)
        self.assertGreater(len(raw), 0)

    def test_parse_stats(self):
        text = {'name': 'Aapoph Serpentfolk', 'family': 'Serpentfolk', 'source': 'Bestiary 2', 'rarity': 'Uncommon', 'size': 'Medium', 'type': 'Humanoid', 'traits': ['Humanoid', 'Mutant', 'Serpentfolk'], 'level': '3', 'spoilers?': '—', 'link': 'https://2e.aonprd.com/Monsters.aspx?ID=799'}
        self.func.get_details(text)

    def test_parse_stats2(self):
        text = {'name': 'Aapoph Serpentfolk', 'family': 'Serpentfolk', 'source': 'Bestiary 2', 'rarity': 'Uncommon', 'size': 'Medium', 'type': 'Humanoid', 'traits': ['Humanoid', 'Mutant', 'Serpentfolk'], 'level': '3', 'spoilers?': '—', 'link': 'https://2e.aonprd.com/Monsters.aspx?ID=333'}
        self.func.get_details(text)

    


    # def test_monster_details(self):
    #     directory_path = os.getcwd()
    #     raw = self.func.pf.load_csv(directory_path+"/monstercsv/RadGridExport.csv")

    
    # def test_save_data(self):
    #     self.assertIsNotNone(self.func.save_data(self.func.build_monsters()))
    

if __name__ == '__main__':
    unittest.main()
