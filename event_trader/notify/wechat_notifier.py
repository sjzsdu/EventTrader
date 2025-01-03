from .notifier import Notifier
import itchat  # 添加这个导入

class WeChatNotifier(Notifier):
    def __init__(self, login_callback=None):
        self.logged_in = False
        def on_login():
            self.logged_in = True
            if login_callback:
                login_callback()
        try:
            print("Starting WeChat login...")
            itchat.auto_login(loginCallback=on_login)  # 在初始化时登录微信
            print("WeChat login successful")
        except Exception as e:
            print(f"WeChat login failed: {str(e)}")
            raise

    def wait_for_login(self, timeout=None):
        import time
        start_time = time.time()
        while not self.logged_in:
            if timeout and time.time() - start_time > timeout:
                raise TimeoutError("WeChat login timed out")
            time.sleep(0.1)

    def send_notification(self, message: str, target: str):
        if target == 'self':
            itchat.send(message, toUserName='filehelper')  # 发送给自己
            print(f"通过微信发送通知给自己: {message}")
        else:
            friends = itchat.get_friends()
            friend = next((f for f in friends if f['NickName'] == target or f['RemarkName'] == target), None)
            if friend:
                itchat.send(message, toUserName=friend['UserName'])  # 发送给好友
                print(f"通过微信发送通知给 {target}: {message}")
            else:
                print(f"未找到微信好友: {target}")
