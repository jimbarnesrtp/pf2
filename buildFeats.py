from bs4 import BeautifulSoup
import requests
import json
import datetime

featHolder = {}
featHolder['name'] = 'Pathfinder 2.0 feat list'
featHolder['date'] = datetime.date.today().strftime("%B %d, %Y")

feats = []

def get_details(link):
    res = requests.get(link)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'lxml')
    feat = soup.find_all("div", {'class':'main'})
    detail = soup.find("span", {'id':'ctl00_MainContent_DetailedOutput'})
    #print(detail.contents)
    children = detail.contents
    reachedBreak = False
    detailHolder = []
    for child in children:
        stringContents = str(child)
        if stringContents.startswith("<"):
            if stringContents == "<hr/>":
                reachedBreak = True
        else:
            if reachedBreak:
                detailHolder.append(stringContents)
       #print(child)
       #print('<!!!!!!!!!!!!!!!!!!!!!!!!!>')
    return detailHolder
        


res = requests.get("https://2e.aonprd.com/Feats.aspx")
res.raise_for_status()
soup = BeautifulSoup(res.text, 'lxml')
table = soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_TableElement") 
rows = table.findAll(lambda tag: tag.name=='tr')
t = 0
for row in rows:
    t += 1
    print(row)
    print("-----------------------------------")
    feat = {}
    entries = row.find_all(lambda tag: tag.name=='td')
    if entries is not None:
        if len(entries) > 0:
            name = entries[0].find("a").text
            link = entries[0].find("a")['href']
            #for entry in entries: 
             #   print(entry)
              #  print("row---------------")
            level = entries[1].text
            traits = entries[2].text
            prereq = entries[3].text
            source = entries[4].text


            feat['name'] = name
            feat['level'] = level
            feat['link'] = "https://2e.aonprd.com/" +link
            feat['prereq'] = prereq
            feat['benefits'] = source
            details = get_details(feat['link'])
            feat['text'] = details
            feats.append(feat)
    #if t > 5:
        #break

featHolder['feats'] = feats
json_data = json.dumps(featHolder)
#print(json_data)
filename = "feats-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close