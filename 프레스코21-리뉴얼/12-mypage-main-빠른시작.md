# ⚡ 프레스코21 마이페이지 메인 - 3단계 빠른 시작

> **소요 시간**: 약 10분  
> **난이도**: ⭐⭐☆☆☆ (초급)

---

## 🎯 시작하기 전에

### 필요한 것
- ✅ 메이크샵 관리자 계정
- ✅ 메이크샵 D4 프레임워크 스킨
- ✅ 제공된 파일 4개
  - `12-mypage-main-renewal.html`
  - `12-mypage-main-renewal.css`
  - `12-mypage-tracking-modal.css`
  - `12-mypage-tracking-modal.js`

### 준비 사항
1. **기존 코드 백업** (중요!)
   - 메이크샵 관리자 > 디자인 > 스킨 관리
   - 마이페이지 메인 HTML 전체 복사 → 메모장 저장
   
2. **브라우저 준비**
   - 크롬, 사파리, 파이어폭스 중 하나

---

## 📦 Step 1: HTML 코드 적용 (3분)

### 1-1. 메이크샵 관리자 접속
```
메이크샵 관리자 로그인
↓
디자인 > 스킨 관리
↓
[편집] 버튼 클릭
↓
마이페이지 > 마이페이지 메인 (mypage_main.html) 선택
```

### 1-2. HTML 코드 교체

**기존 코드 구조:**
```html
<!--/include_header(1)/-->
<!-- 기존 내용 -->
<!--/include_footer(1)/-->
```

**새 코드로 교체:**
1. `12-mypage-main-renewal.html` 파일 열기
2. `<main class="container mypage-wrapper myMain">` 부터 `</main>` 까지 복사
3. 메이크샵 편집기에서 기존 `<main>` 태그 부분 선택 후 붙여넣기

**중요!**
- `<!--/include_header(1)/-->` 태그는 그대로 두기
- `<!--/include_footer(1)/-->` 태그는 그대로 두기

### 1-3. 저장
```
[저장] 버튼 클릭
```

---

## 🎨 Step 2: CSS 스타일 적용 (5분)

### 2-1. Pretendard 폰트 추가 (필수!)

메이크샵 스킨 편집기에서 `<head>` 태그 안에 추가:

```html
<head>
    <!-- 기존 meta 태그들... -->
    
    <!-- Pretendard 폰트 -->
    <link rel="stylesheet" as="style" crossorigin 
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
</head>
```

### 2-2. 메인 CSS 추가

**방법 A: 인라인 스타일 (권장 - 가장 빠름)**

`<head>` 태그 안에 추가:

```html
<style>
/* 12-mypage-main-renewal.css 내용 전체 복사해서 붙여넣기 */
:root {
    --myp-primary: #7B8E7E;
    --myp-secondary: #B5A48B;
    /* ... 나머지 CSS ... */
}
</style>
```

**방법 B: 외부 CSS 파일 (선택)**

1. FTP 접속
2. `/skin/현재스킨명/css/` 폴더에 파일 업로드
   - `mypage-main-renewal.css`
   - `mypage-tracking-modal.css`
3. `<head>` 태그에 추가:

```html
<link rel="stylesheet" href="/skin/현재스킨명/css/mypage-main-renewal.css">
<link rel="stylesheet" href="/skin/현재스킨명/css/mypage-tracking-modal.css">
```

### 2-3. 저장 및 확인
```
[저장] 버튼 클릭
↓
[미리보기] 클릭
```

---

## 🚀 Step 3: JavaScript 기능 추가 (2분)

### 3-1. JavaScript 코드 추가

HTML 파일 **맨 아래**, `</body>` 태그 직전에 추가:

**방법 A: 인라인 스크립트 (권장)**

```html
<script>
/* 12-mypage-tracking-modal.js 내용 전체 복사해서 붙여넣기 */
</script>
</body>
</html>
```

**방법 B: 외부 JavaScript 파일 (선택)**

1. FTP로 `/skin/현재스킨명/js/` 폴더에 업로드
   - `mypage-tracking-modal.js`
2. HTML에 추가:

```html
<script src="/skin/현재스킨명/js/mypage-tracking-modal.js"></script>
</body>
</html>
```

### 3-2. 최종 저장
```
[저장] 버튼 클릭
```

---

## ✅ 완료! 확인하기

### 1️⃣ PC 확인
1. 메이크샵 관리자 > [쇼핑몰 바로가기]
2. 마이페이지 메인 접속
3. 확인 사항:
   - ✅ 회원 정보 카드 표시
   - ✅ 주문 진행 상태 프로그레스 바
   - ✅ 주문 내역 카드
   - ✅ [실시간 배송조회] 버튼
   - ✅ [반품신청] 버튼

### 2️⃣ 모바일 확인
1. 크롬 개발자 도구 열기 (F12)
2. 디바이스 툴바 토글 (Ctrl + Shift + M)
3. iPhone 또는 Galaxy 선택
4. 확인 사항:
   - ✅ Card 레이아웃으로 변경
   - ✅ 버튼이 세로로 배치
   - ✅ 터치하기 편한 크기

### 3️⃣ 기능 테스트
1. [실시간 배송조회] 버튼 클릭
   - ✅ 모달 팝업 표시 (현재는 샘플 데이터)
2. ESC 키 또는 [닫기] 클릭
   - ✅ 모달 닫힘
3. [반품신청] 버튼 클릭
   - ✅ 확인 다이얼로그 표시

---

## 🛠️ 문제 해결

### ❌ 스타일이 적용되지 않아요

**해결 방법 1: 캐시 삭제**
```
브라우저에서 Ctrl + F5 (Windows) / Cmd + Shift + R (Mac)
```

**해결 방법 2: 메이크샵 캐시 삭제**
```
메이크샵 관리자 > 디자인 > 캐시 삭제
```

**해결 방법 3: CSS 우선순위 높이기**
```css
/* 클래스 앞에 추가 */
.mypage-wrapper .myp-member-card {
    /* ... */
}
```

### ❌ 레이아웃이 깨져요

**확인사항:**
1. `<meta name="viewport">` 태그가 있는지 확인
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

2. Pretendard 폰트가 로드되었는지 확인
```
개발자 도구(F12) > Network 탭 > pretendard.min.css 파일 확인
```

### ❌ 버튼을 눌러도 아무 반응이 없어요

**확인사항:**
1. JavaScript 파일이 로드되었는지 확인
```
개발자 도구(F12) > Console 탭 > 에러 메시지 확인
```

2. 함수가 정의되었는지 확인
```javascript
// Console에서 입력
console.log(typeof trackDelivery);  // "function" 출력되어야 함
```

---

## 🎨 간단한 커스터마이징

### 메인 컬러 변경하기

CSS 파일 상단에서:

```css
:root {
    --myp-primary: #YOUR_COLOR;        /* 원하는 색상 코드로 변경 */
    --myp-secondary: #YOUR_ACCENT;     /* 포인트 색상 */
}
```

**추천 컬러 조합:**
- 블루 계열: `#4A90E2` + `#7B8E7E`
- 핑크 계열: `#E91E63` + `#F8BBD0`
- 그린 계열: `#4CAF50` + `#81C784`

### 폰트 크기 키우기 (4060 세대 맞춤)

```css
:root {
    --myp-font-base: 18px;    /* 기본 16px → 18px */
}

.myp-member-name {
    font-size: 1.75rem;       /* 제목 더 크게 */
}
```

### 버튼 크기 키우기

```css
.myp-btn {
    min-height: 52px;         /* 기본 44px → 52px */
    padding: 16px 28px;       /* 여유 있게 */
    font-size: 1.063rem;      /* 폰트도 크게 */
}
```

---

## 📱 한진택배 API 연동 (선택사항)

### 기본 설정 (JavaScript 파일 상단)

```javascript
const TrackingConfig = {
    API_URL: '/api/hanjin/tracking',  // 서버 API 주소
    API_KEY: 'YOUR_HANJIN_API_KEY',   // 한진택배 API 키
};
```

### 간편 버전 (한진택배 공식 페이지 링크)

JavaScript 파일에서 `trackDelivery` 함수만 수정:

```javascript
function trackDelivery(orderNo) {
    // 송장번호 (실제로는 서버에서 가져와야 함)
    const invoiceNo = '1234567890';
    
    // 한진택배 공식 조회 페이지 열기
    window.open(
        `https://www.hanjin.co.kr/kor/CMS/DeliveryMgr/WaybillResult.do?wblnumText2=${invoiceNo}`,
        '_blank',
        'width=800,height=600'
    );
}
```

---

## 📚 다음 단계

### 1️⃣ 상세 가이드 읽기
- `12-mypage-main-설치가이드.md` - 완전한 설치 및 커스터마이징 가이드
- `12-mypage-main-완성보고서.md` - 프로젝트 전체 개요

### 2️⃣ 한진택배 API 연동
- 한진택배 고객센터 (1588-0011) 문의
- API 키 발급 신청
- 프록시 서버 구축

### 3️⃣ 추가 커스터마이징
- 브랜드 컬러 변경
- 레이아웃 조정
- 추가 기능 구현

---

## 🎉 완료!

축하합니다! 프레스코21 마이페이지 메인 리뉴얼이 완료되었습니다.

이제 고객들에게 더 나은 쇼핑 경험을 제공할 수 있습니다.

**질문이 있으시면 상세 가이드를 참고해주세요!**

---

## 📞 지원

### 메이크샵 공식
- 📞 1544-6526
- 📧 help@makeshop.co.kr

### 한진택배 API
- 📞 1588-0011
- 📧 api@hanjin.co.kr

---

**Happy Shopping! 🛒✨**

