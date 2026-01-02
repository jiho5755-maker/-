# 🚀 GitHub 업로드 & Streamlit Cloud 배포 완전 가이드

## 📌 1단계: GitHub에서 새 저장소 만들기

### 웹 브라우저에서 진행:

1. **GitHub 접속**: https://github.com 
2. **우측 상단 '+' 버튼** 클릭
3. **'New repository'** 선택
4. **저장소 정보 입력**:
   - Repository name: `jangsaui-sin-game` (또는 원하는 이름)
   - Description: "장사의 신 - 경제 교육 게임"
   - **Public** 선택 (Streamlit Cloud는 Public만 지원)
   - ⚠️ **아래 체크박스는 모두 체크 안 함!**
     - ❌ Add a README file (체크 안 함)
     - ❌ Add .gitignore (체크 안 함)
     - ❌ Choose a license (체크 안 함)
5. **'Create repository'** 버튼 클릭

✅ 저장소가 만들어지면 **주소(URL)** 복사해두기!
   예: `https://github.com/당신아이디/jangsaui-sin-game.git`

---

## 💻 2단계: 터미널에서 Git 명령어 실행

### 아래 명령어를 터미널에 복사+붙여넣기 하세요:

```bash
# 작업 디렉토리로 이동
cd "/Users/jangjiho/Desktop/커서AI"

# Git 초기화
git init

# Git 사용자 정보 설정 (처음만)
git config user.name "당신의이름"
git config user.email "당신의이메일@example.com"

# 파일 추가
git add 장사의신-게임.py requirements.txt 장사의신-게임-README.md 장사의신-게임-교사용-해설서.md

# 커밋
git commit -m "장사의 신 게임 초기 버전"

# 기본 브랜치 이름을 main으로 변경
git branch -M main

# GitHub 저장소 연결 (⚠️ YOUR_GITHUB_USERNAME과 YOUR_REPO_NAME을 실제 값으로 변경!)
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git

# GitHub에 업로드
git push -u origin main
```

### ⚠️ 중요: 명령어 수정 필요!

위 명령어에서 다음 부분을 **실제 값으로 변경**하세요:
- `당신의이름` → GitHub 아이디
- `당신의이메일@example.com` → GitHub 가입 시 사용한 이메일
- `YOUR_GITHUB_USERNAME` → GitHub 아이디
- `YOUR_REPO_NAME` → 1단계에서 만든 저장소 이름

---

## 🔐 3단계: GitHub 인증 (push 시 나타남)

`git push` 명령어 실행 시:

### 옵션 A: Personal Access Token 사용 (권장)
1. Username: GitHub 아이디 입력
2. Password: **토큰** 입력 (비밀번호 아님!)

**토큰 만들기:**
1. https://github.com/settings/tokens
2. "Generate new token" → "Generate new token (classic)"
3. Note: "Streamlit Deploy"
4. Expiration: 90 days
5. ✅ **repo** 체크
6. 맨 아래 "Generate token" 클릭
7. 생성된 토큰 복사 (⚠️ 한 번만 보여집니다!)
8. git push 시 Password에 이 토큰 붙여넣기

### 옵션 B: GitHub CLI 사용
```bash
# GitHub CLI 설치 필요 시
brew install gh

# 로그인
gh auth login
```

---

## 🎨 4단계: Streamlit Community Cloud 배포

### 웹 브라우저에서 진행:

1. **Streamlit Cloud 접속**: https://share.streamlit.io

2. **로그인**: 
   - "Sign in" 클릭
   - "Continue with GitHub" 선택

3. **새 앱 배포**:
   - "New app" 버튼 클릭
   
4. **설정 입력**:
   - Repository: 방금 만든 저장소 선택
   - Branch: `main`
   - Main file path: `장사의신-게임.py`
   
5. **"Deploy!" 버튼 클릭**

6. **완료!** 
   - 몇 분 후 앱이 배포됩니다
   - URL은 `https://당신아이디-저장소이름-xxxxx.streamlit.app` 형태

---

## 📱 5단계: 배포된 앱 사용하기

✅ **전세계 어디서나 접속 가능**
✅ **모바일에서도 접속 가능**
✅ **24시간 온라인 유지**
✅ **무료!**

### 앱 관리:
- Streamlit Cloud 대시보드에서 로그, 설정, 재시작 가능
- 코드 수정 후 GitHub에 push하면 자동으로 재배포됨

---

## ❓ 문제 해결

### "Please tell me who you are" 에러
```bash
git config user.name "당신이름"
git config user.email "이메일@example.com"
```

### "remote origin already exists" 에러
```bash
git remote remove origin
git remote add origin https://github.com/아이디/저장소.git
```

### "failed to push" 에러
- GitHub 토큰이 필요합니다 (위 3단계 참고)

### ".venv 폴더가 너무 큼" 경고
- .gitignore 파일이 자동으로 제외시킵니다 (문제 없음)

---

## 🎯 요약

1. ✅ GitHub에서 새 저장소 만들기 (Public으로)
2. ✅ 터미널에서 git 명령어로 업로드
3. ✅ Streamlit Cloud에서 배포
4. ✅ 앱 URL 받고 공유하기!

