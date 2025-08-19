// =================================
// 메인페이지 전용 JavaScript
// =================================

console.log('script.js 로드 완료!');

document.addEventListener('DOMContentLoaded', function() {
    console.log('script.js DOMContentLoaded 실행!');
    // =================================
    // 메인 배너 슬라이드 기능
    // =================================
    var currentSlide = 5;
    var totalSlides = 7;
    var isPlaying = true;
    var slideInterval;

    var prevBtn = document.querySelector('.prev-btn');
    var nextBtn = document.querySelector('.next-btn');
    var pauseBtn = document.querySelector('.pause-btn');
    var currentIndicator = document.querySelector('.indicator.active');

    // 슬라이드 번호 업데이트
    function updateSlideNumber() {
        if (currentIndicator) {
            currentIndicator.textContent = currentSlide;
        }
    }

    // 이전 슬라이드
    function prevSlide() {
        currentSlide = currentSlide > 1 ? currentSlide - 1 : totalSlides;
        updateSlideNumber();
        addSlideAnimation();
    }

    // 다음 슬라이드
    function nextSlide() {
        currentSlide = currentSlide < totalSlides ? currentSlide + 1 : 1;
        updateSlideNumber();
        addSlideAnimation();
    }

    // 자동 재생 시작
    function startAutoplay() {
        slideInterval = setInterval(nextSlide, 4000);
        isPlaying = true;
        if (pauseBtn) {
            pauseBtn.innerHTML = '⏸';
            pauseBtn.title = '정지';
        }
    }

    // 자동 재생 정지
    function stopAutoplay() {
        clearInterval(slideInterval);
        isPlaying = false;
        if (pauseBtn) {
            pauseBtn.innerHTML = '▶';
            pauseBtn.title = '재생';
        }
    }

    // 슬라이드 애니메이션 효과
    function addSlideAnimation() {
        var mainSlide = document.querySelector('.main-slide');
        if (mainSlide) {
            mainSlide.style.transform = 'translateX(-5px)';
            mainSlide.style.transition = 'transform 0.3s ease';
            
            setTimeout(function() {
                mainSlide.style.transform = 'translateX(0)';
            }, 150);
        }
    }

    // 메인 배너 슬라이드 컨트롤 이벤트 리스너 (배너용 prev/next 버튼만)
    var bannerPrevBtn = document.querySelector('.banner-container .prev-btn');
    var bannerNextBtn = document.querySelector('.banner-container .next-btn');
    
    if (bannerPrevBtn) {
        bannerPrevBtn.addEventListener('click', function() {
            prevSlide();
            stopAutoplay();
            setTimeout(startAutoplay, 3000);
        });
    }

    if (bannerNextBtn) {
        bannerNextBtn.addEventListener('click', function() {
            nextSlide();
            stopAutoplay();
            setTimeout(startAutoplay, 3000);
        });
    }

    if (pauseBtn) {
        pauseBtn.addEventListener('click', function() {
            if (isPlaying) {
                stopAutoplay();
            } else {
                startAutoplay();
            }
        });
    }

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

            console.log('자세히보기 클릭됨');
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

    // 로그인 폼 처리
    var loginForm = document.querySelector('.login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            var inputs = this.querySelectorAll('.login-input');
            var loginButton = this.querySelector('.login-button');
            
            // 간단한 유효성 검사
            var isValid = true;
            for (var i = 0; i < inputs.length; i++) {
                if (!inputs[i].value.trim()) {
                    inputs[i].style.borderColor = '#ff4444';
                    isValid = false;
                } else {
                    inputs[i].style.borderColor = '#e9ecef';
                }
            }
            
            if (isValid) {
                // 로그인 버튼 로딩 상태
                loginButton.innerHTML = '로그인 중...';
                loginButton.disabled = true;
                
                // 실제 로그인 처리 (예시)
                setTimeout(function() {
                    loginButton.innerHTML = '로그인';
                    loginButton.disabled = false;
                    console.log('로그인 처리됨');
                }, 1500);
            }
        });
    }

    // 로그인 버튼 클릭 이벤트 (단일 버튼)
    var loginButton = document.querySelector('.login-button');
    if (loginButton && !loginButton.closest('.login-form')) {
        loginButton.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('로그인 버튼 클릭됨');
        });
    }

    // 입력 필드 포커스 이벤트
    var loginInputs = document.querySelectorAll('.login-input');
    for (var i = 0; i < loginInputs.length; i++) {
        loginInputs[i].addEventListener('focus', function() {
            this.style.borderColor = '#0066cc';
            this.style.transform = 'translateY(-1px)';
            this.style.transition = 'all 0.3s ease';
        });
        
        loginInputs[i].addEventListener('blur', function() {
            if (!this.value) {
                this.style.borderColor = '#e9ecef';
            }
            this.style.transform = 'translateY(0)';
        });
        
        // 에러 상태 제거
        loginInputs[i].addEventListener('input', function() {
            if (this.style.borderColor === 'rgb(255, 68, 68)') {
                this.style.borderColor = '#0066cc';
            }
        });
    }

    // 로그인 링크 이벤트
    var loginLinks = document.querySelectorAll('.login-link');
    for (var i = 0; i < loginLinks.length; i++) {
        loginLinks[i].addEventListener('click', function(e) {
            e.preventDefault();
            
            this.style.transform = 'translateY(-1px)';
            this.style.transition = 'transform 0.2s ease';
            
            var self = this;
            setTimeout(function() {
                self.style.transform = 'translateY(0)';
            }, 200);
            
            console.log(this.textContent + ' 클릭됨');
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

    // 자동 재생 시작 (배너용)
    startAutoplay();

    // 페이지 가시성 변경 시 자동재생 제어
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            stopAutoplay();
        } else if (isPlaying) {
            startAutoplay();
        }
    });

    // 메인 슬라이드 호버 시 자동재생 일시정지
    var mainSlide = document.querySelector('.main-slide');
    if (mainSlide) {
        mainSlide.addEventListener('mouseenter', function() {
            if (isPlaying) {
                clearInterval(slideInterval);
            }
        });
        
        mainSlide.addEventListener('mouseleave', function() {
            if (isPlaying) {
                slideInterval = setInterval(nextSlide, 4000);
            }
        });
    }

    // 키보드 네비게이션
    document.addEventListener('keydown', function(e) {
        if (mainSlide && mainSlide.matches(':hover')) {
            if (e.key === 'ArrowLeft' || e.keyCode === 37) {
                e.preventDefault();
                prevSlide();
                stopAutoplay();
                setTimeout(startAutoplay, 3000);
            } else if (e.key === 'ArrowRight' || e.keyCode === 39) {
                e.preventDefault();
                nextSlide();
                stopAutoplay();
                setTimeout(startAutoplay, 3000);
            } else if (e.key === ' ' || e.keyCode === 32) {
                e.preventDefault();
                if (isPlaying) {
                    stopAutoplay();
                } else {
                    startAutoplay();
                }
            }
        }
    });

    // 엔터 키로 로그인
    document.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' || e.keyCode === 13) {
            var focusedElement = document.activeElement;
            if (focusedElement && focusedElement.classList.contains('login-input')) {
                var form = focusedElement.closest('.login-form');
                if (form) {
                    var event = new Event('submit');
                    form.dispatchEvent(event);
                }
            }
        }
    });
});