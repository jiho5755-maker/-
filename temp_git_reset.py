#!/usr/bin/env python3
import subprocess
import os

os.chdir("/Users/jangjiho/Desktop/커서AI")

commands = [
    ["git", "fetch", "origin"],
    ["git", "reset", "--hard", "origin/main"],
    ["git", "clean", "-fd"]
]

for cmd in commands:
    print(f"실행 중: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"오류: {result.stderr}")
    else:
        print("✅ 성공!")
    print()

print("🎉 완료! Streamlit Cloud가 자동으로 재배포됩니다!")
