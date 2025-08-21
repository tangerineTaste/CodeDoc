# home/context_processors.py
from django.conf import settings

def static_version(request):
    """
    모든 템플릿에서 STATIC_VERSION 변수를 사용할 수 있도록 하는 context processor
    CSS/JS 파일의 캐시 버스팅을 위해 사용됩니다.
    
    템플릿에서 {{ STATIC_VERSION }}로 사용 가능
    """
    return {
        'STATIC_VERSION': getattr(settings, 'STATIC_VERSION', '1.0.0')
    }