import threading
import time
from .crawler import crawl_and_save_news

class AutoNewsCrawler:
    def __init__(self, interval_hours=1):
        self.interval = interval_hours * 3600  # 초 단위로 변환
        self.timer = None
        self.is_running = False
        
    def start(self):
        """자동 크롤링 시작"""
        if not self.is_running:
            self.is_running = True
            print("뉴스 자동 크롤링이 시작되었습니다. (1시간마다 실행)")
            self._run()
    
    def stop(self):
        """자동 크롤링 중지"""
        if self.timer:
            self.timer.cancel()
        self.is_running = False
        print("뉴스 자동 크롤링이 중지되었습니다.")
    
    def _run(self):
        """실제 크롤링 실행"""
        try:
            keywords = ['금융', '경제', '투자', '주식', '부동산']
            saved_count, total_count = crawl_and_save_news(keywords)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 뉴스 크롤링 완료: {saved_count}/{total_count}")
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 크롤링 오류: {e}")
        
        # 다음 실행 예약
        if self.is_running:
            self.timer = threading.Timer(self.interval, self._run)
            self.timer.start()

# 전역 인스턴스
auto_crawler = AutoNewsCrawler(interval_hours=1)

# Django 서버 시작시 자동으로 크롤링 시작
def start_auto_crawler():
    auto_crawler.start()
