# for python
import json
from matplotlib import category
import pandas as pd
import os
import time
from collections import defaultdict
from datetime import timedelta
from dotenv import load_dotenv
# for tinkoff
from requests import session
from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now
# for bybit
from pybit.unified_trading import HTTP

def quote_to_float(data):
    return float(data.units + data.nano / (10 ** 9))

def get_tinkoff_by_timeframe_figi(figi: str, days_back_begin: int, ticker: str, interval: CandleInterval,
                     days_back_end: int = 0, save_table: bool = True) -> pd.DataFrame:
    TOKEN_SAND = os.getenv("TOKEN_SAND")
    from_timedelta = now() - timedelta(days=days_back_begin)
    to_timedelta = now() - timedelta(days=days_back_end)
    with Client(TOKEN_SAND) as client:
        data_for_df = defaultdict(list)
        for candle in client.get_all_candles(
                figi=figi,
                from_=from_timedelta,
                to=to_timedelta,
                interval=interval):
            open_price = quote_to_float(candle.open)
            close_price = quote_to_float(candle.close)
            high_price = quote_to_float(candle.high)
            low_price = quote_to_float(candle.low)
            volume = candle.volume
            is_growing = open_price < close_price

            data_for_df['Open'].append(open_price)
            data_for_df['Close'].append(close_price)
            data_for_df['High'].append(high_price)
            data_for_df['Low'].append(low_price)
            data_for_df['Volume'].append(volume)
            data_for_df['Time'].append(candle.time.strftime('%Y-%m-%d %H:%M'))
            data_for_df['IsGrowing'].append(is_growing)
            data_for_df['AvgOpenClose'].append(abs(open_price - close_price))
            data_for_df['DiffOpenClose'].append(abs(open_price - close_price))
            data_for_df['DiffHighLow'].append(abs(high_price - low_price))
        df = pd.DataFrame(data_for_df)
        if save_table:
            interval_name = interval.name.replace("CANDLE_INTERVAL_", "")
            filename = f'''prices_{ticker}_{interval_name}_{str(from_timedelta)[:10]}.csv'''
            df.to_csv(f"data\\{filename}")
        return df


def get_tinkoff_figi():
    from tinkoff.invest import Client
    from tinkoff.invest.services import InstrumentsService, MarketDataService

    with Client(os.getenv('TOKEN_SAND')) as client:
        instruments: InstrumentsService = client.instruments
        market_data: MarketDataService = client.market_data
        l = []
        for method in ['shares', 'bonds', 'etfs']:
            for item in getattr(instruments, method)().instruments:
                l.append({
                    'Ticker': item.ticker,
                    'Figi': item.figi,
                    'Type': method,
                    'Name': item.name,
                })
        df = pd.DataFrame(l)
        df.to_csv('data\\tickers_figi.csv')
        print('data is saved')
        return df


def get_massive_tinkoff_by_timeframe_figi(step_back_days: int,
                     figi: str, begin_days_back: int, ticker: str, interval: CandleInterval, end_days_back: int = 0,
                     save_table: bool = True, ):
    concat_list = []
    for i in range(end_days_back, begin_days_back, step_back_days):
        try:
            concat_list.append(get_tinkoff_by_timeframe_figi(figi=figi,
                                                days_back_begin=i + step_back_days, days_back_end=i,
                                                ticker=ticker, interval=interval, save_table=False))
            print(f'saved {i + step_back_days}')
        except Exception as e:
            print(e)
            break
    df = pd.concat(concat_list, axis=0)
    if save_table:
        interval_name = interval.name.replace('CANDLE_INTERVAL_', '')
        filename = f'prices_massive_{ticker}_{interval_name}_{str(now() - timedelta(days=begin_days_back))[:10]}.csv'
        df.to_csv(f'data\\{filename}')
    return df


def get_bybit_data(limit: int, symbol: str, category: str,):
    # testnet - песочница
    # max_retries = 
    session = HTTP(
    api_key="",
    api_secret="",
    )
    data = session.get_orderbook(category=category, # linear
                                 symbol=symbol,
                                 limit=limit)
    return data

def get_bybit_historical_data(limit: int, symbol: str, category: str,):
    session = HTTP(
    api_key="",
    api_secret="",
    )
    data = session.get_public_trade_history(
    category=category,  # spot
    symbol=symbol,
    limit=limit,
    )
    return data

# a = ask (спрос), b = bid (предложение)
if __name__ == '__main__':
    load_dotenv()
    history = []
    # seconds_range = 60 * 60 * 3 # 3 hours
    seconds_range = 60 # 1 min
    for i in range(seconds_range):
        history.append(get_bybit_data(symbol='BTCUSDT',
                                      limit=10,
                                      category='linear'))
        print(f'iteration {i}')
        time.sleep(1)

    with open('BTCUSDT.json', 'w') as f:
        f.write(json.dumps(history))
    print('data saved')