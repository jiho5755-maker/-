#!/bin/bash
cd "$(dirname "$0")"

echo "========================================="
echo "🚀 로컬 서버를 시작합니다!"
echo "========================================="
echo ""

# 기존 서버 프로세스 종료 (포트 충돌 방지)
lsof -ti:8080 | xargs kill -9 2>/dev/null
sleep 1

# 서버 시작
echo "🌐 서버를 시작합니다..."
python3 -m http.server 8080 &
SERVER_PID=$!

# 서버가 시작될 때까지 대기
sleep 3

# 브라우저 자동 열기 (URL 인코딩 포함)
echo "🌐 브라우저를 자동으로 엽니다..."
open "http://localhost:8080/제휴업체-지도-통합본.html"

echo ""
echo "✅ 서버가 실행 중입니다! (PID: $SERVER_PID)"
echo "✅ 브라우저가 자동으로 열렸습니다!"
echo ""
echo "========================================="
echo "⚠️  중요: 브라우저 주소창을 확인하세요!"
echo "   올바른 URL: http://localhost:8080/제휴업체-지도-통합본.html"
echo "   file:// 로 시작하면 안 됩니다!"
echo "========================================="
echo ""
echo "서버를 종료하려면:"
echo "  1. 이 창을 닫거나"
echo "  2. Ctrl+C를 누르세요"
echo ""
echo "현재 실행 중인 서버 PID: $SERVER_PID"
echo ""

# 서버가 종료될 때까지 대기
wait $SERVER_PID

