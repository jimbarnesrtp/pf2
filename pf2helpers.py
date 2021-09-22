import csv
from bs4 import BeautifulSoup
import requests

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
        res2 = requests.get(link, headers)
        res2.raise_for_status()
        soup2 = BeautifulSoup(res2.text, 'html5lib')
        main = soup2.find("span", {'id':'ctl00_RadDrawer1_Content_MainContent_DetailedOutput'})
        return main

    
    def parse_text_from_html(self, html, blacklist):

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
        multi_list = multi.split(",")
        ret_multi = []
        if (len(multi_list) > 1):
            for mult in multi_list:
                ret_multi.append(self.norm_link(mult))
        
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

        