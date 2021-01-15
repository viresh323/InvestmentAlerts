import json 
import requests
import pandas as pd 

headers = {
       'Connection': 'keep-alive',
       'Cache-Control': 'max-age=0',
       'DNT': '1',
       'Upgrade-Insecure-Requests': '1',
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
       'Sec-Fetch-User': '?1',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
       'Sec-Fetch-Site': 'none',
       'Sec-Fetch-Mode': 'navigate',
       'Accept-Encoding': 'gzip, deflate, br',
       'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
   }

def GetWebRequestData(url):
    data = requests.get(url,headers=headers).json()
    return data["data"]

def GetCurrenOFS():
   result = "Current Offerings\n"
   result += "- - - - - - - - - - \n"
   data = GetWebRequestData("https://www1.nseindia.com/live_market/content/live_watch/offer_sale/current.json")
   result += GetDisplayOFS(data)
   result += "- - - - - - - - - - \n"
   return result    

def GetUpcomingOFS():
   result = "Upcoming Offerings\n"
   result += "- - - - - - - - - - \n"
   data = GetWebRequestData("https://www1.nseindia.com/live_market/content/live_watch/offer_sale/forthcoming.json")
   result += GetDisplayOFS(data)
   result += "- - - - - - - - - - \n"
   return result

def GetUpcomingIPOs():
    data = GetWebRequestData("https://www1.nseindia.com/products/content/equities/ipos/json/rhpJson.json")
    ipoData = pd.DataFrame(data)
    text = "\n Upcoming IPOs \n - - - - - - - - - - \n"
    if ipoData.empty:
        return "No records found\n  - - - - - - - - - - \n"
    for index,item in ipoData.iterrows():
        text += item["RHP_COMPANY_NAME"]
        text += ("\nDate : %s to %s \n"%(item["RHP_START_DT"],item["RHP_END_DT"]))
        text += "- - - - - - - - - - \n"
    
    
    return text


def GetDisplayOFS(ofsData):
    ofsData = pd.DataFrame(ofsData)
    text = ""
    if ofsData.empty:
        return "No records found\n"
    for index,item in ofsData.iterrows():
     text += ("%s"%(item["company"]))
     text += ("\nDate : %s to %s \n"%(item["ofsStartDate"],item["ofsEndDate"]))
    return text
    
def sendToTelegram(text):
    urlString = "https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}"
    apiToken = "" #Give api token of the bot
    chatId = "-1001280951754" #Group Id
    urlString = urlString.format(apiToken, chatId, text)
    response = requests.get(urlString)


def main(): 
  currentOfs =(GetCurrenOFS())
  upcomingOfs = (GetUpcomingOFS())
  upcomingIpo = GetUpcomingIPOs()
  sendToTelegram(currentOfs+upcomingOfs+upcomingIpo)

main()
