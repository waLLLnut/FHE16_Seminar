# FHE 원리 실습 — 서울여대 GSPP Privacy Scholar Camp

동형암호(FHE)의 핵심을 직접 돌려보는 **실습 코드**입니다.
LWE 암호화·복호화 → 동형 **덧셈** → **곱셈(텐서곱)** → **키스위칭(relin)** → **리스케일**, 그리고 2부 **NTT**.

---

## ▶ 실행 방법 — 설치 없이 브라우저에서 (권장)

### 1. JupyterLite — 설치·계정 전혀 필요 없음, 클릭만
브라우저 안에서 바로 실행됩니다 (Pyodide로 numpy까지 자동).

- **실습**: <https://walllnut.github.io/FHE16_Seminar/lab/index.html?path=fhe_lwe_ntt_practice.ipynb>
- **순수 파이썬 버전**: <https://walllnut.github.io/FHE16_Seminar/lab/index.html?path=fhe_lwe_ntt_practice_pure.ipynb>
- **답안지**: <https://walllnut.github.io/FHE16_Seminar/lab/index.html?path=fhe_lwe_ntt_practice_solution.ipynb>

> 열리면 상단 **≫ (Restart & Run All)** 또는 셀마다 **Shift+Enter**. 첫 실행 시 numpy 로딩에 몇 초 걸립니다.

### 2. Google Colab — 구글 로그인만 (numpy 기본 포함)
<https://colab.research.google.com/github/waLLLnut/FHE16_Seminar/blob/main/practice/fhe_lwe_ntt_practice.ipynb>

### 3. 로컬 — 파이썬만 있으면 (설치 0)
```bash
python3 practice/fhe_practice_pure.py
```
표준 라이브러리(`random`, `cmath`)만 사용 → 아나콘다·numpy·pip 없이 실행됩니다.

---

## 파일

| 파일 | 필요 패키지 | 실행 |
|---|---|---|
| `practice/fhe_practice_pure.py` | **없음** (파이썬만) | `python3 fhe_practice_pure.py` |
| `practice/fhe_lwe_ntt_practice_pure.ipynb` | **없음** (numpy 불필요) | JupyterLite / Jupyter |
| `practice/fhe_lwe_ntt_practice.ipynb` | `numpy` | JupyterLite / Colab / Jupyter |
| `practice/fhe_lwe_ntt_practice_solution.ipynb` | `numpy` | **답안지** (★실습 채운 버전) |

- 노트북에는 `★ 실습 1~4`(값·슬롯을 바꿔 실행) 문제가 포함되어 있습니다.
- 생성 스크립트: `build_notebook.py`(numpy), `build_notebook_pure.py`(순수 파이썬), `build_solution.py`(답안지).

## 로컬에서 Jupyter로 열려면
```bash
pip install jupyter numpy      # 순수 버전은 numpy 없이도 됨
jupyter notebook practice/fhe_lwe_ntt_practice.ipynb
```
