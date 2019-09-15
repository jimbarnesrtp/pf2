from bs4 import BeautifulSoup
from bs4 import NavigableString
import requests
import json
import datetime
import re



monsterDetail = {}
link = 'http://pf2.d20pfsrd.com/monster/black-dragon/'
res = requests.get(link)
res.raise_for_status()
soup = BeautifulSoup(res.text, 'lxml')
monster = soup.find_all("div", {'class':'article-content'})

children = monster[0].findChildren(recursive=False)
print(len(children))
monsters = {}
monsterIndex = 0
for child in children:
    #print(child.name)
    
    tagName = child.name

    if tagName == "h4":
        if 'monsters' not in monsters:
            monsters['monsters'] = []
        else:
            monsterIndex += 1
        monsters['monsters'].append({})
        monsters['monsters'][monsterIndex]['name'] = child.contents[0]
        monsters['monsters'][monsterIndex]['level'] = child.find("span", {'class':'monster-level'}).text
        monsters['monsters'][monsterIndex]['link'] = link
        monsters['monsters'][monsterIndex]['type'] = child.find("span", {'class':'monster-type'}).text

    if tagName == "p":


        try:

            pClass = child['class'][0]
            #print(pClass)
        except: 
            pClass = ""

        if pClass == "traits":
            traitsScratch = child.find_all("span", {'class':'trait'})
            traits = []
            if traitsScratch is not None:
                for trait in traitsScratch:
                    traits.append(trait.text)
            monsters['monsters'][monsterIndex]['traits'] = traits
            monsters['monsters'][monsterIndex]['alignment'] = child.find("span", {'class':'alignment'}).text
            monsters['monsters'][monsterIndex]['size'] = child.find("span", {'class':'size'}).text
            frequency = child.find("span", {'class':'frequency'})
            if frequency is not None:
                monsters['monsters'][monsterIndex]['frequency'] = frequency.text
    

print(monsters)

