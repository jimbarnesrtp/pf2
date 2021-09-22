from bs4 import BeautifulSoup
import json
import datetime
from pf2helpers import Pf2Helpers

import os

data_holder = {}
data_holder['name'] = 'Pathfinder 2.0 MonsterList v2'
data_holder['date'] = datetime.date.today().strftime("%B %d, %Y")



class BuildMonsters:

    #"Name","Family","Source","Rarity","Size","Type","Traits","Level","Spoilers?"
    blacklist = ['[document]','noscript','header','html','meta','head', 'input','script', 'h1','img','i','a','b','h3']

    pf = Pf2Helpers()
    
    def normalize_monster_data(self, data_list):
        norm_monsters = []
        link_list = ['name', 'source', 'rarity', 'family', 'type']
        for data in data_list:
            keys = list(data.keys())
            new_data = {}
            for key in keys:
                if key in link_list:
                    new_data[key] = self.pf.norm_link(data[key])
                elif key == 'traits':
                    new_data[key] = self.pf.norm_multi(data[key])
                else:
                    new_data[key] = data[key]
            new_data['link'] = self.pf.norm_url(data['name'])
            full_data = self.get_details(new_data)

            norm_monsters.append(new_data)
        return norm_monsters

    def get_details(self, data):
        main = self.pf.load_html(data['link'])
        children = self.pf.split_children(main)


        return data


    def build_monsters(self):
        all_data = []
        cur_path = os.getcwd()
       
        file_name = cur_path+"/monstercsv/RadGridExport.csv"
        raw_data = self.pf.load_csv(file_name)
        all_data = self.normalize_monster_data(raw_data)
        return all_data

    def save_data(self, data):
        data_holder['monsters'] = data
        json_data = json.dumps(data_holder, indent=4)
#       print(json_data)
        filename = "monsters-pf2-v2.json"
        f = open(filename, "w")
        f.write(json_data)
        f.close
        return json_data

def main():
    bf = BuildMonsters()
    bf.save_data(bf.build_monsters())


        
