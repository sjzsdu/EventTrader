import akshare as ak
from .base_fetcher import BaseFetcher
import pandas as pd
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from event_trader.trading_time_checker import TradingTimeChecker
if TYPE_CHECKING:
    from event_trader.stock_data import StockData
class StockHistFetcher(BaseFetcher):
    def __init__(self, stock_data: 'StockData'):
        super().__init__(stock_data, "stock_hist")
        
    def fetch_data(self):
        start_date_formatted = datetime.strptime(self.stock_data.start_date, '%Y-%m-%d').strftime('%Y%m%d')
        end_date_formatted = datetime.strptime(self.stock_data.end_date, '%Y-%m-%d').strftime('%Y%m%d')
        
        try:
            print("Fetching data from the internet:")
            data = ak.stock_zh_a_hist(
                symbol=self.stock_data.code, 
                period=self.stock_data.period, 
                start_date=start_date_formatted, 
                end_date=end_date_formatted, 
                adjust=self.stock_data.adjust
            )
            if data is None or data.empty:
                raise ValueError("No data returned from the API.")
            return data
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()
        
