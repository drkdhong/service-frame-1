# apps/adminx/views.py
import datetime
from flask import render_template
from sqlalchemy import func
from . import adminx
from apps.dbmodels import UsageLog, User
from apps.decorators import admin_required
from apps.extensions import db

@adminx.route('/dashboard')
@admin_required
def dashboard():
    total_users = 2  # User.query.count()
    total_services = 3  # AIService.query.count()
    pending_subscriptions = 4 # Subscription.query.filter_by(status='pending').count()
    
    # 최근 7일간 서비스 사용량 (로그인 제외)
    #seven_days_ago = datetime.now() - datetime.timedelta(days=7)
    recent_service_usage = 0

    #recent_service_usage = db.session.query(func.sum(UsageLog.usage_count))\
    #                                .filter(UsageLog.timestamp >= seven_days_ago)\
    #                                .filter(UsageLog.usage_type.notin_([UsageLog.UsageType.LOGIN]))\
    #                                .scalar() or 0

    return render_template('adminx/dashboard.html',
                           title='관리자 대시보드',
                           total_users=total_users,
                           total_services=total_services,
                           pending_subscriptions=pending_subscriptions,
                           recent_service_usage=recent_service_usage)

@adminx.route('/users')
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('adminx/users.html', title='사용자 관리', users=users)
