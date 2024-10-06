import pandas as pd
import os

from collections import defaultdict
# from dotenv import load_dotenv # to load tokens from .env
from datetime import timedelta

from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now


def glass():
    return
    # tinkoff.invest.services.


def quote_to_float(data):
    return float(data.units + data.nano / (10 ** 9))


def writedown_deal():
    pass


def get_by_timeframe(token: str, figi: str, days_back_begin: int, ticker: str, interval: CandleInterval,
                     days_back_end: int = 0, save_table: bool = True) -> pd.DataFrame:
    from_timedelta = now() - timedelta(days=days_back_begin)
    to_timedelta = now() - timedelta(days=days_back_end)
    with Client(token) as client:
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


def get_instruments_figi():
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


'''def post_order():
    from tinkoff.invest import MoneyValue
    from tinkoff.invest.sandbox.client import SandboxClient
    with SandboxClient(os.getenv('TOKEN_SAND')) as client:
        print(client.users.get_accounts())
        print(client.users)
        client.orders.post_order()
'''


def get_massive_data(days_step_back: int,
                     figi: str, days_back_begin: int, ticker: str, interval: CandleInterval, days_back_end: int = 0,
                     save_table: bool = True, ):
    concat_list = []
    for i in range(days_back_end, days_back_begin, days_step_back):
        try:
            concat_list.append(get_by_timeframe(token=TOKEN_SAND, figi=figi,
                                                days_back_begin=i + days_step_back, days_back_end=i,
                                                ticker=ticker, interval=interval, save_table=False))
            print(f'saved {i + days_step_back}')
        except Exception as e:
            print(e)
            break
    df = pd.concat(concat_list, axis=0)
    if save_table:
        interval_name = interval.name.replace('CANDLE_INTERVAL_', '')
        filename = f'prices_massive_{ticker}_{interval_name}_{str(now() - timedelta(days=days_back_begin))[:10]}.csv'
        df.to_csv(f'data\\{filename}')
    return df


def main():
    get_by_timeframe(figi='BBG004730N88', days_back_begin=250, ticker='SBER',
                     interval=CandleInterval.CANDLE_INTERVAL_HOUR)
    # get_instruments_figi()


if __name__ == '__main__':
    TOKEN_SAND = 't.3tvbLKeMoC9j1m1X6tSGFbCMfoQgmFURDmrPIovANrYB_xUGnqjBVm1WyxhL2G9glC5B_4y6LR5NDHkYWu6fEA'
    TOKEN_REAL = 't.L0VPuvAkoSXzTsElwSrS2RM_DZFQgnPdYG7gEDSASeRcPEKaUDsoyTpnhvU_jDg70ysXMjaWOULrnVcvsqENhw'
    testacc_id = '6466677e-38b1-44c1-99c3-1dec7caeff4e'
    tg_api_id = 27652585
    tg_api_hash = '7484bada002fc45758ce353a31ff2da1'
    phone = '+79648395469'
    username = 'AlexAsadullin'

    # load_dotenv() # to load tokens
    get_massive_data(figi='BBG004730N88', days_back_begin=1200,
                     days_back_end=0, days_step_back=50, ticker='MOEX',
                     interval=CandleInterval.CANDLE_INTERVAL_3_MIN)
    
    '''get_by_timeframe(token=TOKEN_SAND,
                     figi='BBG004730N88', days_back_begin=600, ticker='SBER',
                     interval=CandleInterval.CANDLE_INTERVAL_2_MIN, save_table=True)'''
