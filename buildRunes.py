from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import time

runeHolder = {}
runeHolder['name'] = 'Pathfinder 2.0 Runes list'
runeHolder['date'] = datetime.date.today().strftime("%B %d, %Y")


def get_multi(link):
    items = []
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    main = soup2.find("span", {'id':'ctl00_MainContent_DetailedOutput'})
    traits = main.find_all("span", {"class" : lambda L: L and L.startswith('trai')})
    traitHolder = []
    for trait in traits:
        traitHolder.append(trait.text)
    children = main.contents
    reachedBreak = False
    reachedItem = False
    detailHolder = []
    notFirstH2 = False
    inHeader = False
    parentDetails = {}
    parentDetails['traits'] = traitHolder
    item = {}
    item['link'] = link
    tagType = ""
    string = ""
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
            if child.name == "h2":
                if notFirstH2: 
                    
                    item['text'] = string.join(detailHolder) + string.join(itemDetailHolder)
                    for key in parentDetails.keys():
                        item[key] = parentDetails[key]
                    items.append(item)
                    item = {}
                    item['link'] = link
                    itemDetailHolder = []
                else:

                    notFirstH2 = True
            
                reachedBreak = False
                reachedItem = True
                inHeader = False
                name = child.text
                start = child.text.find("Item")
                item['name'] = child.text[0:start]
            if child.name == "b":
                if(child.text != "Source"):
                    tagType = child.text.lower().replace(" ", "")
                    
            if child.name == "a":

                try:
                    if child['class'][0] == "external-link" :
                        item['source'] = child.text
                except:
                    if reachedBreak:
                        if tagType != "":
                            if tagType in item:
                                parentDetails[tagType] += " " + child.text
                            else:
                                parentDetails[tagType] = child.text
                    elif inHeader:
                        if tagType != "":
                            if tagType in item:
                                parentDetails[tagType] += " " + child.text
                            else:
                                parentDetails[tagType] = child.text
                    else:
                        tagType = ""
                
        else:
            
            if reachedBreak:
                if tagType == "level":
                    item['level'] = int(stringContents.replace(";","").strip()) 
                elif(tagType != ""):
                    if not stringContents.isspace():
                        parentDetails[tagType] = stringContents.strip()
                        tagType = ""
                else: 
                    detailHolder.append(stringContents.strip())
            if inHeader:
                if tagType != "":
                    parentDetails[tagType] = stringContents.strip()
                    tagType = ""
            if reachedItem:
                
                if tagType == "level":
                    item['level'] = int(stringContents.replace(";","").strip()) 
                elif tagType != "":
                    item[tagType] = stringContents.strip()
                    tagType = ""
                else:
                    if not stringContents.isspace():
                        itemDetailHolder.append(stringContents.strip())
                    #print(stringContents)

    for key in parentDetails.keys():
        item[key] = parentDetails[key]
    item['text'] = string.join(detailHolder) + string.join(itemDetailHolder)
    items.append(item)
    
    return items

def get_single(link):
    details = {}
    itemDetails = {}
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    detail = soup2.find(lambda tag: tag.name=='span' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_DetailedOutput") 

    traits = detail.find_all("span", {"class" : lambda L: L and L.startswith('trai')})
    traitHolder = []
    for trait in traits:
        traitHolder.append(trait.text)
    details['traits'] = traitHolder
    children = detail.contents
    reachedBreak = False
    detailHolder = []
    tagType = ""
    for child in children:

        stringContents = str(child)
        if stringContents.startswith("<"):
            if child.name == "h1":
                name = child.text
                start = name.find("Item")
                details['name'] = name[0:start].strip()
            if child.name == "hr":
                tagType = ""
                reachedBreak = True
            
            if child.name == "a":
                try:
                    if child['class'][0] == "external-link" :
                        
                        details['source'] = child.text
                except:
                    pass
                tagType = ""
            if child.name == "b":

                if(child.text != "Source"):
                    tagType = child.text.lower().replace(" ", "")
            if child.name == "img":
                details['actions'] = child['alt']
            if child.name == "i":
                if(reachedBreak):
                    detailHolder.append(child.text) 
            #else:
                #if not stringContents.isspace() :
                    #detailHolder.append(child.text)        
        else:
            if reachedBreak:
                if tagType == "level":
                    details['level'] = int(stringContents.replace(";","").strip()) 
                elif tagType != "":
                    if not stringContents.isspace():
                            details[tagType] = stringContents.strip()
                else:
                    if not stringContents.isspace() :
                        detailHolder.append(stringContents.strip())
            else:
                if tagType != "":
                    if not stringContents.isspace():
                        details[tagType] = stringContents.strip()
                

       #print(child)
        string = " "
        details['text'] = string.join(detailHolder)
    return details

def get_armor_runes():

    listOfLinks = []
    listOfLinks.append("https://2e.aonprd.com/Equipment.aspx?Category=23&Subcategory=26")
    listOfLinks.append("https://2e.aonprd.com/Equipment.aspx?Category=23&Subcategory=24")

    itemHolder = []
    for link in listOfLinks:
        res2 = requests.get(link)
        res2.raise_for_status()
        soup2 = BeautifulSoup(res2.text, 'lxml')
        table = soup2.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_TreasureElement")

        rows = table.findAll(lambda tag: tag.name=='tr')
        t = 0
        for row in rows:
            t += 1
            #print(row)
            #print("-----------------------------------")
            item = {}
            entries = row.find_all(lambda tag: tag.name=='td')
            if entries is not None:
                if len(entries) > 0:
                    name = entries[0].find("a").text
                    item['name'] = name
                    item['link'] = "https://2e.aonprd.com/"+entries[0].find("a")['href']
                    if entries[1].text == "—":
                        item['level'] = 0
                    else:
                        item['level'] = int(entries[1].text)
                    item['price'] = entries[2].text.replace(u'\u2014', '')

                    if any(x['link'] == item['link'] for x in itemHolder):
                        #print("shortName:", shortName)
                        for item2 in itemHolder:
                            if item2['link'] == item['link']:
                                item2['multi'] = True
                    elif "Bloodbane" in item['name']:
                        item['multi'] = True
                        itemHolder.append(item)
                    else:
                        item['multi'] = False
                        itemHolder.append(item)
            #if t >6:
                #break

    
    
    items = []
    for item in itemHolder:
        #print(item)
        print("Getting armor rune :", item['name'],"This url:", item['link'],"|is it multi:",item['multi'])
        if item['multi'] == True:
            multiHolder = get_multi(item['link'])
            for multi in multiHolder:
                multi['category'] = "armor rune"
                items.append(multi)
        else:
            single = get_single(item['link'])
            single['category'] = "armor rune"
            single['level'] = item['level']
            single['price'] = item['price']
            items.append(single)

    return items

def get_weapon_runes():
    listOfLinks = []
    listOfLinks.append("https://2e.aonprd.com/Equipment.aspx?Category=23&Subcategory=25")
    listOfLinks.append("https://2e.aonprd.com/Equipment.aspx?Category=23&Subcategory=27")

    itemHolder = []
    for link in listOfLinks:
        res2 = requests.get(link)
        res2.raise_for_status()
        soup2 = BeautifulSoup(res2.text, 'lxml')
        table = soup2.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_TreasureElement")

        rows = table.findAll(lambda tag: tag.name=='tr')
        t = 0
        for row in rows:
            t += 1
            #print(row)
            #print("-----------------------------------")
            item = {}
            entries = row.find_all(lambda tag: tag.name=='td')
            if entries is not None:
                if len(entries) > 0:
                    name = entries[0].find("a").text
                    item['name'] = name
                    item['link'] = "https://2e.aonprd.com/"+entries[0].find("a")['href']
                    if entries[1].text == "—":
                        item['level'] = 0
                    else:
                        item['level'] = int(entries[1].text)
                    item['price'] = entries[2].text.replace(u'\u2014', '')

                    if any(x['link'] == item['link'] for x in itemHolder):
                        #print("shortName:", shortName)
                        for item2 in itemHolder:
                            if item2['link'] == item['link']:
                                item2['multi'] = True
                    elif "Bloodbane" in item['name']:
                        item['multi'] = True
                        itemHolder.append(item)
                    else:
                        item['multi'] = False
                        itemHolder.append(item)
            #if t >6:
                #break

    
    
    items = []
    for item in itemHolder:
        #print(item)
        print("Getting weapon rune :", item['name'],"This url:", item['link'],"|is it multi:",item['multi'])
        if item['multi'] == True:
            multiHolder = get_multi(item['link'])
            for multi in multiHolder:
                multi['category'] = "weapon rune"
                items.append(multi)
        else:
            single = get_single(item['link'])
            single['category'] = "weapon rune"
            single['level'] = item['level']
            single['price'] = item['price']
            items.append(single)

    return items

def get_all():
    runeHolder['armorRunes'] = get_armor_runes()
    runeHolder['weaponRunes'] = get_weapon_runes()
    
    
    return runeHolder

#print(get_all())
json_data = json.dumps(get_all())
#print(json_data)
filename = "runes-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close