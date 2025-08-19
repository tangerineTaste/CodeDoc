# news_crawling_test.py - 실제 뉴스 크롤링 테스트
from news import NewsDataCrolling
import os
from dotenv import load_dotenv

print("🔍 네이버 뉴스 크롤링 테스트 시작!")
print("=" * 50)

# 환경변수 로드
load_dotenv()

# API 키 확인
client_id = os.getenv('Client_ID')
client_secret = os.getenv('Client_Secret')

print("1. API 키 확인...")
if client_id and client_secret:
    print(f"   ✅ Client ID: {client_id[:10]}...")
    print(f"   ✅ Client Secret: {client_secret[:10]}...")
else:
    print("   ❌ API 키가 설정되지 않았습니다!")
    print("   💡 .env 파일에 다음과 같이 설정하세요:")
    print("      Client_ID=your_naver_client_id")
    print("      Client_Secret=your_naver_client_secret")
    exit()

print("\n2. 뉴스 크롤링 테스트...")

# 실제 뉴스 크롤링 시도
try:
    print("   🔄 '금융' 키워드로 뉴스 5개 수집 중...")
    crawler = NewsDataCrolling("금융", 5)
    news_list = crawler.news_data
    
    if news_list:
        print(f"   ✅ {len(news_list)}개 뉴스 수집 성공!")
        
        print("\n📰 수집된 뉴스 목록:")
        print("-" * 80)
        for i, news in enumerate(news_list, 1):
            print(f"{i}. 제목: {news['title']}")
            print(f"   설명: {news['description']}")
            print(f"   날짜: {news['pubDate']}")
            print(f"   링크: {news['link']}")
            print("-" * 80)
        
        # 금융 뉴스 필터링 테스트
        print("\n3. 금융 뉴스 필터링 테스트...")
        filtered_news = NewsDataCrolling.filter_weather_news(news_list)
        
        if filtered_news:
            print(f"   ✅ 금융 관련 뉴스 {len(filtered_news)}개 필터링됨!")
            
            print("\n🎯 필터링된 금융 뉴스:")
            print("-" * 80)
            for i, news in enumerate(filtered_news, 1):
                print(f"{i}. 제목: {news['title']}")
                print(f"   카테고리: {news['category']}")
                print(f"   출처: {news['source']}")
                print(f"   날짜: {news['pubDate']}")
                print("-" * 80)
        else:
            print("   ⚠️ 금융 관련 뉴스가 필터링되지 않았습니다.")
            print("   💡 키워드를 '경제' 또는 '주식'으로 다시 시도해보세요.")
    
    else:
        print("   ❌ 뉴스 수집 실패!")
        print("   💡 API 키를 다시 확인해보세요.")

except Exception as e:
    print(f"   ❌ 크롤링 오류: {e}")
    import traceback
    traceback.print_exc()

# 다른 키워드로도 테스트
print("\n4. 다른 키워드 테스트...")
test_keywords = ["경제", "주식", "부동산"]

for keyword in test_keywords:
    try:
        print(f"\n   🔄 '{keyword}' 키워드로 뉴스 3개 수집 중...")
        crawler = NewsDataCrolling(keyword, 3)
        news_list = crawler.news_data
        
        if news_list:
            print(f"      ✅ {len(news_list)}개 뉴스 수집됨")
            # 첫 번째 뉴스만 출력
            first_news = news_list[0]
            print(f"      📰 첫 번째 뉴스: {first_news['title'][:60]}...")
        else:
            print(f"      ❌ '{keyword}' 뉴스 수집 실패")
    except Exception as e:
        print(f"      ❌ '{keyword}' 테스트 오류: {e}")

print("\n" + "=" * 50)
print("🎉 뉴스 크롤링 테스트 완료!")
print("💡 결과가 만족스럽다면 Django에 통합하세요!")
