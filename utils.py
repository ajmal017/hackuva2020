import string

import requests
import alpha_vantage
from alpha_vantage.timeseries import TimeSeries
import matplotlib
from google.oauth2 import service_account
from matplotlib import pyplot as plt
#import google.datalab.storage as storage
import pandas as pd
from newsapi.newsapi_client import NewsApiClient
import os
from datetime import date, timedelta
from datetime import datetime
from dateutil.rrule import rrule, DAILY

from io import BytesIO
import numpy as np
#import googleapiclient.discovery

from alpha_vantage.techindicators import TechIndicators
from sklearn import preprocessing
import statsmodels.api as sm

from google.cloud import language_v1
from google.cloud.language_v1 import enums



AV_API_KEY = "LBTZOMI8UAQDHHRK"
OPEN = "1. open"
HIGH = "2. high"
LOW = "3. low"
CLOSE = "4. close"
VOLUME = "5. volume"

#have to use double quotes for JSON!!
def get_raw_input_data(stock="DJI"):
    ts = TimeSeries(key=AV_API_KEY, output_format='pandas')
    d, md = ts.get_daily(symbol=stock, outputsize='compact')
    #data_dow, meta_data_dow = ts.get_daily(symbol='DJI', outputsize='compact')
    #data_sp, meta_data_sp = ts.get_daily(symbol='INX',outputsize='compact')
    d = d.loc['2020-01-01':'2020-03-27']
    d[CLOSE] = d[CLOSE].pct_change()
    d = d[d[CLOSE] <= 100]
    d = d.dropna(axis=0)

    TI = TechIndicators(key=AV_API_KEY, output_format='pandas')

    rsi_data, meta_data = TI.get_rsi(symbol=stock, interval="daily", time_period=14)
    macd_data, meta_data = TI.get_macd(symbol=stock, interval="daily")
    sma_data, meta_data = TI.get_sma(symbol=stock, time_period=30)
    bbands_data, meta_data = TI.get_bbands(symbol=stock)

    input_data = pd.DataFrame(columns=["Volume", "Price_Change"], index=d.index)
    input_data["Volume"] = d[VOLUME]
    input_data["Price_Change"] = d[CLOSE]
    input_data = input_data.merge(rsi_data, left_index=True, right_index=True)
    input_data = input_data.merge(sma_data, left_index=True, right_index=True)
    input_data = input_data.merge(macd_data, left_index=True, right_index=True)
    input_data = input_data.merge(bbands_data, left_index=True, right_index=True)
    input_data = input_data.merge(load_covid(), left_index=True, right_index=True)
    input_data = input_data.merge(gen_sentiment_df(stock), left_index=True, right_index=True)
    return input_data

def get_clean_input_data(stock="DJI"):
    input_data = get_raw_input_data(stock)
    input_data = input_data.apply(lambda x: (x - np.mean(x)) / (np.max(x) - np.min(x)))
    return input_data

def get_model_summary(input_data):
    summary = get_model(input_data).summary()
    results = get_model(input_data)
    return [summary,results]
def get_model(input_data):
    X = input_data.drop('Price_Change', axis=1)
    y = input_data["Price_Change"]
    X = sm.add_constant(X)
    mlr = sm.OLS(y, X).fit()
    return mlr
def load_covid():
    df = pd.read_csv("covid_df.csv", index_col=0, parse_dates=True,infer_datetime_format=True)
    return df

def analyze_sentiment(text_content):
    client = language_v1.LanguageServiceClient(credentials=service_account.Credentials.from_service_account_file('key.json'))
    type_ = enums.Document.Type.PLAIN_TEXT
    language = "en"
    document = {"content": text_content.translate(str.maketrans('', '', string.punctuation)), "type": type_, "language": language}
    encoding_type = enums.EncodingType.UTF8
    response = client.analyze_sentiment(document)
    return response.document_sentiment

def gen_sentiment_df(stock="DJI"):
    newsapi = NewsApiClient(api_key='f8970a68f49e43a18c9b5aff8e2bcfe1')
    a = date(2020, 2, 29)
    b = date(2020, 3, 27)
    sentiments = {}
    query = "stocks & " + stock
    for dt in rrule(DAILY, dtstart=a, until=b):
        str_date = str(dt.strftime("%Y-%m-%d"))
        all_articles = newsapi.get_everything(q=query,
                                              from_param=str_date,
                                              to=str_date,
                                              language='en',
                                              sort_by='relevancy',
                                              page=1)
        headlines = ""
        for a in all_articles['articles']:
            if isinstance(a["title"], str):
                headlines += a["title"]
        i = analyze_sentiment(headlines)
        sentiments[dt] = {i.magnitude, i.score}
    sentiment_df = pd.DataFrame(list(sentiments.values()), columns=["magnitude", "score"], index=sentiments.keys())
    sentiment_df = sentiment_df.fillna(0)
    return sentiment_df

