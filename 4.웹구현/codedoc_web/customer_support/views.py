from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

def notice_list(request):
    """공지사항 목록 페이지"""
    # 임시 공지사항 데이터 (더 많은 데이터 추가)
    notices = [
        {'id': 1, 'title': '집중호우로 인한 수해 피해고객 특별지원 안내', 'date': '2025.07.23', 'is_new': True, 'content': '...'},
        {'id': 2, 'title': '통장생명 우리금융그룹 편입 안내', 'date': '2025.07.08', 'is_new': False, 'content': '...'},
        {'id': 3, 'title': '신용등 진위확인 서비스 임시 중단 안내', 'date': '2025.07.03', 'is_new': False, 'content': '...'},
        {'id': 4, 'title': '시스템 점검 관련 안내', 'date': '2025.06.30', 'is_new': False, 'content': '...'},
        {'id': 5, 'title': '개인정보처리방침 개정 안내', 'date': '2025.06.19', 'is_new': False, 'content': '...'},
        {'id': 6, 'title': '전자금융거래 관련 약관 개정 안내', 'date': '2025.05.30', 'is_new': False, 'content': '...'},
        {'id': 7, 'title': '휴일 고객센터 운영시간 변경 안내', 'date': '2025.05.25', 'is_new': False, 'content': '...'},
        {'id': 8, 'title': '모바일 앱 업데이트 안내', 'date': '2025.05.20', 'is_new': False, 'content': '...'},
        {'id': 9, 'title': '보안인증서 갱신 안내', 'date': '2025.05.15', 'is_new': False, 'content': '...'},
        {'id': 10, 'title': '금리 변동 안내', 'date': '2025.05.10', 'is_new': False, 'content': '...'},
        {'id': 11, 'title': '신규 서비스 런칭 안내', 'date': '2025.05.05', 'is_new': False, 'content': '...'},
        {'id': 12, 'title': '고객 만족도 조사 안내', 'date': '2025.04.30', 'is_new': False, 'content': '...'},
        {'id': 13, 'title': '연말정산 서비스 안내', 'date': '2025.04.25', 'is_new': False, 'content': '...'},
        {'id': 14, 'title': '특별 프로모션 이벤트 안내', 'date': '2025.04.20', 'is_new': False, 'content': '...'},
        {'id': 15, 'title': '약관 및 정책 변경사항 안내', 'date': '2025.04.15', 'is_new': False, 'content': '...'},
    ]
    
    # 페이지네이션 (10개씩)
    paginator = Paginator(notices, 10)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    context = {
        'notices': page_obj,
        'total_count': len(notices)
    }
    
    return render(request, 'customer_support/notice_list.html', context)
    
    # 페이지네이션 (10개씩)
    paginator = Paginator(notices, 10)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    context = {
        'notices': page_obj,
        'total_count': len(notices)
    }
    
    return render(request, 'customer_support/notice_list.html', context)

def notice_detail(request, notice_id):
    """공지사항 상세 페이지"""
    # 임시 데이터에서 해당 공지사항 찾기
    notices = [
        {
            'id': 1,
            'title': '집중호우로 인한 수해 피해고객 특별지원 안내',
            'date': '2025.07.23',
            'content': '집중호우로 피해를 입으신 고객님들께 특별 지원을 안내드립니다. 자세한 사항은 고객센터로 문의해주세요.'
        },
        # 나머지 공지사항들...
    ]
    
    notice = None
    for n in notices:
        if n['id'] == notice_id:
            notice = n
            break
    
    if not notice:
        notice = {'id': notice_id, 'title': '공지사항을 찾을 수 없습니다.', 'date': '', 'content': ''}
    
    context = {'notice': notice}
    return render(request, 'customer_support/notice_detail.html', context)

def service_guide(request):
    """서비스 가이드 페이지"""
    guides = [
        {
            'id': 1,
            'title': '회원가입 및 로그인 가이드',
            'date': '2025.01.15',
            'category': '기본서비스'
        },
        {
            'id': 2,
            'title': '상품 가입 절차 안내',
            'date': '2025.01.10',
            'category': '상품가입'
        },
        {
            'id': 3,
            'title': '온라인 뱅킹 이용 방법',
            'date': '2025.01.05',
            'category': '온라인서비스'
        },
    ]
    
    context = {'guides': guides}
    return render(request, 'customer_support/service_guide.html', context)