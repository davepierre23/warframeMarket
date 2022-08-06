from email import message
from bs4 import BeautifulSoup 
from bs4.element import ResultSet
import requests 
import json
import logging as log
import boto3
log.basicConfig(format='%(message)s', level=log.INFO)

PRELINK="https://ps4.warframe.market/items/"
linkPrime = "https://warframe.fandom.com/wiki/Category:Primed_Mods"
linkGalvatinized = "https://warframe.fandom.com/wiki/Category:Galvanized_Mods"
linkArbitrations = "https://warframe.fandom.com/wiki/Arbitrations"
emailOn=True
ORDERS="orders"
PAYLOAD="payload"
arn ="arn:aws:sns:ca-central-1:004369745227:stockPortfolio"
 

def sendEmail(message):
    sns = boto3.resource('sns')
    topic_arn= arn
    topic=sns.Topic(arn=topic_arn)
    if(emailOn):
        response = topic.publish(Message=message)
        message_id = response['MessageId']
        return message_id
def constructLink(link,gameName):
    return link+"/"+gameName

def getBuyOrders(array):
    return filterByValue(array,"buy")

def filterByValue(array, orderType):
    fitleredList = filter(lambda x: x["order_type"] == orderType, array)
    return list(fitleredList)
def getListGalvantinzedMods(link=linkGalvatinized):
    
    # make request to site
    r = requests.get(linkGalvatinized,timeout=5) 
    soup = BeautifulSoup(r.text, "html5lib")

    #market orders are find in a script tag 
    galvantinzedMods=soup.findAll("a",attrs={"class": "category-page__member-link"})
    nameOfMods = []

    for mod in galvantinzedMods:
        nameOfMods.append(getReadyLink(mod.text))    
    return nameOfMods
    

def searchWarFramePrices(link):
    try:
    # make request to site
        r = requests.get(link,timeout=5) 
        soup = BeautifulSoup(r.text, "html5lib")

        #market orders are find in a script tag 
        offerTags=soup.find(id="application-state")
        orders = json.loads(offerTags.contents[0])
        orders = (orders[PAYLOAD][ORDERS])
        sellOrders = getBuyOrders(orders)
        sellOrders =parseSellData(link,sellOrders)
        return sellOrders
    except BaseException as err:
        log.debug("Failed to look up the following" + link)
        return []

def getListPrimeMods():
    # make request to site
    r = requests.get(linkPrime,timeout=5) 
    soup = BeautifulSoup(r.text, "html5lib")

    #market orders are find in a script tag 
    galvantinzedMods=soup.findAll("a",attrs={"class": "category-page__member-link"})
    nameOfMods = []

    for mod in galvantinzedMods:
        nameOfMods.append(getReadyLink(mod.text))
    return nameOfMods

def checkPrimeMods():
    return checkMods(getListPrimeMods)

def checkGalvantizedMods():
    return checkMods(getListGalvantinzedMods)

def checkMods(getListModes):
    queueMods = getListModes()
    modList = []
    for modLink in queueMods:
        listMod = searchWarFramePrices(modLink)
        modList.extend(listMod)
    modList.sort(key=lambda x: x["platinum"])
    return sumarrySellOrders(modList)
 
 
#take the names and replace it with the link to parse for ps4
def getReadyLink(name):
    name = name.lower()
    name =name.replace(" ", "_")
    name =name.replace("-", "_")
    return PRELINK+name

#take the names and replace it with the link to parse for ps4
def getItemFromLink(name):
    name = name.lower()
    name =name.split("/")
    log.debug(name)
    return name[-1]


def parseSellData(item,data):
    log.debug("Data parsing ")
    log.debug(item)
    log.debug(data)
    newDataModels = []
    for order in data:
        newData= {}
        newData["item"] = item
        newData["platinum"]= order["platinum"]
        newData["modRank"]=order["mod_rank"]
        newData["userInterest"]=order["user"]["ingame_name"]
        newDataModels.append(newData)

    return newDataModels


def sumarrySellOrders(sellOrders):
    message=""
    message+="Summary number of sell orders "+str(len(sellOrders))
    message+=("\n \n")
    i=1
    for item in sellOrders:
        message+=('{}: - {}\n'.format(i, item))
        i = i +1
        message+=("\n")
    message+=("\n")

    log.info(message)
    return message

def getCurrentSteelPathReward(link="https://warframe.fandom.com/wiki/The_Steel_Path"):
    message=""
      # make request to site
    r = requests.get(link,timeout=5) 
    soup = BeautifulSoup(r.text, "html5lib")

    count =0
    #the text we are looking for is the element
    for div in  soup.find_all("span"):
        if("is available for " in div.text ):
            count+=1
            if(count==2):
                log.debug(div.text)
                message+=div.text
                message+="this week"
                return message
               
def main():
    messages =[]
    
    messages.append(getCurrentSteelPathReward())
    messages.append(checkGalvantizedMods())
    messages.append(checkPrimeMods())
    for message in messages:
        sendEmail(message)
    
def lambda_handler(event, context):
    main()

main()

