// product_recommendation/static/product_recommendation/js/product_recommend.js

// 전역 함수로 정의 (직접 HTML에서 호출 가능)
function goToAIRecommend() {
    console.log('goToAIRecommend 함수 호출');
    // alert 제거됨
    
    // 여러 방법으로 시도
    try {
        console.log('페이지 이동 시도...');
        window.location.href = '/products/recommend/ai/';
    } catch (error) {
        console.error('오류:', error);
        // 대체 방법
        window.location.assign('/products/recommend/ai/');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('페이지 로드 완료');

    // 서비스별 상세 정보
    const serviceDetails = {
        '맞춤설계로 Smart하게': {
            description: 'AI 기반 분석을 통해 고객님의 라이프스타일과 재정 상황을 종합적으로 분석하여 최적의 맞춤상품을 추천합니다.',
            benefits: ['개인 맞춤형 포트폴리오', 'AI 기반 리스크 분석', '실시간 상품 비교', '전문가 상담 연결']
        },
        '자녀보호터 노후대비까지': {
            description: '생애주기별 필요한 다양한 보장상품을 체계적으로 설계하여 현재와 미래의 안정을 동시에 보장합니다.',
            benefits: ['생애주기별 맞춤 보장', '교육비 준비 플랜', '노후 자금 설계', '가족 보호 종합 솔루션']
        },
        '간편설문조사로 Quick하게': {
            description: '5분 내외의 간단한 설문을 통해 즉시 개인화된 상품 추천을 받을 수 있는 빠른 진단 서비스입니다.',
            benefits: ['5분 내 빠른 진단', '즉시 결과 확인', '모바일 최적화', '간편한 UI/UX']
        },
        '나와 비슷한 사람들의 선택': {
            description: '수십만 고객의 실제 선택 데이터를 바탕으로 나와 유사한 조건의 사람들이 선택한 검증된 상품을 추천합니다.',
            benefits: ['빅데이터 기반 분석', '유사 고객군 매칭', '검증된 상품 추천', '만족도 기반 랭킹']
        }
    };

    // 모달 표시 함수
    function showServiceDetail(title, detail) {
        console.log('모달 열기:', title);
        
        // 기존 모달이 있으면 제거
        const existingModal = document.querySelector('.service-modal');
        if (existingModal) {
            document.body.removeChild(existingModal);
        }

        const modal = document.createElement('div');
        modal.className = 'service-modal';
        modal.style.opacity = '0';
        
        let benefitsHtml = '';
        for (let i = 0; i < detail.benefits.length; i++) {
            benefitsHtml += '<li>' + detail.benefits[i] + '</li>';
        }
        
        modal.innerHTML = 
            '<div class="modal-content">' +
                '<div class="modal-header">' +
                    '<h3>' + title + '</h3>' +
                    '<span class="close-btn">&times;</span>' +
                '</div>' +
                '<div class="modal-body">' +
                    '<p>' + detail.description + '</p>' +
                    '<h4>주요 특징:</h4>' +
                    '<ul>' + benefitsHtml + '</ul>' +
                    '<div class="modal-footer">' +
                        '<button class="detail-btn">자세히 보기</button>' +
                    '</div>' +
                '</div>' +
            '</div>';
        
        document.body.appendChild(modal);
        
        // 모달 표시 애니메이션
        setTimeout(function() {
            modal.style.opacity = '1';
        }, 10);
        
        // 닫기 버튼 이벤트
        const closeBtn = modal.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                console.log('모달 닫기 버튼 클릭');
                modal.style.opacity = '0';
                setTimeout(function() {
                    if (document.body.contains(modal)) {
                        document.body.removeChild(modal);
                    }
                }, 300);
            });
        }
        
        // 배경 클릭으로 닫기
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                console.log('모달 배경 클릭');
                modal.style.opacity = '0';
                setTimeout(function() {
                    if (document.body.contains(modal)) {
                        document.body.removeChild(modal);
                    }
                }, 300);
            }
        });
        
        // 자세히 보기 버튼
        const detailBtn = modal.querySelector('.detail-btn');
        if (detailBtn) {
            detailBtn.addEventListener('click', function() {
                alert(title + ' 상세 페이지로 이동합니다!');
            });
        }
    }

    // 시작 버튼 이벤트
    const startBtn = document.getElementById('startRecommendBtn');
    if (startBtn) {
        console.log('시작 버튼 찾음:', startBtn);
        
        startBtn.addEventListener('click', function(e) {
            console.log('버튼 클릭 이벤트 발생');
            e.preventDefault();
            
            try {
                console.log('페이지 이동 시도...');
                
                // 직접 이동
                window.location.href = '/products/recommend/ai/';
                
                // 대체 방법 1
                // window.location.assign('/products/recommend/ai/');
                
                // 대체 방법 2
                // window.location.replace('/products/recommend/ai/');
                
            } catch (error) {
                console.error('페이지 이동 오류:', error);
                alert('페이지 이동 중 오류가 발생했습니다.');
            }
        });
    } else {
        console.error('시작 버튼을 찾을 수 없습니다!');
    }

    // 서비스 카드들 찾기
    const serviceCards = document.querySelectorAll('.service-card');
    console.log('찾은 카드 수:', serviceCards.length);
    
    // 각 카드에 이벤트 추가
    serviceCards.forEach(function(card, index) {
        const titleElement = card.querySelector('.service-title');
        const titleText = titleElement ? titleElement.textContent : '';
        
        // 클릭 이벤트
        card.addEventListener('click', function() {
            console.log('카드 클릭됨:', index);
            card.style.transform = 'scale(0.98)';
            setTimeout(function() {
                card.style.transform = '';
            }, 150);
        });

        // 더블클릭으로 모달 열기
        card.addEventListener('dblclick', function(e) {
            e.preventDefault();
            console.log('카드 더블클릭:', titleText);
            if (titleText && serviceDetails[titleText]) {
                showServiceDetail(titleText, serviceDetails[titleText]);
            }
        });

        // 마우스 오버 이벤트
        card.addEventListener('mouseenter', function() {
            const numberCircle = card.querySelector('.number-circle');
            const features = card.querySelectorAll('.feature-tag');
            
            if (numberCircle) {
                numberCircle.style.transform = 'rotate(360deg) scale(1.1)';
                numberCircle.style.transition = 'all 0.5s ease';
            }
            
            features.forEach(function(tag, tagIndex) {
                setTimeout(function() {
                    tag.style.transform = 'translateY(-3px) scale(1.05)';
                    tag.style.transition = 'all 0.3s ease';
                }, tagIndex * 100);
            });
        });
        
        card.addEventListener('mouseleave', function() {
            const numberCircle = card.querySelector('.number-circle');
            const features = card.querySelectorAll('.feature-tag');
            
            if (numberCircle) {
                numberCircle.style.transform = 'rotate(0deg) scale(1)';
            }
            
            features.forEach(function(tag) {
                tag.style.transform = 'translateY(0) scale(1)';
            });
        });
    });
    
    // 페이지 로드 애니메이션
    serviceCards.forEach(function(card, index) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(function() {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 200);
    });
});