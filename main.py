import json
import requests
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import os
import configparser


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
    try:
        data = requests.get(url, headers=headers)
        data = data.json()
    except ValueError:
        # Refered Upstox
        s = requests.Session()
        data = s.get("http://nseindia.com", headers=headers)
        data = s.get(url, headers=headers)
        data = data.json()

    if("data" not in data):
        return data

    return data["data"]


def GetCurrenOFS():

    result = "-Current Offerings- \n"
    data = GetWebRequestData(
        "https://www1.nseindia.com/live_market/content/live_watch/offer_sale/current.json")
    ofsText = GetDisplayOFS(data)
    if(ofsText == ""):
        return ""

    result += ofsText
    result += "- - - - - - - - - - \n"
    return result


def GetUpcomingOFS():

    result = "-Upcoming Offerings-\n"
    data = GetWebRequestData(
        "https://www1.nseindia.com/live_market/content/live_watch/offer_sale/forthcoming.json")
    ofsText = GetDisplayOFS(data)
    if(ofsText == ""):
        return ""

    result += ofsText
    result += "- - - - - - - \n"
    return result


def GetUpcomingBuyback():

    result = "-Upcoming Buyback-\n"
    data = GetWebRequestData(
        "https://www1.nseindia.com/live_market/content/live_watch/tender_offer/forthcoming.json")
    buybackText = GetDisplayBuyback(data)

    if(buybackText == ""):
        return ""
    result += buybackText
    result += "- - - - - - - - - - \n"
    return result


def GetCurrentBuyback():

    result = "- Current Buyback -\n"
    data = GetWebRequestData(
        "https://www1.nseindia.com/live_market/content/live_watch/tender_offer/current.json")
    buybackText = GetDisplayBuyback(data)

    if(buybackText == ""):
        return ""
    result += buybackText
    result += "- - - - - - - - - - \n"
    return result


def GetCurrentIPOs():
    data = GetWebRequestData(
        "https://www.nseindia.com/api/ipo-current-issue")

    text = "- CURRENT IPO -\n"
    ipoText = GetDisplayIPO(data)
    if(ipoText == ""):
        return ""

    text += ipoText
    text += " - - - - - - - - - - \n"
    return text


def GetUpcomingIPOs():
    text = "-UPCOMING IPO-\n"
    data = GetWebRequestData(
        "https://www.nseindia.com/api/all-upcoming-issues?category=ipo")
    ipoText = GetDisplayIPO(data)
    if(ipoText == ""):
        return ""

    text += ipoText

    text += " - - - - - - - - - - \n"
    return text


def GetDisplayBuyback(ofsData):
    ofsData = pd.DataFrame(ofsData)
    text = ""
    if ofsData.empty:
        return ""
    for index, item in ofsData.iterrows():
        text += ("%s" % (item["company"]))
        text += ("\nDate : %s to %s \n" %
                 (item["todStartDate"], item["todEndDate"]))
    return text


def GetDisplayOFS(ofsData):
    ofsData = pd.DataFrame(ofsData)
    text = ""
    if ofsData.empty:
        return ""
    for index, item in ofsData.iterrows():
        text += ("%s" % (item["company"]))
        text += ("\nDate : %s to %s \n" %
                 (item["ofsStartDate"], item["ofsEndDate"]))
    return text


def GetDisplayBoardMeetings(data):
    result = ""
    for i in data:
        result += ("%s" % (i["CompanyName"]))
        result += ("%s" % (i["Purpose"]))
        result += ("%s" % (i["DisplayDate"]))

    return result


def GetDisplayEvents(data):
    result = ""
    for i in data:
        if dt.strptime(i["date"], "%d-%b-%Y") < (dt.today() + timedelta(days=10)):
            result += ("%s" % (i["company"]))
            result += ("%s" % (i["purpose"]))
            result += ("- %s \n \n" % (i["date"]))

    return result


def GetDisplayIPO(data):
    result = ""
    for i in data:
        result += ("%s" % (i["companyName"]))
        result += ("\n %s" % (i["issueStartDate"]))
        result += ("- %s \n" % (i["issueEndDate"]))

    return result


def GetBoardMeetings():

    result = "-Board Meetings-\n"

    data = GetWebRequestData(
        "https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/companySnapshot/getBoardMeetings.json")
    resultData = data["rows"]
    result += GetDisplayBoardMeetings(resultData)
    result += "- - - - - - - - - - \n"
    return result


def GetResults():
    result = "-Results- \n"

    data = GetWebRequestData(
        "https://www.nseindia.com/api/event-calendar")

    result += GetDisplayEvents(data)
    result += "- - - - - - - -\n"
    return result

def GetDisplayAnnouncements(data, isOfs):
    buyBackResult = " - BuyBack - \n"
    dividentResult = " - Divident - \n"
    ofsResult = " - Offer for sale - \n"

    for i in data:
        if "Dividend" in i["desc"]:
            dividentResult += ("%s" % (i["symbol"]))
            dividentResult += (" - %s" % (i["desc"]))
            dividentResult += (" - %s \n \n" % (i["sort_date"]))
        if "Buyback" in i["desc"]:
            buyBackResult += ("%s" % (i["symbol"]))
            buyBackResult += (" - %s" % (i["desc"]))
            buyBackResult += (" - %s \n \n" % (i["sort_date"]))
        if "Offer for sale" in i["desc"]:
            ofsResult += ("%s" % (i["symbol"]))
            ofsResult += (" - %s" % (i["desc"]))
            ofsResult += (" - %s \n \n" % (i["sort_date"]))

    buyBackResult += "----------------\n"
    dividentResult += "----------------\n"
    ofsResult += "----------------\n"

    if isOfs == True:
        return ofsResult
    return buyBackResult + dividentResult + ofsResult

def GetAnnouncements(isOfs):
    result = "-Announcements - BuyBack - Divident - \n"

    data = GetWebRequestData(
        "https://www.nseindia.com/api/corporate-announcements?index=equities")

    result += GetDisplayAnnouncements(data, isOfs)
    result += "- - - - - - - -\n"
    return result

def GetDisplayCorporateActions(data):
    buyBackResult = " - BuyBack - \n"
    dividentResult = " - Divident - \n"
    bonusResult = " - Bonus - \n"
    
    for i in data:
        if "Dividend" in i["subject"]:
            dividentResult += ("%s" % (i["symbol"]))
            dividentResult += (" - %s" % (i["subject"]))
            dividentResult += (" - Ex-%s \n \n" % (i["exDate"]))
        if "Buy Back" in i["subject"]:
            buyBackResult += ("%s" % (i["symbol"]))
            buyBackResult += (" - %s" % (i["subject"]))
            buyBackResult += (" - Ex-%s \n \n" % (i["exDate"]))
        if "Bonus" in i["subject"]:
            bonusResult += ("%s" % (i["symbol"]))
            bonusResult += (" - %s" % (i["subject"]))
            bonusResult += (" - Ex-%s \n \n" % (i["exDate"]))

    buyBackResult += "----------------\n"
    dividentResult += "----------------\n"
    bonusResult += "----------------\n"
    return buyBackResult + dividentResult + bonusResult

def GetCorporateActions():
    result = "-Corporate Actions - BuyBack - Divident - Bonus - \n"

    data = GetWebRequestData(
        "https://www.nseindia.com/api/corporates-corporateActions?index=equities")

    result += GetDisplayCorporateActions(data)
    result += "- - - - - - - -\n"
    return result


def sendToTelegram(text):
    urlString = "https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}"

    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'CONFIGURATON.INI'))

    # Give api token of the bot
    apiToken = config.get('TELEGRAM', 'API_TOKEN')
    chatId = config.get('TELEGRAM', 'CHAT_ID')

    text = text.replace("&", "And")
    for i in range(0, len(text), 3800):
        url = urlString.format(
            apiToken, chatId, text[i:i+3800])
        response = requests.get(url)


def main():
    currentOfs = (GetCurrenOFS())
    upcomingOfs = (GetUpcomingOFS())
    upcomingIpo = GetUpcomingIPOs()
    currentIpo = GetCurrentIPOs()
    currentBuyback = GetCurrentBuyback()
    upcomingBuyback = GetUpcomingBuyback()
    dividend = GetBoardMeetings()
    earnings = GetResults()
    announcements = GetAnnouncements(False)
    corporateActions = GetCorporateActions()

    ofsAnnouncements = GetAnnouncements(True) # call this for OFS announcements

    sendToTelegram(currentOfs + upcomingOfs + upcomingIpo +
                    currentIpo + currentBuyback + upcomingBuyback + announcements + corporateActions + ofsAnnouncements)

    if dt.today().weekday() == 2:
        sendToTelegram(dividend + earnings)


main()
