// ===============================
// 단계별 회원가입 JavaScript (간단한 헤더 버전)
// ===============================

console.log('step-signup.js 로드 완료!');

document.addEventListener('DOMContentLoaded', function() {
    console.log('step-signup.js DOMContentLoaded 실행!');
    
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
            step.classList.remove('active', 'slide-in', 'slide-out');
            
            if (index + 1 === stepNumber) {
                setTimeout(() => {
                    step.classList.add('active', 'slide-in');
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
                const username = document.getElementById('id_username').value.trim();
                const password1 = document.getElementById('id_password1').value;
                const password2 = document.getElementById('id_password2').value;
                const email = document.getElementById('id_email').value.trim();
                const usernameChecked = document.getElementById('id_username').dataset.checked;
                
                if (!username) {
                    isValid = false;
                    errorMessages.push('아이디를 입력해주세요.');
                } else if (username.length < 4) {
                    isValid = false;
                    errorMessages.push('아이디는 4자 이상이어야 합니다.');
                } else if (usernameChecked !== 'true') {
                    isValid = false;
                    errorMessages.push('아이디 중복확인을 해주세요.');
                }
                
                if (!password1) {
                    isValid = false;
                    errorMessages.push('비밀번호를 입력해주세요.');
                } else if (password1.length < 8) {
                    isValid = false;
                    errorMessages.push('비밀번호는 8자 이상이어야 합니다.');
                }
                
                if (password1 !== password2) {
                    isValid = false;
                    errorMessages.push('비밀번호가 일치하지 않습니다.');
                }
                
                const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!email) {
                    isValid = false;
                    errorMessages.push('이메일을 입력해주세요.');
                } else if (!emailPattern.test(email)) {
                    isValid = false;
                    errorMessages.push('올바른 이메일 형식이 아닙니다.');
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
                } else if (fullName.length < 2) {
                    isValid = false;
                    errorMessages.push('이름은 2자 이상 입력해주세요.');
                }
                
                if (!age) {
                    isValid = false;
                    errorMessages.push('연령을 입력해주세요.');
                } else if (age < 18 || age > 100) {
                    isValid = false;
                    errorMessages.push('올바른 연령을 입력해주세요. (18-100세)');
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
                const annualIncome = document.getElementById('id_annual_income').value;
                const savingsHabit = document.getElementById('id_savings_habit').value;
                
                if (!jobCategory) {
                    isValid = false;
                    errorMessages.push('직업분류를 선택해주세요.');
                }
                
                if (!annualIncome) {
                    isValid = false;
                    errorMessages.push('연간 소득을 선택해주세요.');
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
    function showStepError(messages) {
        hideStepError();
        
        const currentStepElement = document.getElementById(`step${currentStep}`);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'step-error-messages';
        errorDiv.innerHTML = `
            <div class="error-content">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="10" stroke="#dc3545" stroke-width="2"/>
                    <line x1="15" y1="9" x2="9" y2="15" stroke="#dc3545" stroke-width="2"/>
                    <line x1="9" y1="9" x2="15" y2="15" stroke="#dc3545" stroke-width="2"/>
                </svg>
                <div class="error-text">
                    ${messages.map(msg => `<div>${msg}</div>`).join('')}
                </div>
            </div>
        `;
        
        currentStepElement.querySelector('.step-content').insertBefore(errorDiv, currentStepElement.querySelector('.step-content').firstChild);
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
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
    
    // 다음 버튼 클릭
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            if (validateStep(currentStep)) {
                if (currentStep === 4) {
                    // Step 4에서 Step 5으로 이동할 때 회원가입 처리
                    if (confirm('입력하신 정보로 회원가입을 진행하시겠습니까?')) {
                        this.disabled = true;
                        this.innerHTML = `
                            <div class="spinner" style="width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.3); border-top: 2px solid white; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 10px;"></div>
                            처리중...
                        `;
                        
                        setTimeout(() => {
                            // 실제로는 document.getElementById('signupForm').submit();
                            // 여기서는 Step 5으로 이동
                            currentStep++;
                            showStep(currentStep);
                            // 버튼 원상복구
                            this.disabled = false;
                            this.innerHTML = `
                                다음
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                                    <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                </svg>
                            `;
                        }, 2000);
                    }
                } else if (currentStep < totalSteps) {
                    currentStep++;
                    showStep(currentStep);
                    
                    setTimeout(() => {
                        const nextStepElement = document.getElementById(`step${currentStep}`);
                        const firstInput = nextStepElement.querySelector('.form-input, .form-select, .checkbox-input');
                        if (firstInput) {
                            firstInput.focus();
                        }
                    }, 200);
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
            window.location.href = "{% url 'accounts:login' %}";
        }
    });
}
    
    // ===============================
    // 키보드 네비게이션
    // ===============================
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const activeElement = document.activeElement;
            
            if (activeElement.classList.contains('form-input') || activeElement.classList.contains('form-select')) {
                e.preventDefault();
                
                const currentStepElement = document.getElementById(`step${currentStep}`);
                const inputs = currentStepElement.querySelectorAll('.form-input, .form-select');
                const currentIndex = Array.from(inputs).indexOf(activeElement);
                
                if (currentIndex < inputs.length - 1) {
                    inputs[currentIndex + 1].focus();
                } else {
                    if (currentStep < totalSteps) {
                        nextBtn.click();
                    } else {
                        submitBtn.click();
                    }
                }
            }
        }
    });
    
    // ===============================
    // Step 1: 전체 약관 동의
    // ===============================
    const agreeAllCheckbox = document.getElementById('agreeAll');
    const agreementItems = document.querySelectorAll('.agreement-item');
    
    if (agreeAllCheckbox) {
        agreeAllCheckbox.addEventListener('change', function() {
            agreementItems.forEach(item => {
                item.checked = this.checked;
                updateCheckboxStyle(item);
            });
            hideStepError();
        });
    }
    
    agreementItems.forEach(item => {
        item.addEventListener('change', function() {
            updateCheckboxStyle(this);
            
            if (agreeAllCheckbox) {
                const allChecked = Array.from(agreementItems).every(item => item.checked);
                agreeAllCheckbox.checked = allChecked;
                updateCheckboxStyle(agreeAllCheckbox);
            }
            
            hideStepError();
        });
    });
    
    function updateCheckboxStyle(checkbox) {
    const wrapper = checkbox.closest('.checkbox-wrapper');
    // 전체 약관 동의 체크박스인 경우 색상 변경하지 않음
    if (checkbox.id === 'agreeAll') {
        return;
    }
    
    // 개별 약관 체크박스만 색상 변경
    if (checkbox.checked) {
        wrapper.style.color = 'var(--primary-color)';
    } else {
        wrapper.style.color = '';
    }
}
    
    // ===============================
    // Step 2: 아이디 중복확인
    // ===============================
    const usernameInput = document.getElementById('id_username');
    const usernameCheckBtn = document.getElementById('usernameCheck');
    
    if (usernameCheckBtn) {
        usernameCheckBtn.addEventListener('click', function() {
            const username = usernameInput.value.trim();
            
            if (!username) {
                alert('아이디를 입력해주세요.');
                usernameInput.focus();
                return;
            }
            
            if (username.length < 4) {
                alert('아이디는 4자 이상이어야 합니다.');
                usernameInput.focus();
                return;
            }
            
            this.disabled = true;
            this.textContent = '확인중...';
            
            setTimeout(() => {
                const isAvailable = Math.random() > 0.3;
                
                if (isAvailable) {
                    this.textContent = '사용가능';
                    this.style.background = '#0078FE';
                    this.style.color = 'white';
                    this.style.borderColor = '#0078FE';
                    this.classList.add('success-state'); // CSS 클래스 추가
                    usernameInput.style.borderColor = '#0078FE';
                    usernameInput.dataset.checked = 'true';
                    hideStepError();
                } else {
                    this.textContent = '중복확인';
                    this.disabled = false;
                    alert('이미 사용중인 아이디입니다.');
                    usernameInput.focus();
                }
            }, 1000);
        });
    }
    
    if (usernameInput) {
        usernameInput.addEventListener('input', function() {
            const checkBtn = document.getElementById('usernameCheck');
            if (checkBtn && this.dataset.checked === 'true') {
                checkBtn.textContent = '중복확인';
                checkBtn.style.background = '';
                checkBtn.style.color = '';
                checkBtn.disabled = false;
                this.style.borderColor = '';
                this.dataset.checked = 'false';
            }
            hideStepError();
        });
    }
    
    // ===============================
    // 라디오 버튼 스타일링
    // ===============================
    const radioInputs = document.querySelectorAll('.radio-input');
    
    radioInputs.forEach(function(radio) {
        radio.addEventListener('change', function() {
            const sameNameRadios = document.querySelectorAll(`input[name="${this.name}"]`);
            sameNameRadios.forEach(function(r) {
                r.closest('.radio-wrapper').classList.remove('selected');
            });
            
            this.closest('.radio-wrapper').classList.add('selected');
            hideStepError();
        });
    });
    
    // ===============================
    // 초기화
    // ===============================
    showStep(currentStep);
    
    console.log('단계별 회원가입 초기화 완료!');
});