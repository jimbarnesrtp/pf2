import unittest
from buildFeatsV2 import BuildFeatsV2
import os

class TestBuildFeatsV2(unittest.TestCase):

    def setUp(self):
        unittest.TestLoader.sortTestMethodsUsing = None
        self.func = BuildFeatsV2()

    def test(self):
        self.assertTrue(True)

    def test_load_Feats(self):
        directory_path = os.getcwd()
        self.assertGreater(len(self.func.load_feats(directory_path+"/featscsv/RadGridExport-1.csv")), 0)

    def test_norm_name(self):
        self.assertEqual(self.func.norm_link("<u><a href=\"Feats.aspx?ID=2516\">Aberration Kinship</a></u>"), "Aberration Kinship")

    def test_norm_pfs(self):
        self.assertEqual(self.func.norm_pfs("<img alt=\"PFS Standard\" title=\"PFS Standard\" style=\"height:18px; padding:2px 10px 0px 2px\" src=\"Images\Icons\PFS_Standard.png\">"), "PFS Standard")

    def test_norm_pfs_neg(self):
        self.assertEqual(self.func.norm_pfs("-"), "Excluded")
    
    def test_norm_source(self):
        self.assertEqual(self.func.norm_link("<u><a href=\"Sources.aspx?ID=74\" title=\"Ancestry Guide\">Ancestry Guide</a></u>"), "Ancestry Guide")
    
    def test_norm_rarity(self):
        self.assertEqual(self.func.norm_link("<u><a href=\"Traits.aspx?ID=28\">Common</a></u>"), "Common")
    
    def test_norm_traits(self):
        self.assertEqual(self.func.norm_traits("<u><a href=\"Traits.aspx?ID=338\">Fleshwarp</a></u>"), ['Fleshwarp'])
    
    def test_norm_multi_traits(self):
        self.assertEqual(self.func.norm_traits("<u><a href=\"Traits.aspx?ID=215\">Dhampir</a></u>, <u><a href=\"Traits.aspx?ID=317\">Lineage</a></u>"), ['Dhampir', 'Lineage'])
    
    def test_normurl(self):
        self.assertEqual(self.func.norm_url("<u><a href=\"Feats.aspx?ID=2516\">Aberration Kinship</a></u>"), "https://2e.aonprd.com/Feats.aspx?ID=2516")

    def test_norm_prereqs(self):
        self.assertEqual(self.func.norm_prereqs("trained in <u><a href=\"Skills.aspx?ID=8\">Lore</u></a>"), "trained in Lore")
     

    def test_normalize_feat_data(self):
        directory_path = os.getcwd()
        self.assertGreater(len(self.func.normalize_feat_data(self.func.load_feats(directory_path+"/featscsv/RadGridExport-1.csv"))), 0)
    
    def test_build_feats(self):
        self.assertGreater(len(self.func.build_feats()), 0)

    def test_save_feats(self):
        directory_path = os.getcwd()
        self.func.save_feats(self.func.build_feats())
        #file = open(directory_path+"/feats-pf2-v3.json", "r") 
        #self.assertIsNotNone(file)



if __name__ == '__main__':
    unittest.main()