from datetime import datetime
from .base_repository import BaseRepository
from ..models.strategy_select import StrategySelect
from event_trader.config import PRICE_COL

class StrategySelectRepository(BaseRepository):

    def find_by_symbol_and_date(self, symbol: str, date: datetime.date, strategy: str):
        """根据symbol和date查找记录"""
        return self.db.query(StrategySelect).filter(
            StrategySelect.symbol == symbol,
            StrategySelect.date == date,
            StrategySelect.strategy == strategy
        ).first()

    def create(self, strategy_select: StrategySelect):
        """创建新记录"""
        self.db.add(strategy_select)
        self.commit()
        return strategy_select

    def update(self, strategy_select: StrategySelect):
        """更新现有记录"""
        strategy_select.last_trade_time = datetime.now()
        strategy_select.update_count += 1
        self.commit()
        return strategy_select

    def save_strategy_select(self, symbol: str, strategy_data: dict):
        """保存或更新策略选股记录"""
        today = datetime.now().date()
        existing_record = self.find_by_symbol_and_date(symbol, today, strategy_data.get('name', ''))
        
        if existing_record:
            return self.update(existing_record)
        else:
            strategy_select = StrategySelect(
                date=today,
                symbol=symbol,
                idx=strategy_data.get('index', None),
                strategy=strategy_data.get('name', ''),
                action=strategy_data.get('status', ''),
                price=strategy_data.get('factors', {}).get(PRICE_COL, 0),
                last_trade_time=datetime.now(),
                update_count=0,
                strategy_info={
                    'name': strategy_data.get('name', ''),
                    'description': strategy_data.get('description', ''),
                    'parameters': strategy_data.get('parameters', {}),
                    'status': strategy_data.get('status', ''),
                    'profit': strategy_data.get('profit', 0),
                    'data': strategy_data.get('data', {})
                }
            )
            return self.create(strategy_select)
