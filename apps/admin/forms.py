# apps/admin/forms.py
from wtforms import Form, StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Optional

class UserAdminForm(Form):
    username = StringField('사용자 이름', validators=[DataRequired()])
    email = StringField('이메일', validators=[DataRequired(), Email()])
    is_admin = BooleanField('관리자 여부')

    # This is the custom password field for the form
    password = PasswordField('비밀번호 (변경 시에만 입력)', validators=[Optional()])

    # --- ENSURE THIS FIELD IS PRESENT AND CORRECTLY SPELLED ---
    # We'll even add a unique label to make it easily identifiable if rendered
    created_at = StringField('생성일 (확인용)', render_kw={'readonly': True}, validators=[Optional()])

