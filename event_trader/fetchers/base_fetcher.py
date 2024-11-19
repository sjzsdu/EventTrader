import os
import pandas as pd
import time
from datetime import datetime
from event_trader.config import CACHE_PATH, FETCHER_DEBOUNCE_TIME
from event_trader.trading_time_checker import TradingTimeChecker
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from event_trader.stock_data import StockData
    
class BaseFetcher:
    def __init__(self, stock_data: 'StockData', fileName='basic'):
        self.stock_data = stock_data
        self.csv_path = f"{CACHE_PATH}/{self.stock_data.code}/{fileName}.csv"
        self.last_call_time = None

    def fetch_data(self):
        raise NotImplementedError("Subclasses should implement this method.")
    
    def handle_data(self, data: pd.DataFrame):
        pass

    def load_data_from_csv(self):
        if os.path.exists(self.csv_path):
            data = pd.read_csv(self.csv_path)
            self.handle_data(data)
            return data
        return pd.DataFrame()

    def save_data_to_csv(self, data):
        if not data.empty:
            data['date_saved'] = datetime.now().strftime('%Y-%m-%d')
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            data.to_csv(self.csv_path, index=False)

    def is_data_up_to_date(self, data):
        if data.empty:
            return False
        return TradingTimeChecker.compare_with_nearest_trade_date(data['date_saved'].iloc[-1])
    
    
    
    def fetch_and_cache_data(self):
        if not TradingTimeChecker.is_trading_time():
            data = self.load_data_from_csv()
            if not data.empty and self.is_data_up_to_date(data):
                return data
            else:
                data = self.fetch_data()
                self.save_data_to_csv(data)
                return data
        else:
            current_time = time.time()
            if self.last_call_time is not None:
                if current_time - self.last_call_time < FETCHER_DEBOUNCE_TIME:
                    return self.load_data_from_csv()
            data = self.fetch_data()
            self.save_data_to_csv(data)
            self.last_call_time = time.time()
            return data
