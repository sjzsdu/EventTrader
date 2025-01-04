import os
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)


# 腾讯云短信配置
TENCENT_SECRET_ID = os.getenv("TENCENT_SECRET_ID")
TENCENT_SECRET_KEY = os.getenv("TENCENT_SECRET_KEY")
TENCENT_REGION = os.getenv("TENCENT_REGION")
TENCENT_SMS_APP_ID = os.getenv("TENCENT_SMS_APP_ID")
TENCENT_SMS_SIGN_NAME = os.getenv("TENCENT_SMS_SIGN_NAME")
TENCENT_SMS_TEMPLATE_ID = os.getenv("TENCENT_SMS_TEMPLATE_ID")


# Email config
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 465))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_PASSWORD = os.getenv('FROM_EMAIL')
