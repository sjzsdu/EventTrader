# 股票交易策略系统

## 项目意图

本项目旨在提供一个灵活的股票交易策略框架，允许用户通过多种策略对股票进行分析和交易。该系统支持多种技术指标和策略，用户可以根据自己的需求进行优化和调整。

## 项目特点

- **多策略支持**：内置多种交易策略，包括布林带、KDJ、MACD、移动平均等，用户可以根据市场情况选择合适的策略。
- **灵活的参数优化**：支持对策略参数进行优化，帮助用户找到最佳的交易参数。
- **模拟交易账户**：提供模拟账户功能，用户可以在不承担风险的情况下测试策略的有效性。
- **数据可视化**：使用mplfinance库进行数据可视化，帮助用户更直观地理解市场动态。
- **多线程处理**：使用线程池来提高数据处理效率，支持并发获取多个股票的数据。

## 功能概述

- **股票数据管理**：通过`StocksManager`类管理股票数据，支持从不同的股票市场获取数据。
- **策略实现**：每种策略都继承自`BaseStrategy`类，用户可以自定义自己的策略。
- **账户管理**：`DemoAccount`类用于管理模拟交易账户，包括买入、卖出、计算利润等功能。
- **结果展示**：提供结果展示功能，用户可以查看每种策略的表现和相关指标。

## 安装与使用

### 安装依赖

在使用本项目之前，请确保安装了以下依赖库：

```bash
pip install event_trader
```

### 使用步骤
1. 分析个股的各选股策略的表现
```python
from event_trader.strategies import  MA2Strategy, KDJStrategy, MA1Strategy, BollStrategy, MACDStrategy, PriceDeviationStrategy
from china_stock_data import StockData
from event_trader import friendly_number
stock = StockData('601688')
print(f"{stock['股票简称']}, 市值:{friendly_number(stock['总市值'])}")

for strategy in [MA2Strategy, KDJStrategy, MA1Strategy, BollStrategy, MACDStrategy, PriceDeviationStrategy]:
    st = strategy(stock)
    st.show(transaction = False, days = 30)
```

或者输出各个策略的交易信息
```python
for strategy in [MA2Strategy, KDJStrategy, MA1Strategy, BollStrategy, MACDStrategy, PriceDeviationStrategy]:
    st = strategy(stock)
    print(st.transactions())
```

2. 分析个股
```python
from event_trader import StockInfo
stock = StockInfo('600489')
stock.get_result(t)
```

## 贡献

欢迎任何形式的贡献！如果您有建议或发现了问题，请提交issue或pull request。

## 许可证

本项目采用MIT许可证，详细信息请查看LICENSE文件。

## 联系

如有任何问题或建议，请通过以下方式联系我：

- 邮箱: 122828837@qq.com
- <img src="assets/wx.jpg" alt="微信二维码" width="200">


感谢您的支持，欢迎赞助我喝杯咖啡！


