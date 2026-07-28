#!/usr/bin/env python3
# 순수 파이썬 답안지 생성기 — ★실습 2(n=3) 슬롯을 명시적 for-루프로 채운다.
# 실행:  python3 build_solution_pure.py
import nbformat as nbf
from nbformat.v4 import new_markdown_cell

SRC = 'fhe_lwe_ntt_practice_pure.ipynb'
DST = 'fhe_lwe_ntt_practice_solution.ipynb'

SLOTS = (
    "sbar3 = None   # 확장키 [1, s1, s2, s3]  힌트: r=[1]; for i in range(len(s3)): r.append(s3[i])\n"
    "t3    = None   # 텐서곱 키 sbar3 ⊗ sbar3  힌트: 이중 for 로 sbar3[i]*sbar3[j] append\n"
    "cmul3 = None   # 암호문 텐서곱 c1_3 ⊗ c2_3 (mod q)  힌트: 이중 for 로 (c1_3[i]*c2_3[j])%q append"
)

FILLED = (
    "sbar3 = [1]\n"
    "for i in range(len(s3)):\n"
    "    sbar3.append(s3[i])\n"
    "\n"
    "t3 = []\n"
    "for i in range(len(sbar3)):\n"
    "    for j in range(len(sbar3)):\n"
    "        t3.append(sbar3[i] * sbar3[j])\n"
    "\n"
    "cmul3 = []\n"
    "for i in range(len(c1_3)):\n"
    "    for j in range(len(c2_3)):\n"
    "        cmul3.append((c1_3[i] * c2_3[j]) % q)"
)

nb = nbf.read(SRC, as_version=4)

for cell in nb.cells:
    if cell.cell_type == 'code' and 'n3 = 3' in cell.source and 'sbar3 = None' in cell.source:
        cell.source = cell.source.replace(SLOTS, FILLED)
        cell.outputs = []
        cell.execution_count = None

nb.cells[0].source = nb.cells[0].source.replace(
    '# 동형암호(FHE) 원리 실습 — 순수 파이썬(설치 필요 없음)',
    '# 동형암호(FHE) 원리 실습 — 【답안지】 순수 파이썬', 1)

nb.cells.append(new_markdown_cell(r"""## 부록. 답안 (강사용)

**★ 실습 2 — n=3** (채운 슬롯, 명시적 for-루프)
```python
sbar3 = [1]
for i in range(len(s3)):
    sbar3.append(s3[i])

t3 = []
for i in range(len(sbar3)):
    for j in range(len(sbar3)):
        t3.append(sbar3[i] * sbar3[j])

cmul3 = []
for i in range(len(c1_3)):
    for j in range(len(c2_3)):
        cmul3.append((c1_3[i] * c2_3[j]) % q)
```
출력: 확장키 차원 4, 텐서 차원 16, 덧셈 복호 5, 곱셈 복호 6.

**★ 실습 1** 오류 한계를 키워 $|e_1+e_2|\ge\Delta/2=50$ 이면 덧셈 복호부터 실패.
**★ 실습 3** `TRY_DIGIT_VALUE` 를 무엇으로 두든 분해→재조합이 원래 값과 일치.
**★ 실습 4** `TRY_W=4` 성공(차수 4). `TRY_W=2` 는 차수 8(≠4)이라 원시 4차 근이 아니어서 왕복 실패.
"""))

nbf.write(nb, DST)
print('wrote', DST, '(', len(nb.cells), 'cells )')
