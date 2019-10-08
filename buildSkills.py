from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import time

skillHolder = {}
skillHolder['name'] = 'Pathfinder 2.0 skill list'
skillHolder['date'] = datetime.date.today().strftime("%B %d, %Y")

def get_acrobatics(link):
    items = []
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    main = soup2.find("span", {'id':'ctl00_MainContent_DetailedOutput'})
    traits = main.find_all("span", {"class" : lambda L: L and L.startswith('trai')})
    children = main.contents
    notFirstH1 = False
    inHeader = False
    parentDetails = {}
    item = {}
    item['link'] = link
    tagType = ""
    itemDetailHolder = []
    for child in children:
        
        stringContents = str(child)
        if stringContents.startswith("<"):
            #print(stringContents)
            if child.name == "img":
                parentDetails['actions'] = child['alt']
            if child.name == "hr":
                tagType = ""
                reachedBreak = True
                inHeader = False
            if child.name == "img":
                item['actions'] = child['alt']
            if child.name == "h1":
                inHeader = True

            if child.name == "b":
                if(child.text != "Source"):
                    tagType = child.text
                    
            if child.name == "a":

                try:
                    if child['class'][0] == "external-link" :
                        item['source'] = child.text
                except:
                    pass
                tagType = ""
            if child.name == "ul":
                #print(child.text)
                lis = child.find_all("li")
                if(len(lis) > 0):
                    spellHolder = []
                    for li in lis:
                        spellHolder.append(li.text)
                    item['spells'] = spellHolder
        else:
                
            if tagType != "":
                item[tagType] = stringContents
                tagType = ""
            else:
                if not stringContents.isspace():
                    itemDetailHolder.append(stringContents)
                #print(stringContents)

    for key in parentDetails.keys():
        item[key] = parentDetails[key]
    item['text'] = detailHolder + itemDetailHolder
    items.append(item)
    
    return items


def get_all():
    skillHolder['acrobatics'] = get_acrobatics("https://2e.aonprd.com/Skills.aspx?ID=1")

    #skillHolder['rangedWeapons'] = get

    
    return skillHolder

#print(get_all())
json_data = json.dumps(get_all())
#print(json_data)
filename = "skills-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close