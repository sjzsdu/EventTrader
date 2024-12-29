```markdown
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
pip install pandas mplfinance china-stock-data
```

### 使用步骤

1. **克隆项目**

   ```bash
   git clone https://github.com/yourusername/stock-trading-strategy.git
   cd stock-trading-strategy
   ```

2. **创建股票数据实例**

   ```python
   from event_trader.stocks_manager import StocksManager

   # 创建股票管理实例
   manager = StocksManager(symbols=['601688', '000001'], index='沪深300')
   ```

3. **选择策略并进行优化**

   ```python
   from event_trader.strategies.boll_strategy import BollStrategy

   # 选择布林带策略
   strategy = BollStrategy(manager.stock_data)
   strategy.optimize_parameters()
   ```

4. **进行模拟交易**

   ```python
   account = strategy.calculate_profit()
   print(f"模拟交易利润: {account.get_profit()}%")
   ```

5. **可视化结果**

   ```python
   strategy.show()
   ```

## 贡献

欢迎任何形式的贡献！如果您有建议或发现了问题，请提交issue或pull request。

## 许可证

本项目采用MIT许可证，详细信息请查看LICENSE文件。
```

