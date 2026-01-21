#!/usr/bin/env python3
import subprocess
import os

os.chdir("/Users/jangjiho/Desktop/커서AI")

print("📜 Git 커밋 히스토리 (최근 20개)\n")
print("=" * 80)

result = subprocess.run(
    ["git", "log", "--oneline", "--graph", "--decorate", "-20"],
    capture_output=True,
    text=True
)

print(result.stdout)

print("\n" + "=" * 80)
print("\n📌 현재 버전:")
current = subprocess.run(
    ["git", "log", "-1", "--format=%h - %s (%ar)"],
    capture_output=True,
    text=True
)
print(f"   {current.stdout.strip()}")

print("\n🌟 주요 버전:")
print("   • 150563e - 전략/간단 모드 분리 (현재)")
print("   • 940505a - 시스템 안정성 개선")
print("   • 36f3558 - V3 완성")
print("   • 0966f5d - V2 새로 설계")
