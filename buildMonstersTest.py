from bs4 import BeautifulSoup
from bs4 import NavigableString
import requests
import json
import datetime
import re
from collections import defaultdict


monsterDetail = {}
res = requests.get('http://pf2.d20pfsrd.com/monster/gelatinous-cube/')
res.raise_for_status()
soup = BeautifulSoup(res.text, 'lxml')
monster = soup.find_all("div", {'class':'article-content'})

traitsScratch = monster[0].find_all("span", {'class':'trait'})
traits = []
if traitsScratch is not None:
    for trait in traitsScratch:
        traits.append(trait.text)
monsterDetail['traits'] = traits

monsterDetail['alignment'] = monster[0].find_all("span", {'class':'alignment'})[0].text
monsterDetail['size'] = monster[0].find_all("span", {'class':'size'})[0].text
typeScratch = monster[0].find_all("span", {'class':'monster-type'}) 
if typeScratch is not None:
    if len(typeScratch) > 0:
        monsterDetail['type'] = monster[0].find_all("span", {'class':'monster-type'})[0].text

monsterDetail['specials'] = []
specialScratch = monster[0].find_all("div", {'class':'special-abilities'})
if len(specialScratch) > 0:
    for scratch in specialScratch:
        specials = scratch.find_all("p")
        for special in specials:
            monsterDetail['specials'].append(special.text)

paras = monster[0].find_all("p")
monsterText = []
isFirstLine = True
lastSpellName = ""
for para in paras:
    isLineProcessed = False
    text = para.text
    if "Senses" in text:
        start = text.find("Senses") + 7
        monsterDetail['senses'] = re.split('; |, ',text[start:])
        isLineProcessed = True
    
    if "Languages" in text:
        start = text.find("Languages") + 10
        monsterDetail['languages'] = re.split('; |, ',text[start:])
        isLineProcessed = True

    if "Skills" in text:
        start = text.find("Skills") + 7
        monsterDetail['skills'] = re.split('; |, ',text[start:])
        isLineProcessed = True
    
    if text.startswith("Str"):
        monsterDetail['abilities'] = text.split(',')
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
            monsterDetail['items'] = text[start:].split(',')
        else: 
            monsterDetail['items'] = text[start:end].split(',')
        isLineProcessed = True

    if "AC" in text:
        start = text.find("AC") + 3
        end = text.find(";", start)
        if end < start:
            end = text.find("Fort", start)
        monsterDetail['ac'] = text[start:end]
        isLineProcessed = True

    if "Fort " in text:
        start = text.find("Fort")
        end = text.find(";", start)
        if end < 0 :
            monsterDetail['saves'] = text[start:].split(",")
        else: 
            monsterDetail['saves'] = text[start:end].split(",")
        isLineProcessed = True
    
    if "Will +" in text:
        start = text.find("Will +") + 7
        end = text.find(";", start) + 2
        if end < start:
            print("no extra saves")
        else:
            monsterDetail['saves'].append(text[end:])
        isLineProcessed = True

    if "HP" in text:
        if 'hp' not in monsterDetail:
            start = text.find("HP") + 3
            end = text.find(";", start)
            if end < 0 :
                monsterDetail['hp'] = text[start:].split(',')
            else: 
                monsterDetail['hp'] = text[start:end].split(',')
            
        isLineProcessed = True
    
    if "Immunities" in text:
        start = text.find("Immunities") + 11
        end = text.find(";", start)
        monsterDetail['immunities'] = text[start:end].split(',')
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
            monsterDetail['weaknesses'] = text[start:].split(',')
        else: 
            monsterDetail['weaknesses'] = text[start:end].split(',')
        isLineProcessed = True
    
    if "Resistances" in text:
        start = text.find("Resistances") + 11
        end = text.find(";", start)
        if end < 0 :
            monsterDetail['resistances'] = text[start:].split(',')
        else: 
            monsterDetail['resistances'] = text[start:end].split(',')
        isLineProcessed = True
        
    
    if "Speed" in text:
        if 'speed' not in monsterDetail:
            start = text.find("Speed") + 6
            end = text.find(";", start)
            if end < 0 :
                monsterDetail['speed'] = text[start:].split(',')
            else: 
                monsterDetail['speed'] = text[start:end].split(',')
        isLineProcessed = True
    
    if text.startswith("Melee"):
        
        if 'actions' not in monsterDetail:
            actionHolder = []
            actionHolder.append(text)
            monsterDetail['actions'] = actionHolder
        else:
            monsterDetail['actions'].append(text)
        isLineProcessed = True
    
    if text.startswith("Ranged"):
        if 'actions' not in monsterDetail:
            actionHolder = []
            actionHolder.append(text)
            monsterDetail['actions'] = actionHolder
        else:
            monsterDetail['actions'].append(text)
        isLineProcessed = True

    if (text.startswith("Occult Innate Spells")) or (text.startswith("Divine Innate Spells")) or (text.startswith("Arcane Innate Spells")):
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
        monsterDetail['spells'] = spells
        lastSpellName = 'spells'
        isLineProcessed = True
    
    if (text.startswith("Occult Rituals")) or (text.startswith("Divine Rituals")) :
        rituals = {}
        start = text.find("Rituals") + 8
        end = text.find(";",start)
        ritualsAttack = text[start:end].split(",")
        rituals['dc'] = ritualsAttack[0][3:]
        if len(ritualsAttack) > 1:
            rituals['attack'] = ritualsAttack[1][7:]
        rituals['rituals'] = text[end+1:].split(";")
        monsterDetail['rituals'] = rituals
        lastSpellName = 'rituals'
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
        spells['spells'] = text[end+1:].split(";")
        monsterDetail['spells'] = spells
        lastSpellName = 'spells'
        isLineProcessed = True

    if (text.startswith("Primal Prepared Spells")):
        spells = {}
        start = text.find("Prepared Spells") + 16
        end = text.find(";",start)
        if end < 0 :
            spellAttack = text[start:].split(",")
        else: 
            spellAttack = text[start:end].split(",")
        
        spells['dc'] = spellAttack[0][3:]
        if len(spellAttack) > 1:
            spells['attack'] = spellAttack[1][7:]
        spells['spells'] = text[end+1:].split(";")
        monsterDetail['primalPreparedSpells'] = spells
        lastSpellName = 'primalPreparedSpells'
        isLineProcessed = True

    if (text.startswith("Primal Innate Spells")):
        spells = {}
        start = text.find("Prepared Spells") + 16
        end = text.find(";",start)
        if end < 0 :
            spellAttack = text[start:].split(",")
        else: 
            spellAttack = text[start:end].split(",")
        
        spells['dc'] = spellAttack[0][3:]
        if len(spellAttack) > 1:
            spells['attack'] = spellAttack[1][7:]
        spells['spells'] = text[end+1:].split(";")
        monsterDetail['primalInnateSpells'] = spells
        lastSpellName = 'primalInnateSpells'
        isLineProcessed = True
    
    if not isLineProcessed:
        x = re.search("\A\d+(th|st|rd|nd)", text)
        if x:
            monsterDetail[lastSpellName]['spells'] = text.split(";")
            isLineProcessed = True
        
    if not isLineProcessed:
        if isFirstLine:
            isFirstLine = False
            continue
        else:
            #print(para.parent)
            try:
                #print(para.parent['class'])
                parentClass = para.parent['class'][0]
            except: 
                print("no Parent")
                parentClass = ""
            
            if "special-abilities" != parentClass:
                #print(text)
                monsterText.append(para.text)
            else:
                
                print("skipped")
        
#print(monsterText)
monsterDetail['monsterText'] = monsterText
print(monsterDetail)

