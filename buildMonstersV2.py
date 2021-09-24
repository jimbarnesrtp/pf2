from bs4 import BeautifulSoup
import json
import datetime
from pf2helpers import Pf2Helpers
import os
import re

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
            #print("Link:", new_data['link'])
            #full_data = self.get_details(new_data)
            full_data = new_data

            norm_monsters.append(full_data)
        return norm_monsters

    def get_details(self, data):
        main = self.pf.load_html(data['link'])

        children = self.pf.split_children_by_rule(main, "<h1")
        while("" in children) :
            children.remove("")

        child_pos = 0
        while child_pos < len(children):
            if child_pos == 0:
                header = self.parse_header(children[0])
                for key1 in header:
                    data[key1] = header[key1]
            elif child_pos == 1:
                stats = self.parse_stats(children[1])
                for key2 in stats:
                    data[key2] = stats[key2]
                defense = self.parse_defense(children[1])
                for key3 in defense:
                    data[key3] = defense[key3]
                
            child_pos += 1
            
        
        #data['raw'] = main
        return data

    
    def parse_header(self, header):
        data = {}
        blacklist = ['[document]','noscript','header','html','meta','head', 'input','script', 'h1','img','h3']
        position_of_weak = header.find("<h2>")
        
        raw_text = self.pf.parse_text_from_html(header[0:position_of_weak], blacklist)

        found_spots = re.finditer("Recall Knowledge", raw_text)
        spots = []
        start = 0
        for spot in found_spots:
            part = {}
            part['start'] = start
            part['end'] = spot.start()
            spots.append(part)
            start = spot.start()

        if len(spots) == 0:
            description = raw_text
        else:
            description = raw_text[0:spots[0]['end']]
            dc_checks = raw_text[spots[0]['end']:]
            recall_knowledge = self.parse_recall(dc_checks)
            data['recallKnowledge'] = recall_knowledge

        data['description'] = description

        return data

  

            #Recall Knowledge - Humanoid ( Society ) : DC 20 Recall Knowledge - Undead (Religion) : DC 22
    def parse_recall(self, text):
        knowledges = []
        key = "Recall"

        pieces = text.split(" ")
        start = True
        holder = ""
        for piece in pieces:
            if key == piece:

                if start:
                    holder += piece
                    start = False
                else:
                    part = self.split_by_key(holder, ":")
                    recall = {}
                    recall[part[0]] = part[1]
                    knowledges.append(recall)
                    holder = ""
                    start = False
            else:
                holder += piece
                
        part = self.split_by_key(holder, ":")
        recall = {}
        recall[part[0]] = part[1]
        knowledges.append(recall)

        return knowledges

    def parse_stats(self, child):
        position = child.find("</sup>")
        raw_text = child[position+6:]
        first_hr = raw_text.find("<hr")

        stats_text = raw_text[0:first_hr]
        #print("Stats:", stats_text)
        abilities = self.parse_abilities(stats_text)
        
        
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++")
        #print("Children: ", raw_text)
        return abilities

    def parse_abilities(self, text):
        blacklist = ['[document]','noscript','header','html','meta','head', 'input','script', 'h1','img','h3']
        stripped_text = self.pf.parse_text_from_html(text, blacklist)
        key_words = ['Perception', 'Languages', 'Skills', 'Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha', "Items"]
        objectified = self.pf.objectify_attributes(stripped_text, key_words)

        #print(objectified)
        return objectified

    def parse_defense(self, child):
        position = child.find("<hr/>")
        raw_text = child[position+6:]
        first_hr = raw_text.find("<hr")
        defense_text = raw_text[0:first_hr]
        reaction_pos = defense_text.find('<img alt="Reaction"')
        if reaction_pos > 0:

            holder_defense_text = defense_text[0:reaction_pos]
            reaction_name_position = holder_defense_text.rindex("<b>")
            trimmed_defense_text = defense_text[0:reaction_name_position]
            reaction_text = defense_text[reaction_name_position:]
        else:
            trimmed_defense_text = defense_text
        
        #print("Defense Text:", trimmed_defense_text)
        blacklist = ['[document]','noscript','header','html','meta','head', 'input','script', 'h1','img','h3']
        stripped_text = self.pf.parse_text_from_html(trimmed_defense_text, blacklist)
        checked_text = stripped_text.replace("Attack of Opportunity", "")
        key_words = ['AC', 'Fort', 'Ref', 'Will', 'HP', 'Resistances']
        objectified = self.pf.objectify_attributes(checked_text, key_words)
        if len(reaction_text) > 0:
            objectified['reactions'] = self.pf.parse_text_from_html(reaction_text, blacklist)

        print("Defense:", objectified)
        return objectified


    def split_by_key(self, text, key):
        position = text.find(key)
        pieces = []
        pieces.append(text[0:position])
        pieces.append(text[position+1:])
        return pieces

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


        
