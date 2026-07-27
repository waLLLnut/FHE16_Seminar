# FHE 원리 실습 — 서울여대 GSPP Privacy Scholar Camp

동형암호(FHE)의 핵심을 `numpy`/순수 파이썬으로 직접 돌려보는 **실습 코드**입니다.
LWE 암호화·복호화 → 동형 **덧셈** → **곱셈(텐서곱)** → **키스위칭(relin)** → **리스케일**,
그리고 2부에서 **NTT**(스쿨북 = FFT = NTT, 주파수영역 왕복)를 다룹니다.

## 빠른 실행 — 설치 필요 없음

```bash
python3 practice/fhe_practice_pure.py
```
표준 라이브러리(`random`, `cmath`)만 사용 → 아나콘다·numpy·pip 설치 없이 파이썬만 있으면 바로 실행됩니다.

## 파일

| 파일 | 필요 패키지 | 실행 |
|---|---|---|
| `practice/fhe_practice_pure.py` | **없음** (파이썬만) | `python3 fhe_practice_pure.py` |
| `practice/fhe_lwe_ntt_practice_pure.ipynb` | **없음** (numpy 불필요) | Jupyter |
| `practice/fhe_lwe_ntt_practice.ipynb` | `numpy` | Jupyter / Google Colab |
| `practice/fhe_lwe_ntt_practice_solution.ipynb` | `numpy` | **답안지** (★실습 채운 버전) |

- 생성 스크립트: `build_notebook.py`(numpy 노트북), `build_notebook_pure.py`(순수 파이썬 노트북), `build_solution.py`(답안지).
- 노트북에는 `★ 실습 1~4`(값·슬롯을 바꿔 실행) 문제가 포함되어 있습니다.

## 노트북으로 열려면

```bash
pip install jupyter        # numpy 버전을 쓰려면 numpy 도 함께
jupyter notebook practice/fhe_lwe_ntt_practice_pure.ipynb
```
또는 `.ipynb` 파일을 [Google Colab](https://colab.research.google.com) 에 업로드하면 설치 없이 실행됩니다.
