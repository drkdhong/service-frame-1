from sqlalchemy import or_
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from apps.dbmodels import AIService, Subscription
from apps.main import main
from apps.main.forms import SearchServiceForm
from apps import db
from datetime import datetime

@main.route("/")
def index():
#    if current_user.is_authenticated:
#        return render_template("main/index.html", username=current_user.username)
    return render_template("main/index.html")

@main.route('/services', methods=['GET', 'POST'])
def services():
    """AI 서비스 목록 및 검색 기능."""
    form = SearchServiceForm()
    query = request.args.get('query', '') # URL 파라미터에서 검색어 가져오기
    services_query = AIService.query # 모든 서비스 조회 쿼리 시작

    if form.validate_on_submit(): # 폼이 제출되었을 때
        query = form.search_query.data
        if query:
            # 서비스명, 설명, 키워드에서 검색어 포함 여부 확인 (대소문자 구분 없음)
            services_query = services_query.filter(or_(
                AIService.name.ilike(f'%{query}%'),
                AIService.description.ilike(f'%{query}%'),
                AIService.keywords.ilike(f'%{query}%')
            ))
        else:
            flash('검색어를 입력해주세요.', 'warning')
    elif query: # URL 파라미터로 직접 검색어가 넘어왔을 때 (예: /services?query=iris)
        services_query = services_query.filter(
            or_( # 여기에 단일 or_ 호출 결과가 filter에 전달됩니다.
                AIService.name.ilike(f'%{query}%'),
                AIService.description.ilike(f'%{query}%'),
                AIService.keywords.ilike(f'%{query}%')
            )
        )
    ai_services = services_query.all() # 최종 쿼리 실행하여 서비스 목록 가져오기
    return render_template('main/services.html', title='AI 서비스 목록', ai_services=ai_services, form=form, query=query)

@main.route('/subscribe/<int:service_id>', methods=['POST'])
@login_required # 로그인된 사용자만 구독 가능
def subscribe(service_id):
    """AI 서비스 구독 요청 처리."""
    service = AIService.query.get_or_404(service_id) # 서비스 ID로 서비스 조회, 없으면 404
    
    # 이미 구독 요청이 있는지 확인
    existing_subscription = Subscription.query.filter_by(user_id=current_user.id, ai_service_id=service.id).first()

    if existing_subscription:
        flash(f'이미 "{service.name}" 서비스에 대한 구독 신청이 존재합니다 (상태: {existing_subscription.status}).', 'info')
    else:
        # 새 구독 요청 생성
        new_subscription = Subscription(user_id=current_user.id, ai_service_id=service.id, status='pending', request_date=datetime.utcnow())
        db.session.add(new_subscription)
        db.session.commit()
        flash(f'"{service.name}" 서비스에 대한 구독이 성공적으로 신청되었습니다. 관리자의 승인을 기다려주세요.', 'success')

    return redirect(url_for('main.services'))



