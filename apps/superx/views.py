# apps/superx/views.py
from flask import Flask, flash, redirect, request, render_template, jsonify, abort, current_app, url_for, g
import pickle, os, uuid 
import logging, functools
from apps.extensions import csrf # 이 줄을 추가하여 정의된 csrf 객체를 임포트
from apps.dbmodels import IRIS, db, User, APIKey, UsageLog, UsageType
import numpy as np
from flask_login import current_user, login_required
from . import superx

from datetime import datetime, timedelta

# 관리자 권한 확인 데코레이터
def superx_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('관리자 권한이 필요합니다.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@superx.route('/')
@superx_required
def dashboard():
    # 여기서 실제 데이터를 가져오는 것처럼 흉내 낼 거예요.
    # 나중에 데이터베이스에서 데이터를 가져오는 코드로 바꿀 수 있어요.
    sales_data = {
        'labels': ['1월', '2월', '3월', '4월', '5월', '6월'],
        'data': [120, 190, 300, 500, 200, 300]
    }
    user_data = {
        'labels': ['서울', '경기', '부산', '대구', '광주'],
        'data': [500, 700, 300, 200, 150]
    }
    order_status_data = {
        'labels': ['주문 완료', '배송 중', '배송 완료', '취소'],
        'data': [80, 40, 150, 10]
    }
    daily_visitors_data = {
        'labels': ['1일', '2일', '3일', '4일', '5일', '6일', '7일'],
        'data': [500, 650, 700, 600, 750, 800, 780]
    }

    recent_activities = [
        {'time': '5분 전', 'description': '새로운 사용자 가입: 홍길동'},
        {'time': '1시간 전', 'description': '주문 번호 #123456 결제 완료'},
        {'time': '3시간 전', 'description': '새로운 제품 등록: 스마트폰 케이스'}
    ]
    # render_template 함수를 사용해서 HTML 파일을 웹 브라우저에 보여줄 거예요.
    # 이 함수로 sales_data, user_data, order_status_data, recent_activities를 HTML로 전달해요.
    return render_template('superx/dashboard1.html',
                           sales_data=sales_data,
                           user_data=user_data,
                           order_status_data=order_status_data,
                           daily_visitors_data=daily_visitors_data,
                           recent_activities=recent_activities)
# 차트 데이터를 JSON 형식으로 전달하는 API (이건 나중에 Chart.js에서 데이터를 요청할 때 사용)
@superx.route('/api/chart-data')
def get_chart_data():
    data = {
        'monthlySales': {
            'labels': ['1월', '2월', '3월', '4월', '5월', '6월'],
            'values': [1200, 190, 300, 500, 200, 300]
        },
        'userDistribution': {
            'labels': ['서울', '경기', '부산', '대구', '광주'],
            'values': [500, 700, 300, 200, 150]
        },
        'orderStatus': {
            'labels': ['주문 완료', '배송 중', '배송 완료', '취소'],
            'values': [80, 40, 150, 10]
        },
        'daily_visitors_data' : {
            'labels': ['1일', '2일', '3일', '4일', '5일', '6일', '7일'],
            'data': [500, 650, 700, 600, 750, 800, 780]
        }
    }
    # jsonify는 파이썬 딕셔너리를 웹에서 이해할 수 있는 JSON 형식으로 바꿔줘요.
    return jsonify(data)
