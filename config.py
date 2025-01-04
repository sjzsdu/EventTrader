import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote

# 加载.env文件
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# 数据库配置
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
DB_CONFIG = {
    'mysql': {
        'driver': 'mysql+pymysql',
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'database': os.getenv('DB_NAME', 'event_trader'),
        'username': os.getenv('DB_USER', 'root'),
        'password': quote(os.getenv('DB_PASSWORD', '')),
        'charset': os.getenv('MYSQL_CHARSET', 'utf8mb4'),
        'collation': os.getenv('MYSQL_COLLATION', 'utf8mb4_unicode_ci')
    },
    'sqlite': {
        'driver': 'sqlite',
        'database': os.getenv('DB_NAME', 'db.sqlite3')
    }
}

# 获取当前数据库配置
CURRENT_DB_CONFIG = DB_CONFIG[DB_TYPE]
SQLALCHEMY_DATABASE_URI = '{driver}://{username}:{password}@{host}:{port}/{database}'.format(**CURRENT_DB_CONFIG) \
    if DB_TYPE == 'mysql' else 'sqlite:///{database}'.format(**CURRENT_DB_CONFIG)

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
