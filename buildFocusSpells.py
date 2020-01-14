from bs4 import BeautifulSoup
import requests
import json
import datetime

focusSpellsHolder = {}
focusSpellsHolder['name'] = 'Pathfinder 2.0 focus spell list'
focusSpellsHolder['date'] = datetime.date.today().strftime("%B %d, %Y")

focusSpells = []
res = requests.get("https://2e.aonprd.com/Spells.aspx?Focus=true&Tradition=0")
res.raise_for_status()
soup = BeautifulSoup(res.text, 'lxml')
detail = soup.find(lambda tag: tag.name=='span' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_DetailedOutput") 
children = detail.findChildren(recursive=False)

spellType = ""
spellLevel = ""

for child in children:
    #print(child.name)
    if child.name == "h2":
        if(child.text[0].isdigit()):
            spellType = "spell"
            spellLevel = child.text[0]
        else:
            spellType = "cantrip"
            spellLevel = 0
    if child.name == "a":
        spell = {}
        spell['type'] = spellType
        spell['level'] = int(spellLevel)
        spell['name'] = child.text
        spell['link'] = "https://2e.aonprd.com/"+child['href']
        focusSpells.append(spell)

t = 0
for spell in focusSpells:
    t += 1
    #print("loop numnber:",t)
    #if t > 1:
        #break

    res2 = requests.get(spell['link'])
    print("getting spell:", spell['name'])
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    detail2 = soup2.find(lambda tag: tag.name=='span' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_DetailedOutput") 
    traits = detail2.find_all("span", {"class" : lambda L: L and L.startswith('trai')})
    traitHolder = []
    for trait in traits:
        traitHolder.append(trait.text)
    spell['traits'] = traitHolder

    children2 = detail2.contents
    reachedBreak = False
    detailHolder = []
    tagType = ""
    for child2 in children2:

        stringContents = str(child2)
        #print(stringContents)
        if stringContents.startswith("<"):
            if not reachedBreak:
                if child2.name == "hr":
                    tagType = ""
                    reachedBreak = True
                
                if child2.name == "a":

                    try:
                        if child['class'][0] == "external-link" :
                            item['source'] = child.text
                    except:
                        pass
                if child2.name == "b":

                    if(child2.text != "Source"):
                        tagType = child2.text.lower().replace(" ", "")
            else:
                detailHolder.append(child2.text)        
        else:
            if reachedBreak:
                detailHolder.append(stringContents)
            else:
                if tagType != "":
                    spell[tagType] = stringContents
       #print(child)
    finalText = ""
    for text in detailHolder:
        if text.isspace():
            pass
        elif text == ", ":
            pass
        else:
            #print("text:", text)
            finalText += " "+text
    spell['text'] = finalText.strip()
    #print('<!!!!!!!!!!!!!!!!!!!!!!!!!>')
    



focusSpellsHolder['spells'] = focusSpells
json_data = json.dumps(focusSpellsHolder, indent=4)
filename = "focus-spells-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close
