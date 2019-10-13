from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import time

ritualHolder = {}
ritualHolder['name'] = 'Pathfinder 2.0 rituals list'
ritualHolder['date'] = datetime.date.today().strftime("%B %d, %Y")

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
                    pass
                tagType = ""
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
                itemDetails[tagType] = stringContents
                tagType = ""
            else:
                if not stringContents.isspace():
                    detailHolder.append(stringContents)

    itemDetails['text'] = string.join(detailHolder)
    return itemDetails



def get_rituals(link):
    items = []
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    main = soup2.find(lambda tag: tag.name=='span' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_DetailedOutput")
    children = main.contents
    ftagType = ""
    ritualLevel = ""
    ritualHolder = {}
    for child in children:

        stringContents = str(child)
        #print(stringContents)
        if stringContents.startswith("<"):
            if child.name == "h2":
                ritualLevel = int(child.text[0:1])
            if child.name == "a":
                ritualHolder['name'] = child.text
                ritualHolder['link'] = "https://2e.aonprd.com/"+child['href']
        else:
            ritualHolder['text'] = stringContents
            items.append(ritualHolder)
            ritualHolder = {}

    
    for item in items:
        [print("Getting ritual:", item['name'])]
        itemDetails = get_details(item['link'])
        for key in itemDetails.keys():
            item[key] = itemDetails[key]
    return items




def get_all():
    ritualHolder['rituals'] = get_rituals("https://2e.aonprd.com/Rituals.aspx")

    #ritualHolder['rangedWeapons'] = get

    
    return ritualHolder

#print(get_all())
json_data = json.dumps(get_all())
#print(json_data)
filename = "rituals-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close