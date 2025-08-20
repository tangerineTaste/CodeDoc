from django.core.management.base import BaseCommand
from news.crawler import crawl_and_save_news

class Command(BaseCommand):
    help = '뉴스를 크롤링하고 데이터베이스에 저장합니다'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keywords',
            type=str,
            default='금융,경제,투자',
            help='크롤링할 키워드들 (쉼표로 구분)'
        )

    def handle(self, *args, **options):
        keywords = options['keywords'].split(',')
        
        self.stdout.write(f'뉴스 크롤링 시작: {keywords}')
        
        try:
            saved_count, total_count = crawl_and_save_news(keywords)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'뉴스 크롤링 완료! 총 {total_count}개 중 {saved_count}개 새로 저장됨'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'크롤링 오류: {e}')
            )
