from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import time

weaponHolder = {}
weaponHolder['name'] = 'Pathfinder 2.0 Weapons list'
weaponHolder['date'] = datetime.date.today().strftime("%B %d, %Y")

def get_details(link):
    itemDetails = {}
    res = requests.get(link)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'lxml')
    feat = soup.find_all("div", {'class':'main'})
    detail = soup.find("span", {'id':'ctl00_MainContent_DetailedOutput'})
    #print(detail.contents)
    children = detail.contents
    reachedBreak = False
    reachedCrit = False
    detailHolder = []
    critText = []
    critHolder = {}
    tagType = ""
    for child in children:
        stringContents = str(child)
        if stringContents.startswith("<"):

            if child.name == "hr":
                reachedBreak = True
            if reachedBreak:
                if child.name == "h2":
                    reachedCrit = True
            if reachedCrit:
                if child.name == "a":
                    try:
                        if child['class'][0] == "external-link" : 
                            itemDetails['source'] = child.text
                    except:
                        pass
                    tagType = ""
                if child.name == "b":
                    tagType = child.text
        else:
            if reachedBreak:
                if reachedCrit:
                    if tagType != "":
                        if not stringContents.isspace():
                            critHolder[tagType] = stringContents
                    else:
                        critText.append(stringContents)
                else:
                    detailHolder.append(stringContents)
       #print(child)
       #print('<!!!!!!!!!!!!!!!!!!!!!!!!!>')

    critHolder['text'] = critText
    itemDetails['critSpecial'] = critHolder
    itemDetails['text'] = detailHolder
    return itemDetails



def get_melee_weapons(link):
    items = []
    multiItems = []
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    table = soup2.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_MeleeElement")
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
                item['category'] = entries[1].text
                item['price'] = entries[2].text.replace(u'\u2014', '')
                item['damage'] = entries[3].text
                item['bulk'] = entries[4].text.replace(u'\u2014', '')
                item['hands'] = entries[5].text
                item['group'] = entries[6].text
                item['weaponTraits'] = entries[7].text.split(",")
                print("getting held:",item['name'])
                itemDetails = get_details(item['link'])

                for key in itemDetails.keys():
                    item[key] = itemDetails[key]

                items.append(item)
        #if t > 5:
            #break
    return items

def get_range_weapons(link):
    items = []
    multiItems = []
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    table = soup2.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_RangedElement")
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
                item['category'] = entries[1].text
                item['price'] = entries[2].text.replace(u'\u2014', '')
                item['damage'] = entries[3].text.replace(u'\u2014', '')
                item['range'] = entries[4].text.replace(u'\u2014', '')
                item['reload'] = entries[5].text.replace(u'\u2014', '')
                item['bulk'] = entries[6].text.replace(u'\u2014', '')
                item['hands'] = entries[7].text.replace(u'\u2014', '')
                item['group'] = entries[8].text
                item['weaponTraits'] = entries[9].text.replace(u'\u2014', '').split(",")
                print("getting held:",item['name'])
                itemDetails = get_details(item['link'])

                for key in itemDetails.keys():
                    item[key] = itemDetails[key]

                items.append(item)
        #if t > 5:
            #break
    return items

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
                    tagType = child.text
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
                if tagType != "":
                    if not stringContents.isspace():
                            details[tagType] = stringContents
                else:
                    if not stringContents.isspace() :
                        detailHolder.append(stringContents)
            else:
                if tagType != "":
                    if not stringContents.isspace():
                        details[tagType] = stringContents
                

       #print(child)
        details['text'] = detailHolder
    return details

def get_base_magic_weapons():
    items = []
    multiHolder = get_multi("https://2e.aonprd.com/Equipment.aspx?ID=380")
    for weapon in multiHolder:
        weapon['category'] = "base magic weapon"
        items.append(weapon)
    return items

def get_weapons_from_list(fileName):
    items = []
    listOfPages = codecs.open(fileName, encoding='utf-8')
    t = 0
    for line in listOfPages: 
        t += 1
        runeMD = line.split(",")
        print("Getting weapon for :", runeMD[0],"This url:", runeMD[2].strip('\n'),"|is it multi:",runeMD[1])
        if runeMD[1] == "True":
            multiHolder = get_multi(runeMD[2].strip('\n'))
            for shield in multiHolder:
                shield['category'] = "weapon"
                items.append(shield)
        else:
            items.append(get_single(runeMD[2].strip('\n')))
    return items



def get_all():
    weaponHolder['meleeWeapons'] = get_melee_weapons("https://2e.aonprd.com/Weapons.aspx")
    weaponHolder['rangeWeapons'] = get_range_weapons("https://2e.aonprd.com/Weapons.aspx")
    weaponHolder['baseMagicWeapons'] = get_base_magic_weapons()
    weaponHolder['specialMaterialWeapons'] = get_weapons_from_list("materialWeapons.csv")
    weaponHolder['magicWeapons'] = get_weapons_from_list("magicWeapons.csv")

    #weaponHolder['rangedWeapons'] = get

    
    return weaponHolder

#print(get_all())
json_data = json.dumps(get_all())
#print(json_data)
filename = "weapons-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close