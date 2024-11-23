from datetime import datetime, timedelta
from event_trader.config import HISTORY_DAYS
from event_trader.fetchers import IndexComponentsFetcher, IndexListFetcher
class StockMarket:

    def __init__(self, symbol):
        self.symbol = symbol
        self.fetches = {
            'index_components': IndexComponentsFetcher(self),
            'index_list': IndexListFetcher(self),
        }
        
    def get_data(self, data_type: str):
        if data_type not in self.fetches:
            raise ValueError(f"Unknown data type: {data_type}")
        return self.fetches[data_type].fetch_and_cache_data()
    
    def __getattr__(self, name: str):
        if (name == 'index_components'):
            return self.get_data('index_components')
        if (name == 'index_list'):
            return self.get_data('index_list')
        return f'{name} is not found'
    
    
    def __getitem__(self, key: str):
        fetchers = [self.fetches['index_components']]
        for fetcher in fetchers:
            try:
                return fetcher[key.strip()]
            except KeyError:
                continue 
        raise KeyError(f"Key '{key}' not found in any fetcher")

