// car_banner.js

document.addEventListener('DOMContentLoaded', function() {
    // 캐러셀 기능
    let currentSlide = 5;
    const totalSlides = 7;
    let isPlaying = true;
    let slideInterval;

    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    const pauseBtn = document.querySelector('.pause-btn');
    const currentIndicator = document.querySelector('.indicator.active');

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
        const mainSlide = document.querySelector('.main-slide');
        if (mainSlide) {
            mainSlide.style.transform = 'translateX(-5px)';
            mainSlide.style.transition = 'transform 0.3s ease';
            
            setTimeout(function() {
                mainSlide.style.transform = 'translateX(0)';
            }, 150);
        }
    }

    // 슬라이드 컨트롤 이벤트 리스너
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            prevSlide();
            stopAutoplay();
            setTimeout(startAutoplay, 3000);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
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

    // CTA 버튼 클릭 이벤트
    const ctaButton = document.querySelector('.cta-button');
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
            // 여기에 페이지 이동 코드 추가
            // window.location.href = '/car-service/';
        });
    }

    // 로그인 폼 처리
    const loginForm = document.querySelector('.login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const inputs = this.querySelectorAll('.login-input');
            const loginButton = this.querySelector('.login-button');
            
            // 간단한 유효성 검사
            let isValid = true;
            inputs.forEach(function(input) {
                if (!input.value.trim()) {
                    input.style.borderColor = '#ff4444';
                    isValid = false;
                } else {
                    input.style.borderColor = '#e9ecef';
                }
            });
            
            if (isValid) {
                // 로그인 버튼 로딩 상태
                loginButton.innerHTML = '로그인 중...';
                loginButton.disabled = true;
                
                // 실제 로그인 처리 (예시)
                setTimeout(function() {
                    loginButton.innerHTML = '로그인';
                    loginButton.disabled = false;
                    console.log('로그인 처리됨');
                    // 실제 로그인 로직 또는 페이지 이동
                    // window.location.href = '/dashboard/';
                }, 1500);
            }
        });
    }

    // 입력 필드 포커스 이벤트
    const loginInputs = document.querySelectorAll('.login-input');
    loginInputs.forEach(function(input) {
        input.addEventListener('focus', function() {
            this.style.borderColor = '#0066cc';
            this.style.transform = 'translateY(-1px)';
            this.style.transition = 'all 0.3s ease';
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.style.borderColor = '#e9ecef';
            }
            this.style.transform = 'translateY(0)';
        });
        
        // 에러 상태 제거
        input.addEventListener('input', function() {
            if (this.style.borderColor === 'rgb(255, 68, 68)') {
                this.style.borderColor = '#0066cc';
            }
        });
    });

    // 로그인 링크 이벤트
    const loginLinks = document.querySelectorAll('.login-link');
    loginLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            this.style.transform = 'translateY(-1px)';
            this.style.transition = 'transform 0.2s ease';
            
            setTimeout(function() {
                link.style.transform = 'translateY(0)';
            }, 200);
            
            console.log(this.textContent + ' 클릭됨');
            // 각 링크별 처리 로직 추가
        });
    });

    // 자주 찾는 메뉴 클릭 이벤트
    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(function(item, index) {
        item.addEventListener('click', function() {
            const menuIcon = this.querySelector('.menu-icon');
            const menuText = this.querySelector('.menu-text').textContent;
            
            // 클릭 애니메이션
            this.style.transform = 'translateY(-5px) scale(0.95)';
            this.style.transition = 'transform 0.15s ease';
            
            setTimeout(function() {
                item.style.transform = 'translateY(-3px)';
            }, 150);
            
            // 아이콘 펄스 효과
            menuIcon.style.transform = 'scale(1.1)';
            setTimeout(function() {
                menuIcon.style.transform = 'scale(1)';
            }, 200);
            
            console.log(menuText + ' 메뉴 클릭됨');
            
            // 각 메뉴별 처리
            switch(index) {
                case 0: // 차량정비
                    // window.location.href = '/service/maintenance/';
                    break;
                case 1: // 타이어교체
                    // window.location.href = '/service/tire/';
                    break;
                case 2: // 연료주입
                    // window.location.href = '/service/fuel/';
                    break;
            }
        });
        
        // 호버 효과 강화
        item.addEventListener('mouseenter', function() {
            const menuIcon = this.querySelector('.menu-icon');
            menuIcon.style.transform = 'scale(1.05)';
            menuIcon.style.transition = 'transform 0.3s ease';
        });
        
        item.addEventListener('mouseleave', function() {
            const menuIcon = this.querySelector('.menu-icon');
            menuIcon.style.transform = 'scale(1)';
        });
    });

    // 오일 병 클릭 이벤트 (할인 쿠폰)
    const oilBottle = document.querySelector('.oil-bottle');
    if (oilBottle) {
        oilBottle.addEventListener('click', function() {
            // 애니메이션 리셋 후 재실행
            this.style.animation = 'none';
            this.offsetHeight; // 리플로우 강제 실행
            this.style.animation = 'float 0.5s ease-in-out 3';
            
            // 쿠폰 하이라이트 효과
            const label = this.querySelector('.bottle-label');
            if (label) {
                label.style.background = 'linear-gradient(135deg, #FFE500 0%, #FFC107 100%)';
                label.style.transform = 'scale(1.15)';
                label.style.boxShadow = '0 5px 20px rgba(255, 193, 7, 0.4)';
                label.style.transition = 'all 0.3s ease';
                
                setTimeout(function() {
                    label.style.background = '#fff';
                    label.style.transform = 'scale(1)';
                    label.style.boxShadow = '0 3px 10px rgba(0,0,0,0.15)';
                }, 1500);
            }
            
            console.log('할인 쿠폰 클릭됨! 쿠폰 모달 열기');
            // 쿠폰 모달 또는 페이지 이동
        });
    }

    // 자동 재생 시작
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
    const mainSlide = document.querySelector('.main-slide');
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
            switch(e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    prevSlide();
                    stopAutoplay();
                    setTimeout(startAutoplay, 3000);
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    nextSlide();
                    stopAutoplay();
                    setTimeout(startAutoplay, 3000);
                    break;
                case ' ': // 스페이스바
                    e.preventDefault();
                    if (isPlaying) {
                        stopAutoplay();
                    } else {
                        startAutoplay();
                    }
                    break;
            }
        }
    });

    // 엔터 키로 로그인
    document.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const focusedElement = document.activeElement;
            if (focusedElement && focusedElement.classList.contains('login-input')) {
                const loginForm = focusedElement.closest('.login-form');
                if (loginForm) {
                    loginForm.dispatchEvent(new Event('submit'));
                }
            }
        }
    });
});