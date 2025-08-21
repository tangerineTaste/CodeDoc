// customer_support/static/customer_support/js/notice.js

document.addEventListener('DOMContentLoaded', function() {
    // 탭 버튼 클릭 이벤트
    const tabBtns = document.querySelectorAll('.tab-btn');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // 모든 탭에서 active 클래스 제거
            tabBtns.forEach(b => b.classList.remove('active'));
            
            // 클릭된 탭에 active 클래스 추가
            this.classList.add('active');
            
            // 탭에 따른 필터링 로직 (추후 구현)
            const tabType = this.getAttribute('data-tab');
            console.log('선택된 탭:', tabType);
        });
    });

    // 검색 기능
    const searchBtn = document.querySelector('.notice-search-btn');
    const searchInput = document.querySelector('.search-input');
    
    if (searchBtn && searchInput) {
        searchBtn.addEventListener('click', function() {
            const searchTerm = searchInput.value.trim();
            if (searchTerm) {
                console.log('검색어:', searchTerm);
                // 실제 검색 로직 구현
                searchNotices(searchTerm);
            }
        });
        
        // 엔터키로 검색
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchBtn.click();
            }
        });
    }

    // 공지사항 아이템 클릭 효과
    const noticeItems = document.querySelectorAll('.notice-item');
    
    noticeItems.forEach(item => {
        item.addEventListener('click', function() {
            const link = this.querySelector('.notice-title a');
            if (link) {
                window.location.href = link.href;
            }
        });
    });
});

// 검색 함수
function searchNotices(searchTerm) {
    const noticeItems = document.querySelectorAll('.notice-item');
    let visibleCount = 0;
    
    noticeItems.forEach(item => {
        const title = item.querySelector('.notice-title a').textContent.toLowerCase();
        const isVisible = title.includes(searchTerm.toLowerCase());
        
        if (isVisible) {
            item.style.display = 'flex';
            visibleCount++;
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
        
        document.querySelector('.notice-list').appendChild(noResults);
    }
}

// 검색 결과 없음 숨기기
function hideNoResults() {
    const noResults = document.querySelector('.no-search-results');
    if (noResults) {
        noResults.remove();
    }
}