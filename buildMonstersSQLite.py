from bs4 import BeautifulSoup
from bs4 import NavigableString
import requests
import re
import sqlite3
import json
import datetime
from PIL import Image
# Collect the github page

basewidth = 150

traits_list = ["No Traits", "Aasimar", "Acid", "Aeon", "Air", "Alchemical", "Amphibious",
"Anadi", "Angel", "Aquatic", "Archon", "Azata", "Boggard", "Caligni", "Catfolk", "Changeling",
"Charau-ka", "Cold", "Daemon", "Demon", "Dero", "Devil",  "Dhampir", "Dinosaur", "Drow",
"Duergar","Duskwalker", "Dwarf", "Earth", "Electricity", "Elf", "Evil", "Fire", "Genie",
"Ghost", "Ghoul", "Gnoll", "Gnome", "Goblin", "Golem", "Gremlin", "Grippli", "Hag", "Human",
"Incorporeal", "Inevitable", "Kobold", "Leshy", "Lizardfolk", "Merfolk", "Mindless", "Mummy",
"Mutant", "Nymph", "Orc", "Protean", "Psychopomp", "Rakshasa", "Ratfolk", "Sea Devil", "Shoony",
"Skeleton", "Soulbound", "Sprite", "Swarm", "Tengu", "Tiefling", "Troll", "Vampire", "Velstrac",
"Water", "Werecreature", "Wight", "Wraith", "Xulgath", "Zombie"]

rarity_list = ["Uncommon", "Rare", "Unique"]

attackEle = set(("Critical Success", "Success", "Failure", "Effect", "Frequency", "Requirements", "Saving Throw"))
elements2 = set(("Trigger","Immunities","Resistances","Effect","Weaknesses","Hardness","Frequency"))
#Verify if already exist the location in table and add a new value to it
def add_value(table,location,value):
    if location in table:
        return table[location] + value
    else:
        return value

def get_single(monster_url):
    page = requests.get(monster_url)
    #page = requests.get('https://2e.aonprd.com/Monsters.aspx?ID=113')

    # Create a BeautifulSoup object
    page.raise_for_status()
    soup2 = BeautifulSoup(page.text, 'lxml')
    detail = soup2.find(lambda tag: tag.name == 'span' and tag.has_attr(
        'id') and tag['id'] == "ctl00_MainContent_DetailedOutput")
    attacks = soup2.find_all("span", {'class': 'hanging-indent'})

    knowledgeCheck = ""
    details = {}
    itemDetails = {}
    knowledgeCheck = ""

    inDamage = False
    attack = {}
    attackHolder = []

    spellProc = False
    spellHolder = []
    spell = {}

    ritualProc = False
    ritualHolder = []
    ritual = {}

    ########################## ATTACK  ####################################
    for att in attacks:
        inDamage = False
        inFrequency = False
        inTrigger = False
        inEffect = False
        attack = {}
        children2 = att.contents
        for child2 in children2:
            stringContents2 = str(child2) 
            if stringContents2.startswith("<"):
                if child2.name == "b":
                    inDamage = False
                    inFrequency = False
                    inTrigger = False
                    inEffect = False
                    if "Spells" in stringContents2:
                        spellProc = True
                        if 'name' in spell:
                            spellHolder.append(spell)
                            spell = {}
                        spell['name'] = child2.text
                        
                    else:
                        x = re.search("\A\d+(th|st|rd|nd)", child2.text)
                        if ('Cantrips' in child2.text) or ('Constant' in child2.text) or x:
                            spell['text'] = add_value(spell,'text',child2.text)
                        else:
                            spellProc = False
                            if child2.text == "Damage":
                                inDamage = True
                            elif child2.text == "Frequency":
                                inFrequency = True
                            elif child2.text == "Trigger":
                                inTrigger = True
                            elif child2.text == "Effect":
                                inEffect = True

                            elif child2.text in attackEle or "Stage" in child2.text:
                                attack['text'] += child2.text
                            else:
                                attack['name'] = child2.text
                if child2.name == "i":
                    pass
                if child2.name == "img":
                    attack['actions'] = child2['alt']
                if child2.name == "a":
                    if spellProc:
                        spell['text'] = add_value(spell,'text',child2.text)
                    else:
                        attack['text']=add_value(attack,'text',child2.text)

            else:
                #Aqui é nome simples e tem que colocar no lugar certo
                if inDamage:
                    attack['damage'] = stringContents2
                elif inFrequency:
                    attack['frequency'] = stringContents2
                elif inTrigger:
                    attack['trigger'] = stringContents2
                elif inEffect:
                    attack['effect'] = stringContents2
                else:
                    if spellProc:
                        spell['text'] = add_value(spell,'text',stringContents2)
                    else:
                        attack['text']=add_value(attack,'text',stringContents2)
        if 'name' in attack:
            attackHolder.append(attack)
    ########################## ATTACK  ####################################


    ########################### TRAITS  ####################################
    traits = detail.find_all("span", {"class" : lambda L: L and L.startswith('trai')})
    traitHolder = []
    rarity = ""
    for trait in traits:
        if trait.text in traits_list:
            traitHolder.append(trait.text.strip())    
        if trait.text in rarity_list:
            rarity = trait.text
    details['traits'] = traitHolder
    if rarity == "":
        rarity = "Common"
    details['rarity'] = rarity

    ################# TRAITS  ####################################

    ################# Pegar o resto das coisas  ####################################
    children = detail.contents
    detailHolder = ""
    tagType = ""
    h1Count = 0
    hrCount = 0
    spellProc = False
    inPassive = False
    inActions = False
    inAttacks = False
    pastHp = False
    passiveHolder = []
    actionHolder = []
    passive = {}
    action = {}
    itemHolder = []
    skillsHolder = []
    langHolder = []
    attack = {}
    isDetails = False

        
    for child in children:
        stringContents = str(child)
        if "All Monsters in" in stringContents:
            break
            #Esses dados não importam

        if stringContents.startswith("<"):
            #Separa em qual parte é para saber o que é o texto lido
            if child.name == "t":
                children+=child.contents
                print("Passou T")
            if child.name == "h1":
                ritualProc = False
                spellProc = False
                h1Count += 1
                if h1Count==1:
                   isDetails = True
            else:
                isDetails = False

            if child.name == "h2":
                isDetails = False
      
            if child.name == "h3":
                ritualProc = False
                spellProc = False
                tagType = ""

            if((h1Count>1) or ('recallKnowledge' in details)):
                if child.name == "hr":
                    ritualProc = False
                    hrCount += 1
                    if hrCount == 1:
                        inPassive = False
                        inActions = True
                    if hrCount == 2:
                        inActions = False
                        inAttacks = True
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
                            spell['text'] = add_value(spell,'text',child.text)
                        if ritualProc:
                            ritual['text'] = add_value(ritual,'text',child.text)
                        elif tagType == "Skills":
                            skillsHolder.append(child.text)
                        elif tagType == "Items":
                            itemHolder.append(child.text)
                        elif tagType == "Languages":
                            langHolder.append(child.text)
                        elif tagType == "Resistances":
                            detail[tagType] = add_value(detail,tagType,child.text)
                        elif inPassive:
                            if tagType == "":
                                passive['text'] = add_value(passive,'text',child.text)
                            else:
                                passive[tagType] = add_value(passive,tagType,child.text)
                        elif inActions:
                            if tagType == "":
                                action['text'] = add_value(action,'text',child.text)
                            else:
                                action[tagType] = add_value(action,tagType,child.text)
                        elif(child.img != None):
                            # print('Downloading Image...')
                            pic_url = "https://2e.aonprd.com/"+child.img['src']
                            pic_name =child.img['src'].split('\\')[2] 
                            # with open("Images/"+pic_name, 'wb') as handle:
                            #     response = requests.get(pic_url, stream=True)
                            #     if not response.ok:
                            #         print(response)

                            #     for block in response.iter_content(1024):
                            #         if not block:
                            #             break
                            #         handle.write(block)
                            details['images'] = pic_name
                            # print('Downloded Image')
                            # print('Thumbnail')
                            # image = Image.open("Images/"+pic_name)
                            # wpercent = (basewidth/float(image.size[0]))
                            # hsize = int((float(image.size[1])*float(wpercent)))
                            # image.thumbnail((basewidth,hsize), Image.ANTIALIAS)
                            # image.save("Images/"+pic_name)



                if child.name == "u":
                    if  not child.text.isspace():
                        if tagType == "Skills":
                            skillsHolder.append(child.text) 
                        if tagType == "Items":
                            itemHolder.append(child.text)   
                if child.name == "b":
                    if child.text == "Items":
                        inPassive = False
                    if inPassive:
                        if not child.text in elements2:
                            #print("in here 1")
                            tagType = ""
                            if (len(passive.keys()) > 0):
                                passiveHolder.append(passive)
                                passive = {}
                            passive['name'] = child.text
                        else:
                            #print(child.text)
                            if "Spells" not in child.text:
                                spellProc = False
                                tagType = child.text 
                        
                    elif inActions and pastHp:
                        if not child.text in elements2:
                            #print("in here 1")
                            tagType = ""
                            if (len(action.keys()) > 0):
                                actionHolder.append(action)
                                action = {}
                            action['name'] = child.text
                        else:
                            #print(child.text)
                            if "Spells" not in child.text:
                                spellProc = False
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
                        elif "Rituals" in child.text:
                            spellProc = False
                            ritualProc = True
                            tagType = ""
                            if 'name' in ritual:
                                ritualHolder.append(ritual)
                                ritual = {}
                            ritual['name'] = child.text
                            continue
                        else: 
                            spellProc = False
                        x = re.search("\A\d+(th|st|rd|nd)", child.text)
                        esc = re.escape("(")
                        y = re.search("\A"+esc +"\d+(th|st|rd|nd)",child.text)
                        if 'Cantrips' in child.text or x or y or 'Constant' in child.text or 'Constant' in child.text:
                            if ritualProc:
                                ritual['text'] = add_value(ritual,'text',child.text)
                            else:
                                spellProc = True
                                spell['text'] = add_value(spell,'text',child.text)
                            #print("IN here 3")
                            tagtype = ""
                        else:
                            spellProc = False
                            ritualProc = False
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
                                recallKnowledgeList = child.find_all('a') 
                                knowledgeCheck = recallKnowledgeList[0].text + " (" 
                                for teste in recallKnowledgeList[1:]:
                                    knowledgeCheck+=(teste.text+",")
                                knowledgeCheck=knowledgeCheck[:-1]+")" 
                                knowledgeCheck = knowledgeCheck.replace("Recall Knowledge - ","")
                                details['recallKnowledge'] = add_value(details, 'recallKnowledge',  knowledgeCheck)
                            if tagType == "HP":
                                pastHp = True
                            if tagType == "Cha":
                                inPassive = True
                #print("In here 11:",tagType)  
                
                if child.name == "img":
                    if inActions:
                        action['action'] = child['alt']
                    elif inPassive:
                        passive['action'] = child['alt']
                    else:
                        details['actions'] = child['alt']
                if child.name == "i":
                    #print(spellProc,child.text)
                    if inPassive:
                        passive['text'] = add_value(passive,'text',child.text)
                    elif spellProc:
                        spell['text'] = add_value(spell,'text',child.text)
                    elif ritualProc:
                        ritual['text'] = add_value(ritual,'text',child.text)
                    elif inActions:
                        action['text'] = add_value(action,'text',child.text)
                    elif tagType != "":
                        if not stringContents.isspace():
                            details[tagType]=add_value(details,tagType,child.text)
                    elif h1Count < 2:
                        detailHolder+=child.text 
                
                #print("In here 10:",tagType)                 
                if child.name == "li":
                    if inActions:
                        action['Effect'] += child.text
                    if inPassive:
                        passive['Effect'] += child.text
                if child.name == "ul":
                    if inActions:
                        for ident in child.find_all('li'):
                            action['Effect'] += ("\n"+ident.text)
                    if inPassive:
                        for ident in child.find_all('li'):
                            passive['Effect'] += ("\n"+ident.text)
                #else:
                    #if not stringContents.isspace() :
                        #detailHolder.append(child.text)        
            elif(h1Count==1):
                if child.name == "b":
                    if "Recall Knowledge" in child.text:
                        tagType = child.text
                        recallKnowledgeList = child.find_all('a') 
                        knowledgeCheck = recallKnowledgeList[0].text + " ("
                        for teste in recallKnowledgeList[1:]:
                            knowledgeCheck+=(teste.text+",")
                        knowledgeCheck=knowledgeCheck[:-1]+")" 
                        knowledgeCheck = knowledgeCheck.replace("Recall Knowledge - ","")
                        details['recallKnowledge'] = add_value(
                                details, 'recallKnowledge',  knowledgeCheck)
        else:
            if tagType != "" :
                if not stringContents.isspace():                
                    if inPassive and ('name' in passive) and (tagType != "Speed"):
                        passive[tagType] = add_value(passive,tagType,stringContents)
                    elif inActions and ('name' in action) and (tagType != "Speed"):
                        action[tagType] = add_value(action,tagType,stringContents)
                    else:
                        if tagType == "Skills":
                            skillsHolder.append(stringContents)
                        elif tagType == "Items":
                            itemHolder.append(stringContents)
                        elif "Recall Knowledge" in tagType:
                            details['recallKnowledge'] = add_value(details,'recallKnowledge', stringContents+';')
                        else:
                            details[tagType] = add_value(details,tagType,stringContents)

            else:
                if h1Count < 2:
                    if(isDetails):
                        detailHolder+=stringContents 
                elif inPassive:
                    passive['text']=add_value(passive,'text',stringContents)
                elif spellProc:
                    spell['text']=add_value(spell,'text',stringContents)
                elif ritualProc:
                    ritual['text']=add_value(ritual,'text',stringContents)
                elif inActions:
                    action['text']=add_value(action,'text',stringContents)
        #print("4th:",stringContents,"|type:",tagType)       

        #print(child)
    #print("final:",stringContents)
    if 'name' in action:
        actionHolder.append(action)

    if 'name' in passive:
        passiveHolder.append(passive)

    if 'name' in spell:
        spellHolder.append(spell)

    if 'name' in ritual:
        ritualHolder.append(ritual)

    if  not 'images' in details:
        details['images'] = ""

    if  not 'Immunities' in details:
        details['Immunities'] = ""

    if  not 'Resistances' in details:
        details['Resistances'] = ""

    if  not 'Weaknesses' in details:
        details['Weaknesses'] = ""

    if  not 'Hardness' in details:
        details['Hardness'] = ""

    if  not 'recallKnowledge' in details:
        details['recallKnowledge'] = ""

    details['spells'] = spellHolder
    details['rituals'] = ritualHolder
    details['Languages'] = langHolder
    details['skills'] = skillsHolder
    details['Items'] = itemHolder
    details['passive'] = passiveHolder
    details['actions'] = actionHolder
    details['attacks'] = attackHolder
    details['text'] = detailHolder
#    details_pretty = json.dumps(details, sort_keys=True, indent=4, separators=(',', ': '))
#    print(details_pretty)
    return(details)

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
                
        # if t > 3:
        #      break
    
    for monster in monsters:
        print("Getting details for :",monster['name'])
        monsterDetails = get_single(monster['link'])
        for key in monsterDetails.keys():
            monster[key] = monsterDetails[key]
    return monsters

monsterHolder = {}
monsterHolder['name'] = 'Pathfinder 2.0 monster list'
monsterHolder['date'] = datetime.date.today().strftime("%B %d, %Y")

monsterHolder['monsters'] = get_all()


conn = sqlite3.connect('example.db')
c = conn.cursor()

c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='monsterBasic' ''')
#if the count is 1, then table exists
if c.fetchone()[0]!=1 : 
    print('Creating Table monsterBasic')
    c.execute('''CREATE TABLE monsterBasic(
                monster_id     INTEGER PRIMARY KEY,
                monster_name STRING  NOT NULL,
                monster_level  INTEGER NOT NULL,
                monster_type   STRING  NOT NULL,
                monster_traits STRING  NOT NULL,
                monster_family STRING  NOT NULL,
                monster_size   STRING  NOT NULL,
                monster_rarity   STRING  NOT NULL
    )''')
# else :
# 	print('Table exists.')

c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='monsterAttack' ''')
#if the count is 1, then table exists
if c.fetchone()[0]!=1 : 
    print('Creating Table monsterAttack')
    c.execute('''CREATE TABLE monsterAttack(
                attack_id     INTEGER PRIMARY KEY autoincrement,
                monster_id     INTEGER,
                attack_name STRING  NOT NULL,
                attack_text STRING  NOT NULL,
                attack_action STRING,
                attack_frequency STRING,
                attack_trigger STRING,
                attack_effect STRING,
                attack_damage STRING
    )''')
# else :
# 	print('Table exists.')
c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='monsterAction' ''')
#if the count is 1, then table exists
if c.fetchone()[0]!=1 : 
    print('Creating Table monsterAction')
    c.execute('''CREATE TABLE monsterAction(
                action_id     INTEGER PRIMARY KEY autoincrement,
                monster_id     INTEGER,
                action_name STRING  NOT NULL,
                action_text STRING  NOT NULL,
                action_action STRING,
                action_trigger STRING,
                action_frequency STRING,
                action_effect STRING
    )''')
# else :
# 	print('Table exists.')

c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='monsterPassive' ''')
#if the count is 1, then table exists
if c.fetchone()[0]!=1 : 
    print('Creating Table monsterPassive')
    c.execute('''CREATE TABLE monsterPassive(
                passive_id     INTEGER PRIMARY KEY autoincrement,
                monster_id     INTEGER,
                passive_name STRING  NOT NULL,
                passive_text STRING  NOT NULL,
                passive_action STRING
    )''')
# else :
# 	print('Table exists.')

c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='monsterSpell' ''')
#if the count is 1, then table exists
if c.fetchone()[0]!=1 : 
    print('Creating Table monsterSpell')
    c.execute('''CREATE TABLE monsterSpell(
                spell_id     INTEGER PRIMARY KEY autoincrement,
                monster_id     INTEGER,
                spell_name STRING  NOT NULL,
                spell_text STRING  NOT NULL
    )''')
# else :
# 	print('Table exists.')


c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='monsterRitual' ''')
#if the count is 1, then table exists
if c.fetchone()[0]!=1 : 
    print('Creating Table monsterRitual')
    c.execute('''CREATE TABLE monsterRitual(
                ritual_id     INTEGER PRIMARY KEY autoincrement,
                monster_id     INTEGER,
                ritual_name STRING  NOT NULL,
                ritual_text STRING  NOT NULL
    )''')
# else :
# 	print('Table exists.')

c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='monsterDetails' ''')
#if the count is 1, then table exists
if c.fetchone()[0]!=1 : 
    print('Creating Table monsterDetails')
    c.execute('''CREATE TABLE monsterDetails(
                details_id     INTEGER PRIMARY KEY autoincrement,
                details_AC	   STRING	NOT NULL,
                details_Fort   STRING	NOT NULL,
                details_Ref	   STRING	NOT NULL,
                details_Will   STRING	NOT NULL,
                details_HP	   STRING	NOT NULL,
                details_Perception	STRING	NOT NULL,
                details_Str	   INTEGER	NOT NULL,
                details_Dex	   INTEGER	NOT NULL,
                details_Con	   INTEGER	NOT NULL,
                details_Int	   INTEGER	NOT NULL,
                details_Wis	   INTEGER	NOT NULL,
                details_Cha	   INTEGER	NOT NULL,
                details_Languages	STRING	NOT NULL,
                details_Resistence	STRING	NOT NULL,
                details_Imunities	STRING	NOT NULL,
                details_Weaknesses	STRING	NOT NULL,
                details_Hardness	STRING	NOT NULL,
                details_Speed	    STRING	NOT NULL,
                details_images	    STRING	NOT NULL,
                details_source	    STRING	NOT NULL,
                details_recallKnowledge    STRING	NOT NULL,
                details_text	    STRING	NOT NULL,
                details_Items	    STRING	NOT NULL,
                details_skills	    STRING	NOT NULL,
                details_alignment	STRING	NOT NULL,
                details_actions	    INTEGER	NOT NULL,
                details_passive 	INTEGER	NOT NULL,
                details_spells	    INTEGER	NOT NULL,
                details_rituals	    INTEGER	NOT NULL,
                details_attacks	    INTEGER	NOT NULL
    )''')
# else :
# 	print('Table exists.')
#TODO: trim antes de join
monsterBasic = []
for monsters in monsterHolder['monsters']:
    print("Adding "+monsters['name']+"to database.")
    monsterId = int(monsters['link'].split('=')[1])
    monsterBasic = (
        monsterId,
        monsters['name'],
        monsters['level'],
        monsters['type'],
        ",".join(monsters['traits']),
        monsters['family'],
        monsters['size'],
        monsters['rarity']
        )
    # print(monsterBasic)
    c.execute("SELECT monster_id FROM monsterBasic WHERE monster_id = ?", (monsterId,))
    data=c.fetchone()
    if data is None:
        # print('Adding ' + monsters['name'] + ' into database')
        c.execute('INSERT INTO monsterBasic VALUES (?,?,?,?,?,?,?,?)', monsterBasic)
    # else:
    #     print(monsters['name'] + ' already in database')
    for attack in monsters['attacks']:
        if 'name' in attack:
            if not 'text' in attack:
                attack['text']=""
            if not 'actions' in attack:
                attack['actions']=None
            if not 'frequency' in attack:
                attack['frequency']=None
            if not 'trigger' in attack:
                attack['trigger']=None
            if not 'effect' in attack:
                attack['effect']=None
            if not 'damage' in attack:
                attack['damage']=None
            attackList = (
                    None,
                    monsterId,
                    attack['name'],
                    attack['text'],
                    attack['actions'],   
                    attack['frequency'],
                    attack['trigger'],
                    attack['effect'],
                    attack['damage']
                    )        
#            print(attackList)
            c.execute("SELECT monster_id FROM monsterAttack WHERE monster_id = ? AND attack_text = ?",
             (monsterId,attack['text']))
            data=c.fetchone()
            if data is None:
                c.execute('''INSERT INTO monsterAttack VALUES (?,?,?,?,?,?,?,?,?)''', attackList)
######################## Add Actions ###############################
    for actions in monsters['actions']:
        if 'name' in actions:
            if not 'action' in actions:
                actions['action']=None
            if not 'text' in actions:
                actions['text']=""
            if not 'Trigger' in actions:
                actions['Trigger']=None
            if not 'Frequency' in actions:
                actions['Frequency']=None
            if not 'Effect' in actions:
                actions['Effect']=None
            actionsList = (
                    None,
                    monsterId,
                    actions['name'],
                    actions['text'],
                    actions['action'],   
                    actions['Trigger'],
                    actions['Frequency'],
                    actions['Effect']
                    )        
#            print(attackList)
            c.execute("SELECT monster_id FROM monsterAction WHERE monster_id = ? AND action_name = ?",
             (monsterId,actions['name']))
            data=c.fetchone()
            if data is None:
                c.execute('''INSERT INTO monsterAction VALUES (?,?,?,?,?,?,?,?)''', actionsList)

######################## Add Passive  ###############################
    for passive in monsters['passive']:
        if 'name' in passive:
            if not 'text' in passive:
                passive['text']=""
            if not 'action' in passive:
                passive['action']=None
            passiveList = (
                    None,
                    monsterId,
                    passive['name'],
                    passive['text'],
                    passive['action']
                    )        
#            print(attackList)
            c.execute("SELECT monster_id FROM monsterPassive WHERE monster_id = ? AND passive_name = ?",
             (monsterId,passive['name']))
            data=c.fetchone()
            if data is None:
                c.execute('''INSERT INTO monsterPassive VALUES (?,?,?,?,?)''', passiveList)

######################## Add Spell  ###############################
    for spell in monsters['spells']:
        if 'name' in spell:
            if not 'text' in spell:
                spell['text']=""
            spellList = (
                    None,
                    monsterId,
                    spell['name'],
                    spell['text']
                    )        
#            print(attackList)
            c.execute("SELECT monster_id FROM monsterSpell WHERE monster_id = ? AND spell_name = ? AND spell_text = ?",
             (monsterId,spell['name'],spell['text']))
            data=c.fetchone()
            if data is None:
                c.execute('''INSERT INTO monsterSpell VALUES (?,?,?,?)''', spellList)

######################## Add Ritual  ###############################
    for ritual in monsters['rituals']:
        if 'name' in ritual:
            if not 'text' in ritual:
                ritual['text']=""
            ritualList = (
                    None,
                    monsterId,
                    ritual['name'],
                    ritual['text']
                    )        
#            print(attackList)
            c.execute("SELECT monster_id FROM monsterRitual WHERE monster_id = ? AND ritual_name = ? AND ritual_text = ?",
             (monsterId,ritual['name'],ritual['text']))
            data=c.fetchone()
            if data is None:
                c.execute('''INSERT INTO monsterRitual VALUES (?,?,?,?)''', ritualList)
#TODO: corrigir quando tiver 2 knowlodge
######################## Add Details  ###############################
    will = monsters["Will"]
    if(not ';' in monsters["Will"]):
        will +=";"
    detailsList = (monsterId,
                    monsters["AC"],
                    monsters["Fort"],
                    monsters["Ref"],
                    will,
                    monsters["HP"],
                    monsters["Perception"],
                    int(re.findall("\d+", monsters["Str"])[0]),
                    int(re.findall("\d+", monsters["Dex"])[0]),
                    int(re.findall("\d+", monsters["Con"])[0]),
                    int(re.findall("\d+", monsters["Int"])[0]),
                    int(re.findall("\d+", monsters["Wis"])[0]),
                    int(re.findall("\d+", monsters["Cha"])[0]),
                    ",".join(monsters["Languages"]),
                    monsters["Resistances"],
                    monsters["Immunities"],
                    monsters["Weaknesses"],
                    monsters["Hardness"],
                    monsters["Speed"],
                    monsters["images"],
                    monsters["source"],
                    monsters["recallKnowledge"],
                    monsters["text"],
                    "".join(monsters["Items"]),
                    "".join(monsters["skills"]),
                    monsters["alignment"],
                    len(monsters["actions"]),
                    len(monsters["passive"]),
                    len(monsters["spells"]),
                    len(monsters["rituals"]),
                    len(monsters["attacks"]))        
#    print(detailsList)
    c.execute("SELECT details_id FROM monsterDetails WHERE details_id = ?",
        (monsterId,))
    data=c.fetchone()
    if data is None:
        c.execute('''INSERT INTO monsterDetails VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', detailsList)

conn.commit()

conn.close()

json_data = json.dumps(monsterHolder, indent=4)
#details_pretty = json.dumps(monsters, sort_keys=True, indent=4, separators=(',', ': '))
#print(details_pretty)
filename = "monsters-v2-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close
