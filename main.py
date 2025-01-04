import typer
import signal
import sys
from datetime import datetime
from event_trader.database import init_db as init_database
import schedule
import time as sleep_time
from event_trader import StocksManager

# Flag to control shutdown
shutdown = False

def signal_handler(sig, frame):
    global shutdown
    print("\nShutting down gracefully...")
    shutdown = True

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
    interval: int = typer.Option(5, help="Event trading interval in minutes")
):
    """Start the notification service"""
    
    def job():
        print(f"执行任务: {datetime.now()}")
        sm = StocksManager(index = index)
        sm.show_result()
        

    def schedule_job():
        # if is_market_open():
        job()

    # Schedule the job
    schedule.every(interval).minutes.do(schedule_job)
    print(f"Notification service started. Sending the buy symbols every {interval} minutes during market time")
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    while not shutdown:
        schedule.run_pending()
        sleep_time.sleep(30)
    
    # Clear all scheduled jobs
    schedule.clear()
    print("Notification service stopped.")

if __name__ == "__main__":
    app()
