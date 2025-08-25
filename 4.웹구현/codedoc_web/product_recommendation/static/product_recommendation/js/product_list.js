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
            
            // 상품 섹션 필터링
            filterProducts(filter);
        });
    });

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
        
        aiCards.forEach((card, index) => {
            // AI 추천 카드에 딜레이 애니메이션 추가
            setTimeout(() => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    card.style.transition = 'all 0.5s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, 100);
            }, index * 150); // 연속적인 애니메이션
        });
        
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
    
    // 필터 버튼에 카테고리별 추천 처리 추가
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            handleCategoryRecommendations(filter);
        });
    });

    console.log('상품 목록 페이지 초기화 완료');
    console.log('AI 추천 상품 수:', document.querySelectorAll('.ai-recommended').length);
});
