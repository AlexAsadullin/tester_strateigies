from os import close
import plotly.graph_objects as go
import json
import pandas as pd
import numpy as np
#import pandas_ta as ta
import talib


class Deal:
    def __init__(self, entry_price: float | int, entry_time):
        # entry
        #self.entry_trigger = 
        self.entry_time = entry_time
        self.entry_price = entry_price
        # exit
        self.exit_time = 0
        self.exit_price = 0
        # money
        self.profit = 0

class ShortDeal(Deal):
    def close_deal(self, exit_price: float | int, exit_time):
        #self.exit_trigger = 
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.profit = self.entry_price - self.exit_price
        return self.profit
    def count_profit(self, current_price):
        return self.entry_price - current_price

class LongDeal(Deal):
    def close_deal(self, exit_price: float | int, exit_time):
        #self.exit_trigger = 
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.profit = self.exit_price - self.entry_price
        return self.profit
    def count_profit(self, current_price):
        return current_price - self.entry_price


class Tester:
    def __init__(self, prices_df: pd.DataFrame, max_deal_len: int, min_deal_len: int,
                 long_condition, short_condition,
                 start_deposit: float,
                 long_stop_loss_coef: float, long_take_profit_coef: float,
                 short_stop_loss_coef: float, short_take_profit_coef: float):
        # data
        self.prices_df = prices_df
        # deals
        self.current_deal = 0
        self.deal_len_counter = 0
        self.max_deal_len = max_deal_len
        self.min_deal_len = min_deal_len
        self.now_deal_opened = False
        # conditions
        self.long_condition = long_condition
        self.short_condition = short_condition
        # money
        self.money = start_deposit
        self.deals_history = {'Long': [], 'Short': []}
        # exits
        self.long_stop_loss_coef = long_stop_loss_coef # less 1
        self.long_take_profit_coef = long_take_profit_coef # more 1
        self.short_stop_loss_coef = short_stop_loss_coef # more 1
        self.short_take_profit_coef = short_take_profit_coef # less 1
    
    def _check_all_conditions(self, row, i):
        if self.now_deal_opened:
            self._check_if_deal_should_be_closed(row=row, index=i)
        elif self.long_condition:
            self.current_deal = self._open_long_deal(row=row, index=i)
            print('open long index:', i, end=' ')
        elif self.short_condition:
            self.current_deal = self._open_short_deal(row=row, index=i)
            print('open short index:', i, end=' ')

    def _close_any_deal(self, deal, price, i):
        self.deal_len_counter = 0
        self.now_deal_opened = False
        self.money += deal.close_deal(exit_price=price, exit_time=i)
        self.current_deal = 0
    
    def _check_if_deal_should_be_closed(self, row: pd.Series, index):
        deal = self.current_deal
        deal_name = str(type(deal)).lower()
        length_condition_soft = self.deal_len_counter > self.max_deal_len
        length_condition_hard = self.deal_len_counter > self.max_deal_len * 1.2
        if 'long' in deal_name:
            takeprofit_condition = row['Close'] >= deal.entry_price * self.long_take_profit_coef
            stoploss_condition = row['Close'] <= deal.entry_price * self.long_stop_loss_coef
        else:
            takeprofit_condition = row['Close'] <= deal.entry_price * self.short_take_profit_coef
            stoploss_condition = row['Close'] >= deal.entry_price * self.long_stop_loss_coef
        if takeprofit_condition:
            if 'short' in deal_name:
                self.deals_history['Short'].append(deal)
            else:
                self.deals_history['Long'].append(deal)
            self._close_any_deal(deal=deal, price=row['Close'], i=index)
            
            print('close take profit, profit:', deal.profit, 'len:', self.deal_len_counter)
        elif self.deal_len_counter < self.min_deal_len:
            self.deal_len_counter += 1
        elif stoploss_condition:
            if 'short' in deal_name:
                self.deals_history['Short'].append(deal)
            else:
                self.deals_history['Long'].append(deal)
            self._close_any_deal(deal=deal, price=row['Close'], i=index)
            print('close stop loss, profit:', deal.profit, 'len:', self.deal_len_counter, 'index:', row['Unnamed: 0'])
        elif length_condition_soft and deal.count_profit(current_price=row['Close']) > 0:
            self.deal_len_counter = 0
            self.now_deal_opened = False
            self.money += deal.close_deal(exit_price=row['Close'], exit_time=index)
            if 'short' in deal_name:
                self.deals_history['Short'].append(deal)
            else:
                self.deals_history['Long'].append(deal)
            print('close by length, wait till profit:', deal.profit, 'len:', self.deal_len_counter, 'index:', row['Unnamed: 0'])
        elif length_condition_hard:
            self._close_any_deal(deal=deal, price=row['Close'], i=index)
            if 'short' in deal_name:
                self.deals_history['Short'].append(deal)
            else:
                self.deals_history['Long'].append(deal)
            print('close by length, hard cond. profit:', deal.profit, 'len:', self.deal_len_counter, 'index:', row['Unnamed: 0'])
        else:
            self.deal_len_counter += 1

    def _open_long_deal(self, row: pd.Series, index: int):
        deal = LongDeal(entry_price=row['Close'], entry_time=index)
        self.deal_len_counter = 0
        self.now_deal_opened = True
        return deal
    
    def _open_short_deal(self, row: pd.Series, index: int):
        deal = ShortDeal(entry_price=row['Close'], entry_time=index)
        self.deal_len_counter = 0
        self.now_deal_opened = True
        return deal
    
    def delta_hilbert_test(self, hilbert_delta_long, hilbert_delta_short, delta_len: int):
        self.now_deal_opened = False
        self.deals_history = {'Long': [], 'Short': []}
        self.deal_len_counter = 0
        hilbert_queue, volume_queue, close_queue = [], [], []
        self.prices_df['Hilbert'] = talib.HT_DCPHASE(self.prices_df['Close'])
        for i, row in self.prices_df.iloc[0:delta_len].iterrows():
            hilbert_queue.append(row['Hilbert'])
            volume_queue.append(row['Volume'])
            close_queue.append(row['Close'])
        for i, row in self.prices_df.iloc[delta_len:].iterrows():
            hilbert_delta = hilbert_queue[-1] - hilbert_queue[0]
            volume_delta = volume_queue[-1] - volume_queue[0]
            close_delta = close_queue[-1] - volume_queue[0]
            # conditions 
            self.long_condition = hilbert_delta >= hilbert_delta_long
            self.short_condition = hilbert_delta <= hilbert_delta_short
            
            self._check_all_conditions(row=row, i=i)

            hilbert_queue = hilbert_queue[1:]
            hilbert_queue.append(row['Hilbert'])
            volume_queue = volume_queue[1:]
            volume_queue.append(row['Volume'])
            close_queue = close_queue[1:]
            close_queue.append(row['Close'])
        self.now_deal_opened = False
        self.deal_len_counter = 0

    def delta_rsi_test(self, rsi_delta_long, rsi_delta_short, rsi_len: int, delta_len: int):
        self.now_deal_opened = False
        self.deals_history = {'Long': [], 'Short': []}
        self.deal_len_counter = 0
        rsi_queue, volume_queue, close_queue = [], [], []
        self.prices_df['RSI'] = talib.RSI(real=self.prices_df['Close'], timeperiod=rsi_len) 
        for i, row in self.prices_df.iloc[:delta_len].iterrows():
            rsi_queue.append(row['RSI'])
            volume_queue.append(row['Volume'])
            close_queue.append(row['Close'])
        for i, row in self.prices_df.iloc[delta_len:].iterrows():
            rsi_delta = rsi_queue[-1] - rsi_queue[0]
            volume_delta = volume_queue[-1] - volume_queue[0]
            close_delta = close_queue[-1] - volume_queue[0]
            # conditions 
            self.long_condition = rsi_delta >= rsi_delta_long
            self.short_condition = rsi_delta <= rsi_delta_short

            self._check_all_conditions(row=row, i=i)

            rsi_queue = rsi_queue[1:]
            rsi_queue.append(row['RSI'])
            volume_queue = volume_queue[1:]
            volume_queue.append(row['Volume'])
            close_queue = close_queue[1:]
            close_queue.append(row['Close'])
        self.now_deal_opened = False

    def hilbert_classic_test(self, hlbert_long, hilbert_short):
        self.now_deal_opened = False
        self.deals_history = {'Long': [], 'Short': []}
        self.prices_df['Hilbert'] = talib.HT_DCPHASE(self.prices_df['Close'])
        for i, row in self.prices_df.iterrows():
            self.long_condition = row['Hilbert'] < hlbert_long 
            self.short_condition = row['Hilbert'] > hilbert_short
            
            self._check_all_conditions(row=row, i=i)
            
        self.now_deal_opened = False

    def rsi_classic_test(self, rsi_long, rsi_short, rsi_len: int): 
        self.now_deal_opened = False
        self.deals_history = {'Long': [], 'Short': []}
        self.deal_len_counter = 0
        self.prices_df['RSI'] = talib.RSI(real=self.prices_df['Close'], timeperiod=rsi_len)
        for i, row in self.prices_df.iterrows():
            self.long_condition = row['RSI'] < rsi_long 
            self.short_condition = row['RSI'] > rsi_short
            
            self._check_all_conditions(row=row, i=i)
            
        self.now_deal_opened = False
        
        # TODO: покупаем не 1 шт акций а больше - в зависимости от "уверенности"

    def derivative(self, target_col: str = 'Close'):
        der =  np.gradient(self.prices_df[target_col])
        derivative = pd.DataFrame({'Derivative': der}, index=df.index)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self.prices_df.index, y=self.prices_df['Close'],
                                mode='lines', name='Close',
                                line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=self.prices_df.index, y=derivative['Derivative'],
                                mode='lines', name='Derivative',
                                line=dict(color='red')))
        fig.write_html('derivative.html')
        return derivative

    def pos_neg_analysys(self, currency: str = 'rub'):
        pos_deals, neg_deals, zeros, profit_pos, profit_neg = 0, 0, 0, 0, 0
        total = {'Long': {},
                 'Short': {}}
 
        for key in ['Long', 'Short']:
            for deal in self.deals_history[key]:
                if deal.profit > 0:
                    profit_pos += deal.profit
                    pos_deals += 1
                elif deal.profit < 0:
                    profit_neg += deal.profit
                    neg_deals += 1
                else:
                    zeros += 1
            total[key]['positive'] = pos_deals
            total[key]['negative'] = neg_deals
            total[key]['zeros'] = zeros
            total[key]['abs_profit'] = profit_neg + profit_pos
            total[key]['positive_profit'] = profit_pos
            total[key]['negative_profit'] = profit_neg 
        print(f'absolute profit: {total['Long']['abs_profit'] + total['Short']['abs_profit']}')
        return total