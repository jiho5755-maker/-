# 네이버 지도 API 인증 실패 해결 방법

## 🔴 현재 문제

서버는 정상 작동하지만 네이버 지도 API 인증 실패 에러가 발생합니다.

**원인:** 네이버 클라우드 플랫폼 콘솔에서 Web Service URL이 등록되지 않음

---

## ✅ 해결 방법 (5분)

### Step 1: 네이버 클라우드 플랫폼 콘솔 접속

1. **브라우저에서 접속:**
   ```
   https://console.ncloud.com/
   ```

2. **로그인** (네이버 계정)

---

### Step 2: Maps 애플리케이션 찾기

1. 상단 메뉴: **"Services"** → **"Application Service"** → **"Maps"** 클릭

2. 애플리케이션 목록에서 **"프레스코21_파트너맵"** (또는 해당 애플리케이션) 클릭

---

### Step 3: Web Service URL 등록

1. 페이지 중간 **"Web Service URL"** 섹션 찾기

2. **"URL 추가"** 또는 **"추가"** 버튼 클릭

3. 다음 URL들을 하나씩 추가:

   ```
   http://localhost
   http://127.0.0.1
   http://localhost:8080
   http://127.0.0.1:8080
   ```

   ⚠️ **참고:** 
   - `http://localhost`만 등록해도 포트 번호와 상관없이 작동할 수 있습니다
   - 하지만 확실하게 하려면 `http://localhost:8080`도 추가하는 것이 좋습니다

4. 각 URL 입력 후 **"추가"** 또는 **"저장"** 클릭

5. 페이지 하단 **"저장"** 또는 **"적용"** 버튼 클릭

---

### Step 4: 대기 (5~10분)

네이버 클라우드 플랫폼에서 설정이 적용되는데 시간이 걸립니다.

**5~10분 정도 기다린 후** 다음 단계로 진행하세요.

---

### Step 5: 브라우저 캐시 삭제 및 재테스트

1. **브라우저 캐시 삭제:**
   - **Mac**: Cmd + Shift + Delete
   - **Windows**: Ctrl + Shift + Delete
   - "캐시된 이미지 및 파일" 체크 → "지우기"

2. **또는 강제 새로고침:**
   - **Mac**: Cmd + Shift + R
   - **Windows**: Ctrl + Shift + R

3. **서버 재시작** (선택사항):
   ```bash
   # 터미널에서
   cd "/Users/jangjiho/Desktop/커서AI/프레스코21 제휴업체 맵"
   python3 -m http.server 8080
   ```

4. **브라우저에서 접속:**
   ```
   http://localhost:8080/제휴업체-지도-통합본.html
   ```

5. **결과 확인:**
   - 네이버 지도가 정상적으로 표시되면 ✅ 성공!
   - 여전히 에러가 나면 아래 "추가 확인사항" 참고

---

## 📋 추가 확인사항

### 1. Client ID 확인

HTML 파일의 Client ID와 네이버 콘솔의 Client ID가 일치하는지 확인:

**HTML 파일 (12번째 줄):**
```html
<script type="text/javascript" src="https://oapi.map.naver.com/openapi/v3/maps.js?ncpClientId=bfp8odep5r"></script>
```

**네이버 콘솔:**
- Maps 애플리케이션 페이지 상단에 표시된 Client ID
- 현재: `bfp8odep5r` (일치해야 함)

---

### 2. Web Service URL 등록 확인

네이버 콘솔의 Web Service URL 섹션에 다음이 있는지 확인:

- ✅ `http://localhost` (또는 `http://localhost:8080`)
- ✅ `http://127.0.0.1` (선택사항)

---

### 3. 서비스 선택 확인

Maps 애플리케이션 설정에서 다음 서비스가 선택되어 있는지 확인:

- ✅ **Web Dynamic Map** (필수)
- ✅ **Static Map** (선택사항)
- ✅ **Geocoding** (선택사항)

---

## 🔍 문제 해결 체크리스트

- [ ] 네이버 클라우드 플랫폼 콘솔 접속 성공
- [ ] Maps 애플리케이션 찾기 성공
- [ ] Web Service URL에 `http://localhost` 추가
- [ ] 저장/적용 완료
- [ ] 5~10분 대기
- [ ] 브라우저 캐시 삭제 (Cmd+Shift+R)
- [ ] 서버 재시작
- [ ] `http://localhost:8080/제휴업체-지도-통합본.html` 접속
- [ ] 네이버 지도가 정상적으로 표시됨

---

## 💡 참고사항

### localhost는 포트 번호와 상관없이 작동

`http://localhost`를 등록하면:
- `http://localhost:8080`
- `http://localhost:3000`
- `http://localhost:8000`

등 모든 포트에서 작동합니다.

하지만 확실하게 하려면 `http://localhost:8080`도 명시적으로 등록하는 것이 좋습니다.

---

## 🆘 여전히 안 되면

### 네이버 클라우드 플랫폼 고객센터

- **전화**: 1544-7876
- **문의 내용**:
  ```
  Maps API 사용 중 인증 실패 에러 발생
  Client ID: bfp8odep5r
  Web Service URL: http://localhost 등록 완료
  localhost:8080에서 테스트 중
  인증 실패 원인 확인 부탁드립니다
  ```

---

## ✅ 성공 확인

다음이 모두 확인되면 성공입니다:

1. ✅ 브라우저 주소창: `http://localhost:8080/제휴업체-지도-통합본.html`
2. ✅ 네이버 지도가 정상적으로 표시됨
3. ✅ 마커가 표시됨 (데이터가 있는 경우)
4. ✅ 콘솔(F12)에 네이버 지도 API 인증 오류 없음
5. ✅ 콘솔에 "데이터 로드 완료: X개 업체" 메시지 표시

