# apps/superx/views.py
from flask import Flask, flash, redirect, request, render_template, jsonify, abort, current_app, url_for, g
import pickle, os, uuid 
import logging, functools

from sklearn.calibration import label_binarize
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import auc, roc_curve
from sklearn.model_selection import train_test_split
from sqlalchemy import func
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
    # 1. UsageLog의 최근 7일 접속량 계산 
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_usage = db.session.query(
        func.date(UsageLog.timestamp), func.count(UsageLog.id)
    ).filter(UsageLog.timestamp >= seven_days_ago)\
    .group_by(func.date(UsageLog.timestamp))\
    .order_by(func.date(UsageLog.timestamp)).all()

    #print(f"recent_usage: '{recent_usage}'") # recent_usage: '[('2025-07-03', 4),('2025-07-04', 3)]'
    # recent_usage= [('2025-07-03', 4), ('2025-07-04', 3),('2025-07-05', 1), ('2025-07-06', 2)]

    # 날짜를 저장할 리스트와 판매량을 저장할 리스트를 만듭니다.
    label1 = []
    value1 = []
    monthlySales=recent_usage

    # monthlySales 리스트의 각 항목(튜플)을 하나씩 살펴봅니다.
    for date, sales_count in monthlySales:
        # 튜플의 첫 번째 요소(날짜)를 labels 리스트에 추가합니다.
        label1.append(date)
        # 튜플의 두 번째 요소(판매량)를 values 리스트에 추가합니다.
        value1.append(sales_count)

    # 최종적으로 원하는 딕셔너리 형태로 데이터를 구성합니다.
    """
    data = {
        'monthlySales': {
            'labels': label1,
            'values': value1
        }
    }
    """
    # 2. UsageLog의 usage_type을 기준으로 count를 수행하는 쿼리
    userDistribution = db.session.query(
        UsageLog.usage_type,                  # 사용 유형 (ex: LOGIN_BASED)
        func.count(UsageLog.id)               # 해당 사용 유형의 개수 세기
    ).group_by(UsageLog.usage_type)\
    .order_by(UsageLog.usage_type)\
    .all()

    # 결과 출력
    print("--- Usage Type별 사용 횟수 ---")
    for usage_type, count in userDistribution:
        print(f"Usage Type: {usage_type.value.upper()}, Count: {count}")

    # 날짜를 저장할 리스트와 판매량을 저장할 리스트를 만듭니다.
    label2 = []
    value2 = []

    print(userDistribution)

    # monthlySales 리스트의 각 항목(튜플)을 하나씩 살펴봅니다.
    for usage_type_enum, count in userDistribution:
        # 튜플의 첫 번째 요소(UsageType Enum)에서 문자열 값만 가져와 label2 리스트에 추가합니다.
        label2.append(usage_type_enum.value)
        # 튜플의 두 번째 요소(숫자)를 value2 리스트에 추가합니다.
        value2.append(count)

    print(label2)
    print(value2)

    # 변환된 데이터를 출력해서 확인해봅니다.
    data = {
        'monthlySales': {
            'labels': label1,
            'values': value1
        },
        'userDistribution': {
            'labels': label2,
            'values': value2
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


@superx.route('/api/get_roc_data') # ROC 데이터를 요청하면 이 함수가 실행돼요
def roc_data():
    # 1. 데이터 준비
    iris = load_iris()
    X = iris.data
    y = iris.target
    # 3가지 클래스니까 one-hot 인코딩
    y_bin = label_binarize(y, classes=[0, 1, 2])

    # 2. 데이터 분할
    X_train, X_test, y_train, y_test = train_test_split(X, y_bin, test_size=0.3, random_state=42)

    # 3. 모델 학습
    clf = RandomForestClassifier()
    clf.fit(X_train, y_train)

    # 4. 예측 확률 얻기
    y_score = clf.predict_proba(X_test)

    # 5. ROC 데이터 계산 (클래스별)
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    for i in range(3):  # 3가지 클래스
        fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[i][:, 1])
        roc_auc[i] = auc(fpr[i], tpr[i])

    # 데이터 포장해서 넘기기(자바스크립트에서 쓸 수 있게)
    roc_data = {
        'fpr': [list(fpr[i]) for i in range(3)],
        'tpr': [list(tpr[i]) for i in range(3)],
        'auc': [roc_auc[i] for i in range(3)],
    }
    return jsonify(roc_data)

"""
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
"""

