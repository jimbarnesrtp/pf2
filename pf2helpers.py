import csv
from bs4 import BeautifulSoup
import requests

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
        res2 = requests.get(link)
        res2.raise_for_status()
        soup2 = BeautifulSoup(res2.text, 'html5lib')
        main = soup2.find("span", {'id':'ctl00_RadDrawer1_Content_MainContent_DetailedOutput'})
        return main

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

    def split_children(self, children):
        string_holder = []
        split_children = []

        string = " "

        for child in children:
            string_contents = str(child)
            if string_contents.startswith("<h2"):
                split_children.append(string.join(string_holder))
                string_holder = []
            string_holder.append(string_contents)

        return split_children

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

        