from event_trader.notify.wechat_notifier import WeChatNotifier
import schedule
from datetime import datetime, timedelta, time
from event_trader.notify import WeChatNotifier

nt = WeChatNotifier()
    
# Wait for login to complete
print("请扫描二维码登录微信...")
nt.wait_for_login(timeout=60)  # 60秒超时
def job():
    nt.send_notification('这是个测试呀', 'self')
    print("执行任务:", datetime.now())

def is_market_open():
    return True
    now = datetime.now()
    # 假设交易日为周一到周五，时间为 9:30 到 15:00
    if now.weekday() < 5:  # 0-4 是周一到周五
        market_open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close_time = now.replace(hour=15, minute=0, second=0, microsecond=0)
        return market_open_time <= now <= market_close_time
    return False

def schedule_job():
    if is_market_open():
        job()

# 每隔30分钟检查并执行任务
schedule.every(1).minutes.do(schedule_job)

while True:
    schedule.run_pending()
    time.sleep(30)
