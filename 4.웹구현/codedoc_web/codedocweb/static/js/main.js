// 로그인 모달 관련 함수들 (전역 함수로 정의)
function showLoginModal() {
    document.getElementById('loginModal').style.display = 'flex';
}

function closeLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

function goToLogin() {
    window.location.href = '/accounts/login/';  // 로그인 URL에 맞게 수정
}

// nav 부분 
document.addEventListener('DOMContentLoaded', function() {
    const navItems = document.querySelectorAll('.nav-item');
    const megaDropdown = document.querySelector('.mega-dropdown');
    const menuColumns = document.querySelectorAll('.menu-column');
    let timeoutId;

    console.log('네비게이션 초기화:', navItems.length, '개 메뉴');

    navItems.forEach((item, index) => {
        if (item) {
            item.addEventListener('mouseenter', function() {
                console.log(`메뉴 ${index} 호버됨`);
                clearTimeout(timeoutId);
                
                // 메가 드롭다운 표시
                if (megaDropdown) {
                    megaDropdown.classList.add('show');
                }
                
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
                    if (megaDropdown) {
                        megaDropdown.classList.remove('show');
                    }
                    navItems.forEach(navItem => navItem.classList.remove('active'));
                    menuColumns.forEach(col => col.classList.remove('active-column'));
                }, 200);
            });
        }
    });

    // 하위메뉴 아이템 호버 효과 추가
    setTimeout(() => {
        const dropdownMenuItems = document.querySelectorAll('.mega-dropdown .menu-item');
        
        dropdownMenuItems.forEach((item) => {
            if (item) {
                item.addEventListener('mouseenter', function() {
                    clearTimeout(timeoutId);
                    
                    const parentColumn = this.closest('.menu-column');
                    
                    // 모든 컬럼에서 active 제거
                    menuColumns.forEach(col => col.classList.remove('active-column'));
                    
                    // 모든 대메뉴에서 active 제거
                    navItems.forEach(navItem => navItem.classList.remove('active'));
                    
                    // 해당 컬럼만 active 추가
                    if (parentColumn) {
                        parentColumn.classList.add('active-column');
                        
                        // 해당 컬럼의 인덱스 찾기
                        const columnIndex = Array.from(menuColumns).indexOf(parentColumn);
                        
                        // 해당하는 대메뉴에 active 추가
                        if (navItems[columnIndex]) {
                            navItems[columnIndex].classList.add('active');
                        }
                    }
                });
            }
        });
    }, 100);

    // 메가 드롭다운에 마우스가 있을 때는 닫지 않음
    if (megaDropdown) {
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
    }

    // 모달 외부 클릭시 닫기
    const modal = document.getElementById('loginModal');
    if (modal) {
        document.addEventListener('click', function(e) {
            if (e.target === modal || e.target.classList.contains('modal-overlay')) {
                closeLoginModal();
            }
        });
    }
});