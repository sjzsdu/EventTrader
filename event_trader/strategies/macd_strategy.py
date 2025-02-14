import pandas as pd
from .base_strategy import BaseStrategy
from china_stock_data import StockData
import mplfinance as mpf
from event_trader.config import PRICE_COL

DEFAULT_PARAMS = {
    'short': 12,
    'long': 26,
    'middle': 9,
}

DEFAULT_PARAMS_RANGE = {
    'short': (5, 30),
    'long': (10, 50),
    'middle': (5, 30),
}

# 新增常量定义
LOOKBACK_PERIOD = 20
BUY_THRESHOLD_CLOSE = 1.05
BUY_THRESHOLD_MEDIUM = 1.1
BUY_THRESHOLD_STRICT = 1.03
SELL_THRESHOLD_CLOSE = 0.95
SELL_THRESHOLD_MEDIUM = 0.9
SELL_THRESHOLD_STRICT = 0.97

class MACDStrategy(BaseStrategy):
    """
    MACD 移动平均线收敛/发散指标（Moving Average Convergence Divergence）
    """
    name = 'macd'
    def __init__(self, stock_data: StockData, params = None, params_range = None):
        _params = params if params is not None else DEFAULT_PARAMS
        _params_range = params_range if params_range is not None else DEFAULT_PARAMS_RANGE
        super().__init__(stock_data, MACDStrategy.name, _params, _params_range, None, ['DIF', 'DEA', 'MACD'])
        
    def calculate_factors(self):
        data = self.data
        # 使用pandas的向量化操作
        data['EMA_short'] = data[PRICE_COL].ewm(span=self.short, adjust=False).mean()
        data['EMA_long'] = data[PRICE_COL].ewm(span=self.long, adjust=False).mean()
        data['DIF'] = data['EMA_short'] - data['EMA_long']
        data['DEA'] = data['DIF'].ewm(span=self.middle, adjust=False).mean()
        data['MACD'] = 2 * (data['DIF'] - data['DEA'])
        
    def validate_parameter(self, parameters):
        if parameters['short'] >= parameters['long']:
            return False
        return True 
    
    def buy_signal(self, row, i) -> bool:
        if i < LOOKBACK_PERIOD or pd.isna(row['DIF']) or pd.isna(row['DEA']):
            return False
            
        last = self.data.iloc[i-1]
        
        # 计算过去LOOKBACK_PERIOD天的最低价
        low_period = self.data[PRICE_COL].iloc[i-LOOKBACK_PERIOD:i+1].min()
        
        # 金叉（DIF 上穿 DEA）且价格接近LOOKBACK_PERIOD天低点
        if (row['DIF'] > row['DEA'] and last['DIF'] <= last['DEA'] and
            row[PRICE_COL] < low_period * BUY_THRESHOLD_CLOSE):
            return True
            
        # MACD 柱状图由负转正且逐渐变长，同时价格处于低位
        if (row['MACD'] > 0 and last['MACD'] <= 0 and row['MACD'] > last['MACD'] and
            row[PRICE_COL] < low_period * BUY_THRESHOLD_MEDIUM):
            return True
            
        # 底背离（价格创新低但 MACD 低点抬高）
        if i > 1:
            prev = self.data.iloc[i-2]
            if (row[PRICE_COL] < last[PRICE_COL] and row['MACD'] > last['MACD'] and
                row[PRICE_COL] < low_period * BUY_THRESHOLD_STRICT):
                return True
                
        return False

    def sell_signal(self, row, i) -> bool:
        if i < LOOKBACK_PERIOD or pd.isna(row['DIF']) or pd.isna(row['DEA']):
            return False
            
        last = self.data.iloc[i-1]
        
        # 计算过去LOOKBACK_PERIOD天的最高价
        high_period = self.data[PRICE_COL].iloc[i-LOOKBACK_PERIOD:i+1].max()
        
        # 死叉（DIF 下穿 DEA）且价格接近LOOKBACK_PERIOD天高点
        if (row['DIF'] < row['DEA'] and last['DIF'] >= last['DEA'] and
            row[PRICE_COL] > high_period * SELL_THRESHOLD_CLOSE):
            return True
            
        # MACD 柱状图由正转负且逐渐变短，同时价格处于高位
        if (row['MACD'] < 0 and last['MACD'] >= 0 and row['MACD'] < last['MACD'] and
            row[PRICE_COL] > high_period * SELL_THRESHOLD_MEDIUM):
            return True
            
        # 顶背离（价格创新高但 MACD 高点降低）
        if i > 1:
            prev = self.data.iloc[i-2]
            if (row[PRICE_COL] > last[PRICE_COL] and row['MACD'] < last['MACD'] and
                row[PRICE_COL] > high_period * SELL_THRESHOLD_STRICT):
                return True
                
        return False
        
    def get_plots(self, data):
        high = data['最高'].max()
        lower = data['最低'].max()
        ratio = (high - lower) / 100
        return [
            mpf.make_addplot(data['DIF'] * ratio, color='blue', width=1, label='DIF'),
            mpf.make_addplot(data['DEA'] * ratio, color='orange', width=1, label='DEA'),
            mpf.make_addplot(data['MACD'] * ratio, color='red', width=1, label='MACD')
        ]
