import csv
from bs4 import BeautifulSoup
import requests
import re

headers = {
    'User-Agent': 'PF2 data to rest builder',
    'From': 'jimbarnesrtp'  # This is another valid field
}

class Pf2Helpers():

    
    def load_csv(self, file_name):
        with open(file_name, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            data_list = []
            for row in csv_reader:

                data = {}
                for field in csv_reader.fieldnames:
                    data[field.lower()] = row[field]
                data_list.append(data)
                #print(tl_data)
        return data_list

    def load_html(self, link):
        res2 = requests.get(link, headers, verify=False)
        res2.raise_for_status()
        soup2 = BeautifulSoup(res2.text, 'html5lib')
        main = soup2.find("span", {'id':'ctl00_RadDrawer1_Content_MainContent_DetailedOutput'})
        return main

    
    def parse_text_from_html(self, html, blacklist: list):

        data_to_parse = ""
        if hasattr(html, "find_all"):
            data_to_parse = html
        else:
            data_to_parse = BeautifulSoup(html, 'html5lib')
        text_holder = []
        text = data_to_parse.find_all(text=True)
        for t in text:
            if t.parent.name not in blacklist:
                #print("t:",t," parent:", t.parent.name)
                text_holder.append(t)
        #this was done to remove extraspaces between words and create a better reading space
        return " ".join(" ".join(text_holder).split())

    def norm_link(self, name):
        #print("norm link:", name)
        if name == "—" or name == "":
            return name
        else:
            soup = BeautifulSoup(name, 'html5lib')
            href = soup.find_all("a")
            return href[0].text

    def norm_multi(self, multi):
        #print("Multi:", multi)
        if multi == "—" or multi == "":
            return multi
        ret_multi = []
        found_list = re.finditer("<u>(.*?)</u>", multi)
        for match in found_list:
            ret_multi.append(self.norm_link(match.group()))
        
        return ret_multi

    def norm_url(self, url):

        #print("URL:", url)
        soup = BeautifulSoup(url, 'html5lib')
        href = soup.find_all("a")
        return "https://2e.aonprd.com/"+href[0]['href']

    def split_children_by_rule(self, children, rule):
        string_holder = []
        split_children = []

        string = " "

        for child in children:
            string_contents = str(child)
            if string_contents.startswith(rule):
                split_children.append(string.join(string_holder))
                string_holder = []
            string_holder.append(string_contents)
        split_children.append(string.join(string_holder))


        return split_children

    def split_children(self, children):
        return self.split_children_by_rule(children, "<h2")

    

    def norm_prereqs(self, prereq):
        soup = BeautifulSoup(prereq, 'html5lib')
        text = ''.join(soup.html.findAll(text=True))
        #print("prereqs:", text)
        return text

    def norm_pfs(self, pfs):
        soup = BeautifulSoup(pfs, 'html5lib')
        img = soup.find_all("img")
        if(len(img) == 0):
            return "Excluded"
        else:
            return img[0]['alt']

    def objectify_attributes(self, attrs, key_words: list):

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
                attributes[piece['keyword'].lower()] = attrs[start_loc:]
            else:
                attributes[piece['keyword'].lower()] = attrs[start_loc:piece['end']]
        attributes['raw'] = attrs
        
        return attributes
    
    # will pull out the exact slices to request from the text
    def get_slices_from_locs(self, new_locs: list):
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

        