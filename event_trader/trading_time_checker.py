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

    @classmethod
    def get_nearest_trade_date(cls, date_str=None):
        """
        获取指定日期之前的最近交易日。

        :param date_str: 可选，格式为 '%Y-%m-%d' 的日期字符串。
        :return: 最近的交易日字符串，格式为 '%Y-%m-%d'。
        """
        if date_str is not None:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            date = datetime.now()
        
        trade_dates = cls.load_trade_dates()
        
        # 转换为 datetime 对象列表
        trade_date_objs = [datetime.strptime(d, '%Y-%m-%d') for d in trade_dates]
        
        # 筛选出所有小于或等于指定日期的交易日
        valid_trade_dates = [d for d in trade_date_objs if d <= date]
        
        if not valid_trade_dates:
            raise ValueError("No trading dates found before the given date.")
        
        # 找到距离最近的交易日（即最大的日期）
        nearest_trade_date = max(valid_trade_dates)
        
        return nearest_trade_date.strftime('%Y-%m-%d') 
    
    @classmethod
    def compare_with_nearest_trade_date(cls, compare_date_str, date_str=None):
        """
        比较输入日期和最近的交易日。

        :param compare_date_str: 输入的日期字符串，格式为 '%Y-%m-%d'。
        :return: 如果输入日期小于或等于最近的交易日，返回 False；否则返回 True。
        """
        nearest_trade_date_str = cls.get_nearest_trade_date(date_str)
        nearest_trade_date = datetime.strptime(nearest_trade_date_str, '%Y-%m-%d')
        compare_date = datetime.strptime(compare_date_str, '%Y-%m-%d')
        return compare_date >= nearest_trade_date
