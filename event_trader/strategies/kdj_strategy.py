import pandas as pd
from .base_strategy import BaseStrategy
from china_stock_data import StockData
import mplfinance as mpf


DEFAULT_PARAMS = {
    'n': 9,
    'm1': 3,
    'm2': 3,
}

DEFAULT_PARAMS_RANGE = {
    'n': (5, 20),
    'm1': (2, 20),
    'm2': (2, 20),
}


class KDJStrategy(BaseStrategy):
    """
KDJ指标, 随机振荡器
    """
    name = 'kdj'
    def __init__(self, stock_data: StockData, params = None, params_range = None):
        _params = params if params is not None else DEFAULT_PARAMS
        _params_range = params_range if params_range is not None else DEFAULT_PARAMS_RANGE
        super().__init__(stock_data, KDJStrategy.name, _params, _params_range, None, ['K', 'D', 'J'])
        
    def calculate_factors(self):
        data = self.data
        # 计算最低价和最高价的滚动窗口
        data['L_n'] = data['最低'].rolling(window=self.n, min_periods=1).min()
        data['H_n'] = data['最高'].rolling(window=self.n, min_periods=1).max()

        # 计算RSV
        data['RSV'] = (data['收盘'] - data['L_n']) / (data['H_n'] - data['L_n']) * 100

        # 初始化K值和D值为浮点型
        data['K'] = 50.0
        data['D'] = 50.0

        # 计算K值和D值
        for i in range(1, len(data)):
            k_value = ((self.m1 - 1) / self.m1) * data.loc[i-1, 'K'] + (1 / self.m1) * data.loc[i, 'RSV']
            d_value = ((self.m2 - 1) / self.m2) * data.loc[i-1, 'D'] + (1 / self.m2) * k_value
            
            # 确保赋值时为浮点型
            data.loc[i, 'K'] = float(k_value)
            data.loc[i, 'D'] = float(d_value)

        # 计算J值
        data['J'] = 3.0 * data['K'] - 2.0 * data['D']

    # FILEPATH: /Users/juzhongsun/Codes/pythons/event_trader/event_trader/strategies/kdj_strategy.py

    def buy_signal(self, row, i) -> bool:
        if i < 3 or pd.isna(row['K']) or pd.isna(row['D']) or pd.isna(row['J']):
            return False
        
        last = self.data.iloc[i-1]
        prev = self.data.iloc[i-2]
        prev_prev = self.data.iloc[i-3]
        
        # 金叉确认（连续两天K线上穿D线）
        golden_cross = (row['K'] > row['D'] and last['K'] > last['D'] and 
                        prev['K'] <= prev['D'] and prev_prev['K'] <= prev_prev['D'])
        
        # 超卖区域反转（J值从低于0反弹至高于0，且K值小于30）
        oversold_reversal = (row['J'] > 0 and last['J'] <= 0 and row['K'] < 30)
        
        # 强势底背离（价格创新低但KDJ指标连续两天走高）
        strong_divergence = (row['收盘'] < last['收盘'] < prev['收盘'] and 
                            row['K'] > last['K'] > prev['K'] and row['K'] < 30)
        
        return golden_cross or oversold_reversal or strong_divergence

    def sell_signal(self, row, i) -> bool:
        if i < 3 or pd.isna(row['K']) or pd.isna(row['D']) or pd.isna(row['J']):
            return False
        
        last = self.data.iloc[i-1]
        prev = self.data.iloc[i-2]
        prev_prev = self.data.iloc[i-3]
        
        # 死叉确认（连续两天K线下穿D线）
        death_cross = (row['K'] < row['D'] and last['K'] < last['D'] and 
                    prev['K'] >= prev['D'] and prev_prev['K'] >= prev_prev['D'])
        
        # 超买区域反转（J值从高于100回落至低于100，且K值大于70）
        overbought_reversal = (row['J'] < 100 and last['J'] >= 100 and row['K'] > 70)
        
        # 强势顶背离（价格创新高但KDJ指标连续两天走低）
        strong_divergence = (row['收盘'] > last['收盘'] > prev['收盘'] and 
                            row['K'] < last['K'] < prev['K'] and row['K'] > 70)
        
        return death_cross or overbought_reversal or strong_divergence
        
    def get_plots(self, data):
        high = data['最高'].max()
        lower = data['最低'].max()
        ratio = (high - lower) / 100
        return [
            mpf.make_addplot(data['K'] * ratio, color='blue', width=1, label='K'),
            mpf.make_addplot(data['D'] * ratio, color='orange', width=1, label='D'),
            mpf.make_addplot(data['J'] * ratio, color='red', width=1, label='J')
        ]
