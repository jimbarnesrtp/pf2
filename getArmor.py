from bs4 import BeautifulSoup
import requests
import buildDetailsHR as hrDets


armorHolder = {}


def get_armor(link):
    items = []
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
        print(row)
        print("-----------------------------------")
        item = {}
        entries = row.find_all(lambda tag: tag.name=='td')
        if entries is not None:
            if len(entries) > 0:
                item['name'] = entries[0].find("a").text
                item['link'] = "https://2e.aonprd.com/"+entries[0].find("a")['href']
                item['category'] = "Armor"
                item['armorCategory'] = entries[1].text
                item['level'] = entries[2].text
                item['price'] = entries[3].text
                item['acBonus'] = entries[4].text
                item['dexCap'] = entries[5].text
                item['checkPenalty'] = entries[6].text
                item['speedPenalty'] = entries[7].text
                item['str'] = entries[8].text
                item['bulk'] = entries[9].text
                item['group'] = entries[10].text
                item['traits'] = entries[11].text

                item['text'] = hrDets.get_afterhr(item['link'])

                items.append(item)
        if j > 5:
            break
    return items
    
def get_all(link):
    armorHolder['baseArmor'] = get_armor(link)