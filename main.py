import typer
from typing import Optional
from datetime import datetime, time
from event_trader.notify.wechat_notifier import WeChatNotifier
import schedule
import time as sleep_time

app = typer.Typer()

from china_stock_data import TradingTimeChecker

def is_market_open() -> bool:
    """Check if current time is within market hours using TradingTimeChecker"""
    return TradingTimeChecker.is_trading_time()

@app.command()
def start(
    index: str = typer.Option("000300", help="China stock market index"),
    interval: int = typer.Option(5, help="Event trading interval in minutes")
):
    """Start the notification service"""
    
    def job():
        print(f"执行任务: {datetime.now()}")

    def schedule_job():
        if is_market_open(datetime.now()):
            job()

    # Schedule the job
    schedule.every(interval).minutes.do(schedule_job)
    print(f"Notification service started. Sending the buy symbols every {interval} minutes during market time")
    
    while True:
        schedule.run_pending()
        sleep_time.sleep(30)

if __name__ == "__main__":
    app()
