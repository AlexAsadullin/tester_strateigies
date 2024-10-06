from curses import window
import pandas as pd
import numpy as np
import talib 
import scipy.stats as stats
#import pandas_ta as pdta

import pybit
from requests import session

import time 
import math

import plotly.graph_objects as go
from pybit import unified_trading


api_key = 'gHhfegSB4wvtuc4qZM'
api_secret = '7ji3jSXmW3JB6zcCtayf8I8Fz1Ao2eXxPl4x'

import ta

client = unified_trading.HTTP(
    api_key=api_key,
    api_secret=api_secret
)

# Config:
take_profit_coef = 0.012  # Take Profit +1.2%
stop_loss_coef = 0.009  # Stop Loss -0.9%
timeframe = 15  # 15 minutes
mode = 1  # 1 - Isolated, 0 - Cross
leverage = 10
qty = 50    # Amount of USDT for one order


# Getting balance on Bybit Derivatrives Asset (in USDT)
def get_balance():
    try:
        response = client.get_wallet_balance(accountType="CONTRACT", coin="USDT")['result']['list'][0]['coin'][0]['walletBalance']
        response = float(response)
        return response
    except Exception as err:
        print(err)

print(f'Your balance: {get_balance()} USDT')


# Getting all available symbols from Derivatives market (like 'BTCUSDT', 'XRPUSDT', etc)
def get_tickers():
    try:
        response = client.get_tickers(category="linear")['result']['list']
        symbols = []
        for elem in response:
            if 'USDT' in elem['symbol'] and not 'USDC' in elem['symbol']:
                symbols.append(elem['symbol'])
        return symbols
    except Exception as err:
        print(err)


# Klines is the candles of some symbol (up to 1500 candles). Dataframe, last elem has [-1] index
def get_candles(symbol):
    try:
        response = client.get_kline(
            category='linear',
            symbol=symbol,
            interval=timeframe,
            limit=500
        )['result']['list']
        response = pd.DataFrame(response)
        response.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover']
        response = response.set_index('Time')
        response = response.astype(float)
        response = response[::-1]
        return response
    except Exception as err:
        print(err)


# Getting your current positions. It returns symbols list with opened positions
def get_positions():
    try:
        response = client.get_positions(
            category='linear',
            settleCoin='USDT'
        )['result']['list']
        pos = []
        for elem in response:
            pos.append(elem['symbol'])
        return pos
    except Exception as err:
        print(err)


# Getting last 50 PnL. I used it to check strategies performance
def get_pnl():
    try:
        response = client.get_closed_pnl(category="linear", limit=50)['result']['list']
        pnl = 0
        for elem in response:
            pnl += float(elem['closedPnl'])
        return pnl
    except Exception as err:
        print(err)


# Changing mode and leverage: 
def set_mode(symbol):
    try:
        response = client.switch_margin_mode(
            category='linear',
            symbol=symbol,
            tradeMode=mode,
            buyLeverage=leverage,
            sellLeverage=leverage
        )
        print(response)
    except Exception as err:
        print(err)


# Getting number of decimal digits for price and qty
def get_precisions(symbol):
    try:
        response = client.get_instruments_info(
            category='linear',
            symbol=symbol
        )['result']['list'][0]
        price = response['priceFilter']['tickSize']
        if '.' in price:
            price = len(price.split('.')[1])
        else:
            price = 0
        qty = response['lotSizeFilter']['qtyStep']
        if '.' in qty:
            qty = len(qty.split('.')[1])
        else:
            qty = 0

        return price, qty
    except Exception as err:
        print(err)


# Placing order with Market price. Placing TP and SL as well
def place_order_market(symbol, side):
    price_precision = get_precisions(symbol)[0]
    qty_precision = get_precisions(symbol)[1]
    mark_price = client.get_tickers(
        category='linear',
        symbol=symbol
    )['result']['list'][0]['markPrice']
    mark_price = float(mark_price)
    print(f'Placing {side} order for {symbol}. Mark price: {mark_price}')
    order_qty = round(qty/mark_price, qty_precision)
    time.sleep(2)
    if side == 'buy':
        try:
            tp_price = round(mark_price + mark_price * take_profit_coef, price_precision)
            sl_price = round(mark_price - mark_price * stop_loss_coef, price_precision)
            response = client.place_order(
                category='linear',
                symbol=symbol,
                side='Buy',
                orderType='Market',
                qty=order_qty,
                takeProfit=tp_price,
                stopLoss=sl_price,
                tpTriggerBy='Market',
                slTriggerBy='Market'
            )
            print(response)
        except Exception as err:
            print(err)

    if side == 'sell':
        try:
            tp_price = round(mark_price - mark_price * take_profit_coef, price_precision)
            sl_price = round(mark_price + mark_price * stop_loss_coef, price_precision)
            response = client.place_order(
                category='linear',
                symbol=symbol,
                side='Sell',
                orderType='Market',
                qty=order_qty,
                takeProfit=tp_price,
                stopLoss=sl_price,
                tpTriggerBy='Market',
                slTriggerBy='Market'
            )
            print(response)
        except Exception as err:
            print(err)


# Some RSI strategy. Make your own using this example
def rsi_signal(symbol):
    candle = get_candles(symbol)
    ema = ta.trend.ema_indicator(candle.Close, window=200)
    rsi = ta.momentum.RSIIndicator(candle.Close).rsi(window=180)
    if rsi.iloc[-3] < 30 and rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30:
        return 'up'
    if rsi.iloc[-3] > 70 and rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70:
        return 'down'
    else:
        return 'none'

# William %R signal
def williamsR(symbol):
    candle = get_candles(symbol)
    w = ta.momentum.WilliamsRIndicator(candle.High, candle.Low, candle.Close, lbp=24).williams_r()
    ema_w = ta.trend.ema_indicator(w, window=24)
    if w.iloc[-1] < -99.5:
        return 'up'
    elif w.iloc[-1] > -0.5:
        return 'down'
    elif w.iloc[-1] < -75 and w.iloc[-2] < -75 and w.iloc[-2] < ema_w.iloc[-2] and w.iloc[-1] > ema_w.iloc[-1]:
        return 'up'
    elif w.iloc[-1] > -25 and w.iloc[-2] > -25 and w.iloc[-2] > ema_w.iloc[-2] and w.iloc[-1] < ema_w.iloc[-1]:
        return 'down'
    else:
        return 'none'


if __name__ == '__main__':
    max_pos = 50    # Max current orders
    symbols = get_tickers() # getting all symbols from the Bybit Derivatives

    # Infinite loop
    while True:
        balance = get_balance()
        if balance is None:
            print('Cant connect to API')
            break
        if balance is not None:
            balance = float(balance)
            print(f'Balance: {balance}')
            position = get_positions()
            print(f'You have {len(position)} positions: {position}')

            if len(position) < max_pos:
                for elem in symbols:
                    position = get_positions()
                    if len(position) >= max_pos:
                        break
                    # Signal to buy or sell
                    signal = rsi_signal(elem)
                    if signal == 'up':
                        print(f'Found BUY signal for {elem}')
                        set_mode(elem)
                        time.sleep(2)
                        place_order_market(elem, 'buy')
                        time.sleep(5)
                    if signal == 'down':
                        print(f'Found SELL signal for {elem}')
                        set_mode(elem)
                        time.sleep(2)
                        place_order_market(elem, 'sell')
                        time.sleep(5)
        print('Waiting 1 min')
        time.sleep(60)
        