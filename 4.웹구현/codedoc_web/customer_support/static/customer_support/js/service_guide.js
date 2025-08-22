// customer_support/static/customer_support/js/service_guide.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('서비스 가이드 페이지 로드 완료');
    
    // 호버 효과는 모두 제거하고 기본 기능만 유지
    
    // 부드러운 스크롤 기능
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            const target = document.querySelector(href);
            
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // CTA 버튼 클릭 로깅
    const ctaButtons = document.querySelectorAll('.cta-btn');
    
    ctaButtons.forEach(button => {
        button.addEventListener('click', function() {
            console.log('CTA 버튼 클릭:', this.textContent);
        });
    });
});