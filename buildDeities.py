from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import time

deityHolder = {}
deityHolder['name'] = 'Pathfinder 2.0 deities list'
deityHolder['date'] = datetime.date.today().strftime("%B %d, %Y")

def encoder(words):
    encoded = words.replace(u"\u2019", "'")
    encoded1 = encoded.replace(u"\u2014", "-")
    encoded2 = encoded1.replace(u"\u2011", " ")
    encoded3 = encoded2.replace(u'\u201c', "'")
    encoded4 = encoded3.replace(u'\u201d', "'")
    encoded5 = encoded4.replace(u'\u2026', "...")
    encoded6 = encoded5.replace(u'\u2013', "-")
    encoded7 = encoded6.replace(u'\u2018', "'")
    encoded8 = encoded7.replace(u'\ufb01', "fi")
    encoded9 = encoded8.replace(u'\ufb02', "fl")
    encoded10 = encoded9.replace(u'\u00d7', "x")
    return encoded10

def get_details(link):
    itemDetails = {}
    res = requests.get(link)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'lxml')
    feat = soup.find_all("div", {'class':'main'})
    detail = soup.find("span", {'id':'ctl00_MainContent_DetailedOutput'})
    children = detail.contents
    skipTitle = False
    if children[0].find("a").get('href') == "PFS.aspx":#Only some entries have PFS tags, and if they do then the HTML of the source is broken.  So we break out of it, and then do handling for any issues this causes later.
        children = detail.next_sibling.parent.contents
        skipTitle = True
    reachedBreak = False
    reachedCrit = False
    reachedIntercession = False
    detailHolder = []
    tagType = ""
    string = " "
    divAbility = []
    spellHolder = []
    divinterDesc = ""
    domainHolder = []
    altDomains = []
    alreadyHandled = ["Follower Alignments", "Favored Weapon", "Divine Font"]
    for child in children:
        #print (str(child))
        stringContents = str(child)
        if stringContents.startswith("<"):

            if child.name == "a":
                try:
                    if child['class'][0] == "external-link":
                        if reachedIntercession == False:
                            itemDetails['source'] = encoder(str(child.text))
                        else:
                            itemDetails['divinterSource'] = encoder(str(child.text))
                        tagType = ""
                except:
                    pass
            if child.name == "b":
                tagType = encoder(str(child.text))
            if ((child.name == "i") or ((child.name == "a") and ((child.get("style") == "text-decoration:underline") or (child.find('u'))))) and (tagType not in alreadyHandled):
                if tagType == "Cleric Spells":
                    spellHolder.append(encoder(child.text))
                elif tagType == "Domains":
                    domainHolder.append(encoder(child.string))
                elif tagType == "Alternate Domains":
                    altDomains.append(encoder(child.string))
                else:
                    if itemDetails.get(tagType):#If this tag already has something, we fuse the text with the existing something instead of setting it
                        if child.find("i"):
                            itemDetails[tagType] = (str(itemDetails[tagType]) + "*" + encoder(str(child.string)) + "*")#Markdown seems like a good way to handle *italcs*.
                        else:#In this case it's probably a link tag, which we just want the plain text of.
                            itemDetails[tagType] = (str(itemDetails[tagType]) + encoder(str(child.string)))
                    elif tagType == "":#If we haven't yet hit a tag, then we assume we're in the main text block, and append it to detailHolder.
                        if child.name == "i":
                            detailHolder.append("*" + encoder(str(child.string)) + "*")
                        else:
                            detailHolder.append(encoder(str(child.string)))
                    else:
                        itemDetails[tagType] = encoder(str(child.string))
            if (child.name == "h2") and (child.text == "Divine Intercession"):
                reachedIntercession = True
        else:

            if tagType != "":
                if (tagType not in alreadyHandled):
                    if not stringContents.isspace():
                        if (tagType == "Divine Ability"):
                            divAbility.append(encoder(stringContents).strip().split(' or '))
                        elif (tagType == "Cleric Spells"):
                            if (child.next_sibling.name != None) and (child.next_sibling.name == 'i'): #Only grabs spells until the next thing isn't in italics (we expect spells to be italicized) 
                                spellHolder.append(encoder(stringContents))
                            elif reachedIntercession == True:
                                divinterDesc = divinterDesc + encoder(str(child.string))
                            elif reachedIntercession == False:#If we're still in the main block, there must be some condition on the spell gained, like Apsu's "(metallic dragons only)"
                                spellHolder[-1] = str(spellHolder[-1] + encoder(str(child.string)))#...So we fuse it to the most recent spell entry.
                            else:
                                print ("Unhandled text: " + str(child))
                        elif tagType in ("Domains", "Alternate Domains"):#We don't want this text, as it's just commas.
                            pass
                        else:
                            if itemDetails.get(tagType):
                                itemDetails[tagType] = (str(itemDetails[tagType]) + encoder(str(child.string)))
                            else:
                                itemDetails[tagType] = encoder(str(child.string))
            else:
                if not stringContents.isspace():
                    if (not detailHolder) and (skipTitle == True):#If there's nothing already in detailHolder, then we might need to skip the deity's title.
                        detailHolder.append(" ")
                    elif reachedIntercession == False:
                        detailHolder.append(encoder(stringContents))

       #print(child)
       #print('<!!!!!!!!!!!!!!!!!!!!!!!!!>')
    spellHolder = [spellEntry.strip(",:").strip() for spellEntry in spellHolder]#strips ,: and whitespace from the spellHolder
    spellIter = iter(spellHolder)
    spellDict = dict(zip(spellIter, spellIter))#Dict-ifies the spells, output formatted like: {'1st': 'sleep', '4th': 'fly"}
    for itemEntry in itemDetails:
        itemDetails[itemEntry] = itemDetails[itemEntry].strip(",:").strip()
    itemDetails['domains'] = domainHolder
    itemDetails['altDomains'] = altDomains
    itemDetails['clericSpells'] = spellDict
    itemDetails['text'] = "".join(detailHolder).strip(', ').strip()
    itemDetails['divinterDesc'] = divinterDesc.strip()
    itemDetails['divAbility'] = divAbility
    return itemDetails



def get_entry(link):
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
                if (entries[0].find("a").get('href') == "PFS.aspx"):#Not all entries have PFS tags, so we have to handle them seperately
                    name = entries[0].find("a").find_next("a").text
                    link = "https://2e.aonprd.com/" + entries[0].find("a").find_next("a").get('href')
                    pfsLegal = entries[0].find("a").img.get('alt')
                else:
                    name = entries[0].find("a").text
                    link = "https://2e.aonprd.com/" + entries[0].find("a").get('href')
                    pfsLegal = 'No PFS Data'
                item['name'] = name
                item['link'] = link
                item['PFS'] = pfsLegal
                item['category'] = entries[1].text.strip()
                item['alignment'] = entries[2].text.split(",")
                item['followerAlignments'] = entries[3].text.replace(u'\u2014', '').split(", ")
                item['font'] = entries[4].text.split("/")
                #item['domains'] = entries[5].text.split(", ")#Commented out because we handle this in get_details.
                item['weapon'] = entries[6].text.split(" or ")

                print("getting details for:",item['name'])
                itemDetails = get_details(item['link'])

                for key in itemDetails.keys():
                    item[key] = itemDetails[key]

                items.append(item)
        #if t > 5:
            #break
            
    #Handle Faiths seperately from Deities:
    table2 = soup2.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_FaithElement")
    rows2 = table2.findAll(lambda tag: tag.name=='tr')
    t = 0
    for row in rows2:
        t += 1
        #print(row)
        #print("-----------------------------------")
        item = {}
        entries = row.find_all(lambda tag: tag.name=='td')
        if entries is not None:
            if len(entries) > 0:
                if (entries[0].find("a").get('href') == "PFS.aspx"):#Not all entries have PFS tags, so we have to handle them seperately
                    name = entries[0].find("a").find_next("a").text
                    link = "https://2e.aonprd.com/" + entries[0].find("a").find_next("a").get('href')
                    pfsLegal = entries[0].find("a").img.get('alt')
                else:
                    name = entries[0].find("a").text
                    link = "https://2e.aonprd.com/" + entries[0].find("a").get('href')
                    pfsLegal = 'No PFS Data'
                item['name'] = name
                item['link'] = link
                item['PFS'] = pfsLegal
                item['category'] = "Faiths and Philosophies"
                item['followerAlignments'] = entries[1].text.replace(u'\u2014', '').split(", ")
                #item['domains'] = entries[5].text.split(", ")#Commented out because we handle this in get_details.

                print("getting details for:",item['name'])
                itemDetails = get_details(item['link'])

                for key in itemDetails.keys():
                    item[key] = itemDetails[key]

                items.append(item)
            
            
    return items




def get_all():
    deityHolder['deities'] = get_entry("https://2e.aonprd.com/Deities.aspx")

    #deityHolder['rangedWeapons'] = get

    
    return deityHolder

#print(get_all())
json_data = json.dumps(get_all(), indent=4)
#print(json_data)
filename = "deities-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close
