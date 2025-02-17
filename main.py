import typer
from datetime import datetime
from app.database import init_db as init_database
from app.save_database import save_trade_records
from event_trader import StocksManager

app = typer.Typer()

from china_stock_data import TradingTimeChecker

def is_market_open() -> bool:
    """Check if current time is within market hours using TradingTimeChecker"""
    return TradingTimeChecker.is_trading_time()

@app.command()
def init_db():
    """Initialize database tables"""
    init_database()
    print("Database initialized successfully!")
    
@app.command()
def start(
    index: str = typer.Option("000300", help="China stock market index"),
    allIndex: bool = typer.Option(False, help="Use all stock market index"),
    force: bool = typer.Option(False, help="Force run even if market is closed"),
    optimize: bool = typer.Option(False, help="Opmitize the strategy parameters"),
):
    if not is_market_open() and not force:
        print("Market is closed. No need run")
        return

    """Start the notification service"""
    indexes = [index] if not allIndex else ["000001", "000300", "000905"]
    print(f"Notification service started. Processing indexes: {', '.join(indexes)}")
    
    print(f"执行任务: {datetime.now()}")
    for idx in indexes:
        params = {}
        if optimize:
            params["optimize"] = True
        sm = StocksManager(index=idx)
        sm.add_callback(save_trade_records)
        sm.show_result(**params)

    print("Notification service stopped.")

if __name__ == "__main__":
    app()
