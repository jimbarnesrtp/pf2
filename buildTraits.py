from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import time

condHolder = {}
condHolder['name'] = 'Pathfinder 2.0 Condition list'
condHolder['date'] = datetime.date.today().strftime("%B %d, %Y")


def get_single(link):
    details = {}
    itemDetails = {}
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    detail = soup2.find(lambda tag: tag.name=='span' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_DetailedOutput") 

    children = detail.contents
    reachedBreak = False
    detailHolder = []
    tagType = ""
    for child in children:

        stringContents = str(child)
        if stringContents.startswith("<"):
            if child.name == "h1":
                name = child.text
                details['name'] = name.strip()
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
            if not stringContents.isspace():
                detailHolder.append(stringContents)
        string = " "
       #print(child)
        finalText = ""
        for text in detailHolder:
            if text.isspace():
               pass
            elif text == ", ":
                pass
            else:
                #print("text:", text)
                finalText += text
            
        details['text'] = finalText
    return details



def get_links():
    listOfLinks = []
    listOfLinks.append("https://2e.aonprd.com/Traits.aspx")


    itemHolder = []
    for link in listOfLinks:
        res2 = requests.get(link)
        res2.raise_for_status()
        soup2 = BeautifulSoup(res2.text, 'lxml')
        detail = soup2.find(lambda tag: tag.name=='span' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_DetailedOutput") 

        children = detail.contents
        traitType = ""

        for child in children:

            stringContents = str(child)
            if stringContents.startswith("<"):
                #print(child.name)
                if child.name == "h2":
                    traitType = child.text
                    if traitType == "":
                        traitType = "General"
                    #print(child.text)
                if child.name == "span":
                    trait = {}
                    trait['name'] = child.text
                    trait['type'] = traitType
                    
                    link = child.find("a")
                    if (link is None):
                        pass
                    else:
                        trait['link'] = "https://2e.aonprd.com/"+link['href']
                    itemHolder.append(trait)
                        #print()
                    #print(child.text)
        t = 0
        for item in itemHolder:
            t += 1
            print("get Item:", item['name'],"link:", item['link'])
            try:
                holder = get_single(item['link'])
                for key in holder.keys():
                    item[key] = holder[key]
            except: 
                print("error on getting item", item['name'])
            #if t > 5:
                #break

    return itemHolder


def get_all():
    condHolder['traits'] = get_links()

    
    return condHolder

#print(get_all())
json_data = json.dumps(get_all())
#print(json_data)
filename = "traits-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close