from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import time

spellHolder = {}
spellHolder['name'] = 'Pathfinder 2.0 Spells v2 list'
spellHolder['date'] = datetime.date.today().strftime("%B %d, %Y")

def get_details(link):
    itemDetails = {}
    res = requests.get(link)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'lxml')
    feat = soup.find_all("div", {'class':'main'})
    detail = soup.find("span", {'id':'ctl00_MainContent_DetailedOutput'})
    traits = detail.find_all("span", {"class" : lambda L: L and L.startswith('trai')})
    traitHolder = []
    for trait in traits:
        traitHolder.append(trait.text)
    itemDetails['traits'] = traitHolder
    #print(detail.contents)
    children = detail.contents
    reachedBreak = False
    reachedCrit = False
    detailHolder = []
    tagType = ""
    string = " "
    fontHolder = []
    spellHolder = []
    for child in children:
        stringContents = str(child)
        if stringContents.startswith("<"):
            if child.name == "hr":
                tagType = ""
                reachedBreak = True
            
            if child.name == "a":
                #print(child['class'][0])
                try:
                    if child['class'][0] == "external-link" :
                        
                        itemDetails['source'] = child.text
                except:
                    if not reachedBreak:
                        if tagType in itemDetails:
                            itemDetails[tagType] += child.text
                        else:
                            itemDetails[tagType] = child.text
                    else:
                        tagType = ""
            if child.name == "ul":
                #print(child.text)
                detailHolder.append(child.text)
            if child.name == "b":

                if(child.text != "Source"):
                    tagType = child.text
            if child.name == "img":
                itemDetails['actions'] = child['alt']
            if child.name == "i":
                if(reachedBreak):
                    detailHolder.append(child.text) 
            #else:
                #if not stringContents.isspace() :
                    #detailHolder.append(child.text)        
        else:
            if tagType != "":
                if tagType in itemDetails:
                    itemDetails[tagType] = itemDetails[tagType] + stringContents
                else:
                    itemDetails[tagType] = stringContents.strip()
                #tagType = ""
            else:
                if not stringContents.isspace():
                    detailHolder.append(stringContents)

    itemDetails['text'] = string.join(detailHolder).strip()
    return itemDetails



def get_spells(link):
    items = []
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    main = soup2.find(lambda tag: tag.name=='span' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_DetailedOutput")
    children = main.contents
    ftagType = ""
    spellLevel = ""
    spellHolder = {}
    for child in children:

        stringContents = str(child)
        #print(stringContents)
        if stringContents.startswith("<"):
            if child.name == "h2":
                if child.text[0:1] == "C":
                    spellLevel = 0
                elif child.text[5:6] == "t" or child.text[5:6] == "s" or child.text[5:6] == "n" or child.text[5:6] == "r":
                    spellLevel = int(child.text[4:5])
                else:
                    spellLevel = int(child.text[4:6])
                
            if child.name == "a":
                spellHolder['name'] = child.text
                spellHolder['link'] = "https://2e.aonprd.com/"+child['href']
                spellHolder['level'] = int(spellLevel)
        else:
            spellHolder['text'] = stringContents
            items.append(spellHolder)
            spellHolder = {}

    t = 0
    for item in items:
        t += 1
        [print("Getting spell:", item['name'])]
        itemDetails = get_details(item['link'])
        for key in itemDetails.keys():
            item[key.replace(" ", "").lower().replace("(","").replace(")","").replace("+","plus")] = itemDetails[key]
        #if t > 3:
            #break
    return items

def get_all():
    spellHolder['spells'] = get_spells("https://2e.aonprd.com/Spells.aspx?Tradition=0")


    #spellHolder['rangedWeapons'] = get

    
    return spellHolder

#print(get_all())
json_data = json.dumps(get_all(), indent=4)
#print(json_data)
filename = "spells-pf2-v2.json"
f = open(filename, "w")
f.write(json_data)
f.close