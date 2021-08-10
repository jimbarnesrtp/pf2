from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import time

heldHolder = {}
heldHolder['name'] = 'Pathfinder 2.0 Artifact list'
heldHolder['date'] = datetime.date.today().strftime("%B %d, %Y")

def get_single(link):
    details = {}
    itemDetails = {}
    res2 = requests.get(link['url'])
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'html5lib')
    main = soup2.find("div", {'id': 'main'})
    #print (main)      
    pfsLegal = main.find("img", {'title': 'PFS Standard'})
    if(pfsLegal):
        pfsLegal = True
    else:
        pfsLegal = False
    for finder in main.find_all("a", {'href': link}): # temporary for error into html source
        name = finder.text

    traits = main.find_all("span", {"class" : lambda L: L and L.startswith('trai')})
    #print("traits len:", len(traits))
    traitHolder = []
    for trait in traits:
        traitHolder.append(trait.text)
    details['traits'] = traitHolder
    children = main.contents
    reachedBreak = False
    detailHolder = []
    tagType = ""
    for child in children:

        stringContents = str(child)
        if stringContents.startswith("<"):
            if child.name == "h1":
                try:
                    name = child.text
                    start = name.find("Item")
                    details['name'] = name[0:start].strip()
                    details['level'] = int(name[start+5:].strip())
                except:
                    details['name'] = link['name']
                    details['level'] = link['level']
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
        details['link'] = link['url']
        details['text'] = string.join(detailHolder)
    return details

def get_multi(link):
    print("getting multi for", link)
    string = " "
    items = []
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'html5lib')
    main = soup2.find("div", {'id': 'main'})
    #print (main)      
    pfsLegal = main.find("img", {'title': 'PFS Standard'})
    if(pfsLegal):
        pfsLegal = True
    else:
        pfsLegal = False
    for finder in main.find_all("a", {'href': link}): # temporary for error into html source
        name = finder.text
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
    inChild = False
    parentDetails = {}
    parentDetails['traits'] = traitHolder
    item = {}
    item['link'] = link
    tagType = ""
    itemDetailHolder = []
    inActivate = False
    act = {}
    actHolder = []
    childActHolder = []
    for child in children:
        
        stringContents = str(child)
        if stringContents.startswith("<"):
            #print(stringContents)
            if child.name == "img":
                if inActivate:
                    act['actions'] = child['alt']
                else:
                    parentDetails['actions'] = child['alt']
            if child.name == "hr":
                tagType = ""
                reachedBreak = True
                inHeader = False
            if child.name == "h1":
                inHeader = True

            if child.name == "h2":
                print(child)
                inChild = True
                inActivate = False
                if len(item.keys()) > 0:
                    if len(childActHolder) > 0:
                        item['childActivations'] = childActHolder
                        childActHolder = []
                    items.append(item)
                    item['name'] = child.text
                else:
                    item['name'] = child.text

                if len(act.keys()) > 0:
                    actHolder.append(act)
                    act = {}
            if child.name == "b":
                if(child.text != "Source"):
                    if child.text == "Activate":
                        if len(act.keys()) > 0:
                            actHolder.append(act)
                            act = {}
                        inActivate = True
                    elif child.text == "Destruction":
                        inActivate = False
                        if len(act.keys()) > 0:
                            actHolder.append(act)
                            act = {}
                    tagType = child.text.lower().replace(" ", "")
                
                   
            if child.name == "a":
                #print("in a reachedBreak:", reachedBreak, child.text, tagType) 
                try:
                    if child['class'][0] == "external-link" :
                        item['source'] = child.text
                except:
                    pass
                    if tagType != "":
                        if tagType in parentDetails:
                            parentDetails[tagType] += child.text
                        else:
                            parentDetails[tagType] += child.text
                    else:
                        detailHolder.append(child.text)
                if reachedBreak:
                    if inChild:
                        if tagType != "":
                            if tagType in item:
                                item[tagType] += " " + child.text
                            else:
                                item[tagType] = child.text
                    else: 
                        if tagType != "":
                            parentDetails[tagType] += child.text
                        else:
                            detailHolder.append(child.text)
            if child.name == "i":
                #print("in i reachedBreak:", reachedBreak, child.text, tagType) 
                if reachedBreak :
                    if inChild:
                        if tagType != "":
                            if tagType in item:
                                item[tagType] += " " + child.text.strip()
                            else:
                                item[tagType] = child.text.strip()
                    elif inActivate:
                        if tagType != "":
                            if tagType in act:
                                act[tagType] += " " + child.text.strip()
                            else:
                                act[tagType] = child.text.strip()
                    else:
                        if tagType != "":
                            parentDetails[tagType] += " "  + child.text
                        else:
                            detailHolder.append(child.text)
                        
                    #detailHolder.append(child.text) 
                else:
                    if tagType != "":
                        if tagType in parentDetails:
                            parentDetails[tagType] += " " + child.text.strip()
                        else:
                            parentDetails[tagType] = child.text.strip()
        else:
            if reachedBreak:
                if inActivate:
                    if(tagType != ""):
                        if not stringContents.isspace():
                            if tagType in act:
                                act[tagType] += " " + stringContents.strip()
                            else:
                                act[tagType] = stringContents.strip()
                if inChild:
                    if(tagType != ""):
                        if not stringContents.isspace():
                            if tagType in item:
                                item[tagType] += " " + stringContents.strip()
                            else:
                                item[tagType] = stringContents.strip()
                    else: 
                        detailHolder.append(stringContents)
                elif not inActivate:
                    if tagType != "":
                        if tagType in parentDetails:
                            parentDetails[tagType] += " " + stringContents.strip()
                        else:
                            parentDetails[tagType] = stringContents.strip()
                    else:
                        detailHolder.append(stringContents.strip())
            if inHeader:
                if tagType != "":
                    if tagType in parentDetails:
                        parentDetails[tagType] += stringContents.strip()
                    else:
                        parentDetails[tagType] = stringContents.strip()

    if len(act.keys()) > 0:
        actHolder.append(act)
        act = {}
    
    parentDetails['activations'] = actHolder

    for key in parentDetails.keys():
        #print(key)
        item[key] = parentDetails[key]
    
    item['text'] = string.join(detailHolder + itemDetailHolder)
    items.append(item)
    
    return items

def retrieve_items(links):
    items = []
    t = 0
    for link in links:
        t += 1
        #print(link)
        if link['multi']:
            print("getting held:",link['name'])
            multi_items = get_multi(link['url'])
            for item in multi_items:
                item['category'] = "artifact"
                item['linl'] = link['url']
                if "pfsFlag" in link:
                    item['pfsFlag'] = link['pfsFlag']
                else:
                    item['pfsFlag'] = 'none'
                items.append(item)

        else:
            print("getting held:",link['name'])
            item = get_single(link)
            item['category'] = "artifact"
            items.append(item)
        if t > 1:
            break
    return items

def get_held_items(category):
    res2 = requests.get(category)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    table = soup2.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_TreasureElement")
    rows = table.findAll(lambda tag: tag.name=='tr')
    links = []
    for row in rows:
        entries = row.find_all(lambda tag: tag.name=='td')
        if entries is not None:
            if len(entries) > 0:
                link = {}
                if len(entries[0].find_all("a")) > 1:
                    link['name'] = entries[0].find_all("a")[1].text
                    link['pfsFlag'] = entries[0].find_all("a")[0].find("img")['alt'].strip()
                    link['url'] = "https://2e.aonprd.com/"+entries[0].find_all("a")[1]['href']
                else:
                    link['name'] = entries[0].find("a").text
                    link['url'] = "https://2e.aonprd.com/"+entries[0].find("a")['href']
                if ("(" in link['name']) or ("Orb" in link['name']) :
                    link['multi'] = True
                else:
                    link['multi'] = False
                link['level'] = entries[1].text
            
                links.append(link)
    return retrieve_items(links)


def get_all():
    heldHolder['artifacts'] = get_held_items("https://2e.aonprd.com/Equipment.aspx?Category=45")

    
    return heldHolder

#print(get_all())
json_data = json.dumps(get_all(), indent=4)
#print(json_data)
filename = "artifacts-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close