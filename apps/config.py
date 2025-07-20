#apps/config.py
import os
from datetime import timedelta
if os.environ.get('RENDER', None) != 'true':
    from dotenv import load_dotenv      # render.com이 아닌 로컬 환경에서만 .env를 로드(안해도 됨)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    dotenv_path = os.path.join(BASE_DIR, '..', '.env')
    load_dotenv(dotenv_path)
class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.getenv('SECRET_KEY')
    #API_KEY = os.getenv('API_KEY')
    IRIS_LABELS = ['setosa', 'versicolor', 'virginica']
    INSTANCE_DIR = os.path.join(BASE_DIR, '..', 'instance')
    if not os.path.exists(INSTANCE_DIR):
        os.makedirs(INSTANCE_DIR)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(INSTANCE_DIR, 'mydb.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Flask-Login
    # REMEMBER_COOKIE_DURATION = 3600  # 1시간
    CSRF_ENABLED = True
    CSRF_SESSION_KEY = os.getenv('CSRF_SESSION_KEY', SECRET_KEY) # 없으면,SECRET_KEY사용
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')    
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')    
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
    # API Key 관련 설정 (필요시 추가)
    API_KEY_EXPIRATION_DAYS = 365 # API 키 만료일
    LOGIN_USER_RATE_LIMIT = os.getenv('LOGIN_USER_RATE_LIMIT')    
    API_KEY_RATE_LIMIT = os.getenv('API_KEY_RATE_LIMIT')
    API_KEY_LENGTH = os.getenv('API_KEY_LENGTH')
    print(type(API_KEY_LENGTH))
    # .env 파일에서 세션 유효 기간(분 단위)을 문자열로 읽어옵니다.
    # getenv의 두 번째 인자는 환경 변수가 없을 경우 사용할 기본값입니다.
    session_lifetime_minutes_str = os.getenv('SESSION_LIFETIME_MINUTES', '30')
    # 읽어온 문자열을 정수(int)로 변환합니다.
    try:
        session_lifetime_minutes = int(session_lifetime_minutes_str)
    except ValueError:
        # 만약 환경 변수 값이 숫자로 변환될 수 없는 잘못된 값이라면 기본값으로 30분을 사용합니다.
        session_lifetime_minutes = 30
    # 변환된 정수 값을 사용하여 timedelta 객체를 생성하고, 이를 Flask 설정에 할당합니다.
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=session_lifetime_minutes)
    # 이제 이 PERMANENT_SESSION_LIFETIME 변수를 Flask app의 config에 적용하면 됩니다.
    # 예: app.config['PERMANENT_SESSION_LIFETIME'] = PERMANENT_SESSION_LIFETIME
    # 로깅 설정 (프로덕션 환경)
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    LOG_FILE_PATH = os.path.join(BASE_DIR, 'logs/app.log')
    LOG_LEVEL = 'INFO' # DEBUG, INFO, WARNING, ERROR, CRITICAL
