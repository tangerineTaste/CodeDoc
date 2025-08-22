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

    // 카드 호버 효과 강화
    const productCards = document.querySelectorAll('.product-cards');
    
    productCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // // 스크롤 애니메이션
    // function animateOnScroll() {
    //     const cards = document.querySelectorAll('.product-cards');
        
    //     cards.forEach(card => {
    //         const cardTop = card.getBoundingClientRect().top;
    //         const cardVisible = 150;
            
    //         if (cardTop < window.innerHeight - cardVisible) {
    //             card.classList.add('animate-in');
    //         }
    //     });
    // }

    // // 스크롤 이벤트 리스너
    // window.addEventListener('scroll', animateOnScroll);
    
    // // 페이지 로드 시 애니메이션 실행
    // animateOnScroll();

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

    // 검색 기능 초기화
    initSearch();
});

// // CSS 애니메이션 클래스 (추가 스타일)
// const style = document.createElement('style');
// style.textContent = `
//     .animate-in {
//         animation: slideInUp 0.6s ease forwards;
//     }
    
//     @keyframes slideInUp {
//         from {
//             opacity: 0;
//             transform: translateY(30px);
//         }
//         to {
//             opacity: 1;
//             transform: translateY(0);
//         }
//     }
    
//     .product-cards {
//         opacity: 0;
//         transform: translateY(30px);
//         transition: all 0.3s ease;
//     }
// `;
// document.head.appendChild(style);