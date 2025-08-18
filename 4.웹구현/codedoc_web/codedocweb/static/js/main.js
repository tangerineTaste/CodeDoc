// nav 부분 
// 메리츠 스타일 네비게이션 - 디버깅 추가
document.addEventListener('DOMContentLoaded', function() {
    const navItems = document.querySelectorAll('.nav-item');
    const megaDropdown = document.querySelector('.mega-dropdown');
    const menuColumns = document.querySelectorAll('.menu-column');
    let timeoutId;

    console.log('네비게이션 초기화:', navItems.length, '개 메뉴');

    navItems.forEach((item, index) => {
        item.addEventListener('mouseenter', function() {
            console.log(`메뉴 ${index} 호버됨`);
            clearTimeout(timeoutId);
            
            // 메가 드롭다운 표시
            megaDropdown.classList.add('show');
            
            // 모든 컬럼에서 active 제거
            menuColumns.forEach((col, i) => {
                col.classList.remove('active-column');
                console.log(`컬럼 ${i} active 제거`);
            });
            
            // 해당 컬럼만 active 추가
            if (menuColumns[index]) {
                menuColumns[index].classList.add('active-column');
                console.log(`컬럼 ${index} active 추가`);
            }
            
            // 모든 메뉴에서 active 제거 후 현재 메뉴에 추가
            navItems.forEach(navItem => navItem.classList.remove('active'));
            item.classList.add('active');
        });

        item.addEventListener('mouseleave', function() {
            timeoutId = setTimeout(() => {
                megaDropdown.classList.remove('show');
                navItems.forEach(navItem => navItem.classList.remove('active'));
                menuColumns.forEach(col => col.classList.remove('active-column'));
            }, 200);
        });
    });

    // 메가 드롭다운에 마우스가 있을 때는 닫지 않음
    megaDropdown.addEventListener('mouseenter', function() {
        clearTimeout(timeoutId);
    });

    megaDropdown.addEventListener('mouseleave', function() {
        timeoutId = setTimeout(() => {
            megaDropdown.classList.remove('show');
            navItems.forEach(navItem => navItem.classList.remove('active'));
            menuColumns.forEach(col => col.classList.remove('active-column'));
        }, 200);
    });
});

// main slide 부분
document.addEventListener('DOMContentLoaded', function() {
    let currentSlide = 0;
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.dot');
    const pauseBtn = document.querySelector('.slide-pause');
    let isPlaying = true;
    let slideInterval;

    // 슬라이드 전환 함수
    function showSlide(index) {
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));
        
        slides[index].classList.add('active');
        dots[index].classList.add('active');
        currentSlide = index;
    }

    // 다음 슬라이드
    function nextSlide() {
        currentSlide = (currentSlide + 1) % slides.length;
        showSlide(currentSlide);
    }

    // 자동 슬라이드
    function startSlideShow() {
        slideInterval = setInterval(nextSlide, 4000);
        isPlaying = true;
        pauseBtn.textContent = '⏸️';
    }

    function stopSlideShow() {
        clearInterval(slideInterval);
        isPlaying = false;
        pauseBtn.textContent = '▶️';
    }

    // 점 클릭 이벤트
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            showSlide(index);
            if (isPlaying) {
                stopSlideShow();
                startSlideShow();
            }
        });
    });

    // 일시정지 버튼
    pauseBtn.addEventListener('click', () => {
        if (isPlaying) {
            stopSlideShow();
        } else {
            startSlideShow();
        }
    });

    // 로그인 버튼 클릭 효과
    const loginBtns = document.querySelectorAll('.btn-login');
    loginBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });

    // 자동 슬라이드 시작
    startSlideShow();
});
