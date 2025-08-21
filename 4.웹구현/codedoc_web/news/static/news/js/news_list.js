// news/static/news/js/news_list.js

document.addEventListener('DOMContentLoaded', function() {
    // 카테고리 드롭다운 이벤트
    const categorySelect = document.querySelector('.category-select');
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            const form = document.querySelector('#newsFilterForm');
            if (form) {
                form.submit();
            }
        });
    }

    // 탭 버튼 클릭 이벤트
    const tabBtns = document.querySelectorAll('.tab-btn');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // 모든 탭에서 active 클래스 제거
            tabBtns.forEach(b => b.classList.remove('active'));
            
            // 클릭된 탭에 active 클래스 추가
            this.classList.add('active');
            
            // 탭에 따른 필터링 로직
            const tabType = this.getAttribute('data-tab');
            console.log('선택된 탭:', tabType);
            
            // 카테고리별 페이지 이동
            filterByCategory(tabType);
            
            // 드롭다운도 동기화
            if (categorySelect) {
                categorySelect.value = tabType;
            }
        });
    });

    // 검색 기능
    const searchBtn = document.querySelector('.news-search-btn');
    const searchInput = document.querySelector('.search-input');
    
    if (searchBtn && searchInput) {
        searchBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const searchTerm = searchInput.value.trim();
            performSearch(searchTerm);
        });
        
        // 엔터키로 검색
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchBtn.click();
            }
        });
    }

    // 뉴스 아이템 클릭 효과
    const newsItems = document.querySelectorAll('.news-item');
    
    newsItems.forEach(item => {
        item.addEventListener('click', function(e) {
            // 링크 자체를 클릭한 경우가 아니라면
            if (e.target.tagName !== 'A' && !e.target.closest('a')) {
                const link = this.querySelector('.news-title a');
                if (link) {
                    window.open(link.href, '_blank');
                }
            }
        });
    });

    // 페이지네이션 클릭 시 상단으로 스크롤
    const paginationLinks = document.querySelectorAll('.pagination a');
    
    paginationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // 페이지 전환 시 상단으로 부드럽게 스크롤
            setTimeout(() => {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            }, 100);
        });
    });

    // 초기 로드 시 탭과 드롭다운 동기화
    syncTabAndDropdown();

    console.log('News List JavaScript 로드 완료');
});

// 카테고리별 필터링
function filterByCategory(category) {
    const currentUrl = new URL(window.location);
    const currentSearch = currentUrl.searchParams.get('search') || '';
    
    // URL 파라미터 업데이트
    if (category === 'all') {
        currentUrl.searchParams.delete('category');
    } else {
        currentUrl.searchParams.set('category', category);
    }
    
    // 검색어가 있다면 유지
    if (currentSearch) {
        currentUrl.searchParams.set('search', currentSearch);
    }
    
    // 페이지는 1로 리셋
    currentUrl.searchParams.delete('page');
    
    // 페이지 이동
    window.location.href = currentUrl.toString();
}

// 검색 수행
function performSearch(searchTerm) {
    const currentUrl = new URL(window.location);
    const currentCategory = currentUrl.searchParams.get('category') || '';
    
    // 검색어 설정
    if (searchTerm) {
        currentUrl.searchParams.set('search', searchTerm);
    } else {
        currentUrl.searchParams.delete('search');
    }
    
    // 카테고리 유지
    if (currentCategory && currentCategory !== 'all') {
        currentUrl.searchParams.set('category', currentCategory);
    }
    
    // 페이지는 1로 리셋
    currentUrl.searchParams.delete('page');
    
    // 페이지 이동
    window.location.href = currentUrl.toString();
}

// 검색 함수 (실시간 검색용)
function searchNews(searchTerm) {
    const newsItems = document.querySelectorAll('.news-item');
    let visibleCount = 0;
    
    newsItems.forEach(item => {
        const title = item.querySelector('.news-title a').textContent.toLowerCase();
        const isVisible = title.includes(searchTerm.toLowerCase());
        
        if (isVisible) {
            item.style.display = 'flex';
            visibleCount++;
            
            // 검색어 하이라이트
            const titleElement = item.querySelector('.news-title a');
            const originalText = titleElement.textContent;
            const regex = new RegExp(`(${searchTerm})`, 'gi');
            const highlightedText = originalText.replace(regex, '<mark style="background: #fff3cd; padding: 0 2px;">$1</mark>');
            if (highlightedText !== originalText) {
                titleElement.innerHTML = highlightedText;
            }
        } else {
            item.style.display = 'none';
        }
    });
    
    // 검색 결과 개수 업데이트
    const totalCount = document.querySelector('.total-count');
    if (totalCount) {
        totalCount.textContent = `총 ${visibleCount}건`;
    }
    
    // 검색 결과가 없을 때
    if (visibleCount === 0) {
        showNoResults();
    } else {
        hideNoResults();
    }
}

// 검색 결과 없음 표시
function showNoResults() {
    let noResults = document.querySelector('.no-search-results');
    if (!noResults) {
        noResults = document.createElement('div');
        noResults.className = 'no-search-results';
        noResults.innerHTML = '<p>검색 결과가 없습니다.</p>';
        noResults.style.textAlign = 'center';
        noResults.style.padding = '40px';
        noResults.style.color = '#999';
        
        document.querySelector('.news-list').appendChild(noResults);
    }
}

// 검색 결과 없음 숨기기
function hideNoResults() {
    const noResults = document.querySelector('.no-search-results');
    if (noResults) {
        noResults.remove();
    }
}

// 탭과 드롭다운 동기화
function syncTabAndDropdown() {
    const urlParams = new URLSearchParams(window.location.search);
    const currentCategory = urlParams.get('category') || 'all';
    
    // 탭 활성화
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        const tabCategory = btn.getAttribute('data-tab');
        if (tabCategory === currentCategory) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // 드롭다운 선택
    const categorySelect = document.querySelector('.category-select');
    if (categorySelect) {
        categorySelect.value = currentCategory;
    }
}

// 에러 처리
window.addEventListener('error', function(e) {
    console.error('뉴스 페이지 에러:', e.error);
});

// 페이지 가시성 변경 시 처리
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        console.log('뉴스 페이지가 다시 활성화됨');
    }
});