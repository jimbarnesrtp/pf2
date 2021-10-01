# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import json
import datetime
from pf2helpers import Pf2Helpers
import os
import re

data_holder = {}
data_holder['name'] = 'Pathfinder 2.0 ItemList v2'
data_holder['date'] = datetime.date.today().strftime("%B %d, %Y")

class ItemBuilder():

    blacklist = ['[document]','noscript','header','html','meta','head', 'input','script', 'h1','img','i','a','b','h3']

    pf = Pf2Helpers()


def main():
    bf = ItemBuilder()
    #bf.save_data(bf.build_monsters())

if __name__ == '__main__':
   main()