# 🎨 프레스코21 마이페이지 메인 리뉴얼 - 메이크샵 적용 가이드

> 현대적이고 깔끔한 디자인 | 한진택배 API 연동 최적화 | 반응형 디자인

---

## 📋 목차

1. [개요](#개요)
2. [주요 기능](#주요-기능)
3. [메이크샵 적용 방법](#메이크샵-적용-방법)
4. [한진택배 API 연동](#한진택배-api-연동)
5. [커스터마이징 가이드](#커스터마이징-가이드)
6. [문제 해결](#문제-해결)

---

## 📖 개요

### 디자인 컨셉
- **ON STORE 스킨**의 현대적이고 미니멀한 느낌
- **프레스코21 브랜드 컬러** (세이지 그린 #7B8E7E, 뮤트 골드 #B5A48B) 적용
- **4060 세대 최적화**: 큰 폰트, 충분한 여백, 명확한 버튼

### 주요 개선사항
✅ 회원 정보를 카드 형태로 우아하게 표현  
✅ 주문 진행 상태를 시각적 프로그레스로 표시  
✅ 한진택배 API 연동 버튼 강조 (실시간 배송조회)  
✅ 배송중 단계 하이라이트 애니메이션  
✅ PC는 Table/Row, 모바일은 Card 레이아웃  
✅ 접근성 및 키보드 네비게이션 강화

---

## 🎯 주요 기능

### 1️⃣ 회원 정보 카드
- 그라디언트 배경의 우아한 카드 디자인
- 회원 등급 및 혜택 정보 시각화
- 적립금/예치금/포인트/쿠폰 통계 그리드

### 2️⃣ 주문 진행 상태 (프로그레스 바)
```
주문접수 → 결제완료 → 상품준비중 → 배송중 → 배송완료
```
- 각 단계별 아이콘 및 컬러 구분
- 배송중 단계 펄스 애니메이션 강조
- 실시간 카운트 애니메이션

### 3️⃣ 주문 내역 카드
- 날짜, 상품명, 금액 정보
- **[실시간 배송조회]** 버튼 (한진택배 API 연동)
- **[반품신청]** 버튼
- 선물/정기배송 배지 표시

### 4️⃣ 게시글 내역 & 관심상품
- 깔끔한 리스트 및 그리드 레이아웃
- 호버 효과 및 부드러운 트랜지션
- 모바일에서는 숨김 처리 (성능 최적화)

---

## 🛠️ 메이크샵 적용 방법

### Step 1: 스킨 편집 모드 진입

1. **메이크샵 관리자** 로그인
2. **디자인 > 스킨 관리** 이동
3. 현재 사용 중인 스킨의 **[편집]** 클릭
4. **마이페이지 > 마이페이지 메인 (mypage_main.html)** 선택

---

### Step 2: HTML 코드 교체

#### 기존 코드 백업 (중요! ⚠️)
```html
<!-- 기존 코드 전체를 복사해서 메모장에 저장하세요 -->
```

#### 새 HTML 코드 적용
1. `12-mypage-main-renewal.html` 파일 열기
2. `<!--/include_header(1)/-->` **이후 부분**부터 `<!--/include_footer(1)/-->` **이전 부분**까지 복사
3. 메이크샵 스킨 편집기에 붙여넣기

```html
<!--/include_header(1)/-->

<!-- ✂️ 여기서부터 복사 -->
<main class="container mypage-wrapper myMain">
    ...
</main>
<!-- ✂️ 여기까지 복사 -->

<!--/include_footer(1)/-->
```

---

### Step 3: CSS 코드 적용

#### 방법 A: 인라인 스타일 (권장)

HTML 파일 상단 `<head>` 태그 안에 추가:

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Pretendard 폰트 (필수) -->
    <link rel="stylesheet" as="style" crossorigin 
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
    
    <!-- 마이페이지 메인 스타일 -->
    <style>
        /* 12-mypage-main-renewal.css 내용 전체 복사 */
        :root {
            --myp-primary: #7B8E7E;
            --myp-secondary: #B5A48B;
            ...
        }
        /* ... 나머지 CSS ... */
    </style>
</head>
```

#### 방법 B: 외부 CSS 파일 (선택)

1. **FTP 접속**
2. `/skin/현재스킨명/css/` 폴더 이동
3. `mypage-main-renewal.css` 업로드
4. HTML `<head>` 태그에 추가:

```html
<link rel="stylesheet" href="/skin/현재스킨명/css/mypage-main-renewal.css">
```

---

### Step 4: JavaScript 코드 확인

HTML 파일 하단에 이미 포함되어 있습니다:

```javascript
<script>
// 네비게이션 타이틀 변경
if (typeof changeNaviTitleText === 'function') {
    changeNaviTitleText('마이페이지');
}

// 실시간 배송조회 함수
function trackDelivery(orderNo) {
    // 한진택배 API 연동 코드
}

// 반품신청 함수
function requestReturn(orderNo) {
    // 반품 페이지 이동
}

// 숫자 애니메이션
function animateNumbers() {
    // 카운트업 애니메이션
}
</script>
```

---

### Step 5: 저장 및 미리보기

1. **[저장]** 버튼 클릭
2. **[미리보기]** 클릭하여 확인
3. PC/모바일 반응형 확인

---

## 🚚 한진택배 API 연동

### 준비사항

1. **한진택배 API 키 발급**
   - 한진택배 고객센터 문의: 1588-0011
   - 법인/개인사업자 등록증 필요
   - API 사용 신청서 작성

2. **메이크샵 주문번호 ↔ 한진택배 송장번호 연동**
   - 메이크샵 관리자 > 주문/배송 관리
   - 배송정보에 송장번호 입력 필요

---

### 실시간 배송조회 구현

#### 방법 A: 모달 팝업 (권장)

`trackDelivery` 함수 수정:

```javascript
function trackDelivery(orderNo) {
    // 1. 송장번호 조회 (AJAX)
    fetch(`/api/order/invoice?order_no=${orderNo}`)
        .then(response => response.json())
        .then(data => {
            const invoiceNo = data.invoice_no;
            
            // 2. 한진택배 API 호출
            fetch(`https://api.hanjin.co.kr/tracking?inv_no=${invoiceNo}`, {
                headers: {
                    'Authorization': 'Bearer YOUR_API_KEY'
                }
            })
            .then(response => response.json())
            .then(trackingData => {
                // 3. 모달로 배송 정보 표시
                showTrackingModal(trackingData);
            });
        })
        .catch(error => {
            alert('배송 정보를 불러올 수 없습니다.');
            console.error(error);
        });
}

// 모달 표시 함수
function showTrackingModal(data) {
    const modal = `
        <div class="myp-modal-backdrop" onclick="closeModal()">
            <div class="myp-modal" onclick="event.stopPropagation()">
                <h3>실시간 배송조회</h3>
                <div class="myp-tracking-info">
                    <p><strong>송장번호:</strong> ${data.invoiceNo}</p>
                    <p><strong>현재 위치:</strong> ${data.currentLocation}</p>
                    <p><strong>배송 상태:</strong> ${data.status}</p>
                </div>
                <div class="myp-tracking-timeline">
                    ${data.history.map(item => `
                        <div class="myp-timeline-item">
                            <span>${item.date}</span>
                            <span>${item.location}</span>
                            <span>${item.status}</span>
                        </div>
                    `).join('')}
                </div>
                <button class="myp-btn myp-btn-primary" onclick="closeModal()">닫기</button>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modal);
}

function closeModal() {
    document.querySelector('.myp-modal-backdrop').remove();
}
```

#### 방법 B: 새 창 열기 (간편)

```javascript
function trackDelivery(orderNo) {
    // 한진택배 공식 조회 페이지로 이동
    const invoiceNo = '송장번호'; // 실제로는 서버에서 가져와야 함
    window.open(
        `https://www.hanjin.co.kr/kor/CMS/DeliveryMgr/WaybillResult.do?mCode=MN038&schLang=KR&wblnumText2=${invoiceNo}`,
        '_blank',
        'width=800,height=600'
    );
}
```

#### 방법 C: 외부 서비스 이용 (스윗트래커 등)

```javascript
function trackDelivery(orderNo) {
    // 스윗트래커 API 사용 예시
    const SWEET_TRACKER_API_KEY = 'YOUR_API_KEY';
    
    fetch(`https://info.sweettracker.co.kr/api/v1/trackingInfo?t_key=${SWEET_TRACKER_API_KEY}&t_code=05&t_invoice=${invoiceNo}`)
        .then(response => response.json())
        .then(data => {
            console.log('배송 정보:', data);
            showTrackingModal(data);
        });
}
```

---

### 배송 상태별 동적 스타일 적용

주문 카드에 배송 상태에 따라 클래스 추가:

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // 각 주문 카드 순회
    const orderCards = document.querySelectorAll('.myp-order-card');
    
    orderCards.forEach(card => {
        // 배송 상태 데이터 속성 추가 (서버에서 렌더링 시)
        const deliveryStatus = card.dataset.deliveryStatus;
        
        switch(deliveryStatus) {
            case 'delivery_ing':
                card.classList.add('myp-status-delivery');
                card.style.borderColor = 'var(--myp-primary)';
                card.style.boxShadow = '0 0 0 3px rgba(123, 142, 126, 0.1)';
                break;
            case 'delivery_ok':
                card.classList.add('myp-status-complete');
                break;
            case 'order_ready':
                card.classList.add('myp-status-ready');
                break;
        }
    });
});
```

HTML에서 데이터 속성 추가:

```html
<div class="myp-order-card" data-delivery-status="<!--/order_list@delivery_status/-->">
    ...
</div>
```

---

## 🎨 커스터마이징 가이드

### 브랜드 컬러 변경

CSS 파일 상단 `:root` 변수 수정:

```css
:root {
    /* 메인 컬러 변경 */
    --myp-primary: #YOUR_COLOR;           /* 기본 */
    --myp-primary-light: #YOUR_LIGHT;     /* 연한 버전 */
    --myp-primary-dark: #YOUR_DARK;       /* 진한 버전 */
    
    /* 포인트 컬러 변경 */
    --myp-secondary: #YOUR_ACCENT;
}
```

### 간격 조정

```css
:root {
    --myp-space-xs: 8px;   /* 최소 간격 */
    --myp-space-sm: 12px;
    --myp-space-md: 16px;  /* 기본 간격 */
    --myp-space-lg: 24px;
    --myp-space-xl: 32px;  /* 큰 간격 */
    --myp-space-xxl: 48px; /* 섹션 간격 */
}
```

### 폰트 크기 조정 (4060 세대 고려)

```css
:root {
    --myp-font-base: 16px;    /* 기본 폰트 (권장: 16px 이상) */
    --myp-font-small: 14px;
    --myp-font-large: 18px;
}

/* 특정 요소만 변경 */
.myp-member-name {
    font-size: 1.75rem;  /* 더 크게 */
}

.myp-order-brand {
    font-size: 1.25rem;  /* 더 크게 */
}
```

### 버튼 크기 조정

```css
.myp-btn {
    min-height: 48px;      /* 터치 영역 확대 (권장: 44px 이상) */
    padding: 14px 24px;    /* 여유 있는 패딩 */
    font-size: 1rem;       /* 큰 폰트 */
}
```

### 모바일 레이아웃 조정

```css
@media (max-width: 767px) {
    /* 통계 그리드를 4열로 변경 */
    .myp-stats-grid {
        grid-template-columns: repeat(4, 1fr);
        font-size: 0.75rem;  /* 폰트 축소 */
    }
    
    /* 주문 진행 상태를 2줄로 배치 */
    .myp-progress-item {
        flex: 1 1 calc(50% - var(--myp-space-md));
    }
}
```

---

## ❗ 문제 해결

### Q1. 스타일이 적용되지 않아요

**원인 1: 기존 스타일과 충돌**
```css
/* 기존 스타일보다 우선순위 높이기 */
.mypage-wrapper .myp-member-card {
    /* ... */
}

/* 또는 !important 사용 (최후의 수단) */
.myp-member-card {
    background: var(--myp-white) !important;
}
```

**원인 2: 캐시 문제**
- 브라우저 하드 새로고침: `Ctrl + F5` (Windows) / `Cmd + Shift + R` (Mac)
- 메이크샵 관리자 > 디자인 > 캐시 삭제

**원인 3: CSS 파일 경로 오류**
```html
<!-- 경로 확인 -->
<link rel="stylesheet" href="/skin/YOUR_SKIN_NAME/css/mypage-main-renewal.css">
```

---

### Q2. 메이크샵 가상태그가 작동하지 않아요

**확인사항:**
1. 가상태그 철자 정확한지 확인
2. 조건문 `<!--/if_~/-->` ... `<!--/end_if/-->` 닫힘 확인
3. 반복문 `<!--/loop_~/-->` ... `<!--/end_loop/-->` 닫힘 확인

**디버깅 방법:**
```html
<!-- 가상태그 값 확인 -->
<script>
console.log('회원명:', '<!--/user_name/-->');
console.log('주문개수:', '<!--/three_month_order_all/-->');
</script>
```

---

### Q3. 모바일에서 레이아웃이 깨져요

**확인사항:**
1. `<meta name="viewport">` 태그 있는지 확인
2. 미디어 쿼리 순서 확인 (큰 화면 → 작은 화면)

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

```css
/* 올바른 순서 */
@media (max-width: 1199px) { /* 태블릿 */ }
@media (max-width: 991px) { /* 작은 태블릿 */ }
@media (max-width: 767px) { /* 모바일 */ }
```

---

### Q4. 한진택배 API 연동이 안 돼요

**확인사항:**
1. **API 키 발급** 완료 여부
2. **CORS 에러**: 서버 사이드에서 API 호출 필요
3. **송장번호 형식** 확인

**해결 방법:**
```javascript
// 프록시 서버 사용
fetch('/api/proxy/hanjin-tracking', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        invoiceNo: '1234567890'
    })
})
```

**서버 사이드 프록시 (PHP 예시):**
```php
<?php
// /api/proxy/hanjin-tracking.php
$invoiceNo = $_POST['invoiceNo'];
$apiKey = 'YOUR_API_KEY';

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, "https://api.hanjin.co.kr/tracking?inv_no={$invoiceNo}");
curl_setopt($ch, CURLOPT_HTTPHEADER, array("Authorization: Bearer {$apiKey}"));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
curl_close($ch);

header('Content-Type: application/json');
echo $response;
?>
```

---

### Q5. 숫자 애니메이션이 작동하지 않아요

**확인사항:**
1. `DOMContentLoaded` 이벤트 리스너 실행 확인
2. 콘솔 에러 확인

```javascript
// 디버깅 코드 추가
document.addEventListener('DOMContentLoaded', function() {
    console.log('페이지 로드 완료');
    animateNumbers();
});

function animateNumbers() {
    console.log('숫자 애니메이션 시작');
    const numbers = document.querySelectorAll('.myp-progress-count');
    console.log('대상 요소 개수:', numbers.length);
    // ...
}
```

---

## 📱 브라우저 호환성

| 브라우저 | 최소 버전 | 지원 여부 |
|---------|----------|----------|
| Chrome  | 90+      | ✅ 완벽 지원 |
| Safari  | 14+      | ✅ 완벽 지원 |
| Firefox | 88+      | ✅ 완벽 지원 |
| Edge    | 90+      | ✅ 완벽 지원 |
| IE 11   | -        | ❌ 미지원 |

**IE 11 지원이 필요한 경우:**
```html
<!-- Polyfill 추가 -->
<script src="https://cdn.jsdelivr.net/npm/@babel/polyfill@7.12.1/dist/polyfill.min.js"></script>
```

---

## 🎁 추가 기능 구현 예시

### 1️⃣ 주문 내역 필터링

```html
<div class="myp-order-filter">
    <button onclick="filterOrders('all')" class="active">전체</button>
    <button onclick="filterOrders('delivery_ing')">배송중</button>
    <button onclick="filterOrders('delivery_ok')">배송완료</button>
</div>

<script>
function filterOrders(status) {
    const cards = document.querySelectorAll('.myp-order-card');
    cards.forEach(card => {
        if (status === 'all' || card.dataset.deliveryStatus === status) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}
</script>
```

### 2️⃣ 로딩 스피너 추가

```javascript
function trackDelivery(orderNo) {
    // 로딩 표시
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="myp-loading"></span> 조회중...';
    button.disabled = true;
    
    // API 호출
    fetch(`/api/tracking?order_no=${orderNo}`)
        .then(response => response.json())
        .then(data => {
            showTrackingModal(data);
        })
        .finally(() => {
            // 로딩 해제
            button.innerHTML = originalText;
            button.disabled = false;
        });
}
```

### 3️⃣ 토스트 알림

```javascript
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `myp-toast myp-toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('active'), 100);
    setTimeout(() => {
        toast.classList.remove('active');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// 사용 예시
showToast('배송 정보를 불러왔습니다', 'success');
showToast('오류가 발생했습니다', 'error');
```

---

## 📞 고객 지원

### 메이크샵 공식 지원
- 고객센터: 1544-6526
- 이메일: help@makeshop.co.kr
- 운영시간: 평일 09:00 ~ 18:00

### 한진택배 API 지원
- 고객센터: 1588-0011
- 개발자 문의: api@hanjin.co.kr

### 프레스코21 커스터마이징 문의
- 제작자에게 직접 문의

---

## ✅ 체크리스트

설치 완료 후 아래 항목을 확인하세요:

- [ ] PC에서 레이아웃 정상 표시
- [ ] 모바일에서 Card 레이아웃 정상 표시
- [ ] 회원 정보 카드 표시 확인
- [ ] 주문 진행 상태 프로그레스 바 표시 확인
- [ ] 주문 내역 카드 표시 확인
- [ ] [실시간 배송조회] 버튼 클릭 시 동작 확인
- [ ] [반품신청] 버튼 클릭 시 동작 확인
- [ ] 게시글 내역 표시 확인
- [ ] 관심상품 그리드 표시 확인
- [ ] 빈 상태(Empty State) 표시 확인
- [ ] 호버 효과 및 애니메이션 동작 확인
- [ ] 브라우저 캐시 삭제 후 재확인

---

## 📝 업데이트 내역

### v1.0 (2026.01.06)
- 초기 버전 출시
- 프레스코21 브랜드 컬러 시스템 적용
- 한진택배 API 연동 기능 추가
- 반응형 디자인 구현 (PC: Table/Row, Mobile: Card)
- 접근성 및 키보드 네비게이션 강화

---

## 🙏 감사합니다!

프레스코21 마이페이지 메인 리뉴얼을 선택해주셔서 감사합니다.  
더 나은 사용자 경험을 위해 지속적으로 개선하겠습니다.

**Happy Crafting! 🎨✨**

