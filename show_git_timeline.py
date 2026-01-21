#!/usr/bin/env python3
import subprocess
import os

os.chdir("/Users/jangjiho/Desktop/커서AI")

print("📅 Git 커밋 타임라인 (날짜별)\n")
print("=" * 100)

result = subprocess.run(
    ["git", "log", "--oneline", "--date=format:%Y-%m-%d %H:%M", "--format=%C(yellow)%h%C(reset) - %C(green)%ad%C(reset) - %s", "-30"],
    capture_output=True,
    text=True
)

lines = result.stdout.strip().split('\n')

print("\n🔍 IndentationError 문제 추적:\n")

# 문제가 있을 것으로 예상되는 커밋들
problem_commits = ['a6aa649', '2709f4f', '000d0a1', '7ef839c', 'c3957d2', '3b19547', '9631db8']

for line in lines:
    commit_hash = line.split(' - ')[0].strip() if ' - ' in line else ''
    
    if any(prob in line for prob in problem_commits):
        print(f"⚠️  {line}")
    elif '150563e' in line:
        print(f"✅  {line}  ← 현재 위치 (안정)")
    elif '940505a' in line or '36f3558' in line or '0966f5d' in line:
        print(f"⭐  {line}  ← 추천 안정 버전")
    else:
        print(f"    {line}")

print("\n" + "=" * 100)
print("\n📌 추천 안정 버전:")
print("   1. 150563e - 전략/간단 모드 분리 (현재 위치) ✅")
print("   2. 940505a - 시스템 안정성 개선")
print("   3. 36f3558 - V3 완성 (7가지 기능)")
print("   4. 0966f5d - V2 새로 설계 (초기 안정)")
