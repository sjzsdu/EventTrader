from datetime import datetime, timedelta
from event_trader.fetchers.stock_hist_fetcher import StockHistFetcher
from event_trader.fetchers.stock_info_fetcher import StockInfoFetcher
class StockData:
    # Class variable to cache trade dates
    trade_dates_cache = None

    def __init__(self, code, start_date=None, end_date=None, period="daily", adjust="hfq"):
        self.code = code
        self.period = period
        self.adjust = adjust
        self.start_date = start_date or (datetime.now() - timedelta(days=360)).strftime('%Y-%m-%d')
        self.end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        self.fetches = {
            'stock_hist': StockHistFetcher(self),
            'stock_info': StockInfoFetcher(self),
        }
        
    def get_data(self, data_type):
        if data_type not in self.fetches:
            raise ValueError(f"Unknown data type: {data_type}")
        return self.fetches[data_type].fetch_and_cache_data()
