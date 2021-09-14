import unittest
from buildArcheFeatsV2 import BuildArchetypes
import os

class TestBuildArcheFeatsV2(unittest.TestCase):

    def setUp(self):
        unittest.TestLoader.sortTestMethodsUsing = None
        self.func = BuildArchetypes()

    def test(self):
        self.assertTrue(True)

    def test_load_csv(self):
        self.assertGreater(len(self.func.load_links()), 0)
    
    def test_load_html(self):
        stuff = self.func.load_html("https://2e.aonprd.com/Archetypes.aspx?ID=1")
        #print("stuff:", stuff)
        self.assertIsNotNone(self)

    def test_load_multi(self):
        stuff2 = self.func.get_multi_feats("https://2e.aonprd.com/Archetypes.aspx?ID=1")
        print("stuff2:", stuff2)
        self.assertGreater(len(stuff2),0)
    
    #def test_load_other_arche_feats(self):
        #self.assertGreater(len(self.func.load_other_arch_feats()), 0)
    
    #def test_load_multi2(self):
        #self.assertIsNotNone(self.func.load_html("https://2e.aonprd.com/Archetypes.aspx?ID=45"))
    



if __name__ == '__main__':
    unittest.main()