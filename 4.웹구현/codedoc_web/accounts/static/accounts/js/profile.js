// ===============================
// 프로필 수정 페이지 JavaScript
// ===============================

console.log('profile.js 로드 완료!');

document.addEventListener('DOMContentLoaded', function() {
    console.log('프로필 수정 페이지 초기화 시작');

    // 여기에 추가 - URL 파라미터 확인
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('saved') === 'true') {
        showSuccessNotification('수정한 내용으로 저장되었습니다.');
        const newUrl = window.location.pathname;
        window.history.replaceState({}, document.title, newUrl);
    }
    
    // ===============================
    // 폼 유효성 검사
    // ===============================
    const form = document.querySelector('.profile-edit-form');
    const saveButton = document.querySelector('.save-button');
    
    if (form && saveButton) {
        // 필수 필드 확인
        const requiredFields = form.querySelectorAll('input[required], select[required]');
        
        function validateForm() {
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value || field.value.trim() === '') {
                    isValid = false;
                    field.style.borderColor = '#dc3545';
                } else {
                    field.style.borderColor = 'var(--border-light)';
                }
            });
            
            saveButton.disabled = !isValid;
            
            if (!isValid) {
                saveButton.style.opacity = '0.6';
                saveButton.style.cursor = 'not-allowed';
            } else {
                saveButton.style.opacity = '1';
                saveButton.style.cursor = 'pointer';
            }
            
            return isValid;
        }
        
        // 실시간 유효성 검사
        requiredFields.forEach(field => {
            field.addEventListener('change', validateForm);
            field.addEventListener('input', validateForm);
        });
        
        // 초기 유효성 검사
        validateForm();
        
        // 폼 제출 시 확인
        form.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
                alert('필수 항목을 모두 입력해주세요.');
                return false;
            }

            // 폼 제출 시 변경사항 플래그 초기화
            hasChanges = false;
            
            // 로딩 상태로 변경
            saveButton.disabled = true;
            saveButton.innerHTML = `
                <div style="width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.3); border-top: 2px solid white; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px;"></div>
                저장 중...
            `;
        });
    }
    
    // ===============================
    // 필드별 특별 처리
    // ===============================
    
    // 금융위험태도 필드 처리
    const riskAttitudeField = document.querySelector('#id_금융위험태도');
    if (riskAttitudeField) {
        riskAttitudeField.setAttribute('readonly', true);
        riskAttitudeField.style.backgroundColor = '#f8f9fa';
        riskAttitudeField.style.cursor = 'not-allowed';
        
        // 툴팁 추가
        riskAttitudeField.addEventListener('mouseenter', function() {
            showTooltip(this, '이 값은 시스템에서 자동으로 분석하여 업데이트됩니다.');
        });
    }
    
    // ===============================
    // 섹션 애니메이션
    // ===============================
    const formSections = document.querySelectorAll('.form-section');
    
    // function animateSections() {
    //     formSections.forEach((section, index) => {
    //         section.style.opacity = '0';
    //         section.style.transform = 'translateY(20px)';
            
    //         setTimeout(() => {
    //             section.style.transition = 'all 0.6s ease';
    //             section.style.opacity = '1';
    //             section.style.transform = 'translateY(0)';
    //         }, index * 150);
    //     });
    // }
    
    // // 페이지 로드 시 애니메이션 실행
    // setTimeout(animateSections, 100);
    
    // ===============================
    // 변경 사항 추적
    // ===============================
    const formElements = form ? form.querySelectorAll('input, select') : [];
    let initialValues = {};
    let hasChanges = false;
    
    // 초기값 저장
    formElements.forEach(element => {
        initialValues[element.name] = element.value;
    });
    
    // 변경 사항 감지
    formElements.forEach(element => {
        element.addEventListener('change', function() {
            hasChanges = checkForChanges();
            updateSaveButtonState();
        });
    });
    
    function checkForChanges() {
        for (let element of formElements) {
            if (initialValues[element.name] !== element.value) {
                return true;
            }
        }
        return false;
    }
    
    function updateSaveButtonState() {
        if (saveButton) {
            if (hasChanges) {
                saveButton.classList.add('active');
                saveButton.disabled = false;
            } else {
                saveButton.classList.remove('active');
                saveButton.disabled = true;
            }
        }
    }

    // 초기 상태 설정
    if (saveButton) {
        saveButton.classList.remove('active');
        saveButton.disabled = true;
    }

    // 페이지 이탈 경고
    window.addEventListener('beforeunload', function(e) {
        if (hasChanges) {
            e.preventDefault();
            e.returnValue = '변경사항이 저장되지 않았습니다. 페이지를 나가시겠습니까?';
        }
    });
    
    // ===============================
    // 도구 기능들
    // ===============================
    
    // 툴팁 표시
    function showTooltip(element, message) {
        // 기존 툴팁 제거
        const existingTooltip = document.querySelector('.field-tooltip');
        if (existingTooltip) {
            existingTooltip.remove();
        }
        
        const tooltip = document.createElement('div');
        tooltip.className = 'field-tooltip';
        tooltip.innerHTML = message;
        tooltip.style.cssText = `
            position: absolute;
            background: #333;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            white-space: nowrap;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            pointer-events: none;
        `;
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + 'px';
        tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
        
        // 3초 후 자동 제거
        setTimeout(() => {
            if (tooltip.parentNode) {
                tooltip.remove();
            }
        }, 3000);
        
        element.addEventListener('mouseleave', function() {
            if (tooltip.parentNode) {
                tooltip.remove();
            }
        }, { once: true });
    }
    
    // 필드 포커스 효과
    const formInputs = document.querySelectorAll('.profile-edit-form input, .profile-edit-form select');
    
    // formInputs.forEach(input => {
    //     input.addEventListener('focus', function() {
    //         this.parentElement.style.transform = 'translateY(-2px)';
    //         this.parentElement.style.transition = 'transform 0.3s ease';
    //     });
        
    //     input.addEventListener('blur', function() {
    //         this.parentElement.style.transform = 'translateY(0)';
    //     });
    // });

    console.log('프로필 수정 페이지 초기화 완료');
    });

function showSuccessNotification(message) {
    // 모달 컨테이너 생성
    const modal = document.createElement('div');
    modal.className = 'login-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    
    // 배경 오버레이
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
    `;
    
    // 모달 콘텐츠
    const content = document.createElement('div');
    content.className = 'modal-content';
    content.style.cssText = `
        background: white;
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        position: relative;
        z-index: 10000;
        width: 450px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    `;
    
    // 아이콘
    const icon = document.createElement('div');
    icon.className = 'modal-icon';
    icon.style.marginBottom = '20px';
    icon.innerHTML = `
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="#0078FE" stroke-width="2"/>
            <polyline points="14,2 14,8 20,8" stroke="#0078FE" stroke-width="2"/>
            <line x1="16" y1="13" x2="8" y2="13" stroke="#0078FE" stroke-width="2"/>
            <line x1="16" y1="17" x2="8" y2="17" stroke="#0078FE" stroke-width="2"/>
            <polyline points="10,9 9,9 8,9" stroke="#0078FE" stroke-width="2"/>
        </svg>
    `;
    
    // 제목 수정
    const title = document.createElement('h3');
    title.textContent = '프로필 정보 수정 완료';
    title.style.cssText = `
        font-size: 18px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 15px;
    `;
    
    // 메시지 수정
    const messageP1 = document.createElement('p');
    const messageP2 = document.createElement('p');
    messageP1.textContent = '프로필 정보가 업데이트 되었습니다.';
    messageP2.textContent = '맞춤 상품을 확인하시겠습니까?';
    messageP1.style.cssText = `
        font-size: 16px;
        color: var(--text-secondary);
        margin-bottom: 4px;
        line-height: 1.4;
    `;
    messageP2.style.cssText = `
        font-size: 16px;
        color: var(--text-secondary);
        margin-bottom: 4px;
        line-height: 1.4;
    `;
    
    // 버튼 영역
    const buttons = document.createElement('div');
    buttons.className = 'modal-buttons';
    buttons.style.cssText = `
        display: flex;
        gap: 12px;
        margin-top: 30px;
        justify-content: center;
    `;
    
    // 홈으로 돌아가기 버튼
    const cancelBtn = document.createElement('button');
    cancelBtn.className = 'modal-btn cancel-btn';
    cancelBtn.textContent = '홈으로 돌아가기';
    cancelBtn.style.cssText = `
        padding: 15px 34px;
        border: none;
        border-radius: 15px;
        font-size: 16px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s;
        min-width: 80px;
        background: #f0f0f0;
        color: var(--text-secondary);
    `;

    // 맞춤 상품 보기 버튼
    const confirmBtn = document.createElement('button');
    confirmBtn.className = 'modal-btn confirm-btn';
    confirmBtn.textContent = '맞춤 상품 보기';
    confirmBtn.style.cssText = `
        padding: 15px 34px;
        border: none;
        border-radius: 15px;
        font-size: 16px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s;
        min-width: 80px;
        background: var(--primary-color);
        color: white;
    `;
    
    // 버튼 이벤트 수정
    cancelBtn.addEventListener('click', () => {
        modal.remove();
        window.location.href = '/'; // 홈으로 이동
    });
    confirmBtn.addEventListener('click', () => {
        modal.remove();
        window.location.href = '/products/list/'; // 맞춤 상품 추천 페이지로 이동
    });
    
    overlay.addEventListener('click', () => modal.remove());

    // 요소들 조립
    buttons.appendChild(cancelBtn);
    buttons.appendChild(confirmBtn);
    content.appendChild(icon);
    content.appendChild(title);
    content.appendChild(messageP1);
    content.appendChild(messageP2);
    content.appendChild(buttons);
    modal.appendChild(overlay);
    modal.appendChild(content);

    // DOM에 추가
    document.body.appendChild(modal);
}

// CSS 애니메이션 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes modalSlideIn {
    from { 
        opacity: 0; 
        transform: scale(0.8) translateY(-50px); 
    }
    to { 
        opacity: 1; 
        transform: scale(1) translateY(0); 
    }
}

@keyframes modalSlideOut {
    from { 
        opacity: 1; 
        transform: scale(1) translateY(0); 
    }
    to { 
        opacity: 0; 
        transform: scale(0.8) translateY(-50px); 
    }
}
`;
document.head.appendChild(style);