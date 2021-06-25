from bs4 import BeautifulSoup
import requests

def get_afterhr(link):
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'html5lib')
    feat = soup2.find_all("div", {'class':'main'})
    detail = soup2.find("span", {'id':'ctl00_MainContent_DetailedOutput'})
    #print(detail.contents)
    children = detail.contents
    reachedBreak = False
    detailHolder = []
    for child in children:
        stringContents = str(child)
        if stringContents.startswith("<"):
            if child.name == "hr":
                reachedBreak = True
        else:
            if reachedBreak:
                detailHolder.append(stringContents)
       #print(child)
       #print('<!!!!!!!!!!!!!!!!!!!!!!!!!>')
    return detailHolder