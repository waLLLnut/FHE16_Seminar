#!/usr/bin/env python3
# 답안지(solution) 생성기.  실행:  python3 build_solution.py
# 연습 노트북(fhe_lwe_ntt_practice.ipynb)에서
#   (1) ★ 실습 2(n=3)의 None 슬롯 3곳을 정답으로 채우고
#   (2) 제목을 【답안지】로 표시하고
#   (3) 맨 뒤에 4개 실습의 답안·예상 관찰 요약을 붙인다.
import nbformat as nbf
from nbformat.v4 import new_markdown_cell

SRC = 'fhe_lwe_ntt_practice.ipynb'
DST = 'fhe_lwe_ntt_practice_solution.ipynb'

nb = nbf.read(SRC, as_version=4)

# (1) ★ 실습 2 (n=3) 슬롯 채우기
for cell in nb.cells:
    if cell.cell_type == 'code' and 'n3   = 3' in cell.source:
        s = cell.source
        s = s.replace('sbar3 = None', 'sbar3 = np.concatenate([[1], s3])')
        s = s.replace('t3    = None', 't3    = np.outer(sbar3, sbar3).flatten()')
        s = s.replace('cmul3 = None', 'cmul3 = np.outer(c1_3, c2_3).flatten() % q')
        cell.source = s
        cell.outputs = []
        cell.execution_count = None

# (2) 제목 표시
nb.cells[0].source = nb.cells[0].source.replace(
    '# 동형암호(FHE) 원리 실습 — `numpy` 만으로',
    '# 동형암호(FHE) 원리 실습 — 【답안지】 `numpy` 만으로', 1)

# (3) 부록: 답안 및 예상 관찰
nb.cells.append(new_markdown_cell(r"""## 부록. 답안 및 예상 관찰 (강사용)

**★ 실습 1 — 메시지와 오류를 바꾸면?**
기본값 `TRY_M1, TRY_M2 = 4, -1`, `TRY_ERROR_BOUND = 10` → 개별 복호 $(4, -1)$, 덧셈 복호 $3$.
`TRY_ERROR_BOUND` 를 키워 합산 오류 $|e_1+e_2|$ 가 $\Delta/2 = 50$ 에 근접·초과하면 **덧셈 복호부터** 흔들립니다.

**★ 실습 2 — 3개짜리(n=3)로 직접 해보기** (채운 슬롯)
```python
sbar3 = np.concatenate([[1], s3])          # 확장키 (1, s1, s2, s3)  → 차원 4
t3    = np.outer(sbar3, sbar3).flatten()   # 키 텐서곱               → 차원 16
cmul3 = np.outer(c1_3, c2_3).flatten() % q # 암호문 텐서곱 (mod q)   → 차원 16
```
출력: 확장키 차원 $4$, 텐서 차원 $16$, 덧셈 복호 $5$, 곱셈 복호 $6$.

**★ 실습 3 — 가젯 분해를 직접 확인하기**
`TRY_DIGIT_VALUE = 314159` → 부호 있는 10진 자릿수로 분해한 뒤 $\sum_\ell d_\ell B^\ell$ 로 재조합하면
원래 값(mod $q$)과 정확히 일치합니다. 다른 값을 넣어도 항상 재조합 = 원래 값.

**★ 실습 4 — 단위근을 바꾸면?**
`TRY_W = 4` → 4의 차수 $=4$ (원시 4차 단위근), 왕복 변환 성공.
`TRY_W = 2` 로 바꾸면 2의 차수 $=8\ (\neq 4)$ 이라 **원시 4차 단위근이 아니며**,
NTT 행렬이 이 링에 맞지 않아 왕복 변환이 원래 계수를 복원하지 못합니다.
"""))

nbf.write(nb, DST)
print('wrote', DST, '(', len(nb.cells), 'cells )')
