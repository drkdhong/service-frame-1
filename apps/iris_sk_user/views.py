from flask import Flask, flash, redirect, request, render_template, jsonify, abort, current_app, url_for
import pickle
import os

from apps.dbmodels import IRIS, db, User, APIKey, UsageLog
import numpy as np
from flask_login import current_user, login_required
from apps.iris_sk_user.forms import IrisUserForm
from . import iris_sk_user

# Load model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

#TARGET_NAMES = ['setosa', 'versicolor', 'virginica']
from apps.config import Config
TARGET_NAMES = Config.IRIS_LABELS   # 라벨 읽기

@iris_sk_user.route('/predict', methods=['GET', 'POST'])
@login_required
def iris_predict():
    form = IrisUserForm()
    if form.validate_on_submit():
        sepal_length = form.sepal_length.data
        sepal_width = form.sepal_width.data
        petal_length = form.petal_length.data
        petal_width = form.petal_width.data
    
        features=np.array([[sepal_length, sepal_width, petal_length, petal_width]])
        pred = model.predict(features)[0]
        return render_template('iris_sk_user/index.html',
                               result=TARGET_NAMES[pred],
                               sepal_length=sepal_length, sepal_width=sepal_width,
                               petal_length=petal_length, petal_width=petal_width, form=form, TARGET_NAMES=TARGET_NAMES
                              )
    return render_template('iris_sk_user/index.html',form=form)

@iris_sk_user.route('/save_iris_data', methods=['POST'])
@login_required
def save_iris_data():
    if request.method == 'POST':
        # HTML 폼에서 전송된 모든 데이터를 가져와요.
        sepal_length = request.form.get('sepal_length')
        sepal_width = request.form.get('sepal_width')
        petal_length = request.form.get('petal_length')
        petal_width = request.form.get('petal_width')
        predicted_class = request.form.get('predicted_class')
        confirmed_class = request.form.get('confirmed_class') # 이게 핵심이에요!

        # 새로운 Iris 객체를 만들어요 (테이블의 새 줄과 같아요)
        new_iris_entry = IRIS(
            user_id=current_user.id,
            #api_key_id=
            sepal_length=float(sepal_length), # 저장하기 전에 숫자로 바꿔줘요
            sepal_width=float(sepal_width),
            petal_length=float(petal_length),
            petal_width=float(petal_width),
            predicted_class=predicted_class,
            confirmed_class=confirmed_class,  # 수정되었거나 저장된 값을 저장해요
            confirm =True
            )

        # 새로운 객체를 데이터베이스 세션에 추가해요.
        db.session.add(new_iris_entry)
        # 변경 사항을 데이터베이스에 실제로 저장해요.
        db.session.commit()
        return redirect(url_for('iris_sk_user.iris_predict')) # 예측 페이지로 다시 이동해요
    
    flash('데이터 저장 중 오류가 발생했습니다.', 'danger')
    return redirect(url_for('iris_sk_user.iris_predict'))






"""
    if request.method == 'POST':
        try:
            sl = float(request.form['sepal_length'])
            sw = float(request.form['sepal_width'])
            pl = float(request.form['petal_length'])
            pw = float(request.form['petal_width'])
        except Exception as e:
            return render_template('iris/index.html', error='입력 오류: '+str(e))
        pred = model.predict([[sl, sw, pl, pw]])[0]
        return render_template('iris/index.html',
                               result=TARGET_NAMES[pred],
                               sepal_length=sl, sepal_width=sw,
                               petal_length=pl, petal_width=pw,
                               api_key=request.form.get('api_key'))
    return render_template('iris/index.html')
"""