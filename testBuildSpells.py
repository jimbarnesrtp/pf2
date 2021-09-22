import unittest
from buildSpellsV3 import BuildSpells
import os

class TestBuildSpells(unittest.TestCase):



    def setUp(self):
        unittest.TestLoader.sortTestMethodsUsing = None
        self.func = BuildSpells()

    def test(self):
        self.assertTrue(True)

    # def test_load_spells(self):
    #     directory_path = os.getcwd()
    #     spells = self.func.pf.load_csv(directory_path+"/spellscsv/RadGridExport.csv")
    #     print("Spells:", spells[0])
    #     self.assertGreater(len(spells),0)

    # def test_normalize_spells(self):
    #     directory_path = os.getcwd()
    #     raw = self.func.pf.load_csv(directory_path+"/spellscsv/RadGridExport.csv")
    #     print("Spell:", self.func.normalize_spell_data(raw)[0])
    #     self.assertGreater(len(raw), 0)

    # def test_spell_details(self):
    #     directory_path = os.getcwd()
    #     raw = self.func.pf.load_csv(directory_path+"/spellscsv/RadGridExport.csv")
    #     spell = self.func.get_spell_details(self.func.normalize_spell_data(raw)[0])
    #     print("SpellFull:", spell)
    #     self.assertIsNotNone(spell)
    
    def test_parse_header(self):
        text = '<h1 class="title"><a href="PFS.aspx"><span style="float:left;"><img alt="PFS Standard" src="Images\\Icons\\PFS_Standard.png" style="height:25px; padding:2px 10px 0px 2px" title="PFS Standard"/></span></a>Acid Splash<span style="margin-left:auto; margin-right:0">Cantrip 1</span></h1> <span alt="Acid Trait" class="trait" title="Effects with this trait deal acid damage. Creatures with this trait have a magical connection to acid."><a href="Traits.aspx?ID=3">Acid</a></span> <span alt="Attack Trait" class="trait" title="An ability with this trait involves an attack. For each attack you make beyond the first on your turn, you take a multiple attack penalty."><a href="Traits.aspx?ID=15">Attack</a></span> <span alt="Cantrip Trait" class="trait" title="A spell you can cast at will that is automatically heightened to half your level rounded up."><a href="Traits.aspx?ID=22">Cantrip</a></span> <span alt="Evocation Trait" class="trait" title="Effects and magic items with this trait are associated with the evocation school of magic, typically involving energy and elemental forces."><a href="Traits.aspx?ID=65">Evocation</a></span> <br/> <b>Source</b>   <a class="external-link" href="https://paizo.com/products/btq01y0k?Pathfinder-Core-Rulebook" target="_blank"><i>Core Rulebook pg. 316</i></a>   <sup><a class="external-link" href="Sources.aspx?ID=1">2.0</a></sup> <br/> <b>Traditions</b>   <u><a href="Spells.aspx?Tradition=1">arcane</a></u> ,  <u><a href="Spells.aspx?Tradition=4">primal</a></u> <br/> <b>Bloodline</b>   <u><a href="Bloodlines.aspx?ID=3">demonic</a></u> <br/> <b>Cast</b>   <img alt="Two Actions" class="actiondark" src="Images\\Actions\\TwoActions.png" style="height:15px; padding:0px 2px 0px 2px"/> <img alt="Two Actions" class="actionlight" src="Images\\Actions\\TwoActions_I.png" style="height:15px; padding:0px 2px 0px 2px"/>   <a href="Rules.aspx?ID=283"><u>somatic</u></a> , <a href="Rules.aspx?ID=284"><u>verbal</u></a> <br/> <b>Range</b>  30 feet;  <b>Targets</b>  1 creature'

        data = self.func.parse_header(text)
        print("Data:", data)
        self.assertIsNotNone(data)

    def test_parse_heightened(self):
        text = '<hr/> <b>Heightened (3rd)</b>  The initial damage increases to 1d6 + your spellcasting ability modifier, and the persistent damage increases to 2. <br/> <b>Heightened (5th)</b>  The initial damage increases to 2d6 + your spellcasting ability modifier, the persistent damage increases to 3, and the splash damage increases to 2. <br/> <b>Heightened (7th)</b>  The initial damage increases to 3d6 + your spellcasting ability modifier, the persistent damage increases to 4, and the splash damage increases to 3. <br/> <b>Heightened (9th)</b>  The initial damage increases to 4d6 + your spellcasting ability modifier, the persistent damage increases to 5, and the splash damage increases to 4.'
        blacklist = ['[document]','noscript','header','html','meta','head', 'input','script', 'h1','img','h3']
        data = self.func.pf.parse_text_from_html(text, blacklist)
        parsed = self.func.parse_heightened(data)
        print("Parsed:", parsed)
        self.assertIsNotNone(parsed)

    def test_parse_spell_attributes(self):
        text = '<h1 class="title"><a href="PFS.aspx"><span style="float:left;"><img alt="PFS Standard" src="Images\\Icons\\PFS_Standard.png" style="height:25px; padding:2px 10px 0px 2px" title="PFS Standard"/></span></a>Acid Splash<span style="margin-left:auto; margin-right:0">Cantrip 1</span></h1> <span alt="Acid Trait" class="trait" title="Effects with this trait deal acid damage. Creatures with this trait have a magical connection to acid."><a href="Traits.aspx?ID=3">Acid</a></span> <span alt="Attack Trait" class="trait" title="An ability with this trait involves an attack. For each attack you make beyond the first on your turn, you take a multiple attack penalty."><a href="Traits.aspx?ID=15">Attack</a></span> <span alt="Cantrip Trait" class="trait" title="A spell you can cast at will that is automatically heightened to half your level rounded up."><a href="Traits.aspx?ID=22">Cantrip</a></span> <span alt="Evocation Trait" class="trait" title="Effects and magic items with this trait are associated with the evocation school of magic, typically involving energy and elemental forces."><a href="Traits.aspx?ID=65">Evocation</a></span> <br/> <b>Source</b>   <a class="external-link" href="https://paizo.com/products/btq01y0k?Pathfinder-Core-Rulebook" target="_blank"><i>Core Rulebook pg. 316</i></a>   <sup><a class="external-link" href="Sources.aspx?ID=1">2.0</a></sup> <br/> <b>Traditions</b>   <u><a href="Spells.aspx?Tradition=1">arcane</a></u> ,  <u><a href="Spells.aspx?Tradition=4">primal</a></u> <br/> <b>Bloodline</b>   <u><a href="Bloodlines.aspx?ID=3">demonic</a></u> <br/> <b>Cast</b>   <img alt="Two Actions" class="actiondark" src="Images\\Actions\\TwoActions.png" style="height:15px; padding:0px 2px 0px 2px"/> <img alt="Two Actions" class="actionlight" src="Images\\Actions\\TwoActions_I.png" style="height:15px; padding:0px 2px 0px 2px"/>   <a href="Rules.aspx?ID=283"><u>somatic</u></a> , <a href="Rules.aspx?ID=284"><u>verbal</u></a> <br/> <b>Range</b>  30 feet;  <b>Targets</b>  1 creature'

        data = self.func.parse_spell_attributes(text)
        print("Parsed:", data)
        self.assertIsNotNone(data)

    def test_objectifying_attrs1(self):
        print("Sorted1:", self.func.objectify_spell_attrs("Range 10 feet; Targets 1 object (cook, lift, or tidy only) Duration sustained"))
        print("Sorted2:", self.func.objectify_spell_attrs("Range 30 feet; Targets 1 creature"))
        print("Sorted1:", self.func.objectify_spell_attrs("Range 30 feet; Targets your eidolon , or a creature with the minion trait under your control Duration until the start of your next turn"))
        print("Sorted1:", self.func.objectify_spell_attrs("Range 5 feet; Targets 1 creature Saving Throw Fortitude"))

    


    
    #def test_save_data(self):
        #self.assertIsNotNone(self.func.save_data(self.func.build_monsters()))
    

if __name__ == '__main__':
    unittest.main()
