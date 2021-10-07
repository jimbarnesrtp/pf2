from bs4 import BeautifulSoup
import json
import datetime
from pf2helpers import Pf2Helpers
import os
import re

class BuildSpells:

    data_holder = {}
    data_holder['name'] = 'Pathfinder 2.0 SpellList v3'
    data_holder['date'] = datetime.date.today().strftime("%B %d, %Y")

    pf = Pf2Helpers()

    def build_spells(self):
        all_data = []
        cur_path = os.getcwd()
       
        file_name = cur_path+"/spellscsv/RadGridExport.csv"
        raw_data = self.pf.load_csv(file_name)
        all_data = self.normalize_spell_data(raw_data)
        return all_data

    def normalize_spell_data(self, data_list):
        norm_spells = []
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
            full_data = self.get_spell_details(new_data)
            #full_data = new_data

            norm_spells.append(full_data)
        return norm_spells
    
    def get_spell_details(self, data):
        blacklist = ['[document]','noscript','header','html','meta','head', 'input','script', 'h1','img','h3']
        #print("details:", data)
        main = self.pf.load_html(data['link'])
        children = self.pf.split_children_by_rule(main, "<hr")
        header_data = self.parse_header(children[0])
        for key in header_data.keys():
            data[key] = header_data[key]
        

        data['description'] = self.pf.parse_text_from_html(children[1], blacklist)
        if len(children) > 2:
            data['heightened'] = self.parse_heightened(self.pf.parse_text_from_html(children[2], blacklist))


        
        return data

    def parse_heightened(self, text):
        indicies = []
        found_spots = re.finditer("Heightened", text)
        
        for spot in found_spots:
            if spot.start() != 0:
                string_part = {}
                string_part['end'] = spot.start()
                string_part['start'] = indicies[-1]['end']
                indicies.append(string_part)
            else:
                string_part = {}
                string_part['end'] = spot.start()
                string_part['start'] = 0
                indicies.append(string_part)

        height_list = []
        #print("Indicies:", indicies)
        if len(indicies) > 0:
            for part in indicies:
                if(part['start'] != part['end']):

                    height_list.append(text[part['start']:part['end']])
            height_list.append(text[indicies[-1]['end']:])
        return height_list




    def parse_header(self, child):
        child_data = {}
        data = BeautifulSoup(child, 'html5lib')
        anchors = data.find_all("a")
        img = data.find_all("img", {'class': 'actiondark'})
        if len(img) > 0 :
            child_data['action'] =  img[0]['alt']
        else:
            child_data['action'] = '-'
        for anchor in anchors:
            if "Bloodlines" in anchor['href']:
                child_data['bloodline'] = anchor.text
            elif "Rules" in anchor['href']:
                if 'component' in child_data:
                    add_data = ", " + anchor.text
                    child_data['component'] += add_data
                else:
                    child_data['component'] = anchor.text
        child_data['attributes'] = self.parse_spell_attributes(child)

        return child_data

    def parse_spell_attributes(self, child):
        blacklist = ['[document]','noscript','header','html','meta','head', 'input','script', 'h1','img','h3']

        cast_position = child.find('Cast')  
        bold_past_cast_position = child.find("<b>", cast_position) 
        split_data = child[bold_past_cast_position:]
        split_html = BeautifulSoup(split_data, 'html5lib') 
        attributes = self.pf.parse_text_from_html(split_html, blacklist)
        new_attrs = self.objectify_spell_attrs(attributes)
        new_attrs['raw'] = attributes
        return new_attrs

    def objectify_spell_attrs(self, attrs):
        key_words = ['Targets', 'Range', 'Duration', 'Saving Throw', 'Area']
        attr_locs = []
        for key_word in key_words:
            index = attrs.find(key_word)
            if index > -1:
                attr_loc = {}
                attr_loc['keyword'] = key_word
                attr_loc['start'] = index
                attr_locs.append(attr_loc)
        

        new_locs = sorted(attr_locs, key=lambda loc: loc['start'])
        slices = self.get_slices_from_locs(new_locs)
        attributes = {}
        for piece in slices:
            start_loc = piece['start'] + len(piece['keyword'])
            if piece['end'] == -1:
                attributes[piece['keyword']] = attrs[start_loc:]
            else:
                attributes[piece['keyword']] = attrs[start_loc:piece['end']]
        attributes['raw'] = attrs
        
        return attributes
        
# will pull out the exact slices to request from the text
    def get_slices_from_locs(self, new_locs):
        slices = []
        i = 0
        while i < len(new_locs):
            attr = {}
            t = i +1
            attr['start'] = new_locs[i]['start']
            if t == len(new_locs):
                attr['end'] = -1
            else:
                attr['end'] = new_locs[i+1]['start']
            attr['keyword'] = new_locs[i]['keyword']
            slices.append(attr)
            i += 1
        return slices

    def save_data(self, data):
        self.data_holder['spells'] = data
        json_data = json.dumps(self.data_holder, indent=4)
#       print(json_data)
        filename = "json/spells-pf2-v3.json"
        f = open(filename, "w")
        f.write(json_data)
        f.close
        return json_data



def main():
    bs = BuildSpells()
    bs.save_data(bs.build_spells())

if __name__ == "__main__":
    main()
    