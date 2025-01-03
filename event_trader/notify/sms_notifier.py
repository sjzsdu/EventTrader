from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20210111 import sms_client, models
from .notifier import Notifier

class SMSNotifier(Notifier):
    """短信通知器
    
    使用腾讯云短信服务发送短信通知
    需要提供以下配置参数：
    - secret_id: 腾讯云API密钥ID
    - secret_key: 腾讯云API密钥
    - region: 服务区域
    - sms_app_id: 短信应用ID
    - sign_name: 短信签名
    - template_id: 短信模板ID
    """
    
    def __init__(self):
        """初始化短信通知器"""
        super().__init__()
        self.client = None
        
        try:
            from ..config import (
                TENCENT_SECRET_ID,
                TENCENT_SECRET_KEY,
                TENCENT_REGION,
                TENCENT_SMS_APP_ID,
                TENCENT_SMS_SIGN_NAME,
                TENCENT_SMS_TEMPLATE_ID
            )
            
            # 验证配置
            if not all([TENCENT_SECRET_ID, TENCENT_SECRET_KEY, TENCENT_REGION,
                       TENCENT_SMS_APP_ID, TENCENT_SMS_SIGN_NAME, TENCENT_SMS_TEMPLATE_ID]):
                raise ValueError("短信配置不完整")
                
            self.sms_app_id = TENCENT_SMS_APP_ID
            self.sign_name = TENCENT_SMS_SIGN_NAME
                raise ValueError("短信配置不完整")
                
            # 创建短信客户端
            cred = credential.Credential(secret_id, secret_key)
            self.client = sms_client.SmsClient(cred, region)
            
        except Exception as e:
            self.client = None
            raise RuntimeError(f"短信服务初始化失败: {str(e)}")

    def send_notification(self, message: str, target: str) -> bool:
        """发送短信通知
        
        Args:
            message: 短信内容
            target: 接收手机号码（带国际区号，如+8613812345678）
            
        Returns:
            bool: 发送是否成功
        """
        if not self.client:
            raise RuntimeError("短信服务未初始化")
            
        try:
            # 构造请求参数
            req = models.SendSmsRequest()
            req.SmsSdkAppId = self.sms_app_id
            req.SignName = self.sign_name
            req.TemplateId = self.template_id
            req.TemplateParamSet = [message]
            req.PhoneNumberSet = [target]
            
            # 发送短信
            resp = self.client.SendSms(req)
            
            # 检查响应状态
            if resp.SendStatusSet[0].Code == "Ok":
                return True
            else:
                print(f"短信发送失败: {resp.SendStatusSet[0].Message}")
                return False
                
        except TencentCloudSDKException as e:
            print(f"短信发送失败: {str(e)}")
            return False
            
    def __del__(self):
        """清理资源"""
        if self.client:
            try:
                self.client = None
            except:
                pass
