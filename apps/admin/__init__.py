from flask import Blueprint, redirect, url_for, flash, request
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from wtforms import PasswordField
from wtforms.validators import Optional # Make sure this is imported if used in form_extra_fields
# Assuming apps/admin/forms.py exists and UserAdminForm is defined there
from .forms import UserAdminForm # IMPORTANT: Make sure this import is correct
from apps.extensions import db
from ..auth.models import User # IMPORTANT: Make sure User model is imported

admin = Blueprint('admin', __name__, url_prefix='/admin')

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash('관리자 권한이 필요합니다.', 'warning')
        return redirect(url_for('auth.login', next=request.url))

class BaseAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash('관리자 권한 필요', 'warning')
        return redirect(url_for('auth.login', next=request.url))

class UserAdminView(BaseAdminView):
    column_list = ('id', 'username', 'email', 'is_admin')
    form_excluded_columns = ('password_hash', 'created_at') # Exclude the hash column from direct form input

    # Using the custom WTForms form for full control
    form = UserAdminForm

    # These rules are based on the fields defined in UserAdminForm
    form_create_rules = ('username', 'email', 'is_admin', 'password')
    form_edit_rules = ('username', 'email', 'is_admin', 'password')

    def on_model_change(self, form, model, is_created):
        # --- THIS IS THE CRITICAL PART ---
        # Use the 'password' property setter from the User model
        if form.password.data:
            model.password = form.password.data  # Assigns to the property, which triggers the setter
        elif not is_created and not form.password.data:
            # If not creating and password field is empty, retain original hash
            original_user = db.session.get(User, model.id)
            if original_user:
                model.password_hash = original_user.password_hash

        # Call the parent class's on_model_change
        super().on_model_change(form, model, is_created)