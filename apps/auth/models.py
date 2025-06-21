#apps/auth/models.py
from apps.extension import db, login_manager  # apps.extension에서 db,login_manager를 import
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash 
#hash import
from datetime import datetime
class User(db.Model, UserMixin): 
# db.Model, UserMixin 상속하는 User 클래스 생성
    __tablename__= "users" #삭제시, 테이블 이름은 Model 이름 소문자 
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String, index=True)
    email=db.Column(db.String, unique=True, index= True)
    password_hash=db.Column(db.String)
    is_admin=db.Column(db.Boolean,default=False)
    created_at=db.Column(db.DateTime, default= datetime.now)
    updated_at=db.Column(db.DateTime, default= datetime.now, onupdate=datetime.now)
    @property     # 비밀번호 호출 프로퍼티
    def password(self):
        raise AttributeError("읽을 수 없음")
    @password.setter    # 비밀번호 설정
    def password(self, password):
        self.password_hash=generate_password_hash(password)
    # 비밀번호 체크
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    # 이메일 중복 체크
    def is_duplicate_email(self):
        return User.query.filter_by(email=self.email).first() is not None
    # 현재 로그인하고 있는 사용자 정보 취득 함수 설정 - apps/__init__.py에서도 정의(현재 중복)
    # 데코레이터는 사용자객체로드과정을 Flask-Login에게 알려줌
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
