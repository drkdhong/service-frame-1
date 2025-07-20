#apps/dbmodels.py
import enum
import os
import uuid
from flask import current_app
from apps import db  # apps에서 db를 import
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash 
#hash import
from datetime import datetime
from apps.config import Config

class User(db.Model, UserMixin): 
# db.Model, UserMixin 상속하는 User 클래스 생성
    __tablename__= "users"  # 삭제시, 테이블 이름은 Model 이름 소문자 
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String, index=True)
    email=db.Column(db.String, unique=True, index= True)
    password_hash=db.Column(db.String)
    is_admin=db.Column(db.Boolean,default=False)
    is_active=db.Column(db.Boolean, default=True)  # 활성화 여부
    usage_count = db.Column(db.Integer, default=0)
    # 특정 User에 대한 일일/월간 사용량 제한을 위한 필드 추가 가능 (예: daily_limit, monthly_limit)
    daily_limit = db.Column(db.Integer, default=1000)
    monthly_limit = db.Column(db.Integer, default=5000)
    created_at=db.Column(db.DateTime, default= datetime.now)
    updated_at=db.Column(db.DateTime, default= datetime.now, onupdate=datetime.now)
    api_keys = db.relationship('APIKey', backref='user', lazy=True, cascade='all, delete-orphan')
    usage_logs = db.relationship('UsageLog', backref='user', lazy=True, cascade='all, delete-orphan')
    # 추가  
    prediction_results = db.relationship('PredictionResult', backref='user', lazy=True, cascade='all, delete-orphan')
    subscriptions = db.relationship('Subscription', backref='subscriber', lazy=True, cascade="all, delete-orphan")
    # 추가
    iris_results = db.relationship('IRIS', backref='user', lazy=True, cascade='all, delete-orphan')
    # The 'password' property and its setter
    @property
    def password(self):
        """
        Prevent direct reading of the password.
        Attempting to read `user.password` will raise an AttributeError.
        """
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        """
        Hashes the plain-text password and stores it in password_hash.
        This allows you to do `user.password = "mysecretpassword"`.
        """
        self.password_hash = generate_password_hash(password)
    # Method to check password (you likely already have this or check_password)
    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)
    # 비밀번호 체크
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    # Flask-Login required methods
    @property
    def is_authenticated(self):
        return True
    @property
    def is_anonymous(self):
        return False
    def __repr__(self):
        return f'<User {self.username}>'
    # 이메일 중복 체크
    def is_duplicate_email(self):
        return User.query.filter_by(email=self.email).first() is not None
    # flask-login에서 사용자 ID를 문자열로 반환하기 위한 함수
    # 이 함수는 Flask-Login이 사용자 객체를 로드할 때 사용됨
    def get_id(self):
        return str(self.id)
    # 현재 로그인하고 있는 사용자 정보 취득 함수 설정은 apps/__init__.py에서 정의함

class APIKey(db.Model):
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    key_string = db.Column(db.String(32), unique=True, nullable=False, index=True)
    # 추가
    description = db.Column(db.String(100), nullable=True)
    # 추가
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default= datetime.now)
    last_used = db.Column(db.DateTime)
    usage_count = db.Column(db.Integer, default=0)
    # 특정 API Key에 대한 일일/월간 사용량 제한을 위한 필드 추가 가능 (예: daily_limit, monthly_limit)
    daily_limit = db.Column(db.Integer, default=1000)
    monthly_limit = db.Column(db.Integer, default=5000)
    usage_logs = db.relationship('UsageLog', backref='api_key', lazy=True, cascade="all, delete-orphan")
    # 추가
    prediction_results = db.relationship('PredictionResult', backref='api_key', lazy=True, cascade="all, delete-orphan")
    # 추가
    iris_results = db.relationship('IRIS', backref='api_key', lazy=True, cascade="all, delete-orphan")
    def __init__(self, user_id):
        self.user_id = user_id
        self.generate_key() # Generate key during initialization
    def generate_key(self):
        api_key_length = int(current_app.config.get('API_KEY_LENGTH', 32)) # .get() 메서드를 사용하여 기본값 지정 가능
        print(f"API Key Length Type: {type(api_key_length)}")
        print(f"API Key Length Value: {api_key_length}")
        # UUID를 생성하고, 하이픈을 제거한 후, 정의된 길이만큼 슬라이싱합니다.
        self.key_string = str(uuid.uuid4()).replace('-', '')[:api_key_length]
        print(f"Generated API Key: {self.key_string}")

        #self.key_string = str(uuid.uuid4()).replace('-', '')[:current_app.config.get('API_KEY_LENGTH',32)]
        #self.key_string = str(uuid.uuid4()).replace('-', '')[:current_app.config['API_KEY_LENGTH']]
        print(self.key_string)
    def __repr__(self):
        return f'<APIKey {self.key_string}>'

# 변경
# 사용 타입 Enum
class UsageType(enum.Enum):
    LOGIN = 'login'
    API_KEY = 'api_key'
    WEB_UI = 'web_ui' # 웹 UI를 통한 서비스 사용 추가

# 사용 로그 모델
class UsageLog(db.Model):
    __tablename__ = 'usage_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    ai_service_id = db.Column(db.Integer, db.ForeignKey('aiservice.id'), nullable=True) # AI 서비스 사용 로그가 아닌 로그인 등은 Null 허용
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'), index=True, nullable=True) # API 키 사용 로그가 아닌 경우는 Null 허용
    endpoint = db.Column(db.String(120), nullable=True) # 어떤 엔드포인트에 접근했는지 (예: /api/iris)
    usage_type = db.Column(db.Enum(UsageType), nullable=False)
    usage_count = db.Column(db.Integer, default=1, nullable=False) # 각 로그 항목은 기본적으로 1회 사용
    login_confirm = db.Column(db.String(10), nullable=True) # 로그인 여부 확인용 (예: 'success', 'fail')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    remote_addr = db.Column(db.String(45))
    request_data_summary = db.Column(db.Text)
    response_status_code = db.Column(db.Integer)

    def __repr__(self) -> str:
        return f"<UsageLog(ai_service_id={self.ai_service_id}, usage_type='{self.usage_type}', timestamp={self.timestamp})>"


# 추가
# AI 서비스 모델
class AIService(db.Model):
    __tablename__ = "aiservice"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.String(200), nullable=False) # 쉼표로 구분된 키워드 (예: "iris, 분류, 꽃")

    # 관계
    subscriptions = db.relationship('Subscription', backref='ai_service', lazy=True, cascade="all, delete-orphan")
    usage_logs = db.relationship('UsageLog', backref='ai_service', lazy=True, cascade="all, delete-orphan")
    prediction_results = db.relationship('PredictionResult', backref='ai_service', lazy=True, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<AIService(name='{self.name}')>"


# 예측 결과 기본 모델 (PredictionResult)
class PredictionResult(db.Model):
    __tablename__ = 'prediction_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    ai_service_id = db.Column(db.Integer, db.ForeignKey('aiservice.id'), nullable=False)
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'), index=True)
    predicted_class = db.Column(db.String(50))
    model_version = db.Column(db.String(20), default='1.0')
    confirmed_class = db.Column(db.String(50))
    confirm = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    # 다형성 설정: 어떤 예측 결과 유형인지 구분
    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'prediction_result'
    }

    def __repr__(self) -> str:
        return f"<PredictionResult(user_id={self.user_id}, ai_service_id={self.ai_service_id}, predicted_class='{self.predicted_class}')>"

# 구독 모델
class Subscription(db.Model):
    __tablename__ = "subscription"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ai_service_id = db.Column(db.Integer, db.ForeignKey('aiservice.id'), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False) # pending, approved, rejected
    request_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    approval_date = db.Column(db.DateTime, nullable=True)

    __table_args__ = (db.UniqueConstraint('user_id', 'ai_service_id', name='_user_ai_service_uc'),)

    def __repr__(self) -> str:
        return f"<Subscription(user_id={self.user_id}, ai_service_id={self.ai_service_id}, status='{self.status}')>"

# 추가


class IRIS(db.Model):
    __tablename__ = 'iris_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'), index=True)
    sepal_length = db.Column(db.Float, nullable=False)
    sepal_width = db.Column(db.Float, nullable=False)
    petal_length = db.Column(db.Float, nullable=False)
    petal_width = db.Column(db.Float, nullable=False)
    predicted_class = db.Column(db.String(50)) # 붓꽃 분류 결과 (예: 'setosa', 'versicolor', 'virginica')
    # AI 모델 버전 정보 추가 (추후 모델 업데이트 시 유용)
    model_version = db.Column(db.String(20), default='1.0')
    confirmed_class = db.Column(db.String(50)) # 붓꽃 분류 결과 (예: 'setosa', 'versicolor', 'virginica')
    confirm = db.Column(db.Boolean, default=False) # 사용자가 추론 결과를 확인했는지 여부
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    def __repr__(self):
        return f'<IRIS {self.sepal_length}, {self.sepal_width}, {self.petal_length}, {self.petal_width} -> {self.predicted_class}>'

