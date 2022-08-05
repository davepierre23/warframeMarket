from bs4 import BeautifulSoup 
from bs4.element import ResultSet
import requests 
import json
import re
from datetime import datetime
import os.path
import os
import smtplib
from email.message import EmailMessage

import time


NUM='6139834287'  
ORDERS="orders"
PAYLOAD="payload"
MIN_PRICE="min_price"
TIME_MIN_PRICE_UPDATE="min_price_time"
CURRENT_PRICE="current_price"
TIME_CURR_PRICE_UPDATE="current_price_time"
GAME_FILE="/tmp/gameWishList.json"

PRELINK="https://ps4.warframe.market/items/"

linkGalvatinized = "https://warframe.fandom.com/wiki/Category:Galvanized_Mods"
linkArbitrations = "https://warframe.fandom.com/wiki/Arbitrations"

galvanizedMods ="galvanized_acceleration"

def constructLink(link,gameName):
    return link+"/"+gameName

def saveJson(gamePrices):
    with open(GAME_FILE, "w") as p: 
     json.dump(gamePrices, p)

def loadJson():
    with open(GAME_FILE) as json_file:
        data = json.load(json_file)
        return data


def getListGalvantinzedMods(link=linkGalvatinized):
    
    # make request to site
    r = requests.get(linkGalvatinized,timeout=5) 
    soup = BeautifulSoup(r.text, "html5lib")

    
    #market orders are find in a script tag 
    galvantinzedMods=soup.findAll("a",attrs={"class": "category-page__member-link"})

    nameOfMods = []
    for mod in galvantinzedMods:
    
        nameOfMods.append(getReadyLink(mod.text))

    print(nameOfMods)    
    return nameOfMods
    

def getListArbitrationRewards(link=linkArbitrations):
    
    # make request to site
    r = requests.get(linkGalvatinized,timeout=5) 
    soup = BeautifulSoup(r.text, "html5lib")

    print(soup)
    #market orders are find in a script tag 
    artbitrationRewards=soup.findAll("table")

    print(artbitrationRewards)
    # nameOfMods = []
    # for mod in artbitrationRewards:
    
    #     nameOfMods.append(getReadyLink(mod.text))

    # print(nameOfMods)    
    # return nameOfMods

#take the names and replace it with the link to parse for ps4
def getReadyLink(name):
    name = name.lower()
    name =name.replace(" ", "_")
    return PRELINK+name

#take the names and replace it with the link to parse for ps4
def getItemFromLink(name):
    name = name.lower()
    name =name.split("/")
    print(name)
    return name[-1]


def searchWarFramePrices(link):
    print("Looking up warframe  Items :" + link)
    
    # make request to site
    r = requests.get(link,timeout=5) 
    soup = BeautifulSoup(r.text, "html5lib")

    
    #market orders are find in a script tag 
    offerTags=soup.find(id="application-state")
    orders = json.loads(offerTags.contents[0])
    orders = (orders[PAYLOAD][ORDERS])




    print("list of Buy")
    sellOrders = getBuyOrders(orders)

    sellOrders =parseSellData(link,sellOrders)


    return sellOrders


def parseSellData(item,data):
    print("Data parsing ")
    print(item)
    print(data)
    newDataModels = []
    for order in data:
        newData= {}
        newData["item"] = item
        newData["platinum"]= order["platinum"]
        newData["modRank"]=order["mod_rank"]
        newData["userInterest"]=order["user"]["ingame_name"]
        newDataModels.append(newData)

    return newDataModels


def printSellOrders(sellOrders):
    i=1
    for item in sellOrders:
        print('{}: - {}'.format(i, item))
        i = i +1
        print()
    print()

def checkGalvantizedMods():

    queueMods = getListGalvantinzedMods()
    modList = []
    for modLink in queueMods:
        print("Mod Link checking " +modLink)
        listMod = searchWarFramePrices(modLink)
        print(listMod)
        modList.extend(listMod)
    

    modList.sort(key=lambda x: x["platinum"])

    print("Done listing ")

    print("summary number of sell orders "+str(len(modList)))
    printSellOrders(modList)
    
    


def warframeSteelPath(link="https://warframe.fandom.com/wiki/The_Steel_Path"):
      # make request to site
    r = requests.get(link,timeout=5) 
    soup = BeautifulSoup(r.text, "html5lib")

    
    for div in  soup.find_all("span"):
        if("is available for " in div.text ):
            print(div.text)
            print()


 
        
def main():
    warframeSteelPath()

    

def lambda_handler(event, context):
    main()

main()

