import pandas as pd
from event_trader.config import PRICE_COL, DATE_COL, SYMBOL_COL

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
        self.holdings = {}  # 持有股票及其数量
        self.buy_commission = buy_commission
        self.sell_commission = sell_commission
        self.transactions = []  # 记录交易记录

    def buy(self, data, index, position=1.0):
        """
        根据策略中的数据行记录进行买入操作。
        :param data: 包含日期、收盘价、开盘价、最低价、最高价、成交量等信息的字典
        :param index: 当前交易数据的索引
        :param position: 买入仓位比例，默认为1.0（全仓）
        """
        symbol = data.get(SYMBOL_COL)
        price = data.get(PRICE_COL)
        date = data.get(DATE_COL)
        
        if price <= 0:
            raise ValueError("价格必须为正数")
        
        if self.cash > 0 and 0 < position <= 1:
            max_shares_to_buy = (self.cash * position) // price
            shares_to_buy = (max_shares_to_buy // 100) * 100
            fee = self.buy_commission * price * shares_to_buy
            cost = shares_to_buy * price * (1 + self.buy_commission)
            if cost <= self.cash and shares_to_buy > 0:
                self.holdings[symbol] = self.holdings.get(symbol, 0) + shares_to_buy
                self.cash -= cost
                self.transactions.append({
                    'date': date,
                    'type': 'buy',
                    'symbol': symbol,
                    'price': price,
                    'shares': shares_to_buy,
                    'cash': self.cash,
                    'fee': fee,
                    'index': index
                })

    def sell(self, data, index, position=1.0):
        """
        根据策略中的数据行记录进行卖出操作。
        :param data: 包含日期、收盘价、开盘价、最低价、最高价、成交量等信息的字典
        :param index: 当前交易数据的索引
        :param position: 卖出仓位比例，默认为1.0（全仓）
        """
        symbol = data.get(SYMBOL_COL)
        price = data.get(PRICE_COL)
        date = data.get(DATE_COL)
        
        if price <= 0:
            raise ValueError("价格必须为正数")
        
        if symbol in self.holdings and self.holdings[symbol] > 0 and 0 < position <= 1:
            shares_to_sell = int(self.holdings[symbol] * position)
            fee = self.sell_commission * price * shares_to_sell
            revenue = shares_to_sell * price * (1 - self.sell_commission)
            self.cash += revenue
            self.holdings[symbol] -= shares_to_sell
            self.transactions.append({
                'date': date,
                'type': 'sell',
                'symbol': symbol,
                'price': price,
                'shares': shares_to_sell,
                'cash': self.cash,
                'fee': fee,
                'index': index
            })

    def get_profit(self):
        return (self.cash - self.initial_cash) / self.initial_cash * 100

    def get_transactions(self):
        return pd.DataFrame(self.transactions)

    def reset_account(self):
        """
        重置账户到初始状态。
        """
        self.cash = self.initial_cash
        self.holdings.clear()
        self.transactions.clear()

    def get_account_status(self):
        """
        获取当前账户状态。
        :return: 账户现金、持股和总资产
        """
        total_assets = self.cash
        for symbol, shares in self.holdings.items():
            if shares > 0:
                # 假设使用最后一笔交易价格计算当前持股市值
                last_price = [t['price'] for t in self.transactions if t['symbol'] == symbol][-1]
                total_assets += shares * last_price
        return {
            'cash': self.cash,
            'holdings': self.holdings,
            'total_assets': total_assets
        }
