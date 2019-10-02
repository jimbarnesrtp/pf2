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
            if not stringContents.isspace():
                detailHolder.append(stringContents)

       #print(child)
        details['text'] = detailHolder
    return details



def get_links():
    listOfLinks = []
    listOfLinks.append("https://2e.aonprd.com/Conditions.aspx")


    itemHolder = []
    for link in listOfLinks:
        res2 = requests.get(link)
        res2.raise_for_status()
        soup2 = BeautifulSoup(res2.text, 'lxml')
        links = soup2.select("div.main u a")

        t = 0
        for link1 in links:
            t += 1
            #print(row)
            #print("-----------------------------------")
            item = {}
            name = link1.text
            href = link1['href']

            print("Name:",name,"|link:",href)

            itemHolder.append(get_single("https://2e.aonprd.com/"+href))
                    
                    #item['multi'] = False
                    #itemHolder.append(item)
            #if t >6:
                #break
    return itemHolder


def get_all():
    condHolder['conditions'] = get_links()

    
    return condHolder

#print(get_all())
json_data = json.dumps(get_all())
#print(json_data)
filename = "conditions-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close