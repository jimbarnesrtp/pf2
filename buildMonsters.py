from bs4 import BeautifulSoup
from bs4 import NavigableString
import requests
import json
import datetime
import re

monsterHolder = {}
monsterHolder['name'] = 'Pathfinder 2.0 monster list'
monsterHolder['date'] = datetime.date.today().strftime("%B %d, %Y")

attackEle = set(("Critical Success", "Success", "Failure", "Effect", "Frequency", "Requirement"))

def get_single(link):
    details = {}
    itemDetails = {}
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    detail = soup2.find(lambda tag: tag.name=='span' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_DetailedOutput") 

    attacks = soup2.find_all("span", {'class':'hanging-indent'})

    knowledgeCheck = ""

    inDamage = False
    attack = {}
    attackHolder = []
    spellProc = False
    spellHolder = []
    spell = {}
    for att in attacks:
        inDamage = False
        attack = {}
        children2 = att.contents
        for child2 in children2:
            stringContents2 = str(child2) 

            if stringContents2.startswith("<"):
                if child2.name == "b":
                    if "Spells" in stringContents2:
                        spellProc = True
                        if 'name' in spell:
                            spellHolder.append(spell)
                            spell = {}
                        spell['name'] = child2.text
                        
                    else:
                        x = re.search("\A\d+(th|st|rd|nd)", child2.text)
                        if 'Cantrips' in child2.text:
                            if 'text' in spell:
                                spell['text'] += child2.text
                            else:
                                spell['text'] = child2.text
                        elif x:
                            if 'text' in spell:
                                spell['text'] += child2.text
                            else:
                                spell['text'] = child2.text
                        else:
                            spellProc = False
                            #not sure if this should be in the iff or not
                            if child2.text == "Damage":
                                inDamage = True
                            elif child2.text in attackEle:
                                attack['text'] += child2.text
                            else:
                                attack['name'] = child2.text
                if child2.name == "i":
                    pass
                if child2.name == "img":
                    attack['actions'] = child2['alt']
                if child2.name == "a":
                    if spellProc:
                        if 'text' in spell:
                            spell['text'] += child2.text
                        else:
                            spell['text'] = child2.text
                    elif 'text' in attack:
                        attack['text'] += child2.text
                    else:
                        attack['text'] = child2.text
            else:
                if inDamage:
                    attack['damage'] = stringContents2
                else:
                    if spellProc:
                        if 'text' in spell:
                            spell['text'] += stringContents2
                        else:
                            spell['text'] = stringContents2
                    else:
                        if 'text' in attack:
                            attack['text'] += stringContents2
                        else:
                            attack['text'] = stringContents2
        attackHolder.append(attack)
                




    traits = detail.find_all("span", {"class" : lambda L: L and L.startswith('trai')})
    traitHolder = []
    for trait in traits:
        traitHolder.append(trait.text)
    details['traits'] = traitHolder
    children = detail.contents
    detailHolder = []
    tagType = ""
    h1Count = 0
    hrCount = 0
    inActions = False
    inAttacks = False
    pastHp = False
    actionHolder = []
    action = {}
    itemHolder = []
    skillsHolder = []
    string = ","
    langHolder = []
    attack = {}
    
    
    for child in children:

        stringContents = str(child)
        if "All Monsters in" in stringContents:
            break

        if stringContents.startswith("<"):
            #print(child.name,"|",tagType)
            if child.name == "hr":
                hrCount += 1
                if hrCount == 1:
                    inActions = True
                if hrCount == 2:
                    inActions = False
                    inAttacks = True
                tagType = ""

            if child.name == "h1":
                h1Count += 1
            
            if child.name == "h3":
                tagType = ""
            
            if child.name == "a":

                try:
                    if child['class'][0] == "external-link" :
                        details['source'] = child.text
                        #print("In here 5")
                        tagType = ""
                except:
                    pass
                if not child.text.isspace():
                    #print(child.text,"|",tagType)
                    if spellProc:
                        if 'text' in spell:
                            spell['text'] += child.text
                        else:
                            spell['text'] = child.text
                    elif tagType == "Skills":
                        skillsHolder.append(child.text)
                    elif tagType == "Items":
                        itemHolder.append(child.text)
                    elif tagType == "Languages":
                        langHolder.append(child.text)
                    elif tagType == "Resistances":
                        if tagType in details:
                            details[tagType] += child.text
                        else:
                            details[tagType] = child.text
                    elif inActions:
                        if 'text' in action:
                            action['text'] += child.text
                        else:
                            action['text'] = child.text
            if child.name == "u":
                if  not child.text.isspace():
                    if tagType == "Skills":
                        skillsHolder.append(child.text) 
                    if tagType == "Items":
                        itemHolder.append(child.text)   
            if child.name == "b":
                spellProc = False
                if inActions and pastHp:
                    if child.text != "Trigger" and child.text != "Immunities" and child.text != "Resistances" and child.text != "Effect" and child.text != "Weaknesses":
                        #print("in here 1")
                        tagType = ""
                        if (len(action.keys()) > 0):
                            actionHolder.append(action)
                            action = {}
                        action['name'] = child.text
                    else:
                        #print(child.text)
                        if "Spells" not in child.text:
                            tagType = child.text 
                    
                elif inAttacks: 
                    if "Spells" in child.text:
                        spellProc = True
                        #print("in here 2")
                        tagType = ""
                        if 'name' in spell:
                            spellHolder.append(spell)
                            spell = {}
                        spell['name'] = child.text
                        continue
                    else: 
                        spellProc = False
                    x = re.search("\A\d+(th|st|rd|nd)", child.text)
                    esc = re.escape("(")
                    y = re.search("\A"+esc +"\d+(th|st|rd|nd)",child.text)
                    if 'Cantrips' in child.text:
                        spellProc = True
                        if 'text' in spell:
                            spell['text'] += child.text
                        else:
                            spell['text'] = child.text
                        #print("IN here 3")
                        tagtype = ""
                    elif x:
                        spellProc = True
                        if 'text' in spell:
                            spell['text'] += child.text
                        else:
                            spell['text'] = child.text
                        #print("In here 6")
                        tagtype = ""
                    elif y:
                        spellProc = True
                        if 'text' in spell:
                            spell['text'] += child.text
                        else:
                            spell['text'] = child.text
                        #print("In here 7")
                        tagtype = ""
                    else:
                        spellProc = False
                        #print("2nd:",child.text)
                        if 'name' in attack and (not tagType.startswith("Speed")) :
                            pass
                        else:
                            tagType = child.text
                    #print("3rd:",tagType)
                
                    
                else:      
                    if(child.text != "Source" and child.text != "Trigger" and "Spells" not in child.text):
                        tagType = child.text
                        if "Recall Knowledge" in tagType:
                            startParen = stringContents.find("(")
                            endParen = stringContents.find(")")
                            knowledgeCheckStr = stringContents[startParen:endParen]
                            endForReal = knowledgeCheckStr.find("</a></u>")
                            knowledgeCheck = knowledgeCheckStr[32:endForReal]
                        if tagType == "HP":
                            pastHp = True
            #print("In here 11:",tagType)  
            
            if child.name == "img":
                if inActions:
                    action['action'] = child['alt']
                else:
                    details['actions'] = child['alt']
            if child.name == "i":
                #print(spellProc,child.text)
                if spellProc:
                    if 'text' in spell:
                        spell['text'] += child.text
                    else:
                        spell['text'] = child.text
                elif tagType != "":
                    if not stringContents.isspace():
                        details[tagType] = stringContents
            #print("In here 10:",tagType)                 
            if child.name == "li":
                if inActions:
                    action['Effect'] += child.text
            if child.name == "ul":
                if inActions:
                    action['Effect'] += child.text
            #else:
                #if not stringContents.isspace() :
                    #detailHolder.append(child.text)        
        else:
            if tagType != "" :
                if not stringContents.isspace():
                    
                    if inActions and ('name' in action) and (tagType != "Speed"):
                        action[tagType] = stringContents
                    else:
                        if tagType == "Skills":
                            skillsHolder.append(stringContents)
                        elif tagType == "Items":
                            itemHolder.append(stringContents)
                        elif "Recall Knowledge" in tagType:
                            
                            details['recallKnowledge'] = knowledgeCheck + stringContents
                        else:
                            if tagType in details:
                                details[tagType] += stringContents
                            else:
                                details[tagType] = stringContents
            else:
                if inActions:
                    if 'text' in action:
                        action['text'] += stringContents
                    else:
                        action['text'] = stringContents
                elif h1Count < 2:
                    detailHolder.append(stringContents) 
                elif spellProc:
                    if 'text' in spell:
                        spell['text'] += stringContents
                    else:
                        spell['text'] = stringContents
        #print("4th:",stringContents,"|type:",tagType)       

       #print(child)
    #print("final:",stringContents)
    if 'name' in action:
        actionHolder.append(action)

    if 'name' in spell:
        spellHolder.append(spell)
    details['spells'] = spellHolder
    details['Languages'] = langHolder
    details['skills'] = skillsHolder
    details['items'] = itemHolder
    details['actions'] = actionHolder
    details['attacks'] = attackHolder
    details['text'] = string.join(detailHolder)
    return details

def get_all():
    monsters = []
    res = requests.get("https://2e.aonprd.com/Monsters.aspx?Letter=All")
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')
    table = soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_TableElement") 
    rows = table.findAll(lambda tag: tag.name=='tr')
    t = 0
    for row in rows:
        t += 1
        #print(row)
        #print("-----------------------------------")
        monster = {}
        entries = row.find_all(lambda tag: tag.name=='td')
        #print(len(entries))
        if entries is not None:
            if len(entries) > 0:
                monster['name'] = entries[0].find("a").text
                monster['link'] = "https://2e.aonprd.com/"+entries[0].find("a")['href']
                monster['family'] = entries[1].text
                monster['level'] = int(entries[2].text)
                monster['alignment'] = entries[3].text
                monster['type'] = entries[4].text
                monster['size'] = entries[5].text
                monsters.append(monster)
                
               
                

        #if t > 3:
            #break
    
    for monster in monsters:
        print("Getting details for :",monster['name'])
        monsterDetails = get_single(monster['link'])
        for key in monsterDetails.keys():
            monster[key] = monsterDetails[key]
        
    
    return monsters

monsterHolder['monsters'] = get_all()
json_data = json.dumps(monsterHolder, indent=4)
#print(monsters)
filename = "monsters-v2-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close






