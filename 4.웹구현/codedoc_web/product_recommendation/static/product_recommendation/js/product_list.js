document.addEventListener('DOMContentLoaded', function() {
    // 필터 버튼들
    const filterBtns = document.querySelectorAll('.filter-btn');
    const productSections = document.querySelectorAll('.products-section');

    // 필터 버튼 클릭 이벤트
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            
            // 모든 버튼에서 active 클래스 제거
            filterBtns.forEach(b => b.classList.remove('active'));
            
            // 클릭된 버튼에 active 클래스 추가
            this.classList.add('active');
            
            // 카테고리 전환 시 페이지네이션 초기화
            const currentUrl = new URL(window.location.href);
            
            // 모든 페이지네이션 파라미터 제거
            currentUrl.searchParams.delete('page');
            currentUrl.searchParams.delete('deposits_page');
            currentUrl.searchParams.delete('savings_page');
            currentUrl.searchParams.delete('funds_page');
            currentUrl.searchParams.delete('stocks_page');
            currentUrl.searchParams.delete('mmf_page');
            
            // 카테고리 파라미터 설정
            if (filter !== 'all') {
                currentUrl.searchParams.set('category', filter);
            } else {
                currentUrl.searchParams.delete('category');
            }
            
            // URL 업데이트하고 페이지 새로고침
            window.location.href = currentUrl.toString();
        });
    });

    // 페이지네이션 링크 클릭 이벤트 처리 (수정된 부분)
    function initPaginationHandlers() {
        const paginationLinks = document.querySelectorAll('.pagination a');
        
        paginationLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                // 현재 활성화된 카테고리 확인
                const activeFilter = document.querySelector('.filter-btn.active');
                const currentCategory = activeFilter ? activeFilter.getAttribute('data-filter') : 'all';
                
                // 전체 탭이 아닌 경우에만 URL 파라미터에서 다른 페이지 번호들 제거
                if (currentCategory !== 'all') {
                    const url = new URL(this.href);
                    
                    // 현재 카테고리가 아닌 다른 페이지네이션 파라미터들 제거
                    const otherPageParams = ['page', 'deposits_page', 'savings_page', 'funds_page', 'stocks_page', 'mmf_page'];
                    const currentPageParam = getCurrentPageParam(currentCategory);
                    
                    otherPageParams.forEach(param => {
                        if (param !== currentPageParam) {
                            url.searchParams.delete(param);
                        }
                    });
                    
                    this.href = url.toString();
                }
            });
        });
    }

    // 현재 카테고리에 맞는 페이지 파라미터 이름 반환 (새로 추가된 함수)
    function getCurrentPageParam(category) {
        switch(category) {
            case 'deposit': return 'deposits_page';
            case 'saving': return 'savings_page';
            case 'fund': return 'funds_page';
            case 'stock': return 'stocks_page';
            case 'mmf': return 'mmf_page';
            default: return 'page';
        }
    }

    // 상품 필터링 함수
    function filterProducts(filter) {
        productSections.forEach(section => {
            const category = section.getAttribute('data-category');
            
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
        });
        
        // 카테고리별 AI 추천 상품 처리
        handleCategoryRecommendations(filter);
        
        // 페이지네이션 핸들러 재초기화
        setTimeout(() => {
            initPaginationHandlers();
        }, 100);
    }

    // 페이지 로드 시 URL 파라미터 확인하여 카테고리 설정
    function initFromUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const categoryParam = urlParams.get('category');
        
        if (categoryParam) {
            // URL에 카테고리 파라미터가 있으면 해당 탭 활성화
            const targetBtn = document.querySelector(`[data-filter="${categoryParam}"]`);
            if (targetBtn) {
                // 모든 버튼에서 active 제거
                filterBtns.forEach(b => b.classList.remove('active'));
                // 해당 버튼 활성화
                targetBtn.classList.add('active');
                // 상품 필터링
                filterProducts(categoryParam);
            }
        } else {
            // 파라미터가 없으면 전체 탭 활성화
            const allBtn = document.querySelector('[data-filter="all"]');
            if (allBtn) {
                filterBtns.forEach(b => b.classList.remove('active'));
                allBtn.classList.add('active');
                filterProducts('all');
            }
        }
    }

    // 섹션 애니메이션
    function animateSection(section) {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            section.style.transition = 'all 0.3s ease';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, 50);
    }

    // AI 추천 카드 특별 효과
    function initAIRecommendations() {
        const aiCards = document.querySelectorAll('.ai-recommended');
        
        // aiCards.forEach((card, index) => {
        //     // AI 추천 카드에 딜레이 애니메이션 추가
        //     setTimeout(() => {
        //         card.style.opacity = '0';
        //         card.style.transform = 'translateY(20px)';
                
        //         setTimeout(() => {
        //             card.style.transition = 'all 0.5s ease';
        //             card.style.opacity = '1';
        //             card.style.transform = 'translateY(0)';
        //         }, 100);
        //     }, index * 150); // 연속적인 애니메이션
        // });
        
        // AI 추천 카드 클릭 이벤트 (추후 상세 페이지 연동)
        aiCards.forEach(card => {
            card.addEventListener('click', function() {
                // 추후 상세 페이지로 이동 또는 모달 표시
                console.log('AI 추천 상품 클릭:', this.querySelector('.product-name').textContent);
            });
        });
    }
    
    // 카드 호버 효과 초기화
    function initCardHoverEffects() {
        const productCards = document.querySelectorAll('.product-cards');
        
        productCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                if (!this.classList.contains('ai-recommended')) {
                    this.style.transform = 'translateY(-5px) scale(1.01)';
                } else {
                    this.style.transform = 'translateY(-8px) scale(1.02)';
                }
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
        });
    }

    // 검색 기능 (추후 확장 가능)
    function initSearch() {
        const searchInput = document.querySelector('#productSearch');
        
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                searchProducts(searchTerm);
            });
        }
    }

    // 상품 검색 함수
    function searchProducts(searchTerm) {
        const productCards = document.querySelectorAll('.product-cards');
        
        productCards.forEach(card => {
            const productName = card.querySelector('.product-name').textContent.toLowerCase();
            const companyName = card.querySelector('.info-value').textContent.toLowerCase();
            
            if (productName.includes(searchTerm) || companyName.includes(searchTerm)) {
                card.style.display = 'block';
                card.style.opacity = '1';
            } else {
                card.style.display = 'none';
                card.style.opacity = '0';
            }
        });
    }

    // 카테고리별 AI 추천 상품 표시/숨김 처리
    function handleCategoryRecommendations(filter) {
        const categoryRecommendations = document.querySelectorAll('.category-recommendation');
        
        categoryRecommendations.forEach(rec => {
            const parent = rec.closest('.products-section');
            const parentCategory = parent.getAttribute('data-category');
            
            if (parentCategory === filter || (filter === 'all' && parentCategory === 'all')) {
                rec.style.display = 'block';
            } else {
                rec.style.display = 'none';
            }
        });
    }

    // 초기화 함수들 실행
    initSearch();
    initAIRecommendations();
    initCardHoverEffects();
    initPaginationHandlers();
    initFromUrlParams(); // URL 파라미터 기반 초기 상태 설정

    console.log('상품 목록 페이지 초기화 완료');
    console.log('AI 추천 상품 수:', document.querySelectorAll('.ai-recommended').length);
});