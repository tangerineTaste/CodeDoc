// ===============================
// 단계별 회원가입 JavaScript (간단한 헤더 버전)
// ===============================

console.log('signup.js 로드 완료!');

document.addEventListener('DOMContentLoaded', function() {
    console.log('signup.js DOMContentLoaded 실행!');
    
    // ===============================
    // 변수 선언
    // ===============================
    let currentStep = 1;
    const totalSteps = 5;
    
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    const formSteps = document.querySelectorAll('.form-step');
    const stepIndicator = document.querySelector('.step-indicator');
    const simpleTitle = document.querySelector('.simple-title');
    
    // 단계별 헤더 정보
    const stepHeaders = {
        1: { indicator: 'STEP 01.', title: '약관 동의' },
        2: { indicator: 'STEP 02.', title: '회원정보를 입력해주세요.' },
        3: { indicator: 'STEP 03.', title: '개인정보를 입력해주세요.' },
        4: { indicator: 'STEP 04.', title: '금융정보를 입력해주세요.' },
        5: { indicator: 'STEP 05.', title: '가입완료' }
    };
    
    // ===============================
    // 헤더 업데이트
    // ===============================
    function updateHeader() {
        const header = stepHeaders[currentStep];
        if (stepIndicator && simpleTitle && header) {
            stepIndicator.textContent = header.indicator;
            simpleTitle.textContent = header.title;
        }
    }
    
    // ===============================
    // 단계 표시/숨김
    // ===============================
    function showStep(stepNumber) {
        formSteps.forEach((step, index) => {
            step.classList.remove('active');
            
            if (index + 1 === stepNumber) {
                setTimeout(() => {
                    step.classList.add('active');
                }, 100);
            }
        });
        
        updateButtons();
        updateHeader();
    }
    
    // ===============================
    // 버튼 상태 업데이트
    // ===============================
    function updateButtons() {
        // Step 5에서는 이전 버튼 숨김, 로그인하기 버튼 표시
        if (currentStep === 5) {
            prevBtn.style.display = 'none';
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'flex';
            submitBtn.textContent = '로그인하기';
            return;
        }
        
        // 이전 버튼
        if (currentStep === 1) {
            prevBtn.style.display = 'none';
        } else {
            prevBtn.style.display = 'flex';
        }
        
        // 다음 버튼 (Step 1~4까지 모두 다음 버튼)
        nextBtn.style.display = 'flex';
        submitBtn.style.display = 'none';
    }
    
    // ===============================
    // 단계별 유효성 검사
    // ===============================
    function validateStep(stepNumber) {
        let isValid = true;
        let errorMessages = [];
        
        switch(stepNumber) {
            case 1: // 약관 동의
                const requiredAgreements = document.querySelectorAll('.agreement-item[required]');
                const uncheckedRequired = Array.from(requiredAgreements).filter(item => !item.checked);
                
                if (uncheckedRequired.length > 0) {
                    isValid = false;
                    errorMessages.push('필수 약관에 동의해주세요.');
                }
                break;
                
            case 2: // 기본 정보
                clearAllFieldErrors();
                
                const username = document.getElementById('id_username').value.trim();
                const password1 = document.getElementById('id_password1').value;
                const password2 = document.getElementById('id_password2').value;
                const email = document.getElementById('id_email').value.trim();
                
                if (!username) {
                    isValid = false;
                    showFieldError('id_username', '아이디를 입력해주세요.');
                } else if (username.length < 4) {
                    isValid = false;
                    showFieldError('id_username', '아이디는 4자 이상이어야 합니다.');
                }
                
                // 강화된 비밀번호 검증
                if (!password1) {
                    isValid = false;
                    showFieldError('id_password1', '비밀번호를 입력해주세요.');
                } else {
                    if (password1.length < 8) {
                        isValid = false;
                        showFieldError('id_password1', '비밀번호는 8자 이상이어야 합니다.');
                    } else if (/^\d+$/.test(password1)) {
                        isValid = false;
                        showFieldError('id_password1', '숫자로만 구성된 비밀번호는 사용할 수 없습니다.');
                    } else if (/^[a-zA-Z]+$/.test(password1)) {
                        isValid = false;
                        showFieldError('id_password1', '영문자로만 구성된 비밀번호는 사용할 수 없습니다.');
                    } else if (isCommonPassword(password1)) {
                        isValid = false;
                        showFieldError('id_password1', '일상적인 단어는 비밀번호로 사용할 수 없습니다.');
                    }
                }
                
                if (!password2) {
                    isValid = false;
                    showFieldError('id_password2', '비밀번호 확인을 입력해주세요.');
                } else if (password1 !== password2) {
                    isValid = false;
                    showFieldError('id_password2', '비밀번호가 일치하지 않습니다.');
                }
                
                if (!email) {
                    isValid = false;
                    showFieldError('id_email', '이메일을 입력해주세요.');
                }
                break;
                
            case 3: // 개인 정보  
                const fullName = document.getElementById('id_full_name').value.trim();
                const age = document.getElementById('id_age').value;
                const gender = document.getElementById('id_gender').value;
                const education = document.getElementById('id_education').value;
                const maritalStatus = document.getElementById('id_marital_status').value;
                
                if (!fullName) {
                    isValid = false;
                    errorMessages.push('이름을 입력해주세요.');
                }
                
                if (!age) {
                    isValid = false;
                    errorMessages.push('연령을 입력해주세요.');
                }
                
                if (!gender) {
                    isValid = false;
                    errorMessages.push('성별을 선택해주세요.');
                }
                
                if (!education) {
                    isValid = false;
                    errorMessages.push('교육수준을 선택해주세요.');
                }
                
                if (!maritalStatus) {
                    isValid = false;
                    errorMessages.push('결혼상태를 선택해주세요.');
                }
                break;
                
            case 4: // 금융 정보
                const jobCategory = document.getElementById('id_job_category').value;
                const savingsHabit = document.getElementById('id_savings_habit').value;
                
                if (!jobCategory) {
                    isValid = false;
                    errorMessages.push('직업분류를 선택해주세요.');
                }
                
                if (!savingsHabit) {
                    isValid = false;
                    errorMessages.push('저축습관을 선택해주세요.');
                }
                break;
        }
        
        if (!isValid) {
            showStepError(errorMessages);
        } else {
            hideStepError();
        }
        
        return isValid;
    }
    
    // ===============================
    // 에러 메시지 표시/숨김
    // ===============================
    function showFieldError(fieldId, message) {
        // 기존 에러 메시지 제거
        clearFieldError(fieldId);
        
        const field = document.getElementById(fieldId);
        if (field) {
            const formGroup = field.closest('.form-group');
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'field-error';
            errorDiv.style.color = '#e74c3c';
            errorDiv.style.fontSize = '12px';
            errorDiv.style.marginTop = '5px';
            errorDiv.textContent = message;
            
            formGroup.appendChild(errorDiv);
            
            // 입력 필드 테두리 색상 변경
            field.style.borderColor = '#e74c3c';
        }
    }

    function clearFieldError(fieldId) {
        const field = document.getElementById(fieldId);
        if (field) {
            const formGroup = field.closest('.form-group');
            const existingError = formGroup.querySelector('.field-error');
            if (existingError) {
                existingError.remove();
            }
            // 테두리 색상 원복
            field.style.borderColor = 'var(--border-light)';
        }
    }

    function clearAllFieldErrors() {
        const allErrors = document.querySelectorAll('.field-error');
        allErrors.forEach(error => error.remove());
        
        const allInputs = document.querySelectorAll('.form-input');
        allInputs.forEach(input => {
            input.style.borderColor = 'var(--border-light)';
        });
    }
    
    function hideStepError() {
        const existingError = document.querySelector('.step-error-messages');
        if (existingError) {
            existingError.remove();
        }
    }
    
    // ===============================
    // 이벤트 리스너
    // ===============================

    // 일상적인 비밀번호 체크 함수
    function isCommonPassword(password) {
        const commonPasswords = [
            'password', '12345678', '123456789', 'qwerty123', 'abcdefgh',
            'password1', 'password123', '11111111', '00000000', 'aaaaaaaa',
            'qwertyui', 'asdfghjk', 'zxcvbnm123', '1qaz2wsx', 'qwer1234',
            'admin123', 'test1234', 'user1234', 'welcome123'
        ];
        
        const lowerPassword = password.toLowerCase();
        return commonPasswords.some(common => lowerPassword.includes(common));
    }
    
    // 다음 버튼 클릭
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            if (validateStep(currentStep)) {
                if (currentStep === 4) {
                    // Step 4에서 실제 폼 제출
                    if (confirm('입력하신 정보로 회원가입을 진행하시겠습니까?')) {
                        console.log('폼 제출 중...');
                        
                        // 실제 폼 제출
                        document.getElementById('signupForm').submit();
                    }
                } else if (currentStep < totalSteps) {
                    currentStep++;
                    showStep(currentStep);
                }
            }
        });
    }
    
    // 이전 버튼 클릭
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            if (currentStep > 1) {
                currentStep--;
                showStep(currentStep);
                hideStepError();
            }
        });
    }
    
    // 로그인하기 버튼 클릭 (Step 5에서만)
    if (submitBtn) {
        submitBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (currentStep === 5) {
                // Step 5에서는 로그인 페이지로 이동
                window.location.href = "/accounts/login/";
            }
        });
    }
    
    // ===============================
    // Step 1: 전체 약관 동의
    // ===============================
    const agreeAllCheckbox = document.getElementById('agreeAll');
    const agreementItems = document.querySelectorAll('.agreement-item');
    
    if (agreeAllCheckbox) {
        agreeAllCheckbox.addEventListener('change', function() {
            agreementItems.forEach(item => {
                item.checked = this.checked;
            });
            hideStepError();
        });
    }
    
    agreementItems.forEach(item => {
        item.addEventListener('change', function() {
            if (agreeAllCheckbox) {
                const allChecked = Array.from(agreementItems).every(item => item.checked);
                agreeAllCheckbox.checked = allChecked;
            }
            hideStepError();
        });
    });
    
    // ===============================
    // 초기화
    // ===============================
    // 실시간 에러 메시지 제거 및 비밀번호 실시간 검증
    document.querySelectorAll('.form-input').forEach(input => {
        input.addEventListener('input', function() {
            clearFieldError(this.id);
            
            // 비밀번호 실시간 검증
            if (this.id === 'id_password1' && this.value.length > 0) {
                const password = this.value;
                
                if (password.length < 8) {
                    showFieldError('id_password1', '비밀번호는 8자 이상이어야 합니다.');
                } else if (/^\d+$/.test(password)) {
                    showFieldError('id_password1', '숫자로만 구성된 비밀번호는 사용할 수 없습니다.');
                } else if (/^[a-zA-Z]+$/.test(password)) {
                    showFieldError('id_password1', '영문자로만 구성된 비밀번호는 사용할 수 없습니다.');
                } else if (isCommonPassword(password)) {
                    showFieldError('id_password1', '일상적인 단어는 비밀번호로 사용할 수 없습니다.');
                }
            }
            
            // 비밀번호 확인 실시간 검증
            if (this.id === 'id_password2' && this.value.length > 0) {
                const password1 = document.getElementById('id_password1').value;
                if (this.value !== password1) {
                    showFieldError('id_password2', '비밀번호가 일치하지 않습니다.');
                }
            }
        });
    });

    showStep(currentStep);

    console.log('단계별 회원가입 초기화 완료!');
});
