from .notifier import Notifier

class EmailNotifier(Notifier):
    def send_notification(self, message: str, target: str):
        # 这里实现邮箱通知的逻辑
        print(f"通过邮箱发送通知给 {target}: {message}") 