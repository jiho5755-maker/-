#!/bin/bash

# 장사의 신 게임 - GitHub 배포 자동화 스크립트

echo "🚀 GitHub에 업로드를 시작합니다..."

cd "/Users/jangjiho/Desktop/커서AI"

# 변경사항 확인
git status

echo ""
echo "📦 변경된 파일들을 추가합니다..."
git add .

echo ""
echo "💾 변경사항을 커밋합니다..."
read -p "📝 커밋 메시지를 입력하세요 (Enter = 기본 메시지): " commit_msg

if [ -z "$commit_msg" ]; then
    commit_msg="게임 업데이트"
fi

git commit -m "$commit_msg"

echo ""
echo "🌐 GitHub에 업로드합니다..."
git push origin main

echo ""
echo "✅ 업로드 완료!"
echo "🎉 Streamlit Cloud에서 자동으로 재배포됩니다 (1-2분 소요)"
echo ""
echo "배포 상태 확인: https://share.streamlit.io"

