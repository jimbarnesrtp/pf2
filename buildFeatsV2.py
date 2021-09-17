from bs4 import BeautifulSoup
import requests
import json
import datetime
import csv
import os
from pf2helpers import Pf2Helpers

feat_holder = {}
feat_holder['name'] = 'Pathfinder 2.0 feat list v3'
feat_holder['date'] = datetime.date.today().strftime("%B %d, %Y")

headers = {
    'User-Agent': 'PF2 data to rest builder',
    'From': 'jimbarnesrtp'  # This is another valid field
}
class BuildFeatsV2:

    #"Name","PFS","Source","Rarity","Traits","Level","Prerequisites","Benefits","Spoilers?"
    pf = Pf2Helpers()
    
    def normalize_feat_data(self, data_list):
        norm_feats = []
        link_list = ['name','source', 'rarity', 'family', 'type']
        for data in data_list:
            keys = list(data.keys())
            new_data = {}
            for key in keys:
                if key in link_list:
                    new_data[key] = self.pf.norm_link(data[key])
                elif key == 'pfs':
                    new_data[key] = self.pf.norm_pfs(data[key])
                elif key == 'prerequisites':
                    new_data[key] = self.pf.norm_prereqs(data[key])
                elif key == 'level':
                    new_data[key] = int(data[key])
                elif key == 'traits':
                    new_data[key] = self.pf.norm_multi(data[key])
                else:
                    new_data[key] = data[key]
            new_data['link'] = self.pf.norm_url(data['name'])
            new_data['text'] = self.get_details(new_data['link'])

            norm_feats.append(new_data)
        return norm_feats

    def build_feats(self):
        all_feats = []
        cur_path = os.getcwd()
        i = 1
        while i < 7:
            file_name = cur_path+"/featscsv/RadGridExport-%s.csv" % i
            raw_feats = self.pf.load_csv(file_name)
            all_feats.extend(self.normalize_feat_data(raw_feats))
            i += 1

        
        return all_feats


    def save_feats(self, feats):
        feat_holder['baseFeats'] = feats
        json_data = json.dumps(feat_holder, indent=4)
#       print(json_data)
        filename = "feats-pf2-v3.json"
        f = open(filename, "w")
        f.write(json_data)
        f.close

    def get_details(self, link):
        res = requests.get(link)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html5lib')
        detail = soup.find("span", {'id':'ctl00_RadDrawer1_Content_MainContent_DetailedOutput'})
        imgs = detail.find_all("img")
        #print(detail.contents)
        children = detail.contents
        reached_break = False
        detail_holder = []
        details = {}

        for child in children:
            string_contents = str(child)
            if string_contents.startswith("<"):
                if string_contents == "<hr/>":
                    reached_break = True
                if reached_break:
                    if child.name == "a":
                        detail_holder.append(child.text)
                    if child.name == "ul":
                        #print(child.text)
                        children3 = child.contents
                        for child3 in children3:
                            string_contents3 = str(child3)
                            if string_contents3.startswith("<") and child3.name == "li":
                                    detail_holder.append(child3.text)
                    if child.name == "h2":
                        break

            else:
                if reached_break:
                    detail_holder.append(string_contents)

            string = " "
            details['text'] = string.join(detail_holder)

        action_list = ['Reaction', 'Single Action', 'Two Actions', 'Three Actions']
        for img in imgs:
            if img['alt'] in action_list:
                details['action_cost'] = img['alt']
            else:
                if "action_cost" not in details:
                    details['action_cost'] = "-"
        return details

def main():
    bf = BuildFeatsV2()
    bf.save_feats(bf.build_feats())


if __name__ == "__main__":
    main()