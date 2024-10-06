import pandas as pd
import plotly.graph_objects as go
import numpy as np
import talib
from scipy.stats import norm

df = pd.read_csv('prices_SBER_HOUR_2023-01-24.csv')
df['RSI'] = talib.RSI(df['Close'], timeperiod=18)
print(df['RSI'].mean(), df['RSI'].min(), df['RSI'].max())

df['delta'] = (df['Close'] - df['Close'].shift(10)) * 10
df['Hilbert'] = talib.HT_DCPHASE(df['Close'])
integer = talib.HT_TRENDMODE(df['Close'])
print(f'integer min {integer.min()} max {integer.max()} mean {integer.mean()}')


fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index,
              y=df['Hilbert'],
               ))
fig.add_trace(go.Scatter(x=df.index,
              y=df['Close'],
               ))


fig.write_html(f'my_chart{df["Hilbert"][500]}.html')
