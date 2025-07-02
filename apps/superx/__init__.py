# apps/superx/__init__.py
from flask import Blueprint

superx = Blueprint('superx', __name__, template_folder='templates')

from . import views  # views.py import해서 라우팅 등록