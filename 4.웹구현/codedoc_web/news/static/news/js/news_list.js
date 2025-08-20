document.addEventListener('DOMContentLoaded', function() {
    const refreshBtn = document.getElementById('refreshBtn');
    const floatingRefreshBtn = document.getElementById('floatingRefreshBtn');
    
    // Bootstrap Modal 초기화
    let loadingModal;
    const loadingModalElement = document.getElementById('loadingModal');
    if (loadingModalElement) {
        loadingModal = new bootstrap.Modal(loadingModalElement);
    }

    // 뉴스 새로고침 함수
    function refreshNews() {
        if (loadingModal) {
            loadingModal.show();
        }
        
        fetch('/news/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                keywords: ['금융', '경제', '투자', '주식', '부동산']
            })
        })
        .then(response => response.json())
        .then(data => {
            if (loadingModal) {
                loadingModal.hide();
            }
            
            if (data.success) {
                showAlert('success', data.message);
                // 1.5초 후 페이지 새로고침
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                showAlert('danger', data.message);
            }
        })
        .catch(error => {
            if (loadingModal) {
                loadingModal.hide();
            }
            showAlert('danger', '뉴스 새로고침 중 오류가 발생했습니다.');
            console.error('Error:', error);
        });
    }

    // CSRF 토큰 가져오기
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
    }

    // 알림 표시 함수
    function showAlert(type, message) {
        // 기존 알림 제거
        const existingAlerts = document.querySelectorAll('.alert-floating');
        existingAlerts.forEach(alert => alert.remove());

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed alert-floating`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px; max-width: 400px;';
        
        // 알림 아이콘 설정
        let icon = '';
        switch(type) {
            case 'success':
                icon = '<i class="fas fa-check-circle me-2"></i>';
                break;
            case 'danger':
                icon = '<i class="fas fa-exclamation-circle me-2"></i>';
                break;
            case 'warning':
                icon = '<i class="fas fa-exclamation-triangle me-2"></i>';
                break;
            default:
                icon = '<i class="fas fa-info-circle me-2"></i>';
        }
        
        alertDiv.innerHTML = `
            ${icon}${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // 3초 후 자동 제거
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 3000);
    }

    // 스크롤에 따른 플로팅 버튼 표시/숨김
    function handleScroll() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const floatingBtn = document.getElementById('floatingRefreshBtn');
        
        if (floatingBtn) {
            if (scrollTop > 300) {
                floatingBtn.style.opacity = '1';
                floatingBtn.style.visibility = 'visible';
            } else {
                floatingBtn.style.opacity = '0';
                floatingBtn.style.visibility = 'hidden';
            }
        }
    }

    // 카드 호버 효과
    function addCardEffects() {
        const newsCards = document.querySelectorAll('.news-card');
        
        newsCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });
    }

    // 외부 링크 클릭 시 확인
    function handleExternalLinks() {
        const externalLinks = document.querySelectorAll('a[target="_blank"]');
        
        externalLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                // 필요시 확인 대화상자 표시
                // const confirmed = confirm('외부 사이트로 이동하시겠습니까?');
                // if (!confirmed) {
                //     e.preventDefault();
                // }
            });
        });
    }

    // 이벤트 리스너 등록
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshNews);
    }
    
    if (floatingRefreshBtn) {
        floatingRefreshBtn.addEventListener('click', refreshNews);
        // 초기 상태 설정
        floatingRefreshBtn.style.transition = 'all 0.3s ease';
        floatingRefreshBtn.style.opacity = '0';
        floatingRefreshBtn.style.visibility = 'hidden';
    }

    // 스크롤 이벤트
    window.addEventListener('scroll', handleScroll);

    // 초기화
    addCardEffects();
    handleExternalLinks();

    // 페이지 로드 시 스크롤 위치 확인
    handleScroll();

    console.log('News List JavaScript 로드 완료');
});
