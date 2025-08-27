// ===============================
// 프로필 수정 페이지 JavaScript
// ===============================

console.log('profile.js 로드 완료!');

document.addEventListener('DOMContentLoaded', function() {
    console.log('프로필 수정 페이지 초기화 시작');
    
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
                saveButton.style.background = 'var(--primary-color)';
                saveButton.style.transform = 'translateY(-1px)';
            } else {
                saveButton.style.background = '#ccc';
                saveButton.style.transform = 'translateY(0)';
            }
        }
    }
    
    // ===============================
    // 페이지 이탈 경고
    // ===============================
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
    
    // ===============================
    // 성공 메시지 자동 숨김
    // ===============================
    const successMessages = document.querySelectorAll('.success-message');

    successMessages.forEach(message => {
        const parent = message.parentElement; // 배경 역할 요소가 부모일 경우

            setTimeout(() => {
                message.style.transition = 'opacity 0.5s ease';
                message.style.opacity = '0';

                if (parent) {
                parent.style.transition = 'opacity 0.5s ease';
                parent.style.opacity = '0';
                }

                setTimeout(() => {
                if (parent) parent.remove();
                else message.remove();
                }, 500);
            }, 2000);
        });

    console.log('프로필 수정 페이지 초기화 완료');
    });

// CSS 애니메이션 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .field-tooltip {
        animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-5px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);