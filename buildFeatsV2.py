from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import csv
import os

feat_holder = {}
feat_holder['name'] = 'Pathfinder 2.0 feat list v3'
feat_holder['date'] = datetime.date.today().strftime("%B %d, %Y")


class BuildFeatsV2:

    #"Name","PFS","Source","Rarity","Traits","Level","Prerequisites","Benefits","Spoilers?"


    def load_feats(self, file_name):
        with open(file_name, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            feats_list = []
            for row in csv_reader:

                feat_data = {}
                feat_data['name'] = row['Name']
                feat_data['pfs'] = row['PFS']
                feat_data['source'] = row['Source']
                feat_data['rarity'] = row['Rarity']
                feat_data['traits'] = row['Traits']
                feat_data['level'] = row['Level']
                feat_data['prereqs'] = row['Prerequisites']
                feat_data['benefits'] = row['Benefits']
                feat_data['spoilers'] = row['Spoilers?']
                feats_list.append(feat_data)
                #print(tl_data)
            return feats_list

    
    def normalize_feat_data(self, feat_list):
        norm_feats = []
        for feat in feat_list:
            new_feat = {}
            new_feat['name'] = self.norm_link(feat['name'])
            new_feat['pfs'] = self.norm_pfs(feat['pfs'])
            new_feat['source'] = self.norm_link(feat['source'])
            new_feat['rarity'] = self.norm_link(feat['rarity'])
            new_feat['traits'] = self.norm_traits(feat['traits'])
            new_feat['level'] = int(feat['level'])
            new_feat['link'] = self.norm_url(feat['name'])
            new_feat['prereqs'] = self.norm_prereqs(feat['prereqs'])
            new_feat['benefits'] = feat['benefits']
            new_feat['spoilers'] = feat['spoilers']
            new_feat['text'] = 'text'


            norm_feats.append(new_feat)
        return norm_feats

    def norm_link(self, name):
        soup = BeautifulSoup(name, 'html5lib')
        href = soup.find_all("a")
        return href[0].text

    def norm_pfs(self, pfs):
        soup = BeautifulSoup(pfs, 'html5lib')
        img = soup.find_all("img")
        if(len(img) == 0):
            return "Excluded"
        else:
            return img[0]['alt']

    def norm_traits(self, traits):
        trait_list = traits.split(",")
        ret_traits = []
        if (len(traits) > 1):
            for trait in trait_list:
                ret_traits.append(self.norm_link(trait))
        
        return ret_traits

    def norm_url(self, url):
        soup = BeautifulSoup(url, 'html5lib')
        href = soup.find_all("a")
        return "https://2e.aonprd.com/"+href[0]['href']

    def norm_prereqs(self, prereq):
        soup = BeautifulSoup(prereq, 'html5lib')
        text = ''.join(soup.html.findAll(text=True))
        #print("prereqs:", text)
        return text


    def build_feats(self):
        all_feats = []
        cur_path = os.getcwd()
        i = 1
        while i < 7:
            file_name = cur_path+"/featscsv/RadGridExport-%s.csv" % i
            raw_feats = self.load_feats(file_name)
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

def main():
    bf = BuildFeatsV2()


if __name__ == "__main__":
    main()