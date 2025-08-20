// =================================
    // 메인페이지 전용 JavaScript
    // =================================

    console.log('script.js 로드 완료!');

    document.addEventListener('DOMContentLoaded', function() {
        console.log('script.js DOMContentLoaded 실행!');
        
        // =================================
        // 상품 슬라이더 기능 (setTimeout 방식)
        // =================================
        setTimeout(function() {
            var container = document.getElementById('productsContainer');
            var prevBtn = document.getElementById('prevBtn');
            var nextBtn = document.getElementById('nextBtn');
            
            console.log('=== 상품 슬라이더 디버깅 ===');
            console.log('container:', container);
            console.log('prevBtn:', prevBtn);
            console.log('nextBtn:', nextBtn);
            
            if (container && prevBtn && nextBtn) {
                var currentIndex = 0;
                var maxIndex = 1;
                var slideWidth = 235;
                
                console.log('상품 슬라이더 초기화 완료');
                
                function updateSlider() {
                    var translateX = -currentIndex * slideWidth;
                    container.style.transform = 'translateX(' + translateX + 'px)';
                    container.style.transition = 'transform 0.3s ease';
                    console.log('슬라이더 이동:', translateX + 'px');
                }
                
                prevBtn.addEventListener('click', function() {
                    console.log('이전 버튼 클릭, 현재 인덱스:', currentIndex);
                    currentIndex = Math.max(0, currentIndex - 1);
                    updateSlider();
                });
                
                nextBtn.addEventListener('click', function() {
                    console.log('다음 버튼 클릭, 현재 인덱스:', currentIndex);
                    currentIndex = Math.min(maxIndex, currentIndex + 1);
                    updateSlider();
                });
                
                // 초기 상태 설정
                updateSlider();
            } else {
                console.log('상품 슬라이더 요소를 찾을 수 없습니다!');
                console.log('HTML에서 id 확인 필요: productsContainer, prevBtn, nextBtn');
            }
        }, 1000); // 1초 후 실행

        // =================================
        // main slide
        // =================================

        let currentSlide = 0;
        const slides = document.querySelectorAll('.main-slide .slide-content');
        const indicators = document.querySelectorAll('.carousel-indicators .indicator');
        const prevBtn = document.querySelector('.carousel-btn.prev');
        const nextBtn = document.querySelector('.carousel-btn.next');

        function showSlide(index) {
            // 먼저 모든 슬라이드 비활성화
            slides.forEach((slide, i) => {
                slide.classList.remove('active');
                indicators[i].classList.remove('active');
            });
            
            // 짧은 지연 후 새 슬라이드 활성화
            setTimeout(() => {
                slides[index].classList.add('active');
                indicators[index].classList.add('active');
                currentSlide = index;
            }, 50);
        }

        if (prevBtn && nextBtn) {
            prevBtn.addEventListener('click', () => {
                let newIndex = (currentSlide - 1 + slides.length) % slides.length;
                showSlide(newIndex);
            });

            nextBtn.addEventListener('click', () => {
                let newIndex = (currentSlide + 1) % slides.length;
                showSlide(newIndex);
            });
        }

        // 인디케이터 클릭
        indicators.forEach((indicator, i) => {
            indicator.addEventListener('click', () => showSlide(i));
        });

        // =================================
        // 챗봇 아이콘 클릭 이벤트
        // =================================
        var chatbotBtn = document.getElementById('chatbotBtn');
        if (chatbotBtn) {
            chatbotBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
                // 클릭 애니메이션
                this.style.transform = 'translateY(-1px) scale(0.95)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);
                
                // 챗봇 페이지로 이동
                window.location.href = '/chatbot/';
            });
        }

        // =================================
        // 공지사항 아이템 클릭 이벤트
        // =================================
        var noticeItems = document.querySelectorAll('.notice-item-card');
        noticeItems.forEach(function(item) {
            item.addEventListener('click', function() {
                // 클릭 애니메이션
                this.style.transform = 'translateX(8px) scale(0.98)';
                this.style.transition = 'transform 0.15s ease';
                
                var self = this;
                setTimeout(function() {
                    // 공지사항 목록 페이지로 이동
                    window.location.href = '/customer_support/notices/';
                }, 150);
            });
        });

        // =================================
        // 더보기 버튼 클릭 이벤트
        // =================================
        var moreBtn = document.querySelector('.more-btn');
        if (moreBtn) {
            moreBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
                // 클릭 애니메이션
                this.style.transform = 'translateY(-3px) scale(0.95)';
                this.style.transition = 'transform 0.15s ease';
                
                var self = this;
                setTimeout(function() {
                    window.location.href = '/customer_support/notices/';
                }, 150);
            });
        }

        // =================================
        // 기타 UI 기능들
        // =================================
        
        // CTA 버튼 클릭 이벤트
        var ctaButton = document.querySelector('.cta-button');
        if (ctaButton) {
            ctaButton.addEventListener('click', function(e) {
                e.preventDefault();
                
                // 버튼 클릭 애니메이션
                this.style.transform = 'scale(0.95) translateY(-2px)';
                this.style.transition = 'transform 0.15s ease';
                
                setTimeout(function() {
                    ctaButton.style.transform = 'translateY(-2px)';
                }, 150);

                console.log('상품 추천받기 클릭됨');
            });
        }

        // 상품찾기 버튼 클릭 이벤트
        var searchBtn = document.getElementById('searchBtn');
        if (searchBtn) {
            searchBtn.addEventListener('click', function(e) {
                e.preventDefault();
                console.log('상품찾기 클릭됨');
            });
        }

        // 자주 찾는 메뉴 클릭 이벤트
        var menuItems = document.querySelectorAll('.frequent-menu .quik');
        for (var i = 0; i < menuItems.length; i++) {
            (function(index) {
                var item = menuItems[index];
                
                item.addEventListener('click', function() {
                    var menuIcon = this.querySelector('.menu-icon');
                    var menuText = this.querySelector('.menu-text').textContent;
                    
                    // 클릭 애니메이션
                    this.style.transform = 'translateY(-5px) scale(0.95)';
                    this.style.transition = 'transform 0.15s ease';
                    
                    var self = this;
                    setTimeout(function() {
                        self.style.transform = 'translateY(-3px)';
                    }, 150);
                    
                    // 아이콘 펄스 효과
                    if (menuIcon) {
                        menuIcon.style.transform = 'scale(1.1)';
                        setTimeout(function() {
                            menuIcon.style.transform = 'scale(1)';
                        }, 200);
                    }
                    
                    console.log(menuText + ' 메뉴 클릭됨');
                });
                
                // 호버 효과 강화
                item.addEventListener('mouseenter', function() {
                    var menuIcon = this.querySelector('.menu-icon');
                    if (menuIcon) {
                        menuIcon.style.transform = 'scale(1.05)';
                        menuIcon.style.transition = 'transform 0.3s ease';
                    }
                });
                
                item.addEventListener('mouseleave', function() {
                    var menuIcon = this.querySelector('.menu-icon');
                    if (menuIcon) {
                        menuIcon.style.transform = 'scale(1)';
                    }
                });
            })(i);
        }
    });