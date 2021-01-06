#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import time
import re
 
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
    encoded1 = encoded.replace(u"\u2014", "-")
    encoded2 = encoded1.replace(u"\u2011", " ")
    encoded3 = encoded2.replace(u'\u201c', "'")
    encoded4 = encoded3.replace(u'\u201d', "'")
    return encoded4


def cleanSplit(rawPoint):#This is intended to collect a group of data from a pointer, clean up that data (especially by stripping links), and then pass it back.
    cleanList = []
    while rawPoint != None and rawPoint.name != "h2" and rawPoint.name != "h3":#keeps going until it hits another h tag, or the end of the document
        
        if rawPoint != None and (str(rawPoint) != ", ") and (str(rawPoint.name) != "a"):#skips comma lines
            cleanList.append(encoder(str(rawPoint)))
            rawPoint = rawPoint.next_sibling
        
        while rawPoint != None and str(rawPoint.name) == "a":#extracts text from links
            
            if cleanList:#if there's already a list, we fuse normally
                if str(rawPoint.next_sibling.name) == "a":#if the next thing is a link too, we need to not fuse - it's hopefully useful as a list of items, like languages
                    cleanList.append(rawPoint.text)
                    cleanList.append(rawPoint.next_sibling.text)
                    rawPoint = rawPoint.next_sibling
                elif str(rawPoint.previous_sibling.name) == "a":
                    cleanList.append(rawPoint.text)
                    cleanList.append(rawPoint.next_sibling)#only triggers if the next thing is not a link, but the previous and current are
                    rawPoint = rawPoint.next_sibling
                    
                else:#if neither the next nor the previous thing is a link, we fuse the items
                    cleanList[-1] = encoder(str(cleanList[-1] + rawPoint.text)) # Here we fuse the link's text with both the previous string and the following string.
                    cleanList[-1] = encoder(str(cleanList[-1] + rawPoint.next_sibling))
                    rawPoint = rawPoint.next_sibling
                    
            else:#if there's not already a list, we can't fuse with the last item
                if str(rawPoint.next_sibling.name) == "a":
                    cleanList.append(rawPoint.text)
                    cleanList.append(rawPoint.next_sibling.text)
                    rawPoint = rawPoint.next_sibling
                else:#if the next thing isn't a link, we fuse the item only with the next item
                    cleanList.append(encoder(str(rawPoint.text)))
                    cleanList[-1] = encoder(str(cleanList[-1] + rawPoint.next_sibling))
                    rawPoint = rawPoint.next_sibling
            rawPoint = rawPoint.next_sibling# We already fused with the following string, so we need to skip it for the next iteration of the loop.
            
    cleanList = [cleanItem.strip() for cleanItem in cleanList]#strips whitespace
    return cleanList

 
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
        if (child.find('a').get('href')) == 'PFS.aspx': # check if the thing we're skipping over is a PFS link
            #print (child.find('a').next_sibling.get('href'))
            ancestryLink = child.find('a').next_sibling.get('href') # if it is PFS link, we skip it with next_sibling
            ancestryLinks.append(ancestryLink)
        else:
            #print (child.find('a').get('href'))
            ancestryLink = child.find('a').get('href') # if it's not a PFS link, then we assume it's the link we're looking for
            ancestryLinks.append(ancestryLink)
        #print (ancestryLinks)
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
       

        
        textHolder = []
        textRaw = soup.find("meta", {'name':'description'})['content'] #First we grab the content from the meta tag
        textSplit = re.split('<(.*?)>', textRaw) #Now we split it into groups of strings seperated by < >, to pull out any links
        textClean = (''.join(textSplit[::2])).strip() #Finally, we join every other group together (passing over the link groups) into one string, and strip it of whitespace
        #print (encoder(textClean))
        textHolder.append(encoder(textClean))   
        
        description = []
        descRaw = main.find_all("i")#Finds the i tags, the first of which should have what we want in descRaw[1]
        descSplit = re.split('<(.*?)>', ''.join(descRaw[1])) #Now we split it into groups of strings seperated by < >, to pull out any links.
        descClean = ''.join(descSplit[::2]) #Finally, we join every other group together (passing over the link groups) into one string
        description.append(encoder(descClean))
        
        detail['name'] = name
        
        detail['source'] = encoder(soup.find("a", {'class':'external-link'}).text)#The source should be the text of the first 'a' tag with the "class='external-link" attribute
        
        detail['traits'] = traitHolder
        detail['description'] = description
        detail['text'] = " ".join(textHolder)

        physPoint = soup.find("h2", string='Physical Description').next_sibling
        detail['physical'] = cleanSplit(physPoint)#cleanSplit cleans up the list
        
        socPoint = soup.find("h2", string='Society').next_sibling
        detail['society'] = cleanSplit(socPoint)

        alignPoint = soup.find("h2", string='Alignment and Religion').next_sibling
        detail['alignment'] = cleanSplit(alignPoint)
        
        namesTypePoint = soup.find("h2", string='Names').next_sibling
        detail['namesType'] = cleanSplit(namesTypePoint)
        
        detail['abilityBoosts'] = titleContent(soup.find("h2", string='Ability Boosts'))
        if (soup.find("h2", string='Ability Flaw(s)')):#not all ancestries have flaws
            detail['abilityFlaws'] = titleContent(soup.find("h2", string='Ability Flaw(s)'))        
        detail['hp'] = str(soup.find("h2", string='Hit Points').next_sibling)
        detail['size'] = str(soup.find("h2", string='Size').next_sibling)
        detail['speed'] = str(soup.find("h2", string='Speed').next_sibling)
        
        langPoint = soup.find("h2", string='Languages').next_sibling
        detail['languages'] = cleanSplit(langPoint)
                
        nameList = []
        nameList = (encoder(str(soup.find("h3", string='Sample Names').next_sibling))).split(', ')#We split it in case anyone wants to draw out a single sample name
        nameList = [nameItem.strip() for nameItem in nameList]#strips whitespace from each entry
        detail['nameList'] = nameList 
        
        mightList = []
        mightRaw = soup.find("h2", string='You Might...').next_sibling
        for mightItem in mightRaw.find_all("li"):
            mightList.append(encoder(encoder(mightItem.text)))
        detail['might'] = mightList
        
        probablyList = []
        probablyRaw = soup.find("h2", string='Others Probably...').next_sibling
        for probablyItem in probablyRaw.find_all("li"):
            probablyList.append(encoder(encoder(probablyItem.text)))
        detail['probably'] = probablyList

        detail['pfsLegal'] = pfsLegal


        details.append(detail)
    return details
 
 
ancestryHolder['Ancestries'] = get_details()

json_data = json.dumps(ancestryHolder, indent=4)
# print(json_data)
filename = "ancestry-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close
