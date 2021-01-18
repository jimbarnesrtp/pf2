#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from bs4 import Tag
import requests
import json
import datetime
import codecs
import time
import re

###TODO: Some backgrounds, like "Undercover Lotus Guard", get conditional bonuses to skills without giving you training in them.  Right now those skills get put in 'skillsTrained', which is incorrect.  Find some way to consistently ignore those extra skills.
###TODO: Right now we don't keep italic or bold text markers.  Should we?  If not, we should let the "This tag wasn't captured" section know to ignore <i> tags.
 
backgroundHolder = {}
backgroundHolder['name'] = 'Pathfinder 2.0 background list'
backgroundHolder['date'] = datetime.date.today().strftime("%B %d, %Y")
validAbilities = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']#For when we look for a given background's ability boosts


backgroundLinks = {
        "Backgrounds.aspx": "General", 
        "Backgrounds.aspx?Legacy=true": "Legacy",
        "Backgrounds.aspx?Regional=true": "Regional",
        "Backgrounds.aspx?Group=1": "The Fall of Plaguestone",
        "Backgrounds.aspx?Group=2": "Age of Ashes",
        "Backgrounds.aspx?Group=3": "Extinction Curse",
        "Backgrounds.aspx?Group=4": "Pathfinder Society",
        "Backgrounds.aspx?Group=5": "Agents of Edgewatch"
    } 
 
 
def encoder(words):
    encoded = words.replace(u"\u2019", "'")
    encoded1 = encoded.replace(u"\u2014", "-")
    encoded2 = encoded1.replace(u"\u2011", " ")
    encoded3 = encoded2.replace(u'\u201c', "'")
    encoded4 = encoded3.replace(u'\u201d', "'")
    encoded5 = encoded4.replace(u'\u2026', "...")
    return encoded5


def get_detail_entry(backEntry):
    detail = {}#Package of a given background
    description = []
    abilityBoosts = []
    skillsTrained = []
    featsGained = []
    descSpecial = {}
    prerequisites = []
        
    if str(backEntry.get_text()).endswith("Background"):#Only grabs the entries with "Background" at the end, hopefully avoiding things we don't care about

        entryName = (str(backEntry.get_text()))[:-10]#removes "Background" from the end of the text we found
        detail['name'] = entryName
        
        detail['source'] = backEntry.find_next_sibling("a").get_text()
        
        #link and PFS handling
        if (backEntry.find('a').get('href')) == 'PFS.aspx':#some entries don't have PFS markers at all, making us navigate links differently
            detail['PFS'] = str(backEntry.find('a').span.img.get('alt'))
            if (backEntry.find('a').find_next_sibling('a').get('href').startswith("Backgrounds")):#If there's a PFS link, the thing after it is the background page link
                detail['link'] = str("https://2e.aonprd.com/" + backEntry.find('a').find_next_sibling('a').get('href'))
        elif (isinstance(backEntry.previous_sibling, Tag)) and (backEntry.previous_sibling.find_next('a', attrs={"href": "PFS.aspx"})):#Some of the initial broken entries need special treatment to get the PFS data
            detail['PFS'] = str(backEntry.previous_sibling.find_next('a', attrs={"href": "PFS.aspx"}).span.img.get('alt'))
            if (backEntry.find('a').get('href').startswith("Backgrounds")):#If there's no PFS link, this link should be the background link.
                detail['link'] = str("https://2e.aonprd.com/" + backEntry.find('a').get('href'))
        else:
            detail['PFS'] = "No PFS Data"
            if (backEntry.find('a').get('href').startswith("Backgrounds")):#If there's no PFS link, this link should be the background link.
                detail['link'] = str("https://2e.aonprd.com/" + backEntry.find('a').get('href'))

        #Set our pointer, skipping over whitetext and sup tags
        descPoint = backEntry.find_next_sibling("a").next_sibling
        if (descPoint.name is None) and (descPoint.strip() == ''):#skip over whitespace
            descPoint = descPoint.next_sibling
        while descPoint.name == 'sup':#Some things have sup tags, some don't.  We need to skip over said tags.
            descPoint = descPoint.next_sibling
        
        while descPoint != None and descPoint.name != "h2" and descPoint.name != "h3" and descPoint.next_sibling != None:
            if isinstance(descPoint, Tag):#Note that our `from bs4 import Tag` is necessary to check for the Tag type
                
                #Bold block
                if (descPoint.name == 'b'):#Ability boosts, Activates, and Prerequisites (including prereq Regions) are all in bold <b> tags
                    if (str(descPoint.text) == "Activate"):#Activate, like in the "Cursed" background
                        descSpecial['specType'] = str(encoder(descPoint.text))
                        descSpecial['specAction'] = str(encoder(descPoint.find_next_sibling('img').get('alt')))
                        descSpecial['specDescription'] = []
                        if descPoint.find_next_sibling('a').get('href').startswith("Traits"):
                            descSpecial['specTrait'] = descPoint.find_next_sibling('a').text
                        while descPoint != None and descPoint.name != "h2" and descPoint.name != "h3":
                            if descPoint.string != None:
                                if descSpecial['specDescription']:
                                    descSpecial['specDescription'][-1] = str(descSpecial['specDescription'][-1] + descPoint.string)
                                else:
                                    descSpecial['specDescription'].append(str(descPoint.string))
                            descPoint = descPoint.next_sibling
                        if descSpecial['specDescription']:
                            descSpecial['specDescription'][-1] = encoder(descSpecial['specDescription'][-1].rstrip())#rstrip gets rid or right-trailing whitespace
                            
                    elif (str(descPoint.text) in ("Prerequisites", "Region")):#Prerequisites, like in the "Hookclaw Digger" background, including Regional prerequisites
                        prerequisites.append(str(descPoint.text))
                        while (descPoint.next_sibling != None) and not ((descPoint.name == None) and (descPoint.next_sibling.name == None)):#We're checking if both the current point and the following point are tagless text.  If they are, then we've found a linebreak, and we want to break out of the loop.
                            descPoint = descPoint.next_sibling
                            if (descPoint.name == "a"):
                                prerequisites.append(str(descPoint.text))
                            else:
                                prerequisites.append(str(descPoint))
                        descPoint = descPoint.next_sibling
                        
                    elif (str(descPoint.text) in validAbilities):#Valid ability boosts
                        abilityBoosts.append(str(descPoint.text))
                        
                    else:
                        print ("We didn't handle this bold text: " + str(descPoint.text))
                
                #Underlined block
                elif descPoint.name == 'u':#Most skill and feat links are <u>nderlined
                    if descPoint.find('a').get('href').startswith("Skills"):
                        skillsTrained.append(str(descPoint.text))
                    elif descPoint.find('a').get('href').startswith("Feats"):
                        featsGained.append(str(descPoint.text))
                elif descPoint.name == 'a':#...Some are underlined with an <a> tag's style attribute
                    if descPoint.get('href').startswith("Skills"):
                        skillsTrained.append(str(descPoint.text))
                    elif descPoint.get('href').startswith("Feats"):
                        featsGained.append(str(descPoint.text))
                        
                elif descPoint.name == 'h1':#There are some regional categories that we can ignore, stored in h1 tags
                    pass
                        
                else:
                    print("This tag wasn't captured:" + str(descPoint))
                    
                #Description block
                if description:#if description already has elements
                    if (isinstance(descPoint, Tag)) and (descPoint.name != "h2"): 
                        description[-1] = str(description[-1] + encoder(descPoint.text))#We need to fuse the tag with both halves of the text block it's inside of
                    elif (descPoint.name != "h2"):
                        description[-1] = str(description[-1] + encoder(descPoint))
                else:#if description is empty, there's nothing on that side to fuse with.
                    if (isinstance(descPoint, Tag)) and (descPoint.name != "h2"):
                        description.append(str(encoder(descPoint.text)))
                    elif (descPoint.name != "h2"):
                        description.append(str(encoder(descPoint)))
                if not isinstance(descPoint.next_sibling, Tag):#This fuses the latter half of the text
                    description[-1] = str(description[-1] + encoder(descPoint.next_sibling))
                    descPoint = descPoint.next_sibling#Skip over the text we already handled
                    
            else:#if it's not a tag, we just append it to the description
                description.append(str(encoder(descPoint)))
                
            if descPoint.nextSibling != None and descPoint.name != "h2" and descPoint.name != "h3":
                descPoint = descPoint.next_sibling

        #Setting detail, so that we can return it all in one nice background package
        description[-1] = description[-1].rstrip()#gets rid of all the extra whitespace at the end of the description
        detail['prerequisites'] = ''.join(prerequisites)
        detail['description'] = ' '.join(description)
        detail['abilityBoosts'] = abilityBoosts
        detail['skillsTrained'] = skillsTrained
        detail['featsGained'] = featsGained
        detail['descSpecial'] = descSpecial
    #print (detail)
    return detail


def get_detail_list(eachEntry):
   
    detail_list = []#Package of everything from the page
    res = requests.get("https://2e.aonprd.com/" + eachEntry)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'lxml')

    for linebreak in soup.find_all('br'):
        linebreak.extract()
    main = soup.find("div", {'id': 'main'})
    
    backEntries = main.find_all("h2")#pulls out each h2 section into items in a list
    
    ###This next block is for handling the source's broken HTML tags.  If the source is ever fixed, this should be commented out.

    if backgroundLinks[eachEntry] in ['General', 'Legacy', 'Regional', 'Pathfinder Society', 'Agents of Edgewatch']:#These pages have their first background entries broken, so we wrap it up in an h2 tag.
        wrapper = soup.new_tag('h2')
        backEntries[1] = backEntries[1].parent.next_sibling.wrap(wrapper)
        backEntries[1].string.replace_with(str(backEntries[1].string + "Background"))
        #print ("Wrapped: " + str(backEntries[1]))
    
    ###
    
    del backEntries[0]#We don't need the first entry, because it's not a background entry.
    
    for backEntry in backEntries:#for each h2 section in our list
        detail_list.append(get_detail_entry(backEntry))

    return detail_list
 



for eachEntry in backgroundLinks:
    backgroundHolder[backgroundLinks[eachEntry]] = get_detail_list(eachEntry)#Tags each page with its name ("General", "Regional", etc.)


json_data = json.dumps(backgroundHolder, indent=4)
# print(json_data)
filename = "backgrounds_aon-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close
