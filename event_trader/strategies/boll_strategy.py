import pandas as pd
from .base_strategy import BaseStrategy
from china_stock_data import StockData
import mplfinance as mpf
from event_trader.config import PRICE_COL


DEFAULT_PARAMS = {
    'window': 20,
    "std": 2
}

DEFAULT_PARAMS_RANGE = {
    'window': (5, 40),
    "std": (0.5, 3)
}

DEFAULT_PARAMS_STEP = {
    'std': 0.2
}

class BollStrategy(BaseStrategy):
    """
布林带（BOLL）
中轨（中线） ：
通常是一个特定周期的简单移动平均线（SMA），例如20天的移动平均线。
上轨和下轨：
上轨：中轨加上一个设定的倍数的标准差。
下轨：中轨减去同样倍数的标准差。
标准的倍数通常设定为2，这意味着上、下轨分别在平均值的上下两个标准差处。
    """
    name = 'boll'
    def __init__(self, stock_data: StockData, params = None, params_range = None, params_step = None):
        _params = params if params is not None else DEFAULT_PARAMS
        _params_range = params_range if params_range is not None else DEFAULT_PARAMS_RANGE
        _params_step = params_step if params_step is not None else DEFAULT_PARAMS_STEP
        super().__init__(stock_data, BollStrategy.name, _params, _params_range, _params_step, ['moving_avg', 'upper', 'down'])
        
    def calculate_factors(self):
        window = self.parameters['window']
        self.data['moving_avg'] = self.data[PRICE_COL].rolling(window=window).mean()
        # 计算标准差
        self.data['std'] = self.data[PRICE_COL].rolling(window=window).std()

        # 计算布林带上下轨
        self.data['upper'] = self.data['moving_avg'] + (self.data['std'] * self.parameters['std'])
        self.data['down'] = self.data['moving_avg'] - (self.data['std'] * self.parameters['std'])
        
    def buy_signal(self, row, i) -> bool:
        # 确保布林带数据有效
        if i == 0 or pd.isna(row['down']):
            return False
            
        last = self.data.iloc[i-1]
        
        # 价格触及下轨且有反转迹象
        if row[PRICE_COL] <= row['down'] and row[PRICE_COL] > last[PRICE_COL]:
            return True
            
        # 布林带收缩后的向上突破
        if i > 1:
            prev_band_width = self.data.iloc[i-1]['upper'] - self.data.iloc[i-1]['down']
            curr_band_width = row['upper'] - row['down']
            if curr_band_width < prev_band_width * 0.8:  # 布林带收缩
                if row[PRICE_COL] > row['moving_avg'] and row[PRICE_COL] > last[PRICE_COL]:
                    return True
                    
        # 布林带扩张时的趋势延续
        if i > 1:
            prev_band_width = self.data.iloc[i-1]['upper'] - self.data.iloc[i-1]['down']
            curr_band_width = row['upper'] - row['down']
            if curr_band_width > prev_band_width * 1.2:  # 布林带扩张
                if row[PRICE_COL] > row['moving_avg'] and row[PRICE_COL] > last[PRICE_COL]:
                    return True
                    
        return False

    def sell_signal(self, row, i) -> bool:
        if i==0 or pd.isna(row['upper']):
            return False
            
        last = self.data.iloc[i-1]
        
        # 价格触及上轨且有反转迹象
        if row[PRICE_COL] >= row['upper'] and row[PRICE_COL] < last[PRICE_COL]:
            return True
            
        # 布林带收缩后的向下突破
        if i > 1:
            prev_band_width = self.data.iloc[i-1]['upper'] - self.data.iloc[i-1]['down']
            curr_band_width = row['upper'] - row['down']
            if curr_band_width < prev_band_width * 0.8:  # 布林带收缩
                if row[PRICE_COL] < row['moving_avg'] and row[PRICE_COL] < last[PRICE_COL]:
                    return True
                    
        # 布林带扩张时的趋势延续
        if i > 1:
            prev_band_width = self.data.iloc[i-1]['upper'] - self.data.iloc[i-1]['down']
            curr_band_width = row['upper'] - row['down']
            if curr_band_width > prev_band_width * 1.2:  # 布林带扩张
                if row[PRICE_COL] < row['moving_avg'] and row[PRICE_COL] < last[PRICE_COL]:
                    return True
                    
        return False

    def get_plots(self, data):
        return [
            mpf.make_addplot(data['moving_avg'], width=0.8, color='blue', label=f'{self.parameters["window"]}-Day MA'),
            mpf.make_addplot(data['upper'], width=0.8, color='purple', label=f'{self.parameters["window"]}-Upper'),
            mpf.make_addplot(data['down'], width=0.8, color='green', label=f'{self.parameters["window"]}-Down')
        ]
