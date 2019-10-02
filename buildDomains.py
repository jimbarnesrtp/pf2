from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import time

domainHolder = {}
domainHolder['name'] = 'Pathfinder 2.0 domains list'
domainHolder['date'] = datetime.date.today().strftime("%B %d, %Y")

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
    godHolder = []
    string = ","
    tagType = ""
    for child in children:
        stringContents = str(child)
        if stringContents.startswith("<"):
            if child.name == "b":
                tagType = child.text
            if child.name == "a":
                if tagType == "Source":
                    itemDetails[tagType] = child.text
            if child.name == "u":
                if tagType == "Deities":
                    godHolder.append(child.text)

    itemDetails['deities'] = string.join(godHolder)

    return itemDetails



def get_domains(link):
    items = []
    multiItems = []
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    table = soup2.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_DomainElement")
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
                item['description'] = entries[1].text
                item['domainSpell'] = entries[2].text.replace(u'\u2014', '')
                item['advancedDomainSpell'] = entries[3].text

                print("getting domain:",item['name'])
                itemDetails = get_details(item['link'])

                for key in itemDetails.keys():
                    item[key] = itemDetails[key]

                items.append(item)
        #if t > 5:
            #break
    return items




def get_all():
    domainHolder['domains'] = get_domains("https://2e.aonprd.com/Domains.aspx")

    #domainHolder['rangedWeapons'] = get

    
    return domainHolder

#print(get_all())
json_data = json.dumps(get_all())
#print(json_data)
filename = "domains-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close