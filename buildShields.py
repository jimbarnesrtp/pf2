from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import time
import buildDetailsHR as hrDets

shieldHolder = {}
shieldHolder['name'] = 'Pathfinder 2.0 shields list'
shieldHolder['date'] = datetime.date.today().strftime("%B %d, %Y")


def get_multi(link):
    string = " "
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
                print(child.text)
                className = ""
                try:
                    className = child['class'][0]
                except:
                    className = ""
                if className == "title":
                    if notFirstH2: 
                        
                        item['text'] = string.join(detailHolder + itemDetailHolder)
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
                    pass
                if reachedBreak:
                    if tagType != "":
                        if tagType in item:
                            item[tagType] += " " + child.text
                        else:
                            item[tagType] = child.text
                else:
                    tagType = ""
            if child.name == "i":

                if(reachedBreak):
                    if tagType != "":
                        if tagType in item:
                            item[tagType] += " " + child.text.strip()
                        else:
                            item[tagType] = child.text.strip()
                    #detailHolder.append(child.text) 
                else:
                    if tagType != "":
                        if tagType in parentDetails:
                            parentDetails[tagType] += " " + child.text.strip()
                        else:
                            parentDetails[tagType] = child.text.strip()
        else:
            
            if reachedBreak:
                if(tagType != ""):
                    if not stringContents.isspace():
                        if tagType in item:
                            item[tagType] += " " + stringContents.strip()
                        else:
                            item[tagType] = stringContents.strip()
                        
                        tagType = ""
                else: 
                    detailHolder.append(stringContents)
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
                        itemDetailHolder.append(stringContents)
                    #print(stringContents)

    for key in parentDetails.keys():
        item[key] = parentDetails[key]
    
    item['text'] = string.join(detailHolder + itemDetailHolder)
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
                details['level'] = int(name[start+5:].strip())
            if child.name == "hr":
                tagType = ""
                reachedBreak = True
            
            if child.name == "a":
                try:
                    if child['class'][0] == "external-link" :
                        
                        details['source'] = child.text.strip()
                except:
                    pass
                if reachedBreak:
                    if tagType != "":
                        if tagType in details:
                            details[tagType] += " " + child.text.strip()
                        else:
                            details[tagType] = child.text.strip()
                    else:
                        detailHolder.append(child.text)
                else:
                    tagType = ""
            if child.name == "b":

                if(child.text != "Source"):
                    tagType = child.text.lower().replace(" ", "")
            if child.name == "img":
                details['actions'] = child['alt']
            if child.name == "i":

                if(reachedBreak):
                    if tagType != "":
                        if tagType in details:
                            details[tagType] += " " + child.text.strip()
                        else:
                            details[tagType] = child.text.strip()
                    #detailHolder.append(child.text) 
                else:
                    if tagType != "":
                        if tagType in details:
                            details[tagType] += " " + child.text.strip()
                        else:
                            details[tagType] = child.text.strip()      
        else:
            if reachedBreak:
                if tagType == "level":
                    
                    details['level'] = int(stringContents.replace(";","").strip())
                if tagType != "":
                    if not stringContents.isspace():
                            if tagType in details:
                                details[tagType] += stringContents
                            else:
                                details[tagType] = stringContents
                            
                else:
                    if not stringContents.isspace() :
                        detailHolder.append(stringContents)
            else:
                if tagType != "":
                    if not stringContents.isspace():
                        if tagType in details:
                            details[tagType] += " " + stringContents.strip()
                        else:
                            details[tagType] = stringContents.strip()
                

       #print(child)
        string = " "
        details['link'] = link
        details['text'] = string.join(detailHolder)
    return details


def get_shields(link):

    itemHolder = []
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
                item['bulk'] = entries[3].text

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
        print("Getting shield :", item['name'],"This url:", item['link'],"|is it multi:",item['multi'])
        if item['multi'] == True:
            multiHolder = get_multi(item['link'])
            for multi in multiHolder:
                multi['category'] = "shield"
                items.append(multi)
        else:
            single = get_single(item['link'])
            single['category'] = "shield"
            single['level'] = item['level']
            single['price'] = item['price']
            items.append(single)

    return items

def get_base_shields(link):
    items = []
    multiItems = []
    res2 = requests.get(link)
    res2.raise_for_status()
    string = " "
    soup2 = BeautifulSoup(res2.text, 'lxml')
    item = soup2.find_all("div", {'class':'main'})
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

                
                item['category'] = "shield"
                item['price'] = entries[1].text
                item['acBonus'] = entries[2].text
                item['speedPenalty'] = entries[3].text.replace(u'\u2014', '')
                item['bulk'] = entries[4].text
                item['hardness'] = int(entries[5].text)
                item['hp_bt'] = entries[6].text

                item['text'] = string.join(hrDets.get_afterhr(item['link']))

                
                print("getting shield:",item['name'])
                    

                items.append(item)
        #if t > 5:
            #break
    return items


def get_all():
    shieldHolder['baseShields'] = get_base_shields("https://2e.aonprd.com/Shields.aspx")
    shieldHolder['specialMaterialShields'] = get_shields("https://2e.aonprd.com/Equipment.aspx?Category=28&Subcategory=29")
    shieldHolder['specificShields'] = get_shields("https://2e.aonprd.com/Equipment.aspx?Category=28&Subcategory=30")


    
    
    return shieldHolder

#print(get_all())
json_data = json.dumps(get_all(), indent=4)
#print(json_data)
filename = "shields-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close