
from .database import SessionLocal
from .database.repositories.strategy_select_repository import StrategySelectRepository


def save_trade_records(df, symbol, market):
    """保存策略选股记录到数据库"""
    with SessionLocal() as db:
        repository = StrategySelectRepository(db)
        try:
            for _, row in df.iterrows():
                if row['status'] in ['Buy', 'Sell']:
                    strategy_data = {
                        'index': market.index,
                        'name': row.get('name', ''),
                        'status': row['status'],
                        'row': row.get('row', {}),
                        'description': row.get('description', ''),
                        'parameters': row.get('parameters', {}),
                        'profit': row.get('profit', 0),
                        'factors': row.get('factors', {})
                    }
                    repository.save_strategy_select(symbol, strategy_data)
        except Exception as e:
            print(f"Error saving strategy select record: {e}")