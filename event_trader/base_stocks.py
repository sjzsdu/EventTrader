from abc import ABC, abstractmethod
from china_stock_data import StockMarket
from .utils import is_a_share
import json
import os
from datetime import datetime

class BaseStocks(ABC):
    def __init__(self, symbols=None, index=None, start=None, limit=None, **kwargs):
        self.kwargs = kwargs
        self.trained_stocks = self._load_training_history()
        
        # 只存储股票代码列表，而不是预测实例
        self.symbols = []
        if symbols is not None:
            self.symbols = symbols
        elif index:
            self.stock_market = StockMarket(index)
            codes = self.stock_market['index_codes']
            
            if start is None:
                start = 0
            if limit is None:
                limit = len(codes)

            actual_limit = min(start + limit, len(codes))

            for i in range(start, actual_limit):
                symbol = codes[i]
                if is_a_share(symbol):
                    self.symbols.append(symbol)

    def _get_history_file(self):
        # 为每个预测器类型创建单独的训练历史文件
        predictor_name = self.__class__.__name__
        if not os.path.exists('data/training_history'):
            os.makedirs('data/training_history')
        return f'data/training_history/{predictor_name}_history.json'

    def _load_training_history(self):
        history_file = self._get_history_file()
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_training_history(self):
        history_file = self._get_history_file()
        with open(history_file, 'w') as f:
            json.dump(self.trained_stocks, f)
    
    def train(self, **kwargs):
        res = {}
        length = len(self.symbols)
        
        for i, symbol in enumerate(self.symbols):
            # 检查是否已经训练过
            if symbol in self.trained_stocks:
                print(f"跳过已训练的股票 {symbol}, 上次训练时间: {self.trained_stocks[symbol]}")
                continue
                
            # 创建预测实例
            stock = self.create_prediction_instance(symbol, **self.kwargs)
            
            # 训练
            ret = stock.train(**kwargs)
            res[symbol] = ret
            
            # 记录训练时间
            self.trained_stocks[symbol] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._save_training_history()
            
            # 删除预测实例释放内存
            del stock
            
            print(f"{symbol}训练完成", f"已完成{i+1}/{length}")
            
        return res

    def evaluate(self, **kwargs):
        percents = []
        res = {}
        for symbol in self.symbols:
            stock = self.create_prediction_instance(symbol, **self.kwargs)
            percent = stock.evaluate(**kwargs)
            print(f"{symbol}评估完成", f"准确率: {percent}")
            res[symbol] = percent
            percents.append(percent)
            del stock  # 评估后释放内存
        return res, sum(percents) / len(percents)
            
    def predict(self, **kwargs):
        res = {}
        for symbol in self.symbols:
            stock = self.create_prediction_instance(symbol, **self.kwargs)
            out = stock.predict(**kwargs)
            res[symbol] = out
            del stock  # 预测后释放内存
        return res
    
    def module_file(self): 
        # 创建一个临时实例来获取文件路径
        temp_stock = self.create_prediction_instance(self.symbols[0], **self.kwargs)
        file_path = temp_stock.module_file()
        del temp_stock
        return file_path
    
    @abstractmethod
    def create_prediction_instance(self, symbol, **kwargs):
        """创建预测实例，子类需要实现这个方法"""
        pass
    
    def train_test(self, **kwargs):
        for symbol in self.symbols:
            stock = self.create_prediction_instance(symbol, **self.kwargs)
            stock.train_test(**kwargs)
            del stock  # 训练测试后释放内存
