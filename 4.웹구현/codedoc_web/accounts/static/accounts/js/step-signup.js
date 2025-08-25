// 간단한 회원가입 처리
console.log('step-signup.js loaded');

document.addEventListener('DOMContentLoaded', function() {
    let currentStep = 1;
    const totalSteps = 5;
    
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn'); 
    const submitBtn = document.getElementById('submitBtn');
    const formSteps = document.querySelectorAll('.form-step');
    const stepIndicator = document.querySelector('.step-indicator');
    const simpleTitle = document.querySelector('.simple-title');
    
    const stepHeaders = {
        1: { indicator: 'STEP 01.', title: '약관 동의' },
        2: { indicator: 'STEP 02.', title: '회원정보를 입력해주세요.' },
        3: { indicator: 'STEP 03.', title: '개인정보를 입력해주세요.' },
        4: { indicator: 'STEP 04.', title: '금융정보를 입력해주세요.' },
        5: { indicator: 'STEP 05.', title: '가입완료' }
    };
    
    function updateHeader() {
        const header = stepHeaders[currentStep];
        if (stepIndicator && simpleTitle && header) {
            stepIndicator.textContent = header.indicator;
            simpleTitle.textContent = header.title;
        }
    }
    
    function showStep(stepNumber) {
        formSteps.forEach((step, index) => {
            step.classList.remove('active');
            if (index + 1 === stepNumber) {
                step.classList.add('active');
            }
        });
        updateButtons();
        updateHeader();
    }
    
    function updateButtons() {
        if (currentStep === 5) {
            prevBtn.style.display = 'none';
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'flex';
            return;
        }
        
        prevBtn.style.display = currentStep === 1 ? 'none' : 'flex';
        nextBtn.style.display = 'flex';
        submitBtn.style.display = 'none';
    }
    
    // 다음 버튼 이벤트
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            if (currentStep === 4) {
                // Step 4에서 실제 폼 제출
                console.log('Submitting form...');
                document.getElementById('signupForm').submit();
            } else if (currentStep < totalSteps) {
                currentStep++;
                showStep(currentStep);
            }
        });
    }
    
    // 이전 버튼 이벤트  
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            if (currentStep > 1) {
                currentStep--;
                showStep(currentStep);
            }
        });
    }
    
    // 로그인 버튼 이벤트
    if (submitBtn) {
        submitBtn.addEventListener('click', function() {
            window.location.href = '/accounts/login/';
        });
    }
    
    // 전체 약관 동의
    const agreeAllCheckbox = document.getElementById('agreeAll');
    const agreementItems = document.querySelectorAll('.agreement-item');
    
    if (agreeAllCheckbox) {
        agreeAllCheckbox.addEventListener('change', function() {
            agreementItems.forEach(item => {
                item.checked = this.checked;
            });
        });
    }
    
    // 초기화
    showStep(currentStep);
    console.log('step-signup.js initialized');
});
