from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from config import SQLALCHEMY_DATABASE_URI

Base = declarative_base()

class StrategySelect(Base):
    """策略选股记录表"""
    __tablename__ = 'strategy_select'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, comment='选股日期')
    symbol = Column(String(20), nullable=False, comment='股票代码')
    idx = Column(String(20), nullable=False, comment='来源指数')
    strategy = Column(String(50), nullable=False, comment='策略名称')
    action = Column(Enum('Buy', 'Sell'), nullable=False, comment='交易动作')
    price = Column(Float, nullable=False, comment='交易价格')
    last_trade_time = Column(DateTime, nullable=True, comment='最新交易时间')
    update_count = Column(Integer, default=0, comment='更新次数')
    strategy_info = Column(JSON, nullable=True, comment='策略信息')
    remark = Column(String(255), nullable=True, comment='备注')

    def __repr__(self):
        return f"<StrategySelect(id={self.id}, symbol={self.symbol}, strategy={self.strategy}, action={self.action})>"
