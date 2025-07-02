# apps/superman/views.py
from flask import Flask, flash, redirect, request, render_template, jsonify, abort, current_app, url_for, g
import pickle, os, uuid 
import logging, functools
from apps.extensions import csrf # 이 줄을 추가하여 정의된 csrf 객체를 임포트
from apps.dbmodels import IRIS, db, User, APIKey, UsageLog, UsageType
import numpy as np
from flask_login import current_user, login_required
from . import superman

from datetime import datetime, timedelta

# 관리자 권한 확인 데코레이터
def superman_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('관리자 권한이 필요합니다.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@superman.route('/')
@superman_required
def dashboard():
    # 샘플 데이터
    users_count = 120
    sales_data = [10, 30, 20, 34, 45, 60, 55]
    sales_labels = ['월', '화', '수', '목', '금', '토', '일']

    pie_labels = ['Desktop', 'Mobile', 'Tablet']
    pie_data = [60, 30, 10]

    bar_labels = ['A', 'B', 'C', 'D']
    bar_data = [12, 19, 3, 5]

    return render_template('superman/dashboard.html',
                           users_count=users_count,
                           sales_data=sales_data,
                           sales_labels=sales_labels,
                           pie_labels=pie_labels,
                           pie_data=pie_data,
                           bar_labels=bar_labels,
                           bar_data=bar_data
    )

@superman.route('/chart')
@superman_required
def chartboard():
    # 카운트, 차트, 테이블 등 필요한 데이터를 준비합니다.
    users_count = 120
    new_msg_count = 5

    sales_data = [10, 30, 20, 34, 45, 60, 55]
    sales_labels = ['월', '화', '수', '목', '금', '토', '일']

    pie_labels = ['Desktop', 'Mobile', 'Tablet']
    pie_data = [60, 30, 10]

    bar_labels = ['A', 'B', 'C', 'D']
    bar_data = [12, 19, 3, 5]

    # 새 알림(공지) 목록 샘플
    notifications = [
        {"msg": "오늘 18시에 서버 점검이 있습니다.", "type": "info"},
        {"msg": "신규 회원 가입이 승인되었습니다.", "type": "success"},
        {"msg": "고객지원 문의가 2건 도착했습니다.", "type": "warning"}
    ]

    # 최근 유저 목록 테이블 (샘플)
    recent_users = [
        {"name": "홍길동", "email": "hong@school.com", "date": "2024-06-08"},
        {"name": "이순신", "email": "lee@school.com", "date": "2024-06-08"},
        {"name": "김영희", "email": "kim@school.com", "date": "2024-06-07"},
        {"name": "박철수", "email": "park@school.com", "date": "2024-06-07"}
    ]

    # 추가 차트 : radar (성적 비교)
    radar_labels = ["수학", "영어", "과학", "국어", "사회"]
    radar_data = [85, 90, 70, 95, 80]

    return render_template('superman/chartboard.html',
                           users_count=users_count,
                           new_msg_count=new_msg_count,
                           sales_data=sales_data,
                           sales_labels=sales_labels,
                           pie_labels=pie_labels,
                           pie_data=pie_data,
                           bar_labels=bar_labels,
                           bar_data=bar_data,
                           notifications=notifications,
                           recent_users=recent_users,
                           radar_labels=radar_labels,
                           radar_data=radar_data
    )

@superman.route('/chartx')
@superman_required
def chartman():
        # 대시보드에 표시할 데이터 (예시)
    user_data = {
        'labels': ['1월', '2월', '3월', '4월', '5월', '6월'],
        'datasets': [{
            'label': '신규 가입자',
            'data': [100, 120, 150, 130, 180, 200],
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1
        }]
    }

    product_sales_data = {
        'labels': ['제품 A', '제품 B', '제품 C', '제품 D'],
        'datasets': [{
            'label': '판매량',
            'data': [500, 700, 300, 600],
            'backgroundColor': [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)'
            ],
            'borderColor': [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)'
            ],
            'borderWidth': 1
        }]
    }

    traffic_source_data = {
        'labels': ['직접', '검색', '소셜 미디어', '레퍼럴'],
        'datasets': [{
            'data': [300, 200, 150, 100],
            'backgroundColor': [
                'rgba(255, 99, 132, 0.7)',
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 206, 86, 0.7)',
                'rgba(75, 192, 192, 0.7)'
            ],
            'hoverOffset': 4
        }]
    }
    return render_template('superman/chartman.html',
                           user_data=user_data,
                           product_sales_data=product_sales_data,
                           traffic_source_data=traffic_source_data)
