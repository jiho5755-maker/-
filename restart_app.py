#!/usr/bin/env python3
import subprocess
import os

os.chdir("/Users/jangjiho/Desktop/커서AI")

# Git 커밋 먼저
subprocess.run(["git", "add", "."], check=True)
subprocess.run(["git", "commit", "-m", "🛍️ 여러 상품 판매 시스템 완성"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("\n" + "="*60)
print("✅ Git 커밋 완료!")
print("="*60)
print("\n📢 다음 단계:")
print("\n1️⃣ Streamlit Cloud에서 앱 재시작:")
print("   👉 https://share.streamlit.io/")
print("   👉 'Manage app' 클릭")
print("   👉 'Reboot app' 클릭")
print("\n2️⃣ 또는 로컬에서 실행 중이면:")
print("   👉 터미널에서 Ctrl+C로 중지")
print("   👉 streamlit run 장사의신/장사의신-게임.py 다시 실행")
print("\n3️⃣ 브라우저에서 새로고침 (Ctrl+F5 또는 Cmd+Shift+R)")
print("="*60)
print("\n그러면 '📦 여러 상품 판매' 체크박스가 보입니다!")
print("="*60)
