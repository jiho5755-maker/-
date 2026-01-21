#!/usr/bin/env python3
import subprocess
import os

os.chdir("/Users/jangjiho/Desktop/커서AI")

# Git add
subprocess.run(["git", "add", "."], check=True)

# Git commit
commit_message = """🛍️ Phase 3-1: 여러 상품 판매 시스템 완성

✨ 새로운 기능:
- 학생 등록 시 메인 상품 외 추가 상품(최대 5개) 등록 가능
- 각 상품별 원가, 판매가, 재고 개별 관리
- 판매 시 상품 선택 기능 (드롭다운)
- 상품별 판매 기록 추적

🔧 구현 내용:
- enable_multi_products 플래그 추가
- products 배열: {name, cost, price, inventory, sales}
- 상품별 재고 구매 UI
- 상품별 판매 기록 자동 저장
- 기존 단일 상품 모드와 완벽 호환

📊 데이터 구조:
products: [
  {name, cost, price, inventory, sales: {round_1, round_2}}
]

이제 학생들이 다양한 상품을 판매할 수 있습니다! 🎊"""

subprocess.run(["git", "commit", "-m", commit_message], check=True)

# Git push
subprocess.run(["git", "push", "origin", "main"], check=True)

print("\n✅ 여러 상품 판매 시스템 커밋 완료!")
