from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import csv
import os
from pf2helpers import Pf2Helpers

feat_holder = {}
feat_holder['name'] = 'Pathfinder 2.0 ArcheType Feat List'
feat_holder['date'] = datetime.date.today().strftime("%B %d, %Y")

class BuildArchetypes:

    holder = []

    blacklist = ['[document]','noscript','header','html','meta','head', 'input','script', 'h1','img','b','h3']

    pf = Pf2Helpers()

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
    

    def load_other_archetypes(self):
        list_of_links2 = []
        main = self.pf.load_html("https://2e.aonprd.com/Archetypes.aspx")
        h2s = main.find_all("h2", {"class": "title"})
        for row in h2s:
            #print(row.text)
            links = row.find_all("a")

            if len(links) > 1:
                link_to_use = links[1]
            else:
                link_to_use = links[0]
            
            list_of_links2.append({'class': link_to_use.text, 'link':"https://2e.aonprd.com/"+link_to_use['href']})
        return list_of_links2

    
    def parse_data(self, html):
        arch_data = {}
        #print("Type:", type(html))
        data = BeautifulSoup(html, 'html5lib')
        h1s = data.find_all("h1", {"class": "title"})
        anchors = data.find_all("a", {"class": "external-link"})
        img = data.find_all("img")
        arch_data['name'] = h1s[0].text
        arch_data['source'] = anchors[0].text
        if(len(img) == 0):
            arch_data['pfsFlag'] = "Excluded"
        else:
            arch_data['pfsFlag'] = img[0]['alt']
        
        text_holder = []
        text = data.find_all(text=True)
        for t in text:
            if t.parent.name not in self.blacklist:
                #print("t:",t," parent:", t.parent.name)
                text_holder.append(t)
#' '.join(mystring.split())
        arch_data['description'] = " ".join(" ".join(text_holder).split())



        return arch_data

                    
    def build_archetype(self, children):
        for child in children:
            if child.startswith("<h1"):
                #print("child:", child)
                arch_data = self.parse_data(child)
        return arch_data
                

    def get_archetype_data(self, link):
        archetype = {}

        children = self.pf.load_html(link).contents
        children_list = self.pf.split_children(children)
        archetype = self.build_archetype(children_list)
        
        return archetype

    def load_archetype_data(self, link_items):
        for link_item in link_items:
            #print("link", link_item['link'])
            arch_holder = []
            arch_holder.append(self.get_archetype_data(link_item['link']))
            self.holder.extend(arch_holder)

    def save_archetypes(self):
        feat_holder['archtypes'] = self.holder
        json_data = json.dumps(feat_holder, indent=4)
#       print(json_data)
        filename = "json/archetypes-pf2.json"
        f = open(filename, "w")
        f.write(json_data)
        f.close


def main():
    bf = BuildArchetypes()

    link_items = bf.load_links()
    link_items.extend(bf.load_other_archetypes())
    bf.load_archetype_data(link_items)
    bf.save_archetypes()


if __name__ == "__main__":
    main()
    