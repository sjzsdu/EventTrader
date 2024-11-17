import pandas as pd
from event_trader.config import PRICE_COL, DATE_COL

class DemoAccount:
    def __init__(self, initial_cash=1000000, buy_commission=0.0003, sell_commission=0.0008):
        """
        初始化模拟账户。
        :param initial_cash: 初始资金
        :param buy_commission: 买入佣金比例
        :param sell_commission: 卖出佣金比例
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.shares = 0
        self.buy_commission = buy_commission
        self.sell_commission = sell_commission
        self.transactions = []  # 记录交易记录

    def buy(self, data, index):
        """
        根据策略中的数据行记录进行买入操作。
        :param data: 包含日期、收盘价、开盘价、最低价、最高价、成交量等信息的字典
        """
        price = data.get(PRICE_COL)  # 使用收盘价作为买入价格
        date = data.get(DATE_COL)
        
        if price <= 0:
            raise ValueError("价格必须为正数")
        
        if self.cash > 0:
            max_shares_to_buy = self.cash // price
            shares_to_buy = (max_shares_to_buy // 100) * 100
            fee = self.buy_commission * price * shares_to_buy
            cost = shares_to_buy * price * (1 + self.buy_commission)
            if cost <= self.cash and shares_to_buy > 0:
                self.shares += shares_to_buy
                self.cash -= cost
                self.transactions.append({
                    'date': date,
                    'type': 'buy',
                    'price': price,
                    'shares': shares_to_buy,
                    'cash': self.cash,
                    'fee': fee,
                    'index': index
                })

    def sell(self, data, index):
        """
        根据策略中的数据行记录进行卖出操作。
        :param data: 包含日期、收盘价、开盘价、最低价、最高价、成交量等信息的字典
        """
        price = data.get(PRICE_COL)  # 使用收盘价作为卖出价格
        date = data.get(DATE_COL)
        
        if price <= 0:
            raise ValueError("价格必须为正数")
        
        if self.shares > 0:
            fee = self.sell_commission * price * self.shares
            revenue = self.shares * price * (1 - self.sell_commission)
            self.cash += revenue
            self.transactions.append({
                'date': date,
                'type': 'sell',
                'price': price,
                'shares': self.shares,
                'cash': self.cash,
                'fee': fee,
                'index': index
            })
            self.shares = 0

    def get_profit(self):
        return (self.cash - self.initial_cash) / self.initial_cash * 100

    def get_transactions(self):
        return pd.DataFrame(self.transactions)

    def reset_account(self):
        """
        重置账户到初始状态。
        """
        self.cash = self.initial_cash
        self.shares = 0
        self.transactions.clear()

    def get_account_status(self):
        """
        获取当前账户状态。
        :return: 账户现金、持股和总资产
        """
        total_assets = self.cash + self.shares * self.transactions[-1]['price'] if self.transactions else self.cash
        return {
            'cash': self.cash,
            'shares': self.shares,
            'total_assets': total_assets
        }
