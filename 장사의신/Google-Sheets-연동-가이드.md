# 📊 장사의신 게임 - Google Sheets 연동 가이드

## 🎯 개요

이제 **장사의신 게임**이 Google Sheets와 연동되어, **여러 명이 동시에** PC와 모바일에서 데이터를 공유할 수 있습니다!

### ✅ 해결된 문제
- ❌ **이전**: 각 사용자의 브라우저 세션마다 데이터가 독립적으로 저장됨
- ✅ **현재**: 모든 사용자가 Google Sheets에서 실시간으로 데이터 공유

---

## 🚀 설정 방법

### 1단계: Google Cloud Console 설정

#### 1.1 프로젝트 생성
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 (예: "장사의신-게임")

#### 1.2 Google Sheets API 활성화
1. 좌측 메뉴 → **API 및 서비스** → **라이브러리**
2. "Google Sheets API" 검색 → **사용 설정**
3. "Google Drive API"도 검색 → **사용 설정**

#### 1.3 서비스 계정 생성
1. 좌측 메뉴 → **API 및 서비스** → **사용자 인증 정보**
2. **+ 사용자 인증 정보 만들기** → **서비스 계정** 선택
3. 서비스 계정 이름 입력 (예: "jangsaui-god-service")
4. **완료** 클릭

#### 1.4 서비스 계정 키 생성
1. 생성된 서비스 계정 클릭
2. **키** 탭 → **키 추가** → **새 키 만들기**
3. **JSON** 선택 → **만들기**
4. JSON 파일이 다운로드됩니다 (절대 분실하지 마세요!)

---

### 2단계: Google Sheets 생성

1. [Google Sheets](https://sheets.google.com/) 접속
2. 새 스프레드시트 생성
3. 스프레드시트 이름: **"장사의신_게임_데이터"**
4. 우측 상단 **공유** 클릭
5. 서비스 계정 이메일 주소 추가 (JSON 파일의 `client_email`)
6. **편집자** 권한 부여
7. 스프레드시트 URL 복사 (예: `https://docs.google.com/spreadsheets/d/1A2B3C4D5...`)

---

### 3단계: Streamlit Secrets 설정

#### 로컬 개발 환경 (`.streamlit/secrets.toml`)

프로젝트 폴더에 `.streamlit` 폴더 생성 후 `secrets.toml` 파일 생성:

```toml
# Google Sheets 스프레드시트 URL
spreadsheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit"

# Google Cloud 서비스 계정 정보
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
```

**⚠️ 주의**: 다운로드한 JSON 파일의 내용을 복사해서 위 형식에 맞게 입력하세요!

#### Streamlit Cloud 배포 환경

1. Streamlit Cloud 대시보드 접속
2. 배포된 앱 선택
3. **Settings** → **Secrets** 클릭
4. 위와 동일한 내용을 TOML 형식으로 입력
5. **Save** 클릭

---

## 📖 사용 방법

### ✨ 자동 동기화

데이터가 자동으로 Google Sheets에 저장됩니다:

1. **창업 컨설팅** → 학생 정보 입력 → 자동 저장
2. **판매 관리** → 판매 결과 입력 → 자동 저장
3. **대시보드** → 실시간 순위 확인

### 🔄 수동 새로고침

다른 사용자가 입력한 데이터를 즉시 확인하려면:

1. 사이드바 → **🔄 데이터 새로고침** 버튼 클릭
2. 최신 데이터가 로드됩니다

### 📊 Google Sheets에서 직접 확인

- 사이드바의 **📝 스프레드시트 열기** 링크 클릭
- Google Sheets에서 모든 학생 데이터를 한눈에 확인 가능
- Excel로 내보내기, 차트 생성 등 자유롭게 활용 가능

---

## 🛠️ 문제 해결

### ⚠️ "로컬 모드 (세션 전용)" 메시지

**원인**: Google Sheets 연동 설정이 없음

**해결**:
1. `secrets.toml` 파일 확인
2. 서비스 계정 JSON 정보가 올바르게 입력되었는지 확인
3. 스프레드시트 URL이 정확한지 확인

### ⚠️ "Google Sheets 연결 오류"

**원인**: API 권한 또는 서비스 계정 설정 문제

**해결**:
1. Google Cloud Console에서 Google Sheets API, Google Drive API가 활성화되어 있는지 확인
2. 스프레드시트를 서비스 계정과 공유했는지 확인
3. 서비스 계정에 **편집자** 권한이 있는지 확인

### ⚠️ "데이터 저장 오류"

**원인**: API 요청 제한 또는 네트워크 문제

**해결**:
1. 잠시 후 다시 시도
2. Google Sheets API 할당량 확인
3. 네트워크 연결 확인

---

## 🔒 보안 주의사항

1. **JSON 키 파일 절대 공유 금지**
   - GitHub에 업로드하지 마세요
   - `.gitignore`에 추가하세요: `.streamlit/secrets.toml`

2. **서비스 계정 권한 최소화**
   - 해당 스프레드시트만 공유
   - 불필요한 권한 부여하지 않기

3. **정기적인 키 교체**
   - 보안을 위해 주기적으로 서비스 계정 키 재발급

---

## 📌 데이터 구조

Google Sheets의 열 구조:

| 열 | 항목 | 설명 |
|---|------|------|
| A | 이름 | 학생 이름 |
| B | 사업유형 | 창업 사업 유형 |
| C | 상품등급 | 상품 등급 |
| D | 추천원가 | AI/시스템이 추천한 원가 |
| E | 1R_판매가 | 1라운드 판매 단가 |
| F | 1R_판매량 | 1라운드 판매 수량 |
| G | 1R_매출 | 1라운드 매출액 |
| H | 1R_원가 | 1라운드 총 원가 |
| I | 1R_순이익 | 1라운드 순이익 |
| J | 2R_판매가 | 2라운드 판매 단가 |
| K | 2R_판매량 | 2라운드 판매 수량 |
| L | 2R_매출 | 2라운드 매출액 |
| M | 2R_원가 | 2라운드 총 원가 |
| N | 2R_순이익 | 2라운드 순이익 |

---

## 🎓 선생님/관리자 팁

1. **실시간 모니터링**
   - Google Sheets를 PC에서 열어두고 학생들의 입력을 실시간으로 확인

2. **데이터 분석**
   - Google Sheets의 차트 기능으로 시각화
   - Excel로 내보내기해서 상세 분석

3. **백업**
   - Google Sheets는 자동으로 버전 관리됨
   - **파일** → **버전 기록** → **버전 기록 보기**로 이전 데이터 복원 가능

4. **다중 클래스 운영**
   - 클래스별로 별도의 스프레드시트 생성
   - 각각 다른 URL 사용

---

## 📞 도움이 필요하신가요?

- Google Cloud 설정이 어려우시면 관리자에게 문의하세요
- 오류 메시지를 스크린샷으로 공유해주시면 더 빠르게 도와드릴 수 있습니다

---

**🎉 이제 모든 학생들이 하나의 시스템에서 함께 '장사의신' 게임을 즐길 수 있습니다!**

