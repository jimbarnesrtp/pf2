from bs4 import BeautifulSoup
import requests
import datetime
import json


itemHolder = {}
itemHolder['name'] = 'Pathfinder 2.0 item list'
itemHolder['date'] = datetime.date.today().strftime("%B %d, %Y")

items = []
def get_details(link):
    res3 = requests.get(link)
    res3.raise_for_status()
    soup3 = BeautifulSoup(res3.text, 'lxml')
    itemDetails = soup3.find_all("div", {'class':'main'})
    detail = soup3.find("span", {'id':'ctl00_MainContent_DetailedOutput'})
    itemDetails = {}
    children = detail.contents
    reachedBreak = False
    detailHolder = []
    details = {}
    for child in children:
        stringContents = str(child)
        if reachedBreak:
            if stringContents != "<br/>" and stringContents != "<hr/>":
                if(stringContents.startswith("<a")):
                    details['source'] = child.text
                else:
                    #print("in here", stringContents)
                    try:
                        detailHolder.append(child.text)
                        
                    except Exception as e: 
                        if(len(stringContents.strip()) > 0):
                            detailHolder.append(stringContents.strip())
                        #print("exception:", stringContents)
                        #print(e)
            #detailHolder.append(child.text)

        
        #print('<!!!!!!!!!!!!!!!!!!!!!!!!!>')
    
        if "Source" in stringContents:
            reachedBreak = True
    string = " "
    details['text'] = string.join(detailHolder)
    return details
        
    
def get_adv(link, category):
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
        #print(row)
        #print("-----------------------------------")
        item = {}
        entries = row.find_all(lambda tag: tag.name=='td')
        if entries is not None:
            if len(entries) > 0:
                name = entries[0].find("a").text
                itemLink = "https://2e.aonprd.com/"+entries[0].find("a")['href']
                level = entries[1].text
                price = entries[2].text
                bulk = entries[3].text
                item['name'] = name
                item['link'] = itemLink
                item['level'] = level
                item['price'] = price
                item['bulk'] = bulk
                item['category'] = category
                print("Getting item:", item['name'])
                details = get_details(itemLink)
                len(details.keys())
                for key in details.keys():
                    item[key.lower()] = details[key]

                items.append(item)

        
        #if j > 5:
            #break

    return items

itemHolder['adventuringGear'] = get_adv("https://2e.aonprd.com/Equipment.aspx?Category=1", "Adventuring Gear")

json_data = json.dumps(itemHolder)
#print(json_data)
filename = "advGear-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close