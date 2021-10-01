# -*- coding: utf-8 -*-
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
            full_data = self.load_monster(new_data)
            #full_data = new_data

            norm_monsters.append(full_data)
        return norm_monsters
    
    def load_monster(self, data):
        main_link = data['link']
        print("Monster:", main_link)
        elite_link = main_link+"&Elite=true"
        weak_link = main_link+"&Weak=True"
        main = self.get_details(data['link'], 'main')
        for key in main:
            data[key] = main[key]
        weak = self.get_details(weak_link, 'weak')
        data['weakStats'] = weak
        elite = self.get_details(elite_link, elite_link)
        data['eliteStats'] = elite
        return data

    def get_details(self, link, version):
        main = self.pf.load_html(link)

        children = self.pf.split_children_by_rule(main, "<h1")
        while("" in children) :
            children.remove("")
        data = {}
        child_pos = 0
        while child_pos < len(children):
            if child_pos == 0 and version == 'main':
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
                offensive = self.parse_attack(children[1])
                data['offensive_skills'] = offensive
                #print(attack)
                
            child_pos += 1

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
        
        
        #print("+++++++++++++++++++++++++++++++++++++++++++++++++++")
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
        reaction_text = ""
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

        #print("Defense:", objectified)
        return objectified
        
    def parse_attack(self, child):
        #print("++++++++++++++++++++++++++++++++++++++++++++")
        position = child.find("<hr/>")
        raw_text = child[position+6:]
        first_hr = raw_text.find("<hr")
        attack_text = raw_text[first_hr+6:]
       # print("Attack:", attack_text)
        find_h2 = attack_text.find("<h2")
        find_h3 = attack_text.find("<h3")
        #print("H2:", find_h2, "|h3:", find_h3)
        end_point = self.get_end_point(find_h2, find_h3)
        final_text = attack_text[0:end_point]
        #print("Final Attack: ", final_text)
        
        exclude_list = ['Damage','Saving Throw', 'Stage', 'Cantrips', 'Maximum Duration','(1st)','2nd', '(3rd)', '3rd',  '4th', '5th', '6th', '7th', '8th', '9th']

        spots = []

        found_list = re.finditer("<b>(.*?)</b>", final_text)
        for match in found_list:
            key = final_text[match.start():match.end()]
            if not self.check_key_for_attack(exclude_list, key):
                    part = {}
                    part['start'] = match.start()
                    part['key'] = key
                    spots.append(part)


        # print("-----------------------------")
        # for list_item in spots:
        #     print(list_item)
        
        # print("-------------------------")


        offensive_items = []
        index = 0
        for item in spots:
            #print("########################################")
            #print("key:", item['key'])
            if item == spots[-1]:
                text = final_text[item['start']:-1]
            else:
                next_item = spots[index+1]
                #print("Next Item:", next_item)
                text = final_text[item['start']:next_item['start']]
            
            #print("Text :", text)
            #print("Start:", item['start'])
            offensive_items.append(self.objectify_offensive_part(text))
            #print("########################################")
            index += 1

        #print("########################################")
        return offensive_items

        

    def objectify_offensive_part(self, text):
        #print("text:", text)
        offensive = {}

        match = re.match("<b>(.*?)</b>", text)
        img_find = re.findall('<img alt=["](.*?)["]', text)
        for item in img_find:
            #print("Img = :", item)
            offensive['action'] = item
            break
        
        blacklist = ['[document]','noscript','header','html','meta','head', 'input','script', 'h1','img','h3']
        key = self.pf.parse_text_from_html(match.group(0), blacklist)
        value = self.pf.parse_text_from_html(text[match.end():], blacklist)
        #print("Match:",  key, "|", value)
        offensive[key] = value
        #offensive[]
        #print("Return:", offensive)
        return offensive
    
    def get_end_point(self, find_h2, find_h3):

        if find_h2 > 0 and find_h3 >0:
            if find_h2 > find_h3:
                return find_h3
            else:
                return find_h2
        else:
            if find_h2 > 0:
                return find_h2
            elif find_h3 > 0:
                return find_h3
            else:
                return -1

    def check_key_for_attack(self, list, key):
        #print(list)
        #print("Key:", key)
        #print("IsKeyDigit?", re.match('<b>[-+]?\d+</b>', key))
        if re.match('<b>[-+]?\d+</b>', key):
            return True

        for item in list:
            if item in key or item == key:
                return True
        return False

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

if __name__ == '__main__':
   main()



        
