#!/usr/bin/env python3
import subprocess
import os

os.chdir("/Users/jangjiho/Desktop/커서AI")

print("🔄 안정 버전으로 롤백 중...")
print()

commands = [
    (["git", "reset", "--hard", "150563e"], "Git 리셋"),
    (["git", "push", "origin", "main", "--force"], "GitHub 강제 푸시")
]

for cmd, desc in commands:
    print(f"⚙️  {desc}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"❌ 오류: {result.stderr}")
        break
    else:
        print(f"✅ {desc} 성공!")
    print()

print("🎉 완료! Streamlit Cloud가 1-2분 후 자동 배포됩니다!")
print("📌 버전: 150563e (전략/간단 모드 분리 - 안정 버전)")
