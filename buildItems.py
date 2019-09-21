from bs4 import BeautifulSoup
import requests
import json
import datetime
import buildDetailsHR as hrDets
import advGear
import getArmor

itemHolder = {}
itemHolder['name'] = 'Pathfinder 2.0 item list'
itemHolder['date'] = datetime.date.today().strftime("%B %d, %Y")




def get_sub_links(link):
    res2 = requests.get(linkTarget)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    main = soup2.find("span", {'id':'ctl00_MainContent_SubNavigation'})
    links = main.find_all("a")
    linkHolder = []
    for link in links:
        linkHolder.append(link['href'])
    return linkHolder


res = requests.get("https://2e.aonprd.com/Equipment.aspx")
res.raise_for_status()
soup = BeautifulSoup(res.text, 'lxml')
mainContent = soup.find(lambda tag: tag.name=='span' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_Navigation") 
links = mainContent.find_all("a")
t = 0
for link in links:
    t += 1
    print(link)
    linkTarget = "https://2e.aonprd.com/" +link['href']
    if link.text == "Adventuring Gear":
         itemHolder['adventuringGear'] = advGear.get_adv(linkTarget, link.text)
    if link.text == "Alchemical Items":
        subLinks = get_sub_links(linkTarget)
        for subLink in subLinks:
            print(subLink)

    if link.text == "Armor":
        itemHolder['armor'] = getArmor.get_all(linkTarget)
    if t > 3:
        break



json_data = json.dumps(itemHolder)
#print(json_data)
filename = "items-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close