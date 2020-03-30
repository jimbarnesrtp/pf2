#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import time

heritageHolder = {}
heritageHolder['name'] = 'Pathfinder 2.0 Heritages list'
heritageHolder['date'] = datetime.date.today().strftime("%B %d, %Y")


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
    encoded1 = encoded.replace(u"\u2013", "-")
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
    #print (ancestryLinks)
    return ancestryLinks

def get_heritageLink():
    heritageLinks = []
    for eachEntry in get_ancestryLink():        
        res = requests.get("https://2e.aonprd.com/" + eachEntry)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'lxml')
        for linebreak in soup.find_all('br'):
            linebreak.extract()        
        soup.encoding = "utf-8"
        subNav = soup.find("span", {'id': 'ctl00_MainContent_SubNavigation'})
        try:
            heritageLink = subNav.find_all("a")
            #print (heritageLink)
            #heritageLink = heritageLink.get('href')
            heritageLinks.append(heritageLink[2])
            #heritageLinks.append(heritageLink[2].get('href'))      
            #print (heritageLink[2].text.replace(' Heritages', ''))
            #print (heritageLink[2].get('href'))
            #nameAncestry = heritageLinks.text.replace(' Heritages', '')            
        except:
            pass
    #print ("Heritage links: ", heritageLinks)
    return heritageLinks

""" def get_nameAncestries():
    for eachEntry in get_heritageLink():
        #print (eachEntry.text.replace(' Heritages', ''))
        #print (eachEntry.get('href'))
        nameAncestry = eachEntry.text.replace(' Heritages', '')
    return nameAncestry """


def get_details():
    #herit = {}
    #print (get_herytageLink())
    details = []
    # print "tutti i links", get_ancestryLink()
    for eachEntry in get_heritageLink():
        
        #print (eachEntry.text.replace(' Heritages', ''))
        #print (eachEntry.get('href'))
        nameAncestry = eachEntry.text.replace(' Heritages', '')
        linkAncestry = eachEntry.get('href')
              
        res = requests.get("https://2e.aonprd.com/" + linkAncestry)        
       
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'lxml')
       
        for linebreak in soup.find_all('br'):
            linebreak.extract()
        for linebreak2 in soup.find_all('hr'):
            linebreak2.extract()

        soup.encoding = "utf-8"
        main = soup.find("div", {'id': 'main'})
        print('start with: ', nameAncestry)
        #H1 Problem on HTML page IF and ELSE take element
        for finder in main.find_all("a", {'href': lambda L: L and L.startswith('Heritages.aspx')}):
                      
            detail = {} 
            if not finder.text.endswith('eritages'):
                
                #print(finder.previous_sibling)
                prevElement = finder.previous_sibling
                #print (prevElement.contents)
                pfsLegal = prevElement.find("img", {'title': 'PFS Standard'})
                if(pfsLegal):
                    pfsLegal = True
                else:
                    pfsLegal = False
                
                """ if finder.previous_sibling:
                    print(finder.previous_sibling) """
                #print (finder)
                name = finder.text            
                detail['heritageName'] = name
                th1 = finder.next_sibling
                if th1 is not None:
                    #print('th1', th1)
                    th2 = th1.next_sibling
                    sourceHref = th2.next_sibling
                    #print (sourceHref.text)
                    detail['source'] = sourceHref.text
                    detail['sourceLink'] = sourceHref.get('href')

                else:
                    th1 = finder.parent.next_sibling
                    th2 = th1.next_sibling
                    sourceHref = th2.next_sibling
                    #print (sourceHref)
                    detail['source'] = sourceHref.text
                    detail['sourceLink'] = sourceHref.get('href')

                #print (encoder(sourceHref.next_sibling))
                description = sourceHref.next_sibling
                detail['desc'] = encoder(description)
                ah1 = description.next_sibling
                #print (ah1)
                if ah1 is not None:
                    if ah1.name == 'h3':
                        detailAbility = {} 
                        #print(ah1.text)
                        detailAbility['abilityName'] = ah1.text
                        
                        #print(ah1.child)
                        #print(ah1.find("img").get('alt'))
                        detailAbility['abilityActions'] = ah1.find("img").get('alt')
                        traitsFinder = ah1.next_sibling
                        if traitsFinder.get('class'):
                            traitsHolder = []                        
                            while traitsFinder.get('class'):
                                #print (traitsFinder.text)
                                traitsFinder = traitsFinder.next_sibling
                                traitsHolder.append(traitsFinder.text)
                            
                            #print('traits: ', traitsHolder)
                            detailAbility['abilityTraits'] = traitsHolder
                        else: 
                            pass
                        #sourceAbiHref = th2.next_sibling
                        ak = traitsFinder.next_sibling
                        abiSource = ak.next_sibling                        
                        
                        detailAbility['abilitySource'] = abiSource.text
                        detailAbility['abilitySourceLink'] = abiSource.get('href')
                        
                        
                        extraEleAbi = abiSource.next_sibling
                        if extraEleAbi.name == 'b':                            
                            while extraEleAbi.name == 'b':                            
                                #print(extraEleAbi.text)
                                detailAbility[extraEleAbi.text] = encoder(extraEleAbi.next_sibling)
                                ar = extraEleAbi.next_sibling
                                extraEleAbi = ar.next_sibling
                                #print (extraEleAbi)                            
                        else:
                            pass
                        #abiDesc = ay.next_sibling
                        #print (detailAbility)
                        

                        detail['ability'] = detailAbility             
                detail['pfsLegal'] = pfsLegal
                detail['ancestryName'] = nameAncestry
                details.append(detail)
            else:
                pass
            
        #nameAncestry = {}
        #herit[nameAncestry] = details
        #print (prova)
    return details

    



#print (get_heritageLink())
""" for gillo in get_heritageLink():
    bon = gillo.text.replace(' Heritages', '')
    heritageHolder[bon] = get_details() """

heritageHolder['Heritages'] = get_details()

json_data = json.dumps(heritageHolder, indent=4)
# print(json_data)
filename = "heritages-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close