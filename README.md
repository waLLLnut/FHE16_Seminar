# FHE 원리 실습 — 서울여대 GSPP Privacy Scholar Camp

동형암호(FHE)의 핵심을 **설치 없이 순수 파이썬**으로 직접 돌려보는 실습입니다.
LWE 암호화·복호화 → 동형 **덧셈** → **곱셈(텐서곱)** → **키스위칭(relin)** → **리스케일**, 그리고 2부 **NTT**.

---

## ▶ 실행 방법 — 설치 없이 브라우저에서 (권장)

### 1. JupyterLite — 설치·계정 전혀 필요 없음, 클릭만
브라우저 안에서 바로 실행됩니다.

- **실습**: <https://walllnut.github.io/FHE16_Seminar/lab/index.html?path=fhe_practice_v2.ipynb>
- **답지**: <https://walllnut.github.io/FHE16_Seminar/lab/index.html?path=fhe_practice_v2_solution.ipynb>

> 열리면 상단 **≫ (Restart & Run All)** 또는 셀마다 **Shift+Enter**.

### 2. Google Colab — 구글 로그인만
<https://colab.research.google.com/github/waLLLnut/FHE16_Seminar/blob/main/practice/fhe_practice_v2.ipynb>

---

## 파일

| 파일 | 설명 |
|---|---|
| `practice/fhe_practice_v2.ipynb` | **실습** 노트북 (순수 파이썬, 토이 n=1 / ★실습 n=2) |
| `practice/fhe_practice_v2_solution.ipynb` | **답지** (★실습 채운 버전 + 답안 요약) |

- 모두 표준 라이브러리(`random`, `cmath`)만 사용합니다.
- 생성 스크립트: `build_notebook_pure.py`(실습), `build_solution_pure.py`(답지).
