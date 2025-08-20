import os
from datetime import datetime
from dotenv import load_dotenv
import requests
import re
import urllib.parse
from django.conf import settings
from .models import News
from django.utils import timezone

load_dotenv()

class NewsDataCrawling:
    def __init__(self, word, display=100):
        self.word = word
        self.display = display
        self.news_data = self.getnews_data(word, display)

    def getnews_data(self, word, display=100):
        client_id = os.getenv('Client_ID')
        client_secret = os.getenv('Client_Secret')
        
        if not client_id or not client_secret:
            print("네이버 API 키가 설정되지 않았습니다.")
            return self.get_default_news()
        
        encoded_query = urllib.parse.quote(word)
        url = f'https://openapi.naver.com/v1/search/news.json?query={encoded_query}&display={display}'
        
        headers = {
            'X-Naver-Client-Id': client_id,
            'X-Naver-Client-Secret': client_secret
        }
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                items = response.json()['items']
                news_list = []
                
                for idx, item in enumerate(items):
                    link = item.get('link')
                    title = re.sub('<.*?>', '', item.get('title', ''))
                    title = title.replace('&quot;', '"').replace('&amp;', '&')
                    description = re.sub('<.*?>', '', item.get('description', ''))
                    description = description.replace('&quot;', '"').replace('&amp;', '&')
                    
                    news_data = {
                        'no': idx + 1,
                        'title': title,
                        'link': item.get('link', ''),
                        'description': description,
                        'pubDate': item.get('pubDate', ''),
                        'collected_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    news_list.append(news_data)
                
                print(f"'{word}' 관련 뉴스 {len(news_list)}개 수집 완료")
                return news_list
                
            else:
                print(f"API 오류: {response.status_code}")
                return self.get_default_news()
                
        except Exception as e:
            print(f"오류 발생: {e}")
            return self.get_default_news()
    
    @staticmethod
    def filter_finance_news(news_list):
        """금융 관련 뉴스만 필터링"""
        finance_keywords = ['금융', '경제', '투자', '주식', '증권', '채권', '금리', '환율', '외환', '물가', 
                           '인플레이션', '디플레이션', '부동산', '가계부채', '은행', '보험', '연금', 
                           '자산운용', '펀드', '금융정책']
        
        filtered_news = []
        for news in news_list:
            title = news['title'].lower()
            description = news['description'].lower()
            
            # 제목이나 설명에 금융 키워드가 포함된 경우만
            if any(keyword in title or keyword in description for keyword in finance_keywords):
                # 카테고리 분류
                category = classify_news_category(news['title'], news['description'])
                news['category'] = category
                news['source'] = '네이버 뉴스'
                news['pubDate'] = format_date(news['pubDate'])
                filtered_news.append(news)
        
        return filtered_news
    
    def get_default_news(self):
        """기본 뉴스 데이터"""
        return [
            {
                'title': "'세컨드홈' 특례 지역 발표…지방 부동산 살리기 나섰다",
                'description': "정부가 지방 부동산 시장에 활기를 넣기 위해 '세컨드홈' 카드를 다시 꺼내 들었습니다.",
                'link': '#',
                'pubDate': datetime.now().strftime("%a, %d %b %Y %H:%M:%S"),
                'category': '부동산',
                'source': '금융 NEWS'
            },
            {
                'title': '건설업·지역고용 현 상황은?…외채 건전성 지표도 주목',
                'description': "16일 정부 부처에 따르면 통계청은 오는 22일 '2024년 건설업조사 결과(공사실적부문)'를 발표한다.",
                'link': '#',
                'pubDate': datetime.now().strftime("%a, %d %b %Y %H:%M:%S"),
                'category': '경제지표',
                'source': '금융 NEWS'
            },
            {
                'title': "美 금리인하 기대감에, 금융사-기업들 채권 발행 '봇물'",
                'description': '미국 연방준비제도(연준·Fed)가 9월 정책금리를 인하할 것이란 기대감에 신용도가 높은 금융회사부터 투자가 가능한 곳 중 사실상 신용등급이 가장 낮은 BBB급 기업까지 채권 발행을 서두르고 있다.',
                'link': '#',
                'pubDate': datetime.now().strftime("%a, %d %b %Y %H:%M:%S"),
                'category': '채권',
                'source': '금융 NEWS'
            },
            {
                'title': "유안타증권, '주식 모으기 서비스' 출시",
                'description': "유안타증권은 국내외 주식과 ETF·ETN(상장지수펀드·상장지수증권)을 일정 금액 또는 수량 단위로 자동 매수할 수 있는 '주식 모으기 서비스'를 시작한다고 18일 밝혔다.",
                'link': '#',
                'pubDate': datetime.now().strftime("%a, %d %b %Y %H:%M:%S"),
                'category': '주식/증권',
                'source': '금융 NEWS'
            }
        ]

def classify_news_category(title, description):
    """뉴스 카테고리 분류"""
    text = (title + ' ' + description).lower()
    
    if any(word in text for word in ['주식', '증권', '코스피', '코스닥', '나스닥']):
        return '주식/증권'
    elif any(word in text for word in ['채권', '국채', '회사채']):
        return '채권'
    elif any(word in text for word in ['금리', '기준금리', '금융통화위원회']):
        return '금리'
    elif any(word in text for word in ['환율', '외환', '달러', '원화']):
        return '환율/외환'
    elif any(word in text for word in ['부동산', '아파트', '전세', '주택']):
        return '부동산'
    elif any(word in text for word in ['은행', '대출', '가계부채']):
        return '은행/대출'
    elif any(word in text for word in ['보험', '연금']):
        return '보험/연금'
    elif any(word in text for word in ['펀드', '자산운용', '투자']):
        return '투자/자산관리'
    elif any(word in text for word in ['경제', '물가', '인플레이션', '디플레이션']):
        return '경제지표'
    elif any(word in text for word in ['금융정책', '재정정책', '정부대책']):
        return '정책/규제'
    else:
        return '기타금융'

def format_date(date_str):
    """날짜 포맷팅"""
    try:
        dt = datetime.strptime(date_str[:25], "%a, %d %b %Y %H:%M:%S")
        return dt.strftime("%Y.%m.%d")
    except:
        return datetime.now().strftime("%Y.%m.%d")

def save_news_to_db(news_list):
    """뉴스 데이터를 데이터베이스에 저장"""
    saved_count = 0
    for news_item in news_list:
        try:
            # 중복 체크 후 저장
            news_obj, created = News.objects.get_or_create(
                title=news_item['title'],
                link=news_item['link'],
                defaults={
                    'description': news_item['description'],
                    'category': news_item.get('category', '기타금융'),
                    'source': news_item.get('source', '네이버 뉴스'),
                    'pub_date': news_item.get('pubDate', ''),
                    'collected_time': timezone.now()
                }
            )
            if created:
                saved_count += 1
        except Exception as e:
            print(f"뉴스 저장 오류: {e}")
    
    print(f"새로운 뉴스 {saved_count}개 저장 완료")
    return saved_count

def crawl_and_save_news(keywords=['금융', '경제', '투자']):
    """뉴스 크롤링 및 저장 실행"""
    all_news = []
    
    for keyword in keywords:
        crawler = NewsDataCrawling(keyword, display=50)
        news_data = crawler.news_data
        filtered_news = NewsDataCrawling.filter_finance_news(news_data)
        all_news.extend(filtered_news)
    
    # 중복 제거 (제목 기준)
    unique_news = {}
    for news in all_news:
        if news['title'] not in unique_news:
            unique_news[news['title']] = news
    
    # 데이터베이스에 저장
    saved_count = save_news_to_db(list(unique_news.values()))
    
    return saved_count, len(unique_news)
