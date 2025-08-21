// ===============================
// 로그인/회원가입 페이지 JavaScript
// ===============================

console.log('auth.js 로드 완료!');

document.addEventListener('DOMContentLoaded', function() {
    console.log('auth.js DOMContentLoaded 실행!');
    
    // ===============================
    // 비밀번호 표시/숨기기 토글
    // ===============================
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    passwordToggles.forEach(function(toggle) {
        toggle.addEventListener('click', function() {
            const passwordInput = this.parentElement.querySelector('input[type="password"], input[type="text"]');
            const eyeIcon = this.querySelector('.eye-icon');
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                eyeIcon.innerHTML = `
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94L17.94 17.94z" stroke="currentColor" stroke-width="2"/>
                    <path d="M1 1l22 22" stroke="currentColor" stroke-width="2"/>
                    <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                `;
            } else {
                passwordInput.type = 'password';
                eyeIcon.innerHTML = `
                    <path d="M1 12S5 4 12 4s11 8 11 8-4 8-11 8S1 12 1 12z" stroke="currentColor" stroke-width="2"/>
                    <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                `;
            }
        });
    });
    
    // ===============================
    // 폼 제출 시 로딩 애니메이션
    // ===============================
    const authForms = document.querySelectorAll('.login-form, .signup-form');
    
    authForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('.login-button, .signup-button');
            const buttonText = submitButton.querySelector('.button-text');
            const buttonLoader = submitButton.querySelector('.button-loader');
            
            // 버튼 상태 변경
            submitButton.disabled = true;
            buttonText.style.display = 'none';
            buttonLoader.style.display = 'block';
            
            // 3초 후에 버튼 복원 (실제로는 페이지가 이동하거나 에러 처리됨)
            setTimeout(function() {
                submitButton.disabled = false;
                buttonText.style.display = 'block';
                buttonLoader.style.display = 'none';
            }, 3000);
        });
    });
    
    // ===============================
    // 실시간 입력 유효성 검사
    // ===============================
    const formInputs = document.querySelectorAll('.form-input');
    
    formInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            validateInput(this);
        });
        
        input.addEventListener('input', function() {
            clearInputError(this);
        });
    });
    
    function validateInput(input) {
        const value = input.value.trim();
        const inputName = input.name;
        
        // 기존 에러 메시지 제거
        clearInputError(input);
        
        let errorMessage = '';
        
        switch(inputName) {
            case 'username':
                if (!value) {
                    errorMessage = '아이디를 입력해주세요.';
                } else if (value.length < 4) {
                    errorMessage = '아이디는 4자 이상이어야 합니다.';
                }
                break;
                
            case 'password':
                if (!value) {
                    errorMessage = '비밀번호를 입력해주세요.';
                } else if (value.length < 8) {
                    errorMessage = '비밀번호는 8자 이상이어야 합니다.';
                }
                break;
                
            case 'password_confirm':
                const originalPassword = document.querySelector('input[name="password"]').value;
                if (!value) {
                    errorMessage = '비밀번호 확인을 입력해주세요.';
                } else if (value !== originalPassword) {
                    errorMessage = '비밀번호가 일치하지 않습니다.';
                }
                break;
                
            case 'email':
                const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!value) {
                    errorMessage = '이메일을 입력해주세요.';
                } else if (!emailPattern.test(value)) {
                    errorMessage = '올바른 이메일 형식이 아닙니다.';
                }
                break;
        }
        
        if (errorMessage) {
            showInputError(input, errorMessage);
        }
    }
    
    function showInputError(input, message) {
        input.style.borderColor = '#e74c3c';
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.style.color = '#e74c3c';
        errorDiv.style.fontSize = '12px';
        errorDiv.style.marginTop = '5px';
        errorDiv.textContent = message;
        
        input.parentElement.appendChild(errorDiv);
    }
    
    function clearInputError(input) {
        input.style.borderColor = 'var(--border-light)';
        
        const existingError = input.parentElement.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
    }
    
    // ===============================
    // 체크박스 애니메이션
    // ===============================
    const checkboxes = document.querySelectorAll('.checkbox-input');
    
    checkboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            const wrapper = this.closest('.checkbox-wrapper');
            
            if (this.checked) {
                wrapper.style.color = 'var(--primary-color)';
            } else {
                wrapper.style.color = 'var(--text-secondary)';
            }
        });
    });
    
    // ===============================
    // 키보드 네비게이션
    // ===============================
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const activeElement = document.activeElement;
            
            if (activeElement.classList.contains('form-input')) {
                const form = activeElement.closest('form');
                const inputs = form.querySelectorAll('.form-input');
                const currentIndex = Array.from(inputs).indexOf(activeElement);
                
                if (currentIndex < inputs.length - 1) {
                    // 다음 입력 필드로 이동
                    e.preventDefault();
                    inputs[currentIndex + 1].focus();
                }
                // 마지막 입력 필드에서는 폼 제출
            }
        }
    });
    
    // ===============================
    // 페이지 진입 시 첫 번째 입력 필드에 포커스
    // ===============================
    const firstInput = document.querySelector('.form-input');
    if (firstInput) {
        setTimeout(function() {
            firstInput.focus();
        }, 100);
    }
});