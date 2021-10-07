# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import json
import datetime
from pf2helpers import Pf2Helpers
import os
import re

data_holder = {}
data_holder['name'] = 'Pathfinder 2.0 ItemList v2'
data_holder['date'] = datetime.date.today().strftime("%B %d, %Y")

class ItemBuilder():

    item_keywords = ['name','source', 'rarity', 'category', 'subcategory']

    blacklist = ['[document]','noscript','header','html','meta','head', 'input','script', 'h1','img','i','a','b','h3']

    pf = Pf2Helpers()

    weapons = []

    def load_all_items(self):
        all_data = []
        cur_path = os.getcwd()
        i = 1
        while i < 5:
            file_name = cur_path+"/itemcsv/RadGridExport-%s.csv" % i
            raw_data = self.pf.load_csv(file_name)
            all_data.extend(raw_data)
            i += 1

        self.load_weapons()
        return all_data

    def load_weapons(self):
        cur_path = os.getcwd()
        raw_data = self.pf.load_csv(cur_path+"/itemcsv/BaseWeapons.csv")
        link_list = ['name','source', 'rarity', 'group']
        self.weapons = self.normalize_data(raw_data, link_list)

    #""Price","Damage","Hands","Range","Reload","Bulk","Group"

    
    def normalize_data(self, data_list, link_list):
        norm_data = []

        for data in data_list:
            keys = list(data.keys())
            new_data = {}
            for key in keys:
                if key in link_list:
                    new_data[key] = self.pf.norm_link(data[key])
                elif key == 'pfs':
                    new_data[key] = self.pf.norm_pfs(data[key])
                elif key == 'level':
                    value = data[key]
                    if value == "—":
                        new_data[key] = value
                    else:
                        new_data[key] = int(value)
                elif key == 'traits':
                    new_data[key] = self.pf.norm_multi(data[key])
                else:
                    new_data[key] = data[key]
            new_data['link'] = self.pf.norm_url(data['name'])
            norm_data.append(new_data)

        return norm_data

    def populate_data(self, data):
        new_data = {}
        new_data.update(data)
        

        main = self.pf.load_html(new_data['link'])
        if new_data['category'] == "Snares":
            new_data = self.parse_others(new_data, main)
        if new_data['category'] == "Vehicles":
            new_data = self.parse_vehicles(new_data, main)
        elif new_data['category'] != "Wands":
            new_data = self.parse_regular(new_data, main)

        #print('HTML', main)
        if new_data['category'] == "Weapons":
            new_data = self.parse_weapon_preload_stats(new_data)

        return new_data
    
    def parse_vehicles(self, new_data, main):
        blacklist = ['[document]','noscript','header','html','meta','head', 'input','script', 'h1','img','h3', 'h2', 'h1']
        children = self.pf.split_children_by_rule(main, "<h2")
        while("" in children) :
            children.remove("")
        child_pos = 0
        while child_pos < len(children):
            if child_pos == 0:
                stats = self.pf.parse_text_from_html(children[0], blacklist)
                key_words = ['Price', 'Hands', 'Range', 'Category', 'Group', 'Traits', 'Damage', 'Bulk', 'Source', 'Favored Weapon', 'Usage', 'Space', 'Crew', 
            'Piloting Check', 'AC', 'Fort', 'Hardness', 'HP', 'Immunities', 'Speed', 'Collision','Passengers']
                objectified = self.pf.objectify_attributes(stats, key_words)
                new_data.update(objectified)
                new_data.pop("raw", None)
            child_pos += 1
        return new_data


    def parse_others(self, new_data, main):
        blacklist = ['[document]','noscript','header','html','meta','head', 'input','script', 'h1','img','h3']
        children = self.pf.split_children_by_rule(main, "<hr")
        while("" in children) :
            children.remove("")
        child_pos = 0
        while child_pos < len(children):
            if child_pos == 1:
                description = self.pf.parse_text_from_html(children[child_pos], blacklist)
                new_data['description'] = description
            child_pos += 1
        return new_data


    def parse_regular(self, new_data, main):
        blacklist = ['[document]','noscript','header','html','meta','head', 'input','script', 'h1','img','h3']
        children = self.pf.split_children_by_rule(main, "<h2")
        while("" in children) :
            children.remove("")
        child_pos = 0
        while child_pos < len(children):
            if child_pos == 0:
                pos = children[0].find("<hr")
            
                stats= self.parse_details(children[0][0:pos])
                if new_data['category'] == 'Weapons'and "Category" in stats:
                    weapon_cat = stats['Category']
                    stats.pop("Category", None)
                    stats['weaponCat'] = weapon_cat
                for key in stats:
                    new_data[key.lower()] = stats[key]
                new_data.pop("raw", None)
                new_data['description'] = self.pf.parse_text_from_html(children[0][pos:], blacklist)

            elif child_pos > 0:
                if "Critical Specialization Effects" in children[child_pos]:
                    crit = self.parse_crit(children[child_pos])
                    new_data['critEffects'] = crit
                elif "Traits" in children[child_pos]:
                    traits = self.parse_traits(children[child_pos])
                    new_data['traitDetails'] = traits
                
                #print(attack)
                
            child_pos += 1
        return new_data
    
    def parse_details(self, text):

        blacklist = ['[document]','noscript','header','html','meta','head', 'input','script', 'h1','img','h3']
        stripped_text = self.pf.parse_text_from_html(text, blacklist)
        #Source Core Rulebook pg. 282 2.0 Price — (Varies); Damage Varies; Bulk L Hands 1; Range 20 ft. Category Martial Group Bomb; Traits Varies, '
        key_words = ['Price', 'Hands', 'Range', 'Category', 'Group', 'Traits', 'Damage', 'Bulk', 'Source', 'Favored Weapon', 'Usage', 'Space', 'Crew', 
            'Piloting Check', 'AC', 'Fort', 'Hardness', 'HP', 'Immunities', 'Speed', 'Collision','Passengers']
        objectified = self.pf.objectify_attributes(stripped_text, key_words)
        #objectified.pop("Source", None)
        return objectified

    
    def parse_crit(self, text):
        blacklist = ['[document]','noscript','header','html','meta','head', 'input','script', 'h1','img','h3', 'h2']
       
        found_list = re.finditer("<b>(.*?)</b>", text)

        for match in found_list:
            key = text[match.start():match.end()]
            #print("Key:", key)
            if "Source" not in key:
                #print("Match:", text[match.start():])
                stripped_text = self.pf.parse_text_from_html(text[match.start():], blacklist)

        return stripped_text

    def parse_traits(self, text):
        #print("Traits:", text)
        blacklist = ['[document]','noscript','header','html','meta','head', 'input','script', 'h1','img','h3', 'h2']
        traits = []
        found_list = re.finditer('<div class="trait-entry">(.*?)</div>', text)
        for match in found_list:
            trait = {}
            #print(match.group())
            key = re.findall('<b>(.*?)</b>', match.group())[0]
            pos = match.group().find("</b>")
            trait[key] = self.pf.parse_text_from_html(match.group()[pos:], blacklist)
            traits.append(trait)
        return traits

    def parse_weapon_preload_stats(self, data):
        key_list = ['type', 'range', 'reload']
        #print("never called")
        weapon_name = data['name']
        for weapon in self.weapons:
            if weapon['name'] == weapon_name:
                for key in weapon.keys():
                    if key in key_list:
                        data[key] = weapon[key]
 
        return data

    def save_data(self, data):
        data_holder['items'] = data
        json_data = json.dumps(data_holder, indent=4)
#       print(json_data)
        filename = "json/items-pf2-v2.json"
        f = open(filename, "w")
        f.write(json_data)
        f.close
        return json_data
        


def main():
    bf = ItemBuilder()
    data = bf.load_all_items()
    norm_data = bf.normalize_data(data, bf.item_keywords)
    final_data = []
    for data_point in norm_data:
        final_data.append(bf.populate_data(data_point))
    bf.save_data(final_data)


    #bf.save_data(bf.build_monsters())



if __name__ == '__main__':
   main()