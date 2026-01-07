/**
 * ╔═══════════════════════════════════════════════════════════════╗
 * ║  한진택배 배송조회 모달 JavaScript                             ║
 * ║  실시간 배송 추적 & 우아한 UI/UX                              ║
 * ╚═══════════════════════════════════════════════════════════════╝
 */

// =====================================================
// 1. 전역 설정
// =====================================================
const TrackingConfig = {
    // 한진택배 API 설정 (실제 사용 시 변경 필요)
    API_KEY: 'YOUR_HANJIN_API_KEY',
    API_URL: '/api/hanjin/tracking',  // 프록시 서버 엔드포인트
    
    // 스윗트래커 사용 시 (대안)
    SWEET_TRACKER_KEY: 'YOUR_SWEET_TRACKER_KEY',
    SWEET_TRACKER_URL: 'https://info.sweettracker.co.kr/api/v1/trackingInfo',
    CARRIER_CODE: '05',  // 한진택배 코드
    
    // UI 설정
    ANIMATION_DURATION: 300,
    AUTO_CLOSE_DELAY: 0,  // 0이면 자동 닫기 비활성화
};

// =====================================================
// 2. 배송조회 메인 함수
// =====================================================

/**
 * 실시간 배송조회 모달 열기
 * @param {string} orderNo - 주문번호
 */
async function trackDelivery(orderNo) {
    try {
        // 1. 로딩 모달 표시
        showTrackingLoading();
        
        // 2. 주문 정보로부터 송장번호 조회
        const invoiceNo = await getInvoiceNumber(orderNo);
        
        if (!invoiceNo) {
            showTrackingError('송장번호를 찾을 수 없습니다.');
            return;
        }
        
        // 3. 한진택배 API 호출
        const trackingData = await fetchTrackingData(invoiceNo);
        
        if (!trackingData) {
            showTrackingError('배송 정보를 불러올 수 없습니다.');
            return;
        }
        
        // 4. 배송 정보 모달 표시
        showTrackingModal(trackingData);
        
    } catch (error) {
        console.error('배송조회 오류:', error);
        showTrackingError('일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
    }
}

/**
 * 반품신청
 * @param {string} orderNo - 주문번호
 */
function requestReturn(orderNo) {
    const confirmed = confirm(
        '해당 주문의 반품을 신청하시겠습니까?\n\n' +
        '반품 신청 후 고객센터에서 확인 후 처리됩니다.'
    );
    
    if (confirmed) {
        // 반품 신청 페이지로 이동
        location.href = `/mypage/return?order_no=${orderNo}`;
    }
}

// =====================================================
// 3. API 호출 함수
// =====================================================

/**
 * 주문번호로 송장번호 조회
 * @param {string} orderNo - 주문번호
 * @returns {Promise<string|null>} 송장번호
 */
async function getInvoiceNumber(orderNo) {
    try {
        const response = await fetch(`/api/order/invoice?order_no=${orderNo}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        if (!response.ok) {
            throw new Error('송장번호 조회 실패');
        }
        
        const data = await response.json();
        return data.invoice_no || null;
        
    } catch (error) {
        console.error('송장번호 조회 오류:', error);
        return null;
    }
}

/**
 * 한진택배 배송 정보 조회
 * @param {string} invoiceNo - 송장번호
 * @returns {Promise<Object|null>} 배송 정보
 */
async function fetchTrackingData(invoiceNo) {
    try {
        // 방법 1: 자체 프록시 서버 사용
        const response = await fetch(TrackingConfig.API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                invoiceNo: invoiceNo,
                apiKey: TrackingConfig.API_KEY,
            }),
        });
        
        if (!response.ok) {
            throw new Error('배송 정보 조회 실패');
        }
        
        const data = await response.json();
        return formatTrackingData(data);
        
    } catch (error) {
        console.error('배송 정보 조회 오류:', error);
        
        // 방법 2: 스윗트래커 사용 (대안)
        return await fetchTrackingDataFromSweetTracker(invoiceNo);
    }
}

/**
 * 스윗트래커로 배송 정보 조회 (대안)
 * @param {string} invoiceNo - 송장번호
 * @returns {Promise<Object|null>} 배송 정보
 */
async function fetchTrackingDataFromSweetTracker(invoiceNo) {
    try {
        const url = `${TrackingConfig.SWEET_TRACKER_URL}?` +
            `t_key=${TrackingConfig.SWEET_TRACKER_KEY}&` +
            `t_code=${TrackingConfig.CARRIER_CODE}&` +
            `t_invoice=${invoiceNo}`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error('스윗트래커 조회 실패');
        }
        
        const data = await response.json();
        return formatSweetTrackerData(data);
        
    } catch (error) {
        console.error('스윗트래커 조회 오류:', error);
        return null;
    }
}

// =====================================================
// 4. 데이터 포맷팅 함수
// =====================================================

/**
 * 한진택배 API 응답 데이터 포맷팅
 * @param {Object} rawData - 원본 API 응답
 * @returns {Object} 포맷팅된 데이터
 */
function formatTrackingData(rawData) {
    return {
        invoiceNo: rawData.invoice_no,
        sender: rawData.sender_name,
        receiver: rawData.receiver_name,
        status: rawData.delivery_status,
        statusText: getStatusText(rawData.delivery_status),
        currentLocation: rawData.current_location,
        estimatedDate: rawData.estimated_delivery_date,
        history: rawData.tracking_history.map(item => ({
            date: formatDateTime(item.datetime),
            location: item.location,
            status: item.status_text,
            detail: item.detail_message,
        })),
    };
}

/**
 * 스윗트래커 API 응답 데이터 포맷팅
 * @param {Object} rawData - 원본 API 응답
 * @returns {Object} 포맷팅된 데이터
 */
function formatSweetTrackerData(rawData) {
    return {
        invoiceNo: rawData.invoiceNo,
        sender: rawData.senderName,
        receiver: rawData.receiverName,
        status: rawData.level,
        statusText: rawData.levelText,
        currentLocation: rawData.lastDetail?.where || '-',
        estimatedDate: rawData.completeYN === 'Y' ? '배송완료' : '배송중',
        history: rawData.trackingDetails.map(item => ({
            date: `${item.timeString}`,
            location: item.where,
            status: item.kind,
            detail: item.telno,
        })),
    };
}

/**
 * 배송 상태 텍스트 반환
 * @param {string} status - 상태 코드
 * @returns {string} 상태 텍스트
 */
function getStatusText(status) {
    const statusMap = {
        'ready': '상품준비중',
        'pickup': '집화완료',
        'transit': '배송중',
        'out': '배송출발',
        'complete': '배송완료',
    };
    return statusMap[status] || '확인중';
}

/**
 * 날짜/시간 포맷팅
 * @param {string} datetime - 날짜/시간 문자열
 * @returns {string} 포맷팅된 날짜/시간
 */
function formatDateTime(datetime) {
    const date = new Date(datetime);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${year}.${month}.${day} ${hours}:${minutes}`;
}

// =====================================================
// 5. UI 렌더링 함수
// =====================================================

/**
 * 배송조회 모달 표시
 * @param {Object} data - 배송 정보 데이터
 */
function showTrackingModal(data) {
    const modalHTML = `
        <div class="myp-modal-backdrop active" onclick="closeTrackingModal(event)" role="dialog" aria-modal="true" aria-labelledby="modal-title">
            <div class="myp-modal" onclick="event.stopPropagation()">
                <!-- 헤더 -->
                <div class="myp-modal-header">
                    <h3 class="myp-modal-title" id="modal-title">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <path d="M16 3H1V16H16V3Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M16 8H20L23 11V16H16V8Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <circle cx="5.5" cy="19.5" r="2.5" stroke="currentColor" stroke-width="2"/>
                            <circle cx="18.5" cy="19.5" r="2.5" stroke="currentColor" stroke-width="2"/>
                        </svg>
                        실시간 배송조회
                    </h3>
                    <button class="myp-modal-close" onclick="closeTrackingModal()" aria-label="닫기">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </button>
                </div>
                
                <!-- 본문 -->
                <div class="myp-modal-body">
                    <!-- 배송 기본 정보 -->
                    <div class="myp-tracking-info">
                        <div class="myp-tracking-item">
                            <span class="myp-tracking-label">송장번호</span>
                            <span class="myp-tracking-value">${data.invoiceNo}</span>
                        </div>
                        <div class="myp-tracking-item">
                            <span class="myp-tracking-label">배송 상태</span>
                            <span class="myp-delivery-badge status-${data.status}">
                                ${data.statusText}
                            </span>
                        </div>
                        <div class="myp-tracking-item">
                            <span class="myp-tracking-label">보내는 분</span>
                            <span class="myp-tracking-value">${data.sender}</span>
                        </div>
                        <div class="myp-tracking-item">
                            <span class="myp-tracking-label">받는 분</span>
                            <span class="myp-tracking-value">${data.receiver}</span>
                        </div>
                        <div class="myp-tracking-item">
                            <span class="myp-tracking-label">현재 위치</span>
                            <span class="myp-tracking-value highlight">${data.currentLocation}</span>
                        </div>
                        <div class="myp-tracking-item">
                            <span class="myp-tracking-label">예상 도착</span>
                            <span class="myp-tracking-value">${data.estimatedDate}</span>
                        </div>
                    </div>
                    
                    <!-- 배송 타임라인 -->
                    <div class="myp-tracking-timeline">
                        <h4 class="myp-timeline-title">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <path d="M10 18C14.4183 18 18 14.4183 18 10C18 5.58172 14.4183 2 10 2C5.58172 2 2 5.58172 2 10C2 14.4183 5.58172 18 10 18Z" stroke="#7B8E7E" stroke-width="2"/>
                                <path d="M10 6V10L13 11" stroke="#7B8E7E" stroke-width="2" stroke-linecap="round"/>
                            </svg>
                            배송 이력
                        </h4>
                        <div class="myp-timeline-list">
                            ${data.history.map((item, index) => `
                                <div class="myp-timeline-item ${index === 0 ? 'latest' : ''}">
                                    <span class="myp-timeline-date">${item.date}</span>
                                    <span class="myp-timeline-location">${item.location}</span>
                                    <span class="myp-timeline-status">${item.status}</span>
                                    ${item.detail ? `<span class="myp-timeline-detail">${item.detail}</span>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                
                <!-- 푸터 -->
                <div class="myp-modal-footer">
                    <button class="myp-modal-btn myp-modal-btn-secondary" onclick="printTracking()">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M4 6V1H12V6M4 12H2C1.46957 12 0.960859 11.7893 0.585786 11.4142C0.210714 11.0391 0 10.5304 0 10V7C0 6.46957 0.210714 5.96086 0.585786 5.58579C0.960859 5.21071 1.46957 5 2 5H14C14.5304 5 15.0391 5.21071 15.4142 5.58579C15.7893 5.96086 16 6.46957 16 7V10C16 10.5304 15.7893 11.0391 15.4142 11.4142C15.0391 11.7893 14.5304 12 14 12H12M4 9H12V15H4V9Z" fill="currentColor"/>
                        </svg>
                        인쇄하기
                    </button>
                    <button class="myp-modal-btn myp-modal-btn-primary" onclick="closeTrackingModal()">
                        확인
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // 기존 모달이 있으면 제거
    const existingModal = document.querySelector('.myp-modal-backdrop');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 새 모달 추가
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Body 스크롤 방지
    document.body.style.overflow = 'hidden';
    
    // ESC 키로 닫기
    document.addEventListener('keydown', handleEscapeKey);
    
    // 자동 닫기 (설정된 경우)
    if (TrackingConfig.AUTO_CLOSE_DELAY > 0) {
        setTimeout(closeTrackingModal, TrackingConfig.AUTO_CLOSE_DELAY);
    }
}

/**
 * 로딩 상태 모달 표시
 */
function showTrackingLoading() {
    const loadingHTML = `
        <div class="myp-modal-backdrop active" role="dialog" aria-modal="true" aria-labelledby="loading-text">
            <div class="myp-modal">
                <div class="myp-tracking-loading">
                    <div class="myp-tracking-spinner"></div>
                    <p class="myp-tracking-loading-text" id="loading-text">배송 정보를 불러오는 중...</p>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', loadingHTML);
    document.body.style.overflow = 'hidden';
}

/**
 * 에러 상태 모달 표시
 * @param {string} message - 에러 메시지
 */
function showTrackingError(message) {
    // 기존 모달 제거
    const existingModal = document.querySelector('.myp-modal-backdrop');
    if (existingModal) {
        existingModal.remove();
    }
    
    const errorHTML = `
        <div class="myp-modal-backdrop active" onclick="closeTrackingModal(event)" role="dialog" aria-modal="true">
            <div class="myp-modal" onclick="event.stopPropagation()">
                <div class="myp-modal-header">
                    <h3 class="myp-modal-title">배송조회 오류</h3>
                    <button class="myp-modal-close" onclick="closeTrackingModal()" aria-label="닫기">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </button>
                </div>
                <div class="myp-tracking-empty">
                    <div class="myp-tracking-empty-icon">
                        <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                            <circle cx="24" cy="24" r="22" stroke="currentColor" stroke-width="4"/>
                            <path d="M24 14V26M24 34V38" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>
                        </svg>
                    </div>
                    <h4 class="myp-tracking-empty-title">배송 정보를 찾을 수 없습니다</h4>
                    <p class="myp-tracking-empty-text">${message}</p>
                </div>
                <div class="myp-modal-footer">
                    <button class="myp-modal-btn myp-modal-btn-primary" onclick="closeTrackingModal()">확인</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', errorHTML);
}

/**
 * 모달 닫기
 * @param {Event} event - 클릭 이벤트
 */
function closeTrackingModal(event) {
    // Backdrop 클릭 시에만 닫기 (event가 있는 경우)
    if (event && event.target.classList.contains('myp-modal')) {
        return;
    }
    
    const modal = document.querySelector('.myp-modal-backdrop');
    if (modal) {
        modal.classList.remove('active');
        
        setTimeout(() => {
            modal.remove();
            document.body.style.overflow = '';
        }, TrackingConfig.ANIMATION_DURATION);
    }
    
    // ESC 키 이벤트 제거
    document.removeEventListener('keydown', handleEscapeKey);
}

/**
 * ESC 키 핸들러
 * @param {KeyboardEvent} event - 키보드 이벤트
 */
function handleEscapeKey(event) {
    if (event.key === 'Escape') {
        closeTrackingModal();
    }
}

/**
 * 배송 정보 인쇄
 */
function printTracking() {
    window.print();
}

// =====================================================
// 6. 페이지 로드 시 초기화
// =====================================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ 한진택배 배송조회 모듈 로드 완료');
    
    // 숫자 카운트 애니메이션
    animateNumbers();
    
    // 주문 상태에 따른 스타일 적용
    applyOrderStatusStyles();
});

/**
 * 숫자 카운트 애니메이션
 */
function animateNumbers() {
    const numbers = document.querySelectorAll('.myp-progress-count, .myp-stat-value strong');
    
    numbers.forEach(element => {
        const targetText = element.textContent.replace(/,/g, '');
        const target = parseInt(targetText) || 0;
        
        if (target === 0) return;
        
        let current = 0;
        const increment = target / 30;
        const duration = 1000;
        const stepTime = duration / 30;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = target.toLocaleString();
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current).toLocaleString();
            }
        }, stepTime);
    });
}

/**
 * 주문 상태별 스타일 적용
 */
function applyOrderStatusStyles() {
    const orderCards = document.querySelectorAll('.myp-order-card');
    
    orderCards.forEach(card => {
        const status = card.dataset.deliveryStatus;
        
        if (status === 'delivery_ing') {
            card.style.borderColor = 'var(--myp-primary)';
            card.style.boxShadow = '0 0 0 3px rgba(123, 142, 126, 0.1)';
        }
    });
}

// =====================================================
// 7. 전역 함수 노출
// =====================================================
window.trackDelivery = trackDelivery;
window.requestReturn = requestReturn;
window.closeTrackingModal = closeTrackingModal;
window.printTracking = printTracking;

console.log('🚚 한진택배 배송조회 시스템 준비 완료');

