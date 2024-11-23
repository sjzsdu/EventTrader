import akshare as ak
from .base_fetcher import BaseFetcher
import pandas as pd
from typing import Any

class IndexListFetcher(BaseFetcher):
    def __init__(self, stock_market: Any):
        self.stock_market = stock_market
        super().__init__('index-list', main_path='index', file_name="index-list")
        
    def fetch_data(self):
        try:
            print("Fetching index list data!")
            data = ak.index_stock_info()
            if data is None or data.empty:
                raise ValueError("No data returned from the API.")
            return data
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()
