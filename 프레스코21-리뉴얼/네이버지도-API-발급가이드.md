# 🗺️ 네이버 지도 API 발급 및 구현 가이드

## 📌 목차
1. [네이버 클라우드 플랫폼 가입](#1-네이버-클라우드-플랫폼-가입)
2. [API 키 발급](#2-api-키-발급)
3. [도메인 등록](#3-도메인-등록)
4. [사용량 확인](#4-사용량-확인)
5. [실제 구현 코드](#5-실제-구현-코드)

---

## 1. 네이버 클라우드 플랫폼 가입

### Step 1: 회원가입
1. **네이버 클라우드 플랫폼** 접속
   ```
   https://www.ncloud.com/
   ```

2. 우측 상단 **"회원가입"** 클릭

3. 회원가입 방식 선택
   - **개인 회원**: 본인 인증 (휴대폰 또는 아이핀)
   - **사업자 회원**: 사업자 등록증 필요

4. 약관 동의 후 정보 입력
   - 네이버 계정으로 로그인
   - 휴대폰 인증
   - 결제 정보 등록 (신용카드 - 무료 플랜도 등록 필요)

---

## 2. API 키 발급

### Step 2-1: 콘솔 접속
```
https://console.ncloud.com/
```
로그인 → 상단 메뉴 **"Services"** → **"Application Service"** → **"Maps"** 클릭

### Step 2-2: 애플리케이션 등록

1. **"Application 등록"** 버튼 클릭

2. 정보 입력
   ```
   Application 이름: 프레스코21_파트너맵
   Service 선택: [✓] Web Dynamic Map
   ```

3. **"등록"** 클릭

### Step 2-3: 인증 정보 확인

등록 완료 후 다음 정보 확인:

```
Client ID: (여기 표시됨 - 예: abc123def456)
Client Secret: (보안 키)
```

⚠️ **중요**: Client ID를 복사해두세요!

---

## 3. 도메인 등록

### Step 3-1: Web Service URL 등록

보안을 위해 사용할 도메인을 등록해야 합니다.

1. 애플리케이션 목록에서 방금 만든 앱 클릭

2. **"Web Service URL"** 섹션

3. URL 추가
   ```
   개발용:
   http://localhost
   http://127.0.0.1
   
   운영용:
   https://www.foreverlove.co.kr
   https://foreverlove.co.kr
   ```

4. **"추가"** 클릭

### Step 3-2: 로컬 테스트용 설정

로컬에서 테스트하려면:
```
http://localhost:8000
http://127.0.0.1:8000
```
등도 추가해두면 편리합니다.

---

## 4. 사용량 확인

### 무료 사용량
```
Web Dynamic Map API
- 월 10만 건 무료
- 초과 시: 건당 0.5원

예상 사용량 (프레스코21):
- 월 방문자 1,000명 × 지도 조회 5회 = 5,000건
- 충분히 무료 범위 내!
```

### 사용량 모니터링
```
콘솔 > Application Service > Maps > 사용량 조회
```

---

## 5. 실제 구현 코드

### 📍 발급받은 정보 예시
```javascript
// 여러분이 발급받을 정보
const NAVER_CLIENT_ID = 'abc123def456';  // ← 실제 발급받은 ID로 교체
```

---

## 🎯 빠른 시작 (요약)

```
1. https://www.ncloud.com/ 가입
2. 콘솔 > Application Service > Maps
3. Application 등록 → Client ID 복사
4. Web Service URL 등록 (도메인)
5. 05-partner-map-live.html 파일의 YOUR_CLIENT_ID 부분 교체
```

---

## 📞 문제 해결

### Q1. 지도가 안 보여요 (회색 화면)
**A:** Client ID가 잘못되었거나 도메인이 등록되지 않음
- 콘솔에서 F12 누르고 에러 메시지 확인
- Web Service URL에 현재 도메인 추가

### Q2. "Unauthorized" 에러
**A:** 도메인 불일치
```javascript
// 현재 접속 URL 확인
console.log(window.location.href);

// 콘솔에서 등록된 URL과 일치하는지 확인
```

### Q3. 로컬에서 테스트하고 싶어요
**A:** http://localhost 등록
```
1. 콘솔 > 애플리케이션 > Web Service URL
2. http://localhost 추가
3. http://127.0.0.1 추가
4. 저장
```

### Q4. 비용이 걱정돼요
**A:** 월 10만 건까지 무료
- 일반 쇼핑몰은 대부분 무료 범위 내
- 콘솔에서 실시간 사용량 확인 가능
- 한도 초과 시 알림 설정 가능

---

## 🔗 유용한 링크

- **네이버 클라우드**: https://www.ncloud.com/
- **콘솔**: https://console.ncloud.com/
- **API 문서**: https://api.ncloud-docs.com/docs/ai-naver-mapsgeocoding
- **가격**: https://www.ncloud.com/product/applicationService/maps
- **고객센터**: 1544-7876

---

## 📝 체크리스트

구현 전 확인:
- [ ] 네이버 클라우드 가입 완료
- [ ] Maps API 애플리케이션 등록
- [ ] Client ID 발급받음
- [ ] 도메인 등록 (localhost + 운영 도메인)
- [ ] 05-partner-map-live.html에 Client ID 입력
- [ ] 브라우저에서 테스트

---

## 🚀 다음 단계

1. 이 문서대로 API 키 발급
2. `05-partner-map-live.html` 파일 열기
3. `YOUR_CLIENT_ID` 부분을 발급받은 ID로 교체
4. 브라우저에서 파일 열기
5. 지도가 표시되는지 확인!

---

**예상 소요 시간**: 15-20분  
**난이도**: ⭐⭐☆☆☆ (보통)

궁금한 점이 있으면 언제든 물어보세요! 🗺️
