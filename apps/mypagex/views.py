# apps/mypagex/views.py
from apps.extensions import db, login_manager
from .forms import ChangePasswordForm
from apps.dbmodels import User
from flask import render_template, flash, url_for, redirect, request
from flask_login import login_required, login_user, logout_user
from apps import auth  # views.py import해서 라우팅 등록
from . import mypagex ## 추가

# dashboard 엔드포인트
@mypagex.route("/dashboard")
@login_required
def dashboard():
    return render_template("mypagex/dashboard.html")
