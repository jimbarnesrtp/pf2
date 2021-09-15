import unittest
from buildArchetypes import BuildArchetypes
import os

class TestBuildArcheFeatsV2(unittest.TestCase):

    def setUp(self):
        unittest.TestLoader.sortTestMethodsUsing = None
        self.func = BuildArchetypes()

    def test(self):
        self.assertTrue(True)

    def test_load_links(self):
        self.assertGreater(len(self.func.load_links()), 0)
    
    def test_load_html(self):
        stuff = self.func.load_html("https://2e.aonprd.com/Archetypes.aspx?ID=1")
        #print("stuff:", stuff)
        self.assertIsNotNone(stuff)
    
    def test_load_other_arches(self):
        stuff = self.func.load_other_archetypes()
        #print("other arches:", stuff)
        self.assertGreater(len(stuff), 0)

    def test_split_children(self):
        stuff = self.func.split_children(self.func.load_html("https://2e.aonprd.com/Archetypes.aspx?ID=1"))
        #print("stuff2:", stuff)
        self.assertGreater(len(stuff), 0)

    def test_parse_data(self):
        stuff = self.func.split_children(self.func.load_html("https://2e.aonprd.com/Archetypes.aspx?ID=1"))
        
        data = self.func.parse_data(stuff[0])
        self.assertIsNotNone(data)

    #def test_build_archetype(self):
     #   stuff = self.func.split_children(self.func.load_html("https://2e.aonprd.com/Archetypes.aspx?ID=1"))
      #  data = self.func.build_archetype(stuff)
       # self.assertIsNotNone(data)

    #def test_get_archetype_data(self):
     #   stuff = self.func.get_archetype_data("https://2e.aonprd.com/Archetypes.aspx?ID=1")
      #  #print("arch:",stuff)
       # self.assertIsNotNone(stuff)
    
    #def test_load_archetype_data(self):
        #self.func.load_archetype_data(self.func.load_links())
        #print("Arches:", self.func.holder)
        #self.assertGreater(len(self.func.holder), 0)

    #def test_save_archetypes(self):
        #self.func.load_archetype_data(self.func.load_links())
        #self.func.save_archetypes()
        #self.assertTrue(True)





    

    



if __name__ == '__main__':
    unittest.main()