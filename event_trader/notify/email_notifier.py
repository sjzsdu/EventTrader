import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from .notifier import Notifier

class EmailNotifier(Notifier):
    """邮件通知器
    
    使用前需要提供以下SMTP配置参数：
    - smtp_server: SMTP服务器地址
    - smtp_port: SMTP端口
    - email_user: 发件邮箱
    - email_password: 邮箱密码或授权码
    """
    
    def __init__(self, smtp_server: str, smtp_port: int, 
                 email_user: str, email_password: str):
        """初始化邮件通知器
        
        Args:
            smtp_server: SMTP服务器地址
            smtp_port: SMTP端口
            email_user: 发件邮箱
            email_password: 邮箱密码或授权码
        """
        super().__init__()
        self.server = None
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_user = email_user
        self.email_password = email_password
        
        try:
            # 验证配置
            if not all([self.smtp_server, self.email_user, self.email_password]):
                raise ValueError("邮件配置不完整")
                
            # 创建SMTP连接
            self.server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            self.server.login(self.email_user, self.email_password)
            
        except Exception as e:
            self.server = None
            raise RuntimeError(f"邮件服务器初始化失败: {str(e)}")

    def send_notification(self, message: str, target: str) -> bool:
        """发送邮件通知
        
        Args:
            message: 邮件内容
            target: 收件人邮箱地址
            
        Returns:
            bool: 发送是否成功
        """
        if not self.server:
            raise RuntimeError("邮件服务器未初始化")
            
        try:
            # 创建邮件内容
            msg = MIMEText(message, 'plain', 'utf-8')
            msg['From'] = formataddr(('Event Trader', self.email_user))
            msg['To'] = target
            msg['Subject'] = 'Event Trader 通知'
            
            # 发送邮件
            self.server.sendmail(self.email_user, [target], msg.as_string())
            return True
            
        except Exception as e:
            print(f"邮件发送失败: {str(e)}")
            return False
            
    def __del__(self):
        """清理资源"""
        if self.server:
            try:
                self.server.quit()
            except:
                pass
