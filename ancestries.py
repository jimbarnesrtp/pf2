#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import time
 
ancestryHolder = {}
ancestryHolder['name'] = 'Pathfinder 2.0 Ancestry feat list'
ancestryHolder['date'] = datetime.date.today().strftime("%B %d, %Y")
 
 
def titleContent(child):
    societyHolder = []
   
    #del societyHolder[:]
    nextChild = child.next_sibling
    k = 0
    while nextChild.name != "h2" and nextChild.name != "h3" :
        #print("stringa", k, nextChild.encode('utf-8'))
        # cicle <i> (italic) and a href (link) next upgrade change markup for these
        if nextChild.name == "i" or nextChild.name == "a":
            #print("e' una i", child)
            #print(societyHolder)
            del societyHolder[k-1]  # delete previous item
            # take tag and "cut and paste" between previous and next item
            sumChild = (encoder(nextChild.previous_sibling) +
                        encoder(nextChild.text) + encoder(nextChild.next_sibling))
            societyHolder.append(sumChild)
            jumpChild = nextChild.next_sibling
            nextChild = jumpChild.next_sibling
        else:
            #print(encoder(nextChild))          
            societyHolder.append(encoder(nextChild))
            #print(societyHolder)
            nextChild = nextChild.next_sibling
            k += 1
 
    return societyHolder
 
 
 
def encoder(words):
    encoded = words.replace(u"\u2019", "'")
    encoded1 = encoded.replace(u"\u2014", " ")
    encoded2 = encoded1.replace(u"\u2011", " ")
    encoded3 = encoded2.replace(u'\u201c', "'")
    encoded4 = encoded3.replace(u'\u201d', "'")
    return encoded4
 
def get_ancestryLink():
    ancestryLinks = []
    res = requests.get("https://2e.aonprd.com/Ancestries.aspx")
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'lxml')
    # elementi all'interno del DOM
    ancestries = soup.find_all("h2", {'class': 'title'})
    #entries = ancestries.contents
    # print "tutto:", ancestries
    for child in ancestries:
        time.sleep(0.3)
        ancestryLink = child.find('a').next_sibling.get('href')
        ancestryLinks.append(ancestryLink)
        #print ancestryLinks
    return ancestryLinks
 
 
def get_details():
   
    details = []
    # print "tutti i links", get_ancestryLink()
    for eachEntry in get_ancestryLink():
        detail = {}
        #print "ogni entry", eachEntry
        res = requests.get("https://2e.aonprd.com/" + eachEntry)        
        #res = requests.get("C:/Users/lillo/Downloads/Dwarf.html")
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'lxml')
        #print(soup)
        # soup.br.decompose()
        for linebreak in soup.find_all('br'):
            linebreak.extract()        
        soup.encoding = "utf-8"
        main = soup.find("div", {'id': 'main'})
        #print (main)      
        pfsLegal = main.find("img", {'title': 'PFS Standard'})
        if(pfsLegal):
            pfsLegal = True
        else:
            pfsLegal = False
        for finder in main.find_all("a", {'href': eachEntry}): # temporary for error into html source
            name = finder.text
        #name = main.find("a", {'href': eachEntry}).text
 
        print('Start with: ', name)
 
        traitsarray = main.find_all(
            "span", {"class": lambda L: L and L.startswith('trai')})
        traitHolder = []
        for trait in traitsarray:
            traitHolder.append(trait.text)
       
        description = []
        #source = main.find("a", {'class':'title'}).text
        children = main.contents
       
        detailHolder = []
       
 
        for child in children:
 
            stringContents = child.encode('utf-8')
            #print('stringato: ', stringContents)
            if stringContents.startswith("<"):                
                if child.name == "a":
                    #print("href", child)
                    try:
                        if child['class'][0] == "external-link":
                            #print("source", child.text)
                            detail['source'] = child.text
                    except:
                        pass
                   
                if child.name == "b":
                    if child.text != "Source":
                        tagType = child.text.lower()
 
                if child.name == "a":
                    #print("href", child)
                    try:
                        if child['class'][0] == "external-link":
                            nextchild = child.next_sibling
                            if nextchild.name == "i":
                                child = nextchild
                                description.append(encoder(child.text))                              
                                description.extend(titleContent(child))
                    except:
                        pass    
 
                if child.name == "h2":
                    if child.text == "You Might...":
                        ul = child.next_sibling
                        liList = []
                        for li in ul.findAll('li'):
                            liList.append(encoder(encoder(li.text)))
                        detail['might'] = liList
 
                if child.name == "h2":
                    if child.text == "Others Probably...":
                        ul = child.next_sibling
                        liList = []
                        for li in ul.findAll('li'):
                            liList.append(encoder(encoder(li.text)))
                        detail['probably'] = liList
 
                if child.name == "h2":
                    if child.text == "Physical Description":
 
                        detail['physical'] = titleContent(child)
 
                if child.name == "h2":
                    if child.text == "Society":
 
                        detail['society'] = titleContent(child)
 
                if child.name == "h2":
                    if child.text == "Alignment and Religion":
 
                        detail['alignment'] = titleContent(child)
 
                if child.name == "h2":
 
                    if child.text == "Names":
 
                        detail['namesType'] = titleContent(child)
 
                if child.name == "h3":
 
                    if child.text == "Sample Names":
                        nameList = []
                        words = child.next_sibling.split(', ')
                        # for each word in the line:
                        for word in words:
                            nameList.append(encoder(word))
                            # print the word
                        detail['nameList'] = nameList
                if child.name == "h2":
                    if child.text == "Hit Points":
                        detail['hp'] = child.next_sibling
               
                if child.name == "h2":
                    if child.text == "Size":
                        detail['size'] = child.next_sibling
                if child.name == "h2":
                    if child.text == "Speed":
                        detail['speed'] = child.next_sibling
                if child.name == "h2":
                    if child.text == "Ability Boosts":
                        detail['abilityBoosts'] = titleContent(child)
                if child.name == "h2":
                    if child.text == "Ability Flaw(s)":
                        detail['abilityFlaws'] = titleContent(child)
                if child.name == "h2":
                    if child.text == "Languages":
                        #detail['languages'] = titleContent(child)
                        languagesHolder = []
                        #languagesOptHolder = []
                        nextChild = child.next_sibling
                        while nextChild.name != "h2" and nextChild.name != "h3" and nextChild != None:                          
                            if nextChild.name == "a" :
                                languagesHolder.append(encoder(nextChild.text))
                                nextChild = nextChild.next_sibling
                            else:                                
                                languagesHolder.append(encoder(nextChild))
                                #languagesOptHolder.append(encoder(nextChild).split(', '))
                                break                                
                               
                        detail['languages'] = languagesHolder
                        #detail['languagesOpt'] = languagesOptHolder
                if child.name == "h2":
                    if child.text == "Languages":
                        t=0                        
                        while child.find_next("h2"):
                            otherHolder = []
                            titolo = child.find_next("h2")
                            t+= 1
                            if titolo.name == "h2":                                
                                #print(t, "eccolo", titolo.text)
                                otherHolder.append(titolo.text)
                                otherHolder.append(titolo.next_sibling)                            
                               
                                detail['other'+str(t)] = otherHolder
                                child = child.find_next("h2")
 
                else:
                    if not stringContents.isspace():
                        detailHolder.append(encoder(child.text))
           
        detail['pfsLegal'] = pfsLegal
        detail['name'] = name
        detail['traits'] = traitHolder
        detail['description'] = description
        string = " "
        detail['text'] = string.join(detailHolder)
        details.append(detail)
    return details
 
 
ancestryHolder['Ancestries'] = get_details()
 
json_data = json.dumps(ancestryHolder, indent=4)
# print(json_data)
filename = "ancestry-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close