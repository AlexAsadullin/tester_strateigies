from testing_setup import *

df = pd.read_csv('data/prices_massive_MOEX_3_MIN_2021-06-15.csv')

df = df.dropna()
print(df.head())

tester = Tester(prices_df=df, min_deal_len=3, max_deal_len=3480, start_deposit=1000,
                   long_condition=0, short_condition=0,
                   long_stop_loss_coef=0.8, long_take_profit_coef=1.5,
                   short_stop_loss_coef=1.2, short_take_profit_coef=0.5)

'''derivative_df = tester.derivative(target_col='Close')
derivative_df.to_csv('derivative.csv')'''
df['RSI'] = talib.RSI(real=df['Close'], timeperiod=60)
print(tester.prices_df[tester.prices_df['RSI'] > 45])
df = tester.prices_df
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['Close'],
                                 mode='lines', name='Close',
                                 line=dict(color='blue')))
fig.add_trace(go.Scatter(x=df.index, y=df['RSI'],
                                 mode='lines', name='Close',
                                 line=dict(color='blue')))
#fig.show()
#tester.delta_hilbert_test(hilbert_delta_long=-66, hilbert_delta_short=66, delta_len=12)
tester.rsi_classic_test(rsi_long=39, rsi_short=80, rsi_len=35)
print(tester.pos_neg_analysys())
