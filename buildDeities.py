from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import time

deityHolder = {}
deityHolder['name'] = 'Pathfinder 2.0 deities list'
deityHolder['date'] = datetime.date.today().strftime("%B %d, %Y")

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
    tagType = ""
    string = " "
    fontHolder = []
    spellHolder = []
    for child in children:
        stringContents = str(child)
        if stringContents.startswith("<"):

            if child.name == "a":
                try:
                    if child['class'][0] == "external-link" : 
                        itemDetails['source'] = child.text
                except:
                    pass
                tagType = ""
            if child.name == "b":
                tagType = child.text
            if child.name == "i":
                if tagType == "Divine Font":
                    fontHolder.append(child.text)
                if tagType == "Cleric Spells":
                    spellHolder.append(child.text)
        else:

            if tagType != "":
                if (tagType != "Follower Alignments" and tagType != "Favored Weapon" and tagType != "Domains"):
                    if not stringContents.isspace():
                        if tagType == "Cleric Spells":
                            spellHolder.append(stringContents)
                        elif tagType == "Divine Font":
                            fontHolder.append(stringContents)
                        else:
                            itemDetails[tagType] = stringContents
            else:
                if not stringContents.isspace():
                    detailHolder.append(stringContents)

       #print(child)
       #print('<!!!!!!!!!!!!!!!!!!!!!!!!!>')
    itemDetails['fontHolder'] = string.join(fontHolder)
    itemDetails['clericSpells'] =string.join(spellHolder)
    itemDetails['text'] = string.join(detailHolder)
    return itemDetails



def get_domains(link):
    items = []
    multiItems = []
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    table = soup2.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_DeityElement")
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
                item['alignment'] = entries[1].text.split(",")
                item['followerAlignments'] = entries[2].text.replace(u'\u2014', '').split(",")
                item['domains'] = entries[3].text

                print("getting details for:",item['name'])
                itemDetails = get_details(item['link'])

                for key in itemDetails.keys():
                    item[key] = itemDetails[key]

                items.append(item)
        #if t > 5:
            #break
    return items




def get_all():
    deityHolder['deities'] = get_domains("https://2e.aonprd.com/Deities.aspx")

    #deityHolder['rangedWeapons'] = get

    
    return deityHolder

#print(get_all())
json_data = json.dumps(get_all())
#print(json_data)
filename = "deities-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close