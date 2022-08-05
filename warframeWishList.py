from bs4 import BeautifulSoup 
from bs4.element import ResultSet
import requests 
import json
from datetime import datetime
import os.path
import os
import smtplib
from email.message import EmailMessage

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




def updateGameEntry(gamePrices,gameName,maxPrice,minPrice, link):
    #print(f'Game: {gamePrices}')
    if not (gameName in gamePrices):
        #print(f"Inserting new game data {gameName}")
        newEntry ={}
        newEntry[REGULAR_PRICE]=maxPrice
        newEntry[MIN_PRICE]=minPrice
        newEntry["link"] = link
        dateTimeObj = datetime.now()
        timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
        newEntry[TIME_MIN_PRICE_UPDATE]=timestampStr
        gamePrices[gameName]=newEntry
      


        #set the current smallest price for when the query was done
        newEntry[CURRENT_PRICE]=minPrice
        dateTimeObj = datetime.now()
        timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
        newEntry[TIME_CURR_PRICE_UPDATE]=timestampStr
    else:
        #change the regular price which will be the max price
        gameData=gamePrices[gameName]

        #set the current smallest price for when the query was done
        gameData[CURRENT_PRICE]=minPrice
        dateTimeObj = datetime.now()
        timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
        gameData[TIME_CURR_PRICE_UPDATE]=timestampStr
        
        #set the max price to be be the regular price
        if(gameData[REGULAR_PRICE]<maxPrice):
            #print(f"updating new game data old price {gameData[REGULAR_PRICE]} and max {maxPrice}")
            gamePrices[REGULAR_PRICE] =maxPrice
        
        #change the minimum price
        if(gameData[MIN_PRICE]>minPrice):
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
            gameData[TIME_MIN_PRICE_UPDATE]=timestampStr
            #print(f"updating new game data old price {gameData[MIN_PRICE]} and min {minPrice} with time: {timestampStr}")
            gameData[MIN_PRICE] =minPrice
             
 
def searchSwitchPrices(link):
    print("Looking up nintendo switch prices")
    if os.path.isfile(GAME_FILE):
        gamePrices=loadJson()
    else:
        gamePrices={}

    for gameName in switch_watchList:
        linkToParse = constructLink(link,gameName)
        r = requests.get(linkToParse,timeout=5) 
        soup = BeautifulSoup(r.text, "html5lib")
        regularPricesTag=soup.findAll("div" ,"row order-row--1GgmF")
        dicountPricesTag=soup.findAll("div", "btn-primary")
        #print("DiscountPrices")
        discountPrices=[]
        prices=[]
        for price in dicountPricesTag:
            
            splited=str(price).split("$")
            if(len(splited)==2):
                aPrice=splited[1][:5]
                try:
                    
                    aPrice=float(aPrice)
                    discountPrices.append(aPrice)
                    prices.append(aPrice)
                    #print(f'The discounted prices :{aPrice}')
                except:
                    print("An exception occurred")
        #print("regular price:")
        regularPrices=[]
        for price in regularPricesTag:
            tag= price.string
            splited=str(tag).split("$")
            if(len(splited)==2):
                try:
                    aPrice=splited[1]
                    aPrice=float(aPrice)
                    regularPrices.append(aPrice)
                    prices.append(aPrice)
                   # print(f'The regular prices :{aPrice}')
                    
                except:
                    print('Error as occured')
        prices = sorted(prices)
        numElems = len(prices)
        highestPrice= prices[numElems-1]
        smallestPrice= prices[0]

        #print(f"The smallest price {smallestPrice}")
        #print(f"The highest price {highestPrice}")
        #print(f"The prices : {prices}")
        updateGameEntry(gamePrices,gameName,highestPrice,smallestPrice, linkToParse)
    
    saveJson(gamePrices)
 



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
    
    
    


def filterByValue(array, orderType):
    fitleredList = filter(lambda x: x["order_type"] == orderType, array)
    return list(fitleredList)

def getSellOrders(array):
    return filterByValue(array,"sell")
def getBuyOrders(array):
    return filterByValue(array,"buy")

def alert(gamePrices):
    message = ""
    for count, game in enumerate(gamePrices):
        gameData = gamePrices[game]
        #print(f' {count} the data {gameData}')

        try:
            min_price=gameData[MIN_PRICE]
            regPrice=gameData[REGULAR_PRICE]
            curr_price=gameData[CURRENT_PRICE]
            link=gameData["link"]
            discountPrice= (1-(curr_price/regPrice ))*100
            discountPrice = round(discountPrice, 2)

            if(PRICE_DISCOUNT<=discountPrice):
                if(regPrice>curr_price and curr_price<=min_price):
                    #print(f"{game} the current price {curr_price} is currently as the cheapest price on {discountPrice}% discount")
                    message+= f"{game} the current price {curr_price} is currently as the cheapest price on {discountPrice}% discount (reg-price {regPrice}) ({link})\n"
                elif(regPrice>curr_price):
                    #print(f"{game} the current price {curr_price} is cheaper then regular price {regPrice} is on {discountPrice}% discount")
                    message+= f"{game} the current price {curr_price} is cheaper then regular price {regPrice} is on {discountPrice}% discount ({link})\n"
        except TypeError:
            print(f'Error {gameData}')

    print(message)
    return message

def sendMessage(messageBody):
    EMAIL_ADDRESS = "soccermsndave@gmail.com"
    EMAIL_PASSWORD ="wyezzrtstndpuxvt"
    msg = EmailMessage()
    msg['Subject'] = "Game Discount Alert"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ['soccermsndave@hotmail.com']

    msg.set_content(messageBody)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
        
def main():
    getListArbitrationRewards()

    checkGalvantizedMods()
    #getListGalvantinzedMods()

    

def lambda_handler(event, context):
    main()

main()

