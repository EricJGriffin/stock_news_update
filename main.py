import os
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
api_key = os.environ.get("api_key")
twilio_number = os.environ.get("twilio_number")
my_number = os.environ.get("my_number")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
import requests
import datetime as dt
from twilio.rest import Client


## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
stock_url = "https://www.alphavantage.co/query"
parameters = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": STOCK,
    "interval": "60min",
    "apikey": api_key,
}

response = requests.get(stock_url, params=parameters)
data = response.json()
yesterday_close_key = max(data["Time Series (60min)"].keys())
yesterday_close_price = data["Time Series (60min)"][yesterday_close_key]["4. close"]
yesterday_date = yesterday_close_key.split(" ")[0]
previous_date = ""
for i in data["Time Series (60min)"].keys():
    date = i.split(" ")[0]
    if date != yesterday_date:
        previous_date = i
        break
previous_close_price = data["Time Series (60min)"][previous_date]["4. close"]
difference = float(yesterday_close_price) / float(previous_close_price)
# if difference > 1.05 or difference < 0.95:
if difference != 0.0:
    message_difference = 0.0
    dir_symbol = ""
    # if difference > 1.05:
    if difference > 1.02: # you can set the threshold for significant stock price change here
        message_difference = int((difference - 1.00) * 100)
        dir_symbol = "🔺"
    # elif difference < 0.95:
    elif difference < 1.02: # you can set the threshold for significant stock price change here
        message_difference = int((1.00 - difference) * 100)
        dir_symbol = "🔻"
    news_parameters = {
        "function": "NEWS_SENTIMENT",
        "tickers": STOCK,
        "limit": "3",
        "apikey": api_key,
    }
    r = requests.get(stock_url, params=news_parameters)
    news_data = r.json()
    news_pieces = news_data["feed"]
    relavent_articles = [article for article in news_pieces if article["summary"].find(COMPANY_NAME) != -1]
    relavent_articles = relavent_articles[:3]
    send_message = f"{STOCK}: {dir_symbol}{message_difference}%\n"
    for a in relavent_articles:
        send_message += f"Headline: {a['title']}\n"
        send_message += f"Brief: {a['summary']}\n"

    # account_sid = os.environ[TWILIO_ACCOUNT_SID]
    # auth_token = os.environ[TWILIO_AUTH_TOKEN]
    # client = Client(account_sid, auth_token)
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    message = client.messages \
        .create(
        body=send_message,
        from_=twilio_number,
        to=my_number
    )

    print(message.status)





