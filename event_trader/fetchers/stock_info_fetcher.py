import akshare as ak
from .base_fetcher import BaseFetcher
import pandas as pd

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from event_trader.stock_data import StockData
    
class StockInfoFetcher(BaseFetcher):
    def __init__(self, stock_data: 'StockData'):
        super().__init__(stock_data, "stock_info")
        
    def fetch_data(self):
        try:
            print("Fetching data from the internet:")
            data = ak.stock_individual_info_em(
                symbol=self.stock_data.code,
            )
            if data is None or data.empty:
                raise ValueError("No data returned from the API.")
            return data
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()
