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

    def buy_signal(self, row, i) -> bool:
        if i == 0 or pd.isna(row['K']) or pd.isna(row['D']) or pd.isna(row['J']):
            return False
            
        last = self.data.iloc[i-1]
        
        # 金叉（K线由下向上穿过D线）
        if row['K'] > row['D'] and last['K'] <= last['D']:
            return True
            
        # 超卖区域（J值小于0或K值在20以下）
        if row['J'] < 0 or row['K'] < 20:
            return True
            
        # 底背离（价格创新低但 KDJ 低点抬高）
        if i > 1:
            prev = self.data.iloc[i-2]
            if row['收盘'] < last['收盘'] and row['K'] > last['K']:
                return True
                
        return False

    def sell_signal(self, row, i) -> bool:
        if i == 0 or pd.isna(row['K']) or pd.isna(row['D']) or pd.isna(row['J']):
            return False
            
        last = self.data.iloc[i-1]
        
        # 死叉（K线由上向下穿过D线）
        if row['K'] < row['D'] and last['K'] >= last['D']:
            return True
            
        # 超买区域（J值大于100或K值在80以上）
        if row['J'] > 100 or row['K'] > 80:
            return True
            
        # 顶背离（价格创新高但 KDJ 高点降低）
        if i > 1:
            prev = self.data.iloc[i-2]
            if row['收盘'] > last['收盘'] and row['K'] < last['K']:
                return True
                
        return False
        
    def get_plots(self, data):
        high = data['最高'].max()
        lower = data['最低'].max()
        ratio = (high - lower) / 100
        return [
            mpf.make_addplot(data['K'] * ratio, color='blue', width=1, label='K'),
            mpf.make_addplot(data['D'] * ratio, color='orange', width=1, label='D'),
            mpf.make_addplot(data['J'] * ratio, color='red', width=1, label='J')
        ]
