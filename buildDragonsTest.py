from bs4 import BeautifulSoup
from bs4 import NavigableString
import requests
import json
import datetime
import re


link = 'http://pf2.d20pfsrd.com/monster/silver-dragon/'
res = requests.get(link)
res.raise_for_status()
soup = BeautifulSoup(res.text, 'lxml')
monster = soup.find_all("div", {'class':'article-content'})

children = monster[0].findChildren(recursive=False)
monsters = {}
monsterIndex = 0
lastSpellName = ""
isFirstLine = True
aboutHolder = []
aboutText = False
dragonType = ""
for child in children:
    isLineProcessed = False
    #print(child.name)
    
    tagName = child.name
    
    if tagName == "h4":
        classHolder = child.get("class")
        print("in here:", child.text)
        
        if classHolder is None:
            text = child.text
            if text.startswith("Young G"):
                dragonType = "Young Gold Dragon"
            elif text.startswith("Adult G"):
                dragonType = "Adult Gold Dragon"
            elif text.startswith("Ancient Gold"):
                dragonType = "Ancient Gold Dragon"
            continue
        if 'monsters' not in monsters:
            monsters['monsters'] = []
        else:
            monsterIndex += 1
        monsters['monsters'].append({})

        
        monsters['monsters'][monsterIndex]['name'] = child.contents[0]
        monsters['monsters'][monsterIndex]['level'] = child.find("span", {'class':'monster-level'}).text
        monsters['monsters'][monsterIndex]['link'] = link
        monsters['monsters'][monsterIndex]['type'] = child.find("span", {'class':'monster-type'}).text
        monsters['monsters'][monsterIndex]['monsterText'] = []
        monsters['monsters'][monsterIndex]['specials'] = []
        isLineProcessed = True
    
    if tagName == "div":
        print("checking for special")
        try:
            pClass = child['class'][0]
            #print(pClass)
        except: 
            pClass = ""
        print("specialCheck:", pClass)
        if pClass == "special-abilities":
            
            specialScratch = child.findChildren(recursive=False)
            if len(specialScratch) > 0:
                print("in here")
                for scratch in specialScratch:
                    monsters['monsters'][monsterIndex]['specials'].append(scratch.text)

    if tagName == "p":
        text = child.text
        if text == 'About':
            aboutText = True

        try:

            pClass = child['class'][0]
            #print(pClass)
        except: 
            pClass = ""

        if pClass == "traits":
            traitsScratch = child.find_all("span", {'class':'trait'})
            traits = []
            if traitsScratch is not None:
                if(len(traitsScratch) < 2):
                    monsters['monsters'][monsterIndex]['monsterText'].append(traitsScratch[0].text)
                else:
                    monsters['monsters'][monsterIndex]['alignment'] = child.find("span", {'class':'alignment'}).text
                    monsters['monsters'][monsterIndex]['size'] = child.find("span", {'class':'size'}).text
                    frequency = child.find("span", {'class':'frequency'})
                    if frequency is not None:
                        monsters['monsters'][monsterIndex]['frequency'] = frequency.text
                    for trait in traitsScratch:
                        traits.append(trait.text)
            monsters['monsters'][monsterIndex]['traits'] = traits
            print(monsters['monsters'][monsterIndex]['name'])
            isLineProcessed = True
        
        if "Senses" in text:
            start = text.find("Senses") + 7
            monsters['monsters'][monsterIndex]['senses'] = re.split('; |, ',text[start:])
            isLineProcessed = True
        
        if "Languages" in text:
            start = text.find("Languages") + 10
            monsters['monsters'][monsterIndex]['languages'] = re.split('; |, ',text[start:])
            isLineProcessed = True

        if "Skills" in text:
            start = text.find("Skills") + 7
            monsters['monsters'][monsterIndex]['skills'] = re.split('; |, ',text[start:])
            isLineProcessed = True
        
        if text.startswith("Str"):
            monsters['monsters'][monsterIndex]['abilities'] = text.split(',')
            isLineProcessed = True

        if "Items" in text:
            start = text.find("Items") + 6
            end = text.find(";", start)
            endAC = text.find("AC", start)
            if end < 0:
                if not endAC < 0:
                    end = AC 
            else:
                if endAC  < end:
                    end = endAC 
            if end < 0 :
                monsters['monsters'][monsterIndex]['items'] = text[start:].split(',')
            else: 
                monsters['monsters'][monsterIndex]['items'] = text[start:end].split(',')
            isLineProcessed = True

        if "AC" in text:
            start = text.find("AC") + 3
            end = text.find(";", start)
            if end < start:
                end = text.find("Fort", start)
            monsters['monsters'][monsterIndex]['ac'] = text[start:end]
            isLineProcessed = True

        if "Fort " in text:
            start = text.find("Fort")
            end = text.find(";", start)
            if end < 0 :
                monsters['monsters'][monsterIndex]['saves'] = text[start:].split(",")
            else: 
                monsters['monsters'][monsterIndex]['saves'] = text[start:end].split(",")
            isLineProcessed = True
        
        if "Will +" in text:
            start = text.find("Will +") + 7
            end = text.find(";", start) + 2
            if end < start:
                print("no extra saves")
            else:
                monsters['monsters'][monsterIndex]['saves'].append(text[end:])
            isLineProcessed = True

        if "HP" in text:
            if 'hp' not in monsters['monsters'][monsterIndex]:
                start = text.find("HP") + 3
                end = text.find(";", start)
                if end < 0 :
                    monsters['monsters'][monsterIndex]['hp'] = text[start:].split(',')
                else: 
                    monsters['monsters'][monsterIndex]['hp'] = text[start:end].split(',')
                
            isLineProcessed = True
        
        if "Immunities" in text:
            start = text.find("Immunities") + 11
            end = text.find(";", start)
            if end < 0 :
                monsters['monsters'][monsterIndex]['immunities'] = text[start:].split(',')
            else: 
                monsters['monsters'][monsterIndex]['immunities'] = text[start:end].split(',')
            
            isLineProcessed = True

        if "Weaknesses" in text:
            start = text.find("Weaknesses") + 11
            end = text.find(";", start)
            endResistences = text.find("Resistances", start)
            if end < 0:
                if not endResistences < 0:
                    end = endResistences
            else:
                if endResistences < end:
                    end = endResistences
            if end < 0 :
                monsters['monsters'][monsterIndex]['weaknesses'] = text[start:].split(',')
            else: 
                monsters['monsters'][monsterIndex]['weaknesses'] = text[start:end].split(',')
            isLineProcessed = True
        
        if "Resistances" in text:
            start = text.find("Resistances") + 11
            end = text.find(";", start)
            if end < 0 :
                monsters['monsters'][monsterIndex]['resistances'] = text[start:].split(',')
            else: 
                monsters['monsters'][monsterIndex]['resistances'] = text[start:end].split(',')
            isLineProcessed = True
            
        
        if "Speed" in text:
            if 'speed' not in monsters['monsters'][monsterIndex]:
                start = text.find("Speed") + 6
                end = text.find(";", start)
                if end < 0 :
                    monsters['monsters'][monsterIndex]['speed'] = text[start:].split(',')
                else: 
                    monsters['monsters'][monsterIndex]['speed'] = text[start:end].split(',')
            isLineProcessed = True
        
        if text.startswith("Melee"):
            
            if 'actions' not in monsters['monsters'][monsterIndex]:
                actionHolder = []
                actionHolder.append(text)
                monsters['monsters'][monsterIndex]['actions'] = actionHolder
            else:
                monsters['monsters'][monsterIndex]['actions'].append(text)
            isLineProcessed = True
        
        if text.startswith("Ranged"):
            if 'actions' not in monsters['monsters'][monsterIndex]:
                actionHolder = []
                actionHolder.append(text)
                monsters['monsters'][monsterIndex]['actions'] = actionHolder
            else:
                monsters['monsters'][monsterIndex]['actions'].append(text)
            isLineProcessed = True
        
        if text.startswith("Breath Weapon"):
            
            if 'breathWeapon' not in monsters['monsters'][monsterIndex]:
                actionHolder = []
                actionHolder.append(text)
                monsters['monsters'][monsterIndex]['breathWeapon'] = actionHolder
            else:
                monsters['monsters'][monsterIndex]['breathWeapon'].append(text)
            isLineProcessed = True
        
        if  (text.startswith("Divine Innate Spells")) or (text.startswith("Arcane Innate Spells")):
            spells = {}
            start = text.find("Innate Spells") + 13
            end = text.find(";",start)
            if end < 0 :
                spellAttack = text[start:].split(",")
            else: 
                spellAttack = text[start:end].split(",")
            
            spells['dc'] = spellAttack[0][3:]
            if len(spellAttack) > 1:
                spells['attack'] = spellAttack[1][7:]
            spells['spells'] = text[end+1:].split(";")
            monsters['monsters'][monsterIndex]['innateSpells'] = spells
            lastSpellName = 'innateSpells'
            isLineProcessed = True

        if (text.startswith("Occult Spontaneous Spells")) or (text.startswith("Divine Spontaneous Spells")) or (text.startswith("Arcane Spontaneous Spells")):
            spells = {}
            start = text.find("Spontaneous Spells") + 19
            end = text.find(";",start)
            if end < 0 :
                spellAttack = text[start:].split(",")
            else: 
                spellAttack = text[start:end].split(",")
            
            spells['dc'] = spellAttack[0][3:]
            if len(spellAttack) > 1:
                spells['attack'] = spellAttack[1][7:]
            if "Note:" in text:
                spells['note'] = spellAttack[2][5:]
            else: 
                spells['spells'] = text[end+1:].split(";")
            monsters['monsters'][monsterIndex]['spontaneousSpells'] = spells
            lastSpellName = 'spontaneousSpells'
            isLineProcessed = True
        
        if (text.startswith("Primal Prepared Spells")) or (text.startswith("Arcane Prepared Spells")) or (text.startswith("Divine Prepared Spells")) :
            spells = {}
            start = text.find("Prepared Spells") + 16
            end = text.find(";",start)
            if end < 0 :
                spellAttack = text[start:].split(",")
            else: 
                spellAttack = text[start:end].split(",")
            if "" != dragonType:
                position = 0
                for dragon in monsters['monsters']:
                    
                    if dragonType == dragon['name']:
                        monsterIndex = position
                        print("monsterIndex:", monsterIndex)
                    else:
                        position += 1

            spells['dc'] = spellAttack[0][3:]
            if len(spellAttack) > 1:
                spells['attack'] = spellAttack[1][7:]
            if "Note" in text:
                spells['note'] = text[end+6:]
            else: 
                if "dragon, plus" in text:
                    start = text.find("dragon, plus")  + 13
                    print("in here 2", dragonType)
                    
                    previousIndex = monsterIndex - 1                           
                    print (monsterIndex)
                    listHolder =  text[start:].split(";") + monsters['monsters'][previousIndex]['preparedSpells']['spells']
                    spells['spells'] = listHolder
                else:
                    spells['spells'] = text[end+1:].split(";")

            monsters['monsters'][monsterIndex]['preparedSpells'] = spells
            lastSpellName = 'preparedSpells'
            isLineProcessed = True
        
        if not isLineProcessed:
            x = re.search("\A\d+(th|st|rd|nd)", text)
            if x:
                monsters['monsters'][monsterIndex][lastSpellName]['spells'] = text.split(";")
                isLineProcessed = True
            
            if "dragon, plus" in text:
                start = text.find("dragon, plus")  + 13
                previousIndex = monsterIndex - 1
                listHolder =  text[start:].split(";") + monsters['monsters'][previousIndex][lastSpellName]['spells']
                monsters['monsters'][monsterIndex][lastSpellName]['spells'] = listHolder
            
        
        if not isLineProcessed:
            if aboutText:
                aboutHolder.append(text)
            else: 
                try:
                    #print(para.parent['class'])
                    parentClass = para.parent['class'][0]
                except: 
                    #print("no Parent")
                    parentClass = ""
                if "special-abilities" != parentClass:
                    #print(text)
                    monsters['monsters'][monsterIndex]['monsterText'].append(child.text)
                else:
                    
                    print("skipped")

for monster in monsters['monsters']:

    listHolder = monster['monsterText'] + aboutHolder
    monster['monsterText'] = listHolder

json_data = json.dumps(monsters)
print(json_data)

