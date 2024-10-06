import pandas as pd
import plotly.graph_objects as go
import talib
import numpy as np

from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.utils import to_categorical

class AiAnalyzer:
    def __init__(self, dataset: pd.DataFrame):
        self.dataset = dataset
        self.dataset_np = dataset.values

    def create_model(self):
        self.model = Sequential()
    
    def plot_results(self):
        fig = go.Scatter()
        
        
        fig.write_html('my_plot_1.html')


if __name__ == '__main__':
    filepath = 'C:\\trade_strategy1\\data\\prices_SBER_HOUR_2023-01-24.csv'
    df = pd.read_csv(filepath)
    price_analyzer = AiAnalyzer(dataset=df)
    indicator_analyzer = AiAnalyzer(dataset=df)
    matrix = df.values
    print(matrix)
    