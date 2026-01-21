#!/usr/bin/env python3
import subprocess
import os

os.chdir("/Users/jangjiho/Desktop/커서AI")

print("🔧 KeyError 수정 커밋 중...\n")

commands = [
    (["git", "add", "장사의신/장사의신-게임.py"], "변경사항 추가"),
    (["git", "commit", "-m", "🐛 KeyError 수정: BUSINESS_TYPES 안전한 접근"], "커밋"),
    (["git", "push", "origin", "main"], "GitHub 푸시")
]

for cmd, desc in commands:
    print(f"⚙️  {desc}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"❌ 오류: {result.stderr}")
    else:
        print(f"✅ {desc} 성공!")
    print()

print("🎉 완료! Streamlit Cloud가 1-2분 후 자동 배포됩니다!")
