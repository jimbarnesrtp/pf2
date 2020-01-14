from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import time

materialHolder = {}
materialHolder['name'] = 'Pathfinder 2.0 marterial list'
materialHolder['date'] = datetime.date.today().strftime("%B %d, %Y")

def get_multi(link):
    material = {}
    items = []
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    main = soup2.find("span", {'id':'ctl00_MainContent_DetailedOutput'})
    traits = main.find_all("span", {"class" : lambda L: L and L.startswith('trai')})
    table = main.find("table", {"class" : "inner"})
    title = main.find("h1", {"class": "title"})
    dragonArmor = []
    if("Dragonhide" in title.text):
        resistenceTable = main.find_all("table", {"class" : "inner"})[0]
        rows1 = table.findAll(lambda tag: tag.name=='tr')
        l = 0
        
        for row1 in rows1:
            if l > 0:
                entries1 = row1.find_all(lambda tag: tag.name=='td')
                armorHolder = {}
                armorHolder['type'] = entries1[0].text
                armorHolder['resistance'] = entries1[1].text
                dragonArmor.append(armorHolder)
            l += 1
        table = main.find_all("table", {"class" : "inner"})[1]
    rows = table.findAll(lambda tag: tag.name=='tr')
    firstRow = True
    statsList = []
    materialHolder = {}
    materialSpecs = {}
    specsList = []
    for row in rows:

        entries = row.find_all(lambda tag: tag.name=='td')
        if firstRow:
            firstRow = False
        else:
            if entries is not None:
                if len(entries) > 0:
                    if(len(entries) == 2):
                        if 'name' in materialHolder:
                            materialHolder['specs'] = specsList
                            specsList = []
                            statsList.append(materialHolder)
                            materialHolder = {}
                        materialHolder['name'] = entries[0].text
                    else:
                        
                        materialSpecs['name'] = entries[0].text
                        materialSpecs['hardness'] = entries[1].text
                        materialSpecs['hp'] = entries[2].text
                        materialSpecs['bt'] = entries[3].text
                        specsList.append(materialSpecs)
                        materialSpecs = {}
                        
    materialHolder['specs'] = specsList
    statsList.append(materialHolder)

    
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
                name = child.text
                start = child.text.find("Item")
                material['name'] = child.text[0:start]
                material['stats'] = statsList
                if(len(dragonArmor) > 0):
                    material['armorStats'] = dragonArmor
                inHeader = True
            if child.name == "h2":
                #print(child.text)
                className = ""
                try:
                    className = child['class'][0]
                except:
                    className = ""
                if className == "title":
                    if notFirstH2: 
                        
                        item['text'] = detailHolder + itemDetailHolder
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
            
            if reachedBreak:
                if(tagType != ""):
                    if not stringContents.isspace():
                        parentDetails[tagType] = stringContents
                        tagType = ""
                else: 
                    detailHolder.append(stringContents)
            if inHeader:
                if tagType != "":
                    parentDetails[tagType] = stringContents
                    tagType = ""
            if reachedItem:
                
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
    
    material['itemList'] = items
    return material




def get_all():
    listOfLinks = []
    listOfLinks.append("https://2e.aonprd.com/Equipment.aspx?Category=22")
   

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

                    if any(x['link'] == item['link'] for x in itemHolder):
                        #print("shortName:", shortName)
                        for item2 in itemHolder:
                            if item2['link'] == item['link']:
                                item2['multi'] = True
                    else:
                        item['multi'] = False
                        itemHolder.append(item)
            #if t >6:
                #break

    
    
    items = []
    for item in itemHolder:
        #print(item)
        print("Getting materials :", item['name'],"This url:", item['link'],"|is it multi:",item['multi'])
        if item['multi'] == True:
            material = get_multi(item['link'])
            material['category'] = "material"
            items.append(material)
        #else:
         #   single = get_single(item['link'])
          #  single['category'] = "worn item"
           # items.append(single)

    materialHolder['material'] = items

    #wordHolder['rangedWeapons'] = get

    
    return materialHolder

#print(get_all())
json_data = json.dumps(get_all(), indent=4)
#print(json_data)
filename = "material-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close