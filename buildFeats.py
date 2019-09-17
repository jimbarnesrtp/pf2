from bs4 import BeautifulSoup
import requests
import json
import datetime

featHolder = {}
featHolder['name'] = 'Pathfinder 2.0 feat list'
featHolder['date'] = datetime.date.today().strftime("%B %d, %Y")

feats = []

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
            feat['link'] = link
            feat['prereq'] = prereq
            feat['benefits'] = source
            feats.append(feat)


featHolder['feats'] = feats
json_data = json.dumps(featHolder)
print(json_data)