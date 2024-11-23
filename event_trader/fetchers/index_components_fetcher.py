import akshare as ak
from .base_fetcher import BaseFetcher
import pandas as pd
from typing import Any

class IndexComponentsFetcher(BaseFetcher):
    def __init__(self, stock_data: Any):
        super().__init__(stock_data.symbol, main_path='index', file_name="index_components")
        
    def fetch_data(self):
        try:
            print("Fetching index components data!")
            data = ak.index_stock_cons_csindex(self.symbol)
            if data is None or data.empty:
                raise ValueError("No data returned from the API.")
            return data
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()
        
    def fetch_and_cache_data(self):
        data = super().fetch_and_cache_data()
        data['成分券代码'] = data['成分券代码'].astype(str).apply(lambda x: x.zfill(6))
        return data

    def __getitem__(self, key):
        data = self.fetch_and_cache_data()
        try:
            if key == 'index_market':
                return data['交易所'].value_counts()
            elif key == 'index_codes':
                return data['成分券代码'].unique()
            elif key == 'index_names':
                return data['成分券名称'].unique()
            elif key == 'index_codes_names':
                return data['成分券代码', '成分券名称']
            else:
                raise KeyError(f"Key '{key}' not found in DataFrame")
        except KeyError:
            raise KeyError(f"Key '{key}' not found in DataFrame")