#!/usr/bin/env python3
import subprocess
import os

os.chdir("/Users/jangjiho/Desktop/커서AI")

# Git add
subprocess.run(["git", "add", "."], check=True)

# Git commit
commit_message = """🐛 중복 키 오류 수정

- delete_{name} → delete_v2_{name}
- edit_cost_{name} → edit_cost_form_{name}
- edit_capital_{name} → edit_capital_form_{name}
- save_edit_{name} → save_edit_form_{name}

StreamlitDuplicateElementKey 오류 해결"""

subprocess.run(["git", "commit", "-m", commit_message], check=True)

# Git push
subprocess.run(["git", "push", "origin", "main"], check=True)

print("\n✅ 중복 키 수정 완료!")
