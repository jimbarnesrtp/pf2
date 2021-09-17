from bs4 import BeautifulSoup
import json
import datetime
from pf2helpers import Pf2Helpers

import os

class BuildSpells:

    data_holder = {}
    data_holder['name'] = 'Pathfinder 2.0 SpellList v3'
    data_holder['date'] = datetime.date.today().strftime("%B %d, %Y")

    pf = Pf2Helpers()

    def build_monsters(self):
        all_data = []
        cur_path = os.getcwd()
       
        file_name = cur_path+"/spellscsv/RadGridExport.csv"
        raw_data = self.pf.load_csv(file_name)
        #all_data = self.normalize_spell_data(raw_data)
        return all_data

    def normalize_spell_data(self, data_list):
        norm_monsters = []
        link_list = ['name', 'source', 'rarity']
        bool_list = ['focus', 'heightenable', 'cantrip']
        multi_list = ['traits', 'traditions']
        for data in data_list:
            keys = list(data.keys())
            new_data = {}
            for key in keys:
                if key in link_list:
                    new_data[key] = self.pf.norm_link(data[key])
                elif key in bool_list:
                    new_data[key] = bool(data[key])
                elif key == 'pfs':
                    new_data[key] = self.pf.norm_pfs(data[key])
                elif key == 'prerequisites':
                    new_data[key] = self.pf.norm_prereqs(data[key])
                elif key in multi_list:
                    new_data[key] = self.pf.norm_multi(data[key])
                elif key == 'level':
                    new_data[key] = int(data[key])
                else:
                    new_data[key] = data[key]
            new_data['link'] = self.pf.norm_url(data['name'])
            full_data = self.get_details(new_data)

            norm_monsters.append(full_data)
        return norm_monsters
    
    def get_spell_details(self, data):
        main = self.pf.load_html(data['link'])
        children = self.pf.split_children(main)

        data['details'] = children
        return data

    
    def save_data(self, data):
        self.data_holder['spells'] = data
        json_data = json.dumps(self.data_holder, indent=4)
#       print(json_data)
        filename = "spells-pf2-v3.json"
        f = open(filename, "w")
        f.write(json_data)
        f.close
        return json_data



def main():
    bs = BuildSpells()
    #bs.save_data(bs.build_monsters())