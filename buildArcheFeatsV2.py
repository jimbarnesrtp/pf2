from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import csv
import os

feat_holder = {}
feat_holder['name'] = 'Pathfinder 2.0 ArcheType Feat List'
feat_holder['date'] = datetime.date.today().strftime("%B %d, %Y")

class BuildArchetypes:

    holder = {}

    def load_links(self):
        with open("archetypes.csv", encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            arch_list = []
            #"class","link"
            for row in csv_reader:

                arch_data = {}
                arch_data['class'] = row['class']
                arch_data['link'] = row['link']

                arch_list.append(arch_data)
                #print(tl_data)
            return arch_list

    def load_other_arch_feats(self):
        list_of_links2 = []
        main = self.load_html("https://2e.aonprd.com/Archetypes.aspx")
        h2s = main.find_all("h2", {"class": "title"})
        for row in h2s:
            #print(row.text)
            children = row.findChildren(recursive=False)
            #print(children[0]['href'])
            list_of_links2.append({'name': row.text, 'link':"https://2e.aonprd.com/"+children[0]['href']})
        return list_of_links2

    def load_multi_class_feats(self, link_items):
        for link_item in link_items:
            print("link", link_item['link'])
            self.holder[link_item['class']] = self.get_multi_feats(link_item['link'])

    
    def load_html(self, link):
        res2 = requests.get(link)
        res2.raise_for_status()
        soup2 = BeautifulSoup(res2.text, 'html5lib')
        main = soup2.find("span", {'id':'ctl00_RadDrawer1_Content_MainContent_DetailedOutput'})
        return main

    def split_children(self, children):
        string_holder = []
        preamble_holder = []
        split_children = []

        string = " "

        for child in children:
            string_contents = str(child)
            if string_contents.startswith("<h2"):
                split_children.append(string.join(string_holder))
                string_holder = []
            string_holder.append(string_contents)

        return split_children
                    
    
    def get_multi_feats(self, link):
        items = []

        children = self.load_html(link).contents
        items = self.split_children(children)
        
        return items

    def save_feats(self):
        feat_holder['archTypeFeats'] = self.holder
        json_data = json.dumps(self.holder, indent=4)
#       print(json_data)
        filename = "feats-arche-pf2-v3.json"
        f = open(filename, "w")
        f.write(json_data)
        f.close


def main():
    bf = BuildArchetypes()

    link_items = bf.load_links()
    bf.load_multi_class_feats(link_items)
    bf.save_feats()


if __name__ == "__main__":
    main()
    