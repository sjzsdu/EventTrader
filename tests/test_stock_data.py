import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from event_trader.stock_data import StockData
from event_trader.fetchers.stock_hist_fetcher import StockHistFetcher
from event_trader.fetchers.stock_info_fetcher import StockInfoFetcher

class TestStockData(unittest.TestCase):
    def setUp(self):
        self.code = 'TEST'
        self.start_date = (datetime.now() - timedelta(days=360)).strftime('%Y-%m-%d')
        self.end_date = datetime.now().strftime('%Y-%m-%d')
        self.stock_data = StockData(code=self.code)

    @patch('event_trader.fetchers.stock_hist_fetcher.StockHistFetcher.fetch_and_cache_data')
    @patch('event_trader.fetchers.stock_info_fetcher.StockInfoFetcher.fetch_and_cache_data')
    def test_get_data_stock_hist(self, mock_fetch_info, mock_fetch_hist):
        # Mock the return value of fetch_and_cache_data for stock_hist
        mock_fetch_hist.return_value = {'data': 'historical data'}
        result = self.stock_data.get_data('stock_hist')
        self.assertEqual(result, {'data': 'historical data'})
        mock_fetch_hist.assert_called_once()
        mock_fetch_info.assert_not_called()

    @patch('event_trader.fetchers.stock_hist_fetcher.StockHistFetcher.fetch_and_cache_data')
    @patch('event_trader.fetchers.stock_info_fetcher.StockInfoFetcher.fetch_and_cache_data')
    def test_get_data_stock_info(self, mock_fetch_info, mock_fetch_hist):
        # Mock the return value of fetch_and_cache_data for stock_info
        mock_fetch_info.return_value = {'data': 'info data'}
        result = self.stock_data.get_data('stock_info')
        self.assertEqual(result, {'data': 'info data'})
        mock_fetch_info.assert_called_once()
        mock_fetch_hist.assert_not_called()

    def test_get_data_invalid_type(self):
        with self.assertRaises(ValueError) as context:
            self.stock_data.get_data('invalid_type')
        self.assertEqual(str(context.exception), "Unknown data type: invalid_type")

if __name__ == '__main__':
    unittest.main()
