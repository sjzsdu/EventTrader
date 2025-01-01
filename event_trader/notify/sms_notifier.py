from .notifier import Notifier

class SMSNotifier(Notifier):
    def send_notification(self, message: str, target: str):
        # 这里实现短信通知的逻辑
        print(f"通过短信发送通知给 {target}: {message}") 