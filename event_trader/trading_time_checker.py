import akshare as ak
from datetime import datetime

class TradingTimeChecker:
    trade_dates_cache = None

    @classmethod
    def load_trade_dates(cls):
        """
        加载交易日期并缓存。
        """
        if cls.trade_dates_cache is None:
            trade_dates = ak.tool_trade_date_hist_sina()
            cls.trade_dates_cache = trade_dates['trade_date'].astype(str).values
        return cls.trade_dates_cache

    @classmethod
    def is_trading_time(cls, time_str=None):
        """
        检查给定时间或当前时间是否为交易时间。

        :param time_str: 可选，格式为 '%Y-%m-%d %H:%M:%S' 的时间字符串。
        :return: 如果是交易时间，返回 True，否则返回 False。
        """
        if time_str is not None:
            current_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        else:
            current_time = datetime.now()
        
        today = current_time.strftime('%Y-%m-%d')
        
        trade_dates = cls.load_trade_dates()
        if today not in trade_dates:
            return False
        
        current_hour = current_time.hour
        current_minute = current_time.minute
        trading_hours = (9 <= current_hour < 11) or (current_hour == 11 and current_minute <= 30) or (13 <= current_hour < 15)
        
        return trading_hours

