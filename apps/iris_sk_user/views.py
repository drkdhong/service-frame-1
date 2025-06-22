from flask import Flask, request, render_template, jsonify, abort, current_app
import pickle
import os

import numpy as np
from flask_login import login_required
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
                               petal_length=petal_length, petal_width=petal_width, form=form
                              )
    return render_template('iris_sk_user/index.html',form=form)

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