# ⚡ 빠른 시작 가이드 - Google Sheets 연동

## 🎯 5분 안에 설정 완료하기!

### 준비물
- Google 계정
- 5분의 시간 ⏰

---

## 📝 3단계로 끝내기

### 1️⃣ Google Cloud 설정 (2분)

1. **[이 링크](https://console.cloud.google.com/)** 클릭 → Google Cloud Console
2. **프로젝트 만들기** → 이름: `장사의신` → **만들기**
3. 상단 검색창에 `Google Sheets API` 입력 → **사용 설정** 클릭
4. 상단 검색창에 `Google Drive API` 입력 → **사용 설정** 클릭
5. 좌측 메뉴 **API 및 서비스** → **사용자 인증 정보**
6. **+ 사용자 인증 정보 만들기** → **서비스 계정**
7. 이름: `jangsaui-service` → **만들기** → **완료**
8. 방금 만든 서비스 계정 클릭 → **키** 탭 → **키 추가** → **새 키 만들기**
9. **JSON** 선택 → **만들기** 
10. ✅ JSON 파일 다운로드 완료!

---

### 2️⃣ Google Sheets 만들기 (1분)

1. **[이 링크](https://sheets.google.com/)** 클릭 → Google Sheets
2. **빈 스프레드시트** 클릭
3. 이름: `장사의신_게임_데이터`
4. 우측 상단 **공유** 버튼 클릭
5. JSON 파일을 메모장으로 열기 → `client_email` 항목 복사
   - 예: `jangsaui-service@장사의신.iam.gserviceaccount.com`
6. 복사한 이메일 붙여넣기 → **편집자** 선택 → **보내기**
7. 주소창의 URL 복사
   - 예: `https://docs.google.com/spreadsheets/d/1A2B3C4D5.../edit`
8. ✅ 스프레드시트 준비 완료!

---

### 3️⃣ Streamlit 설정 (2분)

#### A. 로컬 개발 환경

1. 프로젝트 폴더에 `.streamlit` 폴더 생성
2. `.streamlit/secrets.toml` 파일 생성
3. 아래 내용 복사해서 붙여넣기:

```toml
spreadsheet_url = "여기에_2단계에서_복사한_URL_붙여넣기"

[gcp_service_account]
type = "service_account"
project_id = "여기에_JSON의_project_id_복사"
private_key_id = "여기에_JSON의_private_key_id_복사"
private_key = "여기에_JSON의_private_key_복사"
client_email = "여기에_JSON의_client_email_복사"
client_id = "여기에_JSON의_client_id_복사"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "여기에_JSON의_client_x509_cert_url_복사"
```

4. JSON 파일 열기 → 해당 값들 복사해서 붙여넣기
5. ✅ 설정 완료!

#### B. Streamlit Cloud 배포

1. [Streamlit Cloud](https://share.streamlit.io/) 접속
2. 배포된 앱 선택
3. **Settings** → **Secrets** 클릭
4. 위의 내용 그대로 붙여넣기
5. **Save** 클릭
6. ✅ 배포 완료!

---

## 🎉 완료! 이제 테스트하세요

1. 터미널에서 실행:
```bash
streamlit run 장사의신-게임.py
```

2. 사이드바에서 확인:
   - ✅ **"Google Sheets 연동 활성화"** 메시지가 보이면 성공!
   - ❌ **"로컬 모드"** 메시지가 보이면 설정 재확인

3. 테스트:
   - 학생 한 명 등록해보기
   - Google Sheets에 자동으로 저장되는지 확인
   - 다른 기기(휴대폰)에서도 같은 링크로 접속해보기

---

## 🚨 문제 해결

### "로컬 모드" 메시지가 뜹니다

**체크리스트:**
- [ ] `.streamlit/secrets.toml` 파일이 있나요?
- [ ] JSON의 내용을 제대로 복사했나요? (특히 `private_key`는 줄바꿈 포함)
- [ ] `spreadsheet_url`을 올바르게 입력했나요?

### "Permission denied" 오류

**해결:**
- Google Sheets에서 서비스 계정 이메일을 **편집자** 권한으로 공유했는지 확인

### 데이터가 저장 안 됩니다

**해결:**
- Google Cloud에서 **Google Sheets API**와 **Google Drive API** 모두 활성화했는지 확인
- 브라우저 새로고침 (F5)

---

## 📞 추가 도움

상세한 설명이 필요하시면 **`Google-Sheets-연동-가이드.md`** 파일을 참고하세요!

**🎉 이제 모든 학생이 하나의 데이터를 공유합니다!**

