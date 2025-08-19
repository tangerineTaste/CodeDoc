from django.apps import AppConfig
import threading
import sys

class NewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "news"
    
    def ready(self):
        # runserver로 실행할 때만 자동 크롤링 시작
        if 'runserver' in sys.argv:
            from .auto_crawler import start_auto_crawler
            # 3초 후 시작
            threading.Timer(3.0, start_auto_crawler).start()
