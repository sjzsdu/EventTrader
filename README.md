# 量化分析工具

本项目是一个量化分析的工具，感谢akshare提供了财经数据接口，本项目是基于akshare提供的A股数据来对各种交易策略进行收益分析的工具，还提供了按照策略提供选股的功能。

## 功能

- **股票数据获取**：高效获取实时和历史股票数据，以进行分析和策略制定。
- **策略开发**：轻松创建和优化买卖策略。
- **回测**：在历史数据上测试您的策略，以评估其潜在盈利能力。
- **参数优化**：微调个股参数，以提高交易指标的准确性。
- **个性化策略开发**：提供选股策略的开发和验证服务，满足用户特定需求。
- **策略组合管理**：支持多组策略对多只股票同时监测，实现在买入点或卖出点的仓位控制和管理。
- **消息推送功能**：通过订阅功能，当捕捉到买卖点时发送通知。

## 安装

```bash
pip install event-trader
```

## 使用

### 个股
1. 个股主要使用StockInfo这个类，可以通过get_result方法获得各个策略的近一年时间中的交易机会以及收益
![strategy profit](/assets/stock-profit.png)
表中的profit是近一年按照该策略交易的预计收益, parameters是调优后的参数。
```python
from event_trader import StockInfo
from event_trader.strategies import SimpleMovingAverageStrategy, UpdateSimpleMovingAverageStrategy,StochasticOscillatorStrategy, OneMovingAverageStrategy, TraditionalBollStrategy, MovingAverageConvergenceDivergenceStrategy

STRATEGIES = {
    'SMA': SimpleMovingAverageStrategy,
    'USMA': UpdateSimpleMovingAverageStrategy,
    'SO': StochasticOscillatorStrategy,
    'OMA': OneMovingAverageStrategy,
    'TB': TraditionalBollStrategy,
    'MACD': MovingAverageConvergenceDivergenceStrategy
}
stock = StockInfo('601688', strategies = STRATEGIES)
stock.get_result()
```
2. 显示策略的买卖点
![strategy buy and sell](/assets/strategy-buy-sell.png)
stock.SMA.show() 调用这个方法可以用来显示K线图，以及策略中的计算因子和买卖点，凭此可以验证交易策略的收益情况
stock.SMA.account.transactions 可以查看策略的具体交易信息。

### 自选股

### 板块

## 开发计划
- **选股策略开发**：正在开发更多的选股策略。如有需求，请联系我以开发和验证个性化的策略。
- **消息推送功能**：计划增加推送功能，当捕捉到买卖点后能够发送消息给订阅者。
- **策略组合功能**：将实现策略组合的功能，支持多组策略对多只股票的监测和仓位管理。

## 许可证

本项目根据 [MIT 许可证](https://opensource.org/licenses/MIT) 授权。

## 联系

如有问题或反馈，请联系：122828837@qq.com。

祝交易顺利！