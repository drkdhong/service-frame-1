from flask import Blueprint

#main = Blueprint('main', __name__,static_folder='static', template_folder='templates')
main = Blueprint('main', __name__, template_folder='templates')
#main = Blueprint('main', __name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

from . import views  # views.py import해서 라우팅 등록
