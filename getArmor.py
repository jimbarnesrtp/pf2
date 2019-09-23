from bs4 import BeautifulSoup
import requests
import buildDetailsHR as hrDets
import json
import datetime
import codecs


armorHolder = {}
armorHolder['name'] = 'Pathfinder 2.0 armor list'
armorHolder['date'] = datetime.date.today().strftime("%B %d, %Y")

def get_base_magic(link):
    items = []
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    item = soup2.find_all("div", {'class':'main'})
    table = soup2.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_TreasureElement")
    rows = table.findAll(lambda tag: tag.name=='tr')
    for row in rows:
        #print(row)
        #print("-----------------------------------")
        item = {}
        entries = row.find_all(lambda tag: tag.name=='td')
        if entries is not None:
            if len(entries) > 0:
                item['name'] = entries[0].find("a").text
                item['link'] = "https://2e.aonprd.com/"+entries[0].find("a")['href']
                item['category'] = "Magic Armor"
                item['level'] = entries[1].text
                item['price'] = entries[2].text
                items.append(item)
    
    itemDetails = []
    traits = []
    detailHolder = []
    if len(items) > 0:
        res = requests.get(items[0]['link'])
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'lxml')
        main = soup.find("span", {'id':'ctl00_MainContent_DetailedOutput'})
        children = main.contents
        reachedBreak = False
        
        traitsHolder = main.find_all("span", {'class':'trait'})
        
        for trait in traitsHolder:
            traits.append(trait.text)
        
        reachedBreak = False
        reachedItem = False
        itemDetail = {}
        itemDetailHolder = []
        notFirstH2 = False
        for child in children:
            
            stringContents = str(child)
            if stringContents.startswith("<"):

                if stringContents == "<hr/>":
                    reachedBreak = True
                if stringContents.startswith("<h2"):
                    if(notFirstH2):
                        
                        itemDetail['itemDetails'] = itemDetailHolder
                        itemDetails.append(itemDetail)
                        itemDetail = {}
                        itemDetailHolder = []
                    else:
                        notFirstH2 = True
                    
                    reachedBreak = False
                    reachedItem = True
                    name = child.text
                    start = child.text.find("Item")
                    itemDetail['name'] = child.text[0:start]
            else:
                if reachedBreak:
                    detailHolder.append(stringContents)
                if reachedItem:
                    itemDetailHolder.append(stringContents)
        itemDetail['itemDetails'] = itemDetailHolder
        itemDetails.append(itemDetail)

    for item in items:
        for itemDetail in itemDetails:

            try:
                if itemDetail['name'] == item['name']:

                    item['traits'] = traits
                    item['about'] = detailHolder
                    item['details'] = itemDetail
            except:
                print("itemDetail:" , itemDetail)
    
    return items


def get_armor(link):
    items = []
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    item = soup2.find_all("div", {'class':'main'})
    main = soup2.find("span", {'id':'ctl00_MainContent_DetailedOutput'})
    #print(detail.contents)
    table = soup2.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_TreasureElement")
    j = 0
    rows = table.findAll(lambda tag: tag.name=='tr')
    for row in rows:
        j += 1
        item = {}
        entries = row.find_all(lambda tag: tag.name=='td')
        if entries is not None:
            if len(entries) > 0:
                item['name'] = entries[0].find("a").text
                item['link'] = "https://2e.aonprd.com/"+entries[0].find("a")['href']
                item['category'] = "Armor"
                item['armorCategory'] = entries[1].text
                item['level'] = entries[2].text.replace(u'\u2014', '')
                item['price'] = entries[3].text.replace(u'\u2014', '')
                item['acBonus'] = entries[4].text
                item['dexCap'] = entries[5].text.replace(u'\u2014', '')
                item['checkPenalty'] = entries[6].text.replace(u'\u2014', '')
                item['speedPenalty'] = entries[7].text.replace(u'\u2014', '')
                item['str'] = entries[8].text.replace(u'\u2014', '')
                item['bulk'] = entries[9].text.replace(u'\u2014', '')
                item['group'] = entries[10].text.replace(u'\u2014', '')
                item['traits'] = entries[11].text.replace(u'\u2014', '')

                item['text'] = hrDets.get_afterhr(item['link'])

                items.append(item)
        #if j > 5:
            #break
    return items

def get_precious():
    items = []
    listOfPages = codecs.open("preciousArmor.csv", encoding='utf-8')
    for line in listOfPages: 
        armorMD = line.split(",")
        print("Getting precious armor for :", armorMD[0],"This url:", armorMD[1])

        res2 = requests.get(armorMD[1].strip('\n'))
        res2.raise_for_status()
        soup2 = BeautifulSoup(res2.text, 'lxml')
        main = soup2.find("span", {'id':'ctl00_MainContent_DetailedOutput'})
        children = main.contents
        reachedBreak = False
        reachedItem = False
        detailHolder = []
        notFirstH2 = False
        item = {}
        for child in children:
            
            stringContents = str(child)
            if stringContents.startswith("<"):

                if child.name == "hr":
                    tagType = ""
                    reachedBreak = True
                if child.name == "h2":
                    if notFirstH2: 
                        item['text'] = detailHolder
                        items.append(item)
                        item = {}
                    else:
                        notFirstH2 = True
                    
                    reachedBreak = False
                    reachedItem = True
                    name = child.text
                    start = child.text.find("Item")
                    item['name'] = child.text[0:start]
                if child.name == "b":
                    if(child.text != "Source"):
                        tagType = child.text
            else:
                if reachedBreak:
                    detailHolder.append(stringContents)
                if reachedItem:
                    if tagType != "":
                        item[tagType] = stringContents
        item['text'] = detailHolder
        items.append(item)

    return items

def get_magic_armor(link):
    items = []
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    item = soup2.find_all("div", {'class':'main'})
    table = soup2.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_TreasureElement")
    rows = table.findAll(lambda tag: tag.name=='tr')
    for row in rows:
        #print(row)
        #print("-----------------------------------")
        item = {}
        entries = row.find_all(lambda tag: tag.name=='td')
        if entries is not None:
            if len(entries) > 0:
                item['name'] = entries[0].find("a").text
                item['link'] = "https://2e.aonprd.com/"+entries[0].find("a")['href']
                item['category'] = "Magic Armor"
                item['level'] = entries[1].text
                item['price'] = entries[2].text
                item['bulk'] = entries[3].text.replace(u'\u2014', '')

                itemDetails = get_armor_details(item['link'])

                for key in itemDetails.keys():
                    item[key] = itemDetails[key]

                items.append(item)
    return items

def get_armor_details(link):
    itemDetails = {}
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    detail2 = soup2.find(lambda tag: tag.name=='span' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_DetailedOutput") 
    traits = detail2.find_all("span", {"class" : lambda L: L and L.startswith('trai')})
    traitHolder = []
    for trait in traits:
        traitHolder.append(trait.text)
    itemDetails['traits'] = traitHolder

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

                    if child2['class'][0] == "external-link" :
                        
                        itemDetails['source'] = child2.text
                    tagType = ""
                if child2.name == "b":

                    if(child2.text != "Source"):
                        tagType = child2.text
            else:
                if not stringContents.isspace() :
                    detailHolder.append(child2.text)        
        else:
            if reachedBreak:
                if not stringContents.isspace() :
                    detailHolder.append(stringContents)
            else:
                if tagType != "":
                    if (tagType != "Bulk") & (tagType!= "Price"):
                        if not stringContents.isspace():
                            itemDetails[tagType] = stringContents
       #print(child)
       
    itemDetails['text'] = detailHolder

    return itemDetails

def get_all():
    armorHolder['baseArmor'] = get_armor("https://2e.aonprd.com/Armor.aspx")
    armorHolder['baseMagicArmor'] = get_base_magic("https://2e.aonprd.com/Equipment.aspx?Category=11&Subcategory=13")
    armorHolder['preciousMaterialArmor'] = get_precious()
    armorHolder['magicArmor'] = get_magic_armor("https://2e.aonprd.com/Equipment.aspx?Category=11&Subcategory=14")
    return armorHolder

#print(get_all())
json_data = json.dumps(get_all())
#print(json_data)
filename = "armor-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close