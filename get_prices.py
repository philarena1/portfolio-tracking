import requests
import keys
from alpha_vantage.timeseries import TimeSeries
import csv
import os
import json
import time
import pandas as pd


def coin_get_current_prices(coin_list):
    symbols = coin_list #comma delimmited string of all

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol='+symbols+'&convert=USD'
    headers = {
     'Accept': 'application/json',
     'Accept-Encoding': 'deflate, gzip',
     'X-CMC_PRO_API_KEY': keys.COINMARKETCAP_PRO_API_KEY
    }
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        response = json.loads(r.text)
        result = response['data']
        current_price = []
        for i in result:
            price = result[i]['quote']['USD']['price']
            current_price.append([result[i]['name'], result[i]['symbol'], result[i]['last_updated'], price])

        df = pd.DataFrame(current_price, columns=['name', 'symbol', 'last_updated', 'price'])
        return df


# get price of stock in JSON
def stock_get_current_price_json(stock_name):
    ts = TimeSeries(key=keys.alpha_key, output_format='json')
    data, meta_data = ts.get_daily(symbol=stock_name, outputsize="compact")
    dates = list(data.keys())
    recent = data[dates[0]]
    recent['stock'] = stock_name
    recent['date'] = dates[0]
    return recent


# takes JSON as argument, and writes to csv
def write_to_file_json(file_name , records):
    filename = file_name
    file_exists = os.path.isfile(filename)

    headers = list(records.keys()) #get all keys
    values = [records[i] for i in headers] #get all values from json
    with open(filename, 'a') as csvfile:
        wr = csv.writer(csvfile)
        if not file_exists:
            wr.writerows([headers])  # file doesn't exist yet, write a header
        wr.writerows([values]) #else, add the regular columns

# takes df as argument, and writes to csv
def write_to_file_df(file_name , records):
    filename = file_name
    file_exists = os.path.isfile(filename)
    with open(file_name, 'a') as csvfile:
        wr = csv.writer(csvfile)
        if not file_exists:
            headers = ['name', 'symbol', 'last_updated', 'price']
            wr.writerows([headers])  # file doesn't exist yet, write a header
        records.to_csv(csvfile, header=False)


# get list of assets by types- only works with crypto or stocks
def get_holdings_list(csv_file):
    holding = pd.read_csv(csv_file,quotechar=",")     #file with all holdings

    stock = []
    crypto = []
    i = 0
    ### separate each into lists based off of asset types
    while i< len(holding):
        if holding.iloc[i]['Type'] == 'crypto':
            crypto.append(holding.iloc[i]['Assets'])

        if holding.iloc[i]['Type'] == 'stock':
            stock.append(holding.iloc[i]['Assets'])
        i = i + 1
    return stock, crypto


# return df with holdings
def get_holdings_df(csv_file):
    holding = pd.read_csv(csv_file,quotechar=",")     #file with all holdings
    return holding


def get_latest_values_from_file(csvfile, drop_duplicate):
    df = pd.read_csv(csvfile)
    most_recent = df.drop_duplicates(drop_duplicate,keep='last') # keep latest values
    return most_recent


def format_df_from_file(recent, asset_type):
    formated_df = pd.DataFrame()
    if asset_type == 'crypto':
        formated_df[['price', 'Asset']] = recent[['price', 'symbol']]

    if asset_type == 'stock':
        formated_df[['price', 'Asset']] = recent[['4. close', 'stock']]

    return formated_df


def valuate_holdings(holdings_csv):
    # get distinct holdings- stock + crypto
    df = get_holdings_df(holdings_csv)
    crypto = set(list(df['Assets'][df['Type'] == 'crypto']))
    stock = list(df['Assets'][df['Type'] == 'stock'])

    # cryptos need comma delimited list
    myString = ",".join(crypto)
    crypto_prices = coin_get_current_prices(myString)
    write_to_file_df('crypto.csv', crypto_prices)

    for s in stock:
        stock_price = stock_get_current_price_json(s)
        write_to_file_json('stock.csv', stock_price)
        time.sleep(20)  # API has limit of 5 pulls per minute

    crypto_recent = format_df_from_file(get_latest_values_from_file('crypto.csv', 'symbol'), 'crypto')
    stock_recent = format_df_from_file(get_latest_values_from_file('stock.csv', 'stock'), 'stock')

    c_df = pd.merge(df, crypto_recent, how='left', left_on='Assets', right_on='Asset')
    s_df = pd.merge(df, stock_recent, how='left', left_on='Assets', right_on='Asset')

    all = c_df.append(s_df)
    prices = all[pd.notnull(all['price'])]
    pd.options.mode.chained_assignment = None  # disable chaining warning
    prices['value'] = prices['price'] * prices['Quantity']
    return prices
