import unittest
import pandas as pd
from china_stock_data import StockData
from event_trader.strategies.boll_strategy import BollStrategy
from event_trader.strategies.kdj_strategy import KDJStrategy
from event_trader.strategies.ma1_strategy import MA1Strategy
from event_trader.strategies.ma2_strategy import MA2Strategy

class TestStrategies(unittest.TestCase):

    def setUp(self):
        # 创建一个简单的示例数据集
        self.stock_data = StockData('601688')

    def test_boll_strategy(self):
        strategy = BollStrategy(self.stock_data)
        strategy.calculate_factors()
        self.assertIn('moving_avg', strategy.data.columns)
        self.assertIn('upper', strategy.data.columns)
        self.assertIn('down', strategy.data.columns)

    def test_kdj_strategy(self):
        strategy = KDJStrategy(self.stock_data)
        strategy.calculate_factors()
        self.assertIn('K', strategy.data.columns)
        self.assertIn('D', strategy.data.columns)
        self.assertIn('J', strategy.data.columns)

    def test_ma1_strategy(self):
        strategy = MA1Strategy(self.stock_data)
        strategy.calculate_factors()
        self.assertIn('moving_avg', strategy.data.columns)
        self.assertIn('mavg_derivative', strategy.data.columns)

    def test_ma2_strategy(self):
        strategy = MA2Strategy(self.stock_data)
        strategy.calculate_factors()
        self.assertIn('short_mavg', strategy.data.columns)
        self.assertIn('long_mavg', strategy.data.columns)

if __name__ == '__main__':
    unittest.main() 