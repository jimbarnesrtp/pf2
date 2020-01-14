from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import time

compHolder = {}
compHolder['name'] = 'Pathfinder 2.0 Companion Animal list'
compHolder['date'] = datetime.date.today().strftime("%B %d, %Y")


def get_multi(link):
    items = []
    string = " "
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    main = soup2.find("span", {'id':'ctl00_MainContent_DetailedOutput'})
    children = main.contents
    reachedBreak = False
    reachedItem = False
    detailHolder = []
    notFirstH1 = False
    inHeader = False
    item = {}
    item['link'] = link
    tagType = ""
    itemDetailHolder = []
    inSpecial = False
    specialHolder = {}
    inAttack = False
    attackHolder = {}
    for child in children:
        
        stringContents = str(child)
        if stringContents.startswith("<"): 

            if child.name == "hr":
                if inSpecial:
                    tagType = ""   

            if child.name == "img":
                if inSpecial:
                    specialHolder['actions'] = child['alt']
                elif inAttack:
                    attackHolder['actions'] = child['alt']
                else:
                    item['actions'] = child['alt']
            if child.name == "span":
                if inSpecial:
                    if 'traits' not in specialHolder:
                        specialHolder['traits'] = []
                    specialHolder['traits'].append(child.text)
            if child.name == "h1": 
                if notFirstH1: 
                    item['special'] = specialHolder
                    item['attacks'].append(attackHolder)
                    item['text'] = string.join(detailHolder) + string.join(itemDetailHolder)
                    items.append(item)
                    item = {}
                    item['link'] = link
                    item['attacks'] = []
                    itemDetailHolder = []
                    inSpecial = False
                    specialHolder = {}
                else:
                    notFirstH1 = True
                reachedItem = True
                name = child.text
                item['name'] = child.text[0:].strip()

                print(item['name'])
            if child.name == "h3":
                inSpecial = True
                specialHolder['name'] = child.text[0:].strip()
                tagType = ""

            if child.name == "b":
                if(child.text != "Source"):
                    tagType = child.text.lower().replace(" ", "")

                    if tagType == "melee":
                        if 'damage' in attackHolder:
                            if 'attacks' not in item:
                                item['attacks'] = []
                            item['attacks'].append(attackHolder)
                            attackHolder = {}
                        inAttack = True
                    elif tagType == "damage":
                        inAttack = True
                    else:
                        inAttack = False
                    
            
            if child.name == "u":
                if inSpecial:
                    if tagType != "":
                        if tagType in specialHolder:
                            specialHolder[tagType] += child.text
                        else:
                            specialHolder[tagType] = child.text
                    else:
                        if "text" in specialHolder:
                            specialHolder['text'] += child.text
                        else:
                            specialHolder['text'] = child.text
                elif inAttack:
                    attackHolder['text'] += child.text
                else:
                    if tagType in item:
                        item[tagType] += child.text
                    else:
                        item[tagType] = child.text
            
            if child.name == "li":
                if inSpecial:
                    if tagType != "":
                        if tagType in specialHolder:
                            specialHolder[tagType] += child.text
                        else:
                            specialHolder[tagType] = child.text
                    else:
                        if 'text' in specialHolder:
                            specialHolder['text'] += child.text
                        else:
                            specialHolder['text'] = child.text
                    
            if child.name == "a":
                try:
                    if child['class'][0] == "external-link" :
                        item['source'] = child.text
                except:
                    if inSpecial:
                        if tagType != "":
                            if tagType in specialHolder:
                                specialHolder[tagType] += child.text
                            else:
                                specialHolder[tagType] = child.text
                        else:
                            if 'text' in specialHolder:
                                specialHolder['text'] += child.text
                            else:
                                specialHolder['text'] = child.text
                    elif inAttack:
                        attackHolder['text'] += child.text
                    else:
                        if tagType in item:
                            item[tagType] += child.text
                        else:
                            item[tagType] = child.text
            if child.name == "i":
                if inSpecial:

                    if tagType in item:
                        item[tagType] += child.text
                    else:
                        item[tagType] = child.text
                else: 
                    if tagType in specialHolder:
                        specialHolder[tagType] += child.text
                    else:
                        specialHolder[tagType] = child.text
        else:
            if notFirstH1:
                if inAttack:
                    #print(stringContents)
                    if tagType == "melee":
                        if 'text' not in attackHolder:
                            attackHolder['text'] = ""
                        attackHolder['text'] += stringContents.strip()

                    elif tagType == "damage":
                        attackHolder['damage'] = stringContents.strip()
                elif inSpecial:
                    if tagType != "":
                        if tagType in specialHolder:
                            specialHolder[tagType] += stringContents.strip()
                        else:
                            specialHolder[tagType] = stringContents.strip()
                    else:
                        if "text" in specialHolder:
                            specialHolder['text'] += stringContents.strip()
                        else:
                            specialHolder['text'] = stringContents.strip()
                else:
                    if not inAttack:
                        if tagType == "level":
                            item['level'] = int(stringContents.replace(";","").strip()) 
                        elif tagType != "":
                            if tagType in item:
                                item[tagType] += stringContents.strip()
                            else:
                                item[tagType] = stringContents.strip()
                        else:
                            if not stringContents.isspace():
                                itemDetailHolder.append(stringContents.strip())
                ##tagType = ""
    item['attacks'].append(attackHolder)
    item['special'] = specialHolder
    item['text'] = string.join(detailHolder + itemDetailHolder)
    items.append(item)
    
    return items

def get_all():
    compHolder['companions'] = get_multi("https://2e.aonprd.com/AnimalCompanions.aspx")

    return compHolder

#print(get_all())
json_data = json.dumps(get_all(), indent=4)
#print(json_data)
filename = "companions-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close