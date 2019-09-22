from bs4 import BeautifulSoup
import requests
import json
import datetime

spellHolder = {}
spellHolder['name'] = 'Pathfinder 2.0 spell list'
spellHolder['date'] = datetime.date.today().strftime("%B %d, %Y")

spells = []

def get_spells(link):
    spellDetail = {}
    res = requests.get(link)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')
    spell = soup.find_all("div", {'class':'article-content'})
    
    traitsScratch = spell[0].find_all("span", {'class':'trait'})
    traits = []
    if traitsScratch is not None:
        for trait in traitsScratch:
            traits.append(trait.text)
    spellDetail['traits'] = traits
    try:
         spellDetail['range'] = spell[0].find_all("span", {'class':'spell-range'})[0].text
    except:
        spellDetail['range'] = ""

    spellDetail['type'] = spell[0].find_all("span", {'class':'spell-type'})[0].text
    try:
        spellDetail['target'] = spell[0].find_all("span", {'class':'spell-targets'})[0].text
    except:
        spellDetail['target'] = ""
    paras = spell[0].find_all("p")
    hrIndex = 0
    for nextSibling in spell[0].children:
        #print(nextSibling)
        if nextSibling.name == 'hr':
            break
        else:
            if nextSibling.name == "p": 
                hrIndex += 1
        
    
    #print('HRINdex:', hrIndex)
    #print(len(paras))

    paraIndex = 0
    spellText = []
    for para in paras:
        text = para.text

        
        
        if "Cast" in text:
            #print(para)
            #print(text)
            start = text.find("Cast") + 4
            end = text.find(";", start)
            #print("Start", start)
            #print("End", end)
            if end < 0 :
                spellDetail['cast'] = text[start:]
            else:
                spellDetail['cast'] = text[start:end]

        if "Duration" in text:
            start = text.find("Duration") + 8
            end = text.find(";", start)
            if end < 0 :
                spellDetail['duration'] = text[start:]
            else: 
                spellDetail['duration'] = text[start:end]
        
        if "Requirements" in text:
            start = text.find("Requirements") + 12
            end = text.find(";", start)
            spellDetail['requirements'] = text[start:end]

        if "Trigger" in text:
            start = text.find("Trigger") + 8
            end = text.find(";", start)
            spellDetail['trigger'] = text[start:end]
        
        if "Range" in text:
            start = text.find("Range") + 5
            end = text.find(";", start)
            spellDetail['range'] = text[start:end]
        
        if "Area" in text:
            start = text.find("Area") + 4
            end = text.find(";", start)
            spellDetail['area'] = text[start:end]

        
        if "Saving Throw" in text:
            start = text.find("Saving Throw") + 12
            end = text.find(";", start)
            if end < 0 :
                spellDetail['savingThrow'] = text[start:]
            else: 
                spellDetail['savingThrow'] = text[start:end]

        if paraIndex > hrIndex:
            #print(para.text)
            spellText.append(para.text)
        paraIndex += 1
        
    
    if spellDetail['cast'] is None:
        spellDetail['cast'] = ""
    #print(spellText)
    spellDetail['spellText'] = spellText
    return spellDetail


res = requests.get("http://pf2.d20pfsrd.com/spell")
res.raise_for_status()
soup = BeautifulSoup(res.text, 'html.parser')
table = soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="archive-data-table") 
rows = table.findAll(lambda tag: tag.name=='tr')
t = 0
for row in rows:
    t += 1
    #print(row)
    #print("-----------------------------------")
    spell = {}
    entries = row.find_all(lambda tag: tag.name=='td')
    #print(len(entries))
    if entries is not None:
        if len(entries) > 0:
            name = entries[0].find("a").text
            link = entries[0].find("a")['href']
            #for entry in entries: 
             #   print(entry)
              #  print("row---------------")
            traditions = entries[1].text
            level = entries[2].text
            source = entries[4].find("a").text

            spellDetails = get_spells(link)
            
            spell['name'] = name
            spell['level'] = level
            spell['link'] = link
            spell['traditions'] = traditions.split(',')
            spell['source'] = source
            for key in spellDetails.keys():
                spell[key] = spellDetails[key]

    if len(spell.keys()) > 0:
        spells.append(spell)
    #if t > 10:
        #break
spellHolder['spells'] = spells
json_data = json.dumps(spellHolder)
#print(spells)
filename = "spells-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close






