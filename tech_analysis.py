import pandas as pd
import pandas_ta as ta
from pylab import *
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

TICKER = 'SBER'
NAME = f'prices_massive_{TICKER}_3_MIN_2008-04-03.csv'


def find_minmaxes(df: pd.DataFrame, n_range=100, ticker='unknown', visualise=False):
    from scipy.signal import argrelextrema
    df['Max'] = df.iloc[argrelextrema(df['Close'].values, np.greater_equal,
                                      order=n_range)[0]]['Close']
    df['Min'] = df.iloc[argrelextrema(df['Close'].values, np.less_equal,
                                      order=n_range)[0]]['Close']
    if visualise:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'],
                                 mode='lines', name='Close',
                                 line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=df.index, y=df['Min'],
                                 mode='markers', name='Min',
                                 marker=dict(color='red', size=8)))
        fig.add_trace(go.Scatter(x=df.index, y=df['Max'],
                                 mode='markers', name='Max',
                                 marker=dict(color='green', size=8)))
        fig.update_layout(title="Mins & Maxs",
                          xaxis_title="time", yaxis_title=f"{ticker} price",
                          showlegend=True)
        fig.write_html(f"charts\\MinMaxes_{ticker}.html")
    return df


def calculate_rsi(df: pd.DataFrame, period: int, ticker='unknown', visualise=False):
    df['RSI'] = ta.rsi(df['Close'])

    if visualise:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02)
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'],
                                 mode='lines', name='Close',
                                 line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'],
                                 mode='lines', name='RSI',
                                 line=dict(color='red')), row=2, col=1)
        fig.add_shape(type="line",
                      x0=df.index[0], x1=df.index[-1], y0=30, y1=30,
                      line=dict(color="grey", width=2),
                      name="RSI = 30", row=2, col=1)
        fig.add_shape(type="line",
                      x0=df.index[0], x1=df.index[-1], y0=70, y1=70,
                      line=dict(color="blue", width=2),
                      name="RSI = 70", row=2, col=1)
        fig.update_layout(title="Цена и RSI",
                          xaxis_title="time", yaxis_title="Цена",
                          yaxis2_title="RSI", showlegend=True,
                          height=600)
        fig.write_html(f"charts\\RSI_{ticker}.html")
    return df


def alligator_teeth(df, len_short=3, len_mid=5, len_long=8, ticker='unknown', visualise=False):
    df["AlligatorShort"] = ta.sma(df.Close, length=len_short).shift(3)  # 3
    df["AlligatorMid"] = ta.sma(df.Close, length=len_mid).shift(5)  # 5
    df["AlligatorLong"] = ta.sma(df.Close, length=len_long).shift(8)  # 8
    df["AlligatorSmaDiff"] = df["AlligatorShort"] - df["AlligatorLong"]
    if visualise:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02)
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'],
                                 mode='lines', name='Close',
                                 line=dict(color='blue')
                                 ), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['AlligatorShort'],
                                 mode='lines', name='AlligatorShort',
                                 line=dict(color='green')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['AlligatorMid'],
                                 mode='lines', name='AlligatorMid',
                                 line=dict(color='yellow')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['AlligatorLong'],
                                 mode='lines', name='AlligatorLong',
                                 line=dict(color='red')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['AlligatorSmaDiff'],
                                 mode='lines', name='AlligatorSmaDiff',
                                 line=dict(color='red')), row=2, col=1)
        fig.update_layout(title="Цена и Alligator",
                          xaxis_title="time", yaxis_title="Цена",
                          yaxis2_title="AlligatorSmaDiff", showlegend=True,
                          height=600)
        fig.write_html(f"charts\\Alligator_{ticker}.html")
    return df


def calculate_ema(df: pd.DataFrame, ticker='unknown', length=200, visualise=False):
    df[f"EMA{length}"] = ta.ema(df.Close, length=length)

    if visualise:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'],
                                 mode='lines', name='Close',
                                 line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=df.index, y=df[f"EMA{length}"],
                                 mode='lines', name=f"EMA{length}",
                                 marker=dict(color='red', size=8)))
        fig.write_html(f"charts\\EMA_{ticker}_{length}.html")
    return df


def dynamic_SnR(df: pd.DataFrame, feature='RSI', visualise=False):
    growth_coeffs = np.log(df['Close'] / df['Close'].shift(1))
    df['Growth_coeff'] = growth_coeffs
    # growth_coeffs.dropna(inplace=True)
    regression = np.polyfit(df['Close'], df[feature], deg=1)
    '''growth_coeffs = pd.Series(growth_coeffs)
    print(growth_coeffs.corr(df['Close']), end='\n\n')'''
    return df


def main(ticker):
    df = pd.read_csv(f'{NAME}', index_col=0)
    df = find_minmaxes(df=df, ticker='', visualise=True, n_range=1500)
    #del df['Unnamed: 0']
    df.to_csv(f'minmaxes_mass.csv')


if __name__ == '__main__':
    main(ticker=TICKER)
