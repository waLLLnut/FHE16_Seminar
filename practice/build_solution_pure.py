#!/usr/bin/env python3
# 순수 파이썬 답안지 생성기 — fhe_lwe_ntt_practice_pure.ipynb 의 ★실습 2(n=3) 슬롯을 채운다.
# 실행:  python3 build_solution_pure.py
import nbformat as nbf
from nbformat.v4 import new_markdown_cell

SRC = 'fhe_lwe_ntt_practice_pure.ipynb'
DST = 'fhe_lwe_ntt_practice_solution.ipynb'

nb = nbf.read(SRC, as_version=4)

# ★ 실습 2 (n=3) 슬롯 채우기 (순수 파이썬 리스트)
for cell in nb.cells:
    if cell.cell_type == 'code' and 'n3   = 3' in cell.source:
        s = cell.source
        s = s.replace('sbar3 = None', 'sbar3 = [1] + s3')
        s = s.replace('t3    = None', 't3    = [sbar3[i]*sbar3[j] for i in range(4) for j in range(4)]')
        s = s.replace('cmul3 = None', 'cmul3 = [(c1_3[i]*c2_3[j]) % q for i in range(4) for j in range(4)]')
        cell.source = s
        cell.outputs = []
        cell.execution_count = None

# 제목 표시
nb.cells[0].source = nb.cells[0].source.replace(
    '# 동형암호(FHE) 원리 실습 — 순수 파이썬(설치 필요 없음)',
    '# 동형암호(FHE) 원리 실습 — 【답안지】 순수 파이썬', 1)

# 부록: 답안 요약
nb.cells.append(new_markdown_cell(r"""## 부록. 답안 (강사용)

**★ 실습 2 — n=3** (채운 슬롯, 순수 파이썬)
```python
sbar3 = [1] + s3
t3    = [sbar3[i]*sbar3[j] for i in range(4) for j in range(4)]
cmul3 = [(c1_3[i]*c2_3[j]) % q for i in range(4) for j in range(4)]
```
출력: 확장키 차원 4, 텐서 차원 16, 덧셈 복호 5, 곱셈 복호 6.

**★ 실습 1** 오류 한계를 키워 $|e_1+e_2|\ge\Delta/2=50$ 이면 덧셈 복호부터 실패.
**★ 실습 3** `TRY_DIGIT_VALUE` 를 무엇으로 두든 분해→재조합이 원래 값과 일치.
**★ 실습 4** `TRY_W=4` 성공(차수 4). `TRY_W=2` 는 차수 8(≠4)이라 원시 4차 근이 아니어서 왕복 실패.
"""))

nbf.write(nb, DST)
print('wrote', DST, '(', len(nb.cells), 'cells )')
