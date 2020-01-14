from bs4 import BeautifulSoup
import requests
import json
import datetime

bgHolder = {}
bgHolder['name'] = 'Pathfinder 2.0 background list'
bgHolder['date'] = datetime.date.today().strftime("%B %d, %Y")
bgHolder['backgrounds'] = []

res = requests.get("http://pf2.d20pfsrd.com/background")
res.raise_for_status()
soup = BeautifulSoup(res.text, 'lxml')
table = soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="archive-data-table") 
rows = table.findAll(lambda tag: tag.name=='tr')
t = 0

for row in rows:
    t += 1
    print(row)
    print("-----------------------------------")
    bg = {}
    entries = row.find_all(lambda tag: tag.name=='td')
    if entries is not None:
        if len(entries) > 0:
            name = entries[0].find("a").text
            link = entries[0].find("a")['href']
            bg['name'] = name
            bg['link'] = link
            source = entries[2].find("a").text
            bg['source'] = source
            res2 = requests.get(link)
            res2.raise_for_status()
            soup2 = BeautifulSoup(res2.text, 'lxml')
            bgScratch = soup2.find_all("div", {'class':'article-content'})
            children = bgScratch[0].findChildren(recursive=False)
            textHolder = []
            bg['ability'] = []
            for child in children:
                #print("in here:", child.text)
                if "Section 15" in child.text:
                    break
                if "Choose two ability boosts" in child.text:
                    start = child.text.find("Choose two ability boosts")
                    textList = child.text[start+26:].split(",")
                    for text in textList:
                        bg['ability'].append(text.strip())
                    
                else:
                    textHolder.append(child.text)
            #print(len(textHolder))
            bg['backgroundText'] = textHolder
    bgHolder['backgrounds'].append(bg)
    #if t > 5:
        #break



json_data = json.dumps(bgHolder, indent=4)
#print(json_data)
filename = "backgrounds-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close

           
