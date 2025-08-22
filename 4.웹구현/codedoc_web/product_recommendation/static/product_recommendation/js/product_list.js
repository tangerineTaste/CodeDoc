document.addEventListener('DOMContentLoaded', function() {
    // 필터 버튼들 (6개로 확장)
    var filterBtns = document.querySelectorAll('.filter-btn');
    var productSections = document.querySelectorAll('.products-section');

    // URL 파라미터에서 현재 활성 탭 감지
    function getActiveTabFromURL() {
        var urlParams = new URLSearchParams(window.location.search);
        
        if (urlParams.has('deposits_page')) {
            return 'deposit';
        } else if (urlParams.has('savings_page')) {
            return 'saving';
        } else if (urlParams.has('funds_page')) {
            return 'fund';
        } else if (urlParams.has('stocks_page')) {
            return 'stock';
        } else if (urlParams.has('mmf_page')) {
            return 'mmf';
        } else if (urlParams.has('page')) {
            return 'all';
        }
        
        return 'all'; // 기본값
    }

    // 페이지 로드 시 올바른 탭 활성화
    function initializeCorrectTab() {
        var activeTab = getActiveTabFromURL();
        
        // 모든 버튼에서 active 클래스 제거
        for (var i = 0; i < filterBtns.length; i++) {
            filterBtns[i].classList.remove('active');
        }
        
        // 올바른 버튼에 active 클래스 추가
        var correctBtn = document.querySelector('.filter-btn[data-filter="' + activeTab + '"]');
        if (correctBtn) {
            correctBtn.classList.add('active');
        }
        
        // 해당 섹션 표시
        filterProducts(activeTab);
    }

    // 필터 버튼 클릭 이벤트
    for (var i = 0; i < filterBtns.length; i++) {
        filterBtns[i].addEventListener('click', function() {
            var filter = this.getAttribute('data-filter');
            
            // 모든 버튼에서 active 클래스 제거
            for (var j = 0; j < filterBtns.length; j++) {
                filterBtns[j].classList.remove('active');
            }
            
            // 클릭된 버튼에 active 클래스 추가
            this.classList.add('active');
            
            // 상품 섹션 필터링
            filterProducts(filter);
        });
    }

    // 상품 필터링 함수 (6개 카테고리 지원)
    function filterProducts(filter) {
        for (var i = 0; i < productSections.length; i++) {
            var section = productSections[i];
            var category = section.getAttribute('data-category');
            
            if (filter === 'all') {
                // 전체 탭: 전체 섹션만 표시, 나머지는 숨김
                if (category === 'all') {
                    section.style.display = 'block';
                    animateSection(section);
                } else {
                    section.style.display = 'none';
                }
            } else if (category === filter) {
                // 해당 카테고리만 표시, 전체 섹션은 숨김
                section.style.display = 'block';
                animateSection(section);
            } else {
                // 나머지 숨김
                section.style.display = 'none';
            }
        }
    }

    // 섹션 애니메이션
    function animateSection(section) {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        
        setTimeout(function() {
            section.style.transition = 'all 0.3s ease';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, 50);
    }

    // 카드 호버 효과 강화
    var productCards = document.querySelectorAll('.product-cards');
    
    for (var i = 0; i < productCards.length; i++) {
        productCards[i].addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        productCards[i].addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    }

    // 상품 타입별 배지 색상 동적 적용
    function applyBadgeColors() {
        var badges = document.querySelectorAll('.product-badge');
        
        for (var i = 0; i < badges.length; i++) {
            var badge = badges[i];
            var text = badge.textContent;
            if (text.indexOf('펀드') !== -1) {
                badge.style.backgroundColor = '#ff9800';
            } else if (text.indexOf('주식') !== -1) {
                badge.style.backgroundColor = '#f44336';
            } else if (text.indexOf('MMF') !== -1) {
                badge.style.backgroundColor = '#4caf50';
            } else if (text.indexOf('예금') !== -1 || text.indexOf('적금') !== -1) {
                badge.style.backgroundColor = '#0078FE';
            }
        }
    }

    // 등락률 색상 적용
    function applyRateColors() {
        var rateElements = document.querySelectorAll('.rate-positive, .rate-negative');
        
        for (var i = 0; i < rateElements.length; i++) {
            var element = rateElements[i];
            if (element.classList.contains('rate-positive')) {
                element.style.color = '#2e7d32';
            } else if (element.classList.contains('rate-negative')) {
                element.style.color = '#c62828';
            }
        }
    }

    // 검색 기능 (추후 확장 가능)
    function initSearch() {
        var searchInput = document.querySelector('#productSearch');
        
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                var searchTerm = this.value.toLowerCase();
                searchProducts(searchTerm);
            });
        }
    }

    // 상품 검색 함수 (모든 상품 타입 지원)
    function searchProducts(searchTerm) {
        var productCards = document.querySelectorAll('.product-cards');
        
        for (var i = 0; i < productCards.length; i++) {
            var card = productCards[i];
            var productName = card.querySelector('.product-name').textContent.toLowerCase();
            var companyNameElement = card.querySelector('.info-value');
            var companyName = companyNameElement ? companyNameElement.textContent.toLowerCase() : '';
            
            // 태그 텍스트 수집
            var tagElements = card.querySelectorAll('.tag');
            var matchesTag = false;
            for (var j = 0; j < tagElements.length; j++) {
                if (tagElements[j].textContent.toLowerCase().indexOf(searchTerm) !== -1) {
                    matchesTag = true;
                    break;
                }
            }
            
            var matchesSearch = productName.indexOf(searchTerm) !== -1 || 
                              companyName.indexOf(searchTerm) !== -1 ||
                              matchesTag;
            
            if (matchesSearch) {
                card.style.display = 'block';
                card.style.opacity = '1';
            } else {
                card.style.display = 'none';
                card.style.opacity = '0';
            }
        }
    }

    // 숫자 포맷팅 함수 (주식 가격, 수익률 등)
    function formatNumbers() {
        var priceElements = document.querySelectorAll('.rate-highlight');
        
        for (var i = 0; i < priceElements.length; i++) {
            var element = priceElements[i];
            var text = element.textContent;
            // 숫자에 천 단위 콤마 추가 (이미 포맷된 경우 제외)
            if (text.indexOf('원') !== -1 && text.indexOf(',') === -1) {
                var number = text.replace(/[^\d]/g, '');
                if (number) {
                    var formatted = parseInt(number, 10).toLocaleString();
                    element.textContent = formatted + '원';
                }
            }
        }
    }

    // 페이지 로드 시 초기화 실행
    applyBadgeColors();
    applyRateColors();
    formatNumbers();
    initSearch();
    
    // 페이지 로드 시 올바른 탭 활성화
    initializeCorrectTab();

    // 필터 변경 시 색상 재적용
    for (var i = 0; i < filterBtns.length; i++) {
        filterBtns[i].addEventListener('click', function() {
            setTimeout(function() {
                applyBadgeColors();
                applyRateColors();
                formatNumbers();
            }, 100);
        });
    }
});