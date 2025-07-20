# apps/main/forms.py
from flask_wtf import FlaskForm # <-- FlaskForm을 정확히 임포트했는지 확인
from wtforms import StringField, SubmitField, FloatField, PasswordField # 필요한 필드 임포트
from wtforms.validators import DataRequired, Email, Optional

class SearchServiceForm(FlaskForm):
    """AI 서비스 검색 폼."""
    search_query = StringField('서비스 검색', validators=[Optional()])
    submit = SubmitField('검색')



