from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs

alHolder = {}
alHolder['name'] = 'Pathfinder 2.0 Alchemical Item list'
alHolder['date'] = datetime.date.today().strftime("%B %d, %Y")


def get_bombs():
    string = " "
    items = []
    listOfPages = codecs.open("bombs.csv", encoding='utf-8')
    t = 0
    for line in listOfPages: 
        t += 1
        alMD = line.split(",")
        print("Getting bomb for :", alMD[0],"This url:", alMD[1].strip('\n'))

        res2 = requests.get(alMD[1].strip('\n'))
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
                    if notFirstH2: 
                        
                        item['text'] = string.join(detailHolder + itemDetailHolder)
                        for key in parentDetails.keys():
                            item[key] = parentDetails[key]
                        items.append(item)
                        item = {}
                        itemDetailHolder = []
                    else:

                        notFirstH2 = True
                
                    reachedBreak = False
                    reachedItem = True
                    inHeader = False
                    name = child.text
                    start = child.text.find("Item")
                    item['name'] = child.text[0:start]
                    item['link'] = alMD[1].strip('\n')
                if child.name == "b":
                    if(child.text != "Source"):
                        tagType = child.text.lower().replace(" ", "")
                        
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
        item['text'] = string.join(detailHolder + itemDetailHolder)
        items.append(item)
        #if t > 0:
            #break
    
    return items

def get_elixirs():
    string = " "
    items = []
    listOfPages = codecs.open("elixirs.csv", encoding='utf-8')
    t = 0
    for line in listOfPages: 
        t += 1
        alMD = line.split(",")
        print("Getting elixir for :", alMD[0],"This url:", alMD[1].strip('\n'))

        res2 = requests.get(alMD[1].strip('\n'))
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
        tagType = ""
        itemDetailHolder = []
        parentName = ""
        parentLevel = ""
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
                if child.name == "h1":
                    #name = child.text
                    start = child.text.find("Item")
                    parentName = child.text[0:start]
                    parentLevel = child.text[start+5:]
                    inHeader = True
                if child.name == "h2":
                    if notFirstH2: 
                        
                        item['text'] = string.join(detailHolder + itemDetailHolder)
                        for key in parentDetails.keys():
                            item[key] = parentDetails[key]
                        items.append(item)
                        item = {}
                        itemDetailHolder = []
                    else:

                        notFirstH2 = True
                
                    reachedBreak = False
                    reachedItem = True
                    inHeader = False
                    #name = child.text
                    start = child.text.find("Item")
                    item['name'] = child.text[0:start]
                    item['link'] = alMD[1].strip('\n')
                if child.name == "b":
                    if(child.text != "Source"):
                        tagType = child.text.lower().replace(" ", "")
                        
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
        if 'name' not in item:
            item['name'] = parentName
            item['link'] = alMD[1].strip('\n')
            item['level'] = int(parentLevel)
        item['text'] = string.join(detailHolder + itemDetailHolder)

        items.append(item)
        #if t > 3:
            #break
    
    return items

def get_poisons(link):
    items = []
    res2 = requests.get(link)
    res2.raise_for_status()
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
                item['name'] = entries[0].find("a").text
                item['link'] = "https://2e.aonprd.com/"+entries[0].find("a")['href']
                item['category'] = "poison"
                item['level'] = int(entries[1].text)
                item['price'] = entries[2].text
                item['bulk'] = entries[3].text.replace(u'\u2014', '')
                print("getting poison:",item['name'])
                itemDetails = get_poison_details(item['link'])

                for key in itemDetails.keys():
                    item[key] = itemDetails[key]

                items.append(item)
        #if t > 2:
            #break
    return items

def get_poison_details(link):
    string = " "
    poisonDetails = {}
    itemDetails = {}
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    detail = soup2.find(lambda tag: tag.name=='span' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_DetailedOutput") 

    traits = detail.find_all("span", {"class" : lambda L: L and L.startswith('trai')})
    traitHolder = []
    for trait in traits:
        traitHolder.append(trait.text)
    poisonDetails['traits'] = traitHolder
    children = detail.contents
    reachedBreak = False
    detailHolder = []
    tagType = ""
    for child in children:

        stringContents = str(child)
        if stringContents.startswith("<"):
            if child.name == "hr":
                tagType = ""
                reachedBreak = True
            
            if child.name == "a":
                try:
                    if child['class'][0] == "external-link" :
                        
                        poisonDetails['source'] = child.text
                except:
                    pass
                tagType = ""
            if child.name == "b":

                if(child.text != "Source"):
                    tagType = child.text.lower().replace(" ", "")
            if child.name == "img":
                poisonDetails['actions'] = child['alt']
            #else:
                #if not stringContents.isspace() :
                    #detailHolder.append(child.text)        
        else:
            if reachedBreak:
                if tagType != "":
                    if not stringContents.isspace():
                            poisonDetails[tagType] = stringContents
                else:
                    if not stringContents.isspace() :
                        detailHolder.append(stringContents)
            else:
                if tagType != "":
                    if (tagType != "Bulk") & (tagType!= "Price"):
                        if not stringContents.isspace():
                            poisonDetails[tagType] = stringContents
                

       #print(child)
        poisonDetails['text'] = string.join(detailHolder)
    return poisonDetails

def get_tools(link):
    items = []
    res2 = requests.get(link)
    res2.raise_for_status()
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
                item['name'] = entries[0].find("a").text
                item['link'] = "https://2e.aonprd.com/"+entries[0].find("a")['href']
                item['category'] = "tools"
                item['level'] = 0 if entries[1].text == "—" else int(entries[1].text)
                item['price'] = entries[2].text
                item['bulk'] = entries[3].text.replace(u'\u2014', '')
                print("getting tool:",item['name'])
                itemDetails = get_tool_details(item['link'])

                for key in itemDetails.keys():
                    item[key] = itemDetails[key]

                items.append(item)
        #if t > 2:
            #break
    return items

def get_tool_details(link):
    toolDetails = {}
    itemDetails = {}
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    detail = soup2.find(lambda tag: tag.name=='span' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_DetailedOutput") 

    traits = detail.find_all("span", {"class" : lambda L: L and L.startswith('trai')})
    traitHolder = []
    for trait in traits:
        traitHolder.append(trait.text)
    toolDetails['traits'] = traitHolder
    children = detail.contents
    reachedBreak = False
    detailHolder = []
    tagType = ""
    for child in children:

        stringContents = str(child)
        if stringContents.startswith("<"):
            if child.name == "hr":
                tagType = ""
                reachedBreak = True
            
            if child.name == "a":
                try:
                    if child['class'][0] == "external-link" :
                        
                        toolDetails['source'] = child.text
                except:
                    if reachedBreak:
                        if tagType == "":
                            detailHolder.append(child.text)

                tagType = ""
            if child.name == "b":

                if(child.text != "Source"):
                    tagType = child.text.lower().replace(" ", "")
            if child.name == "img":
                toolDetails['actions'] = child['alt']
            #else:
                #if not stringContents.isspace() :
                    #detailHolder.append(child.text)        
        else:
            if reachedBreak:
                if tagType != "":
                    if not stringContents.isspace():
                            toolDetails[tagType] = stringContents
                else:
                    if not stringContents.isspace() :
                        detailHolder.append(stringContents)
            else:
                if tagType != "":
                    if (tagType != "Bulk") & (tagType!= "Price"):
                        if not stringContents.isspace():
                            toolDetails[tagType] = stringContents
                

       #print(child)
        string = " "
        toolDetails['text'] = string.join(detailHolder)
    return toolDetails

def get_all():
    alHolder['bombs'] = get_bombs()
    alHolder['elixirs'] = get_elixirs()
    alHolder['poisons'] = get_poisons("https://2e.aonprd.com/Equipment.aspx?Category=6&Subcategory=9")
    alHolder['tools'] = get_tools("https://2e.aonprd.com/Equipment.aspx?Category=6&Subcategory=10")

    
    return alHolder

#print(get_all())
json_data = json.dumps(get_all(), indent=4)
#print(json_data)
filename = "alchemical-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close