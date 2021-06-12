from datetime import datetime as dt
import azure.functions as func
import requests
import pandas as pd
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
        # Refered Unofficed
        s = requests.Session()
        data = s.get("http://nseindia.com", headers=headers)
        data = s.get(url, headers=headers)
        data = data.json()

    return data


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


def getMarketSentiment():
    data = GetWebRequestData(
        "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20200")
    marketdata = data["advance"]
    adv = marketdata["advances"]
    dec = marketdata["declines"]

    ratio = int(adv)/int(dec)
    sentiment = "Market Sentiment : "

    if(ratio >= 0 and ratio < 0.3):
        sentiment += "Super Bearish adha, hushar hsm"
    elif(ratio >= 0.3 and ratio < 0.5):
        sentiment += "Kind of Bearish, risk thogobyada.. short maad"
    elif(ratio >= 0.5 and ratio < 0.8):
        sentiment += "Neutral, wait maadpa.."
    elif(ratio >= 0.8 and ratio < 1):
        sentiment += "Kind of Bullish guru, pat antha close maad trade "
    elif(ratio >= 1 and ratio < 1.5):
        sentiment += "Bullish adha nod, avnoun!!" 
    else:
        sentiment = "Super Bullish, hodi 9!!"

    return sentiment


def main(mytimer: func.TimerRequest) -> None:
    sendToTelegram(getMarketSentiment())
