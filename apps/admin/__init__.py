# admin/__init__.py
from flask import Blueprint, redirect, url_for, flash, request
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from apps.extension import db  # db 가져오기
from ..auth.models import User # 모델 가져오기
from werkzeug.security import generate_password_hash # 비밀번호 암호화
admin = Blueprint('admin', __name__, url_prefix='/admin') 
# Flask-Admin은 자체적으로 라우팅하므로, Blueprint는 URL 프리픽스만 설정
# from . import routes # Flask-Admin은 자체적으로 라우팅하므로 routes 파일은 없어도 됨
# 관리자 전용 접근 제한 뷰
class MyAdminIndexView(AdminIndexView):
    # 관리자 페이지의 첫 화면 (대시보드)에 접근할 수 있는지 확인
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    # 접근 권한이 없을 때 어떻게 할지 (로그인 페이지로 보내거나 메시지 표시)
    def inaccessible_callback(self, name, **kwargs):
        flash('관리자 권한이 필요합니다.', 'warning')
        return redirect(url_for('auth.login', next=request.url))
# 각 모델별 관리자 뷰
class BaseAdminView(ModelView):
    def is_accessible(self):    # 이 모델 뷰에 접근할 수 있는지 확인 (모든 관리자 뷰에 적용)
        return current_user.is_authenticated and current_user.is_admin
    def inaccessible_callback(self, name, **kwargs):   # 접근 권한이 없을 때 어떻게 할지
        flash('관리자 권한 필요', 'warning')
        return redirect(url_for('auth.login', next=request.url))
class UserAdminView(BaseAdminView):
    column_list = ('id', 'username', 'email', 'is_admin', 'created_at') # 사용자 테이블에서 보여 줄 컬럼 목록
    form_excluded_columns = ('password_hash',)   # 사용자 추가/수정 시 비밀번호 필드를 직접 처리
    form_edit_rules = ('username', 'email', 'is_admin', 'created_at', 'password') # 수정시 입력항목
    form_create_rules = ('username', 'email', 'is_admin', 'password')  # 생성시 입력항목
    def on_model_change(self, form, model, is_created):   # 비밀전호 처리방안
        if form.password.data: # 비밀번호를 입력하면(필드에 값이 있으면)
            model.set_password(form.password.data) # 암호화하여 저장
        elif not is_created and not form.password.data:    # 비밀번호 입력안하면 기존 비밀번호 해시를 유지
            original_user = db.session.query(User).get(model.id)
            model.password_hash = original_user.password_hash
        super().on_model_change(form, model, is_created)   # 부모 클래스 메소드 실행
    def scaffold_form(self):       # 사용자 추가/수정 폼에 'password' 필드를 추가 즉 새비번 입력가능하도록 설정
        form_class = super().scaffold_form()
        from wtforms import PasswordField
        form_class.password = PasswordField('비밀번호 (변경 시에만 입력)')
        return form_class
"""
class APIKeyAdminView(BaseAdminView):
    column_list = ('id', 'key_string', 'user', 'is_active', 'created_at', 'last_used', 'usage_count')
    column_labels = dict(user='사용자') # 'user' 컬럼 이름을 '사용자'로 표시
    column_searchable_list = ['key_string', 'user.username'] # 검색 가능 컬럼
    column_filters = ['is_active', 'user.username'] # 필터링 가능 컬럼
    form_columns = ('user', 'is_active') # API 키 문자열은 자동 생성되므로 폼에서 제외
class UsageLogAdminView(BaseAdminView):
    column_list = ('id', 'user', 'api_key', 'endpoint', 'timestamp')
    column_labels = dict(user='사용자', api_key='API 키')
    column_searchable_list = ['user.username', 'api_key.key_string', 'endpoint']
    column_filters = ['endpoint', 'timestamp']
    can_create = False # 사용량 로그는 관리자가 직접 만들 수 없음
    can_edit = False # 사용량 로그는 관리자가 직접 수정할 수 없음
"""
