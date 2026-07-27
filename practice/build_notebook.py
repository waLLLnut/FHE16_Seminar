#!/usr/bin/env python3
# fhe_lwe_ntt_practice.ipynb 생성기 (nbformat).  실행:  python3 build_notebook.py
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

nb = new_notebook()
c = []
def md(t): c.append(new_markdown_cell(t))
def code(t): c.append(new_code_cell(t))

md(r"""# 동형암호(FHE) 원리 실습 — `numpy` 만으로

**서울여대 GSPP Privacy Scholar Camp · 이승환 (waLLLnut / LatticA)**

이 노트북은 무거운 FHE 라이브러리 없이 `numpy` 만으로 동형암호의 핵심을 직접 돌려봅니다.

> **두 가지 사용법**
> 1. 설명을 들으며 **Run All** — 기본값에서는 모든 셀이 처음부터 끝까지 실행됩니다.
> 2. `★ 실습` 셀의 `TRY_...` 값만 바꿔 다시 실행 — 완성 코드를 실험하며 결과를 예측합니다.
>
> **주의:** 차원 $n=2$와 아래의 균등분포는 원리를 보기 위한 장난감 설정입니다.
> 실제 보안 파라미터나 안전한 LWE 구현으로 사용하면 안 됩니다.
> (곱셈 절 뒤 **★ 실습 2** 에서 같은 파이프라인을 $n=3$ 으로 직접 채워 봅니다.)

**1부 — LWE 암호와 동형연산**
1. LWE 암호화 / phase / 복호화
2. 덧셈 (그대로 더하기)
3. 곱셈 (비밀키·암호문의 **텐서곱**) — phase가 $\Delta{=}10^2$ 에서 $\Delta^2{=}10^4$ 로 커짐
4. **키스위칭**: 텐서곱으로 커진 2차 키를 다시 원래 키로
5. **리스케일**: $1/\Delta$ 로 나눠 원래 스케일로 복귀

**2부 — NTT (다항식 곱셈 가속)**
6. 스쿨북 순환 합성곱 (mod 17, $N{=}4$, $X^4-1$)
7. FFT 로 같은 결과
8. 원시근 4로 만든 **NTT 행렬**로 같은 곱셈
9. 주파수 영역에서 mod 17 왕복
""")

md(r"""## 0. 파라미터 설정

- 차원 $n=2$, 모듈러스 $q=10^6$, 스케일 인자 $\Delta=10^2$
- 비밀키·오류는 설명을 단순화하기 위해 $[-10,10]$ 균등 샘플
- 재현성을 위해 시드 고정 (`seed=42`)

실제 LWE 계열 구현은 스킴과 보안 수준에 맞는 차원·모듈러스·분포를 별도로 선택합니다.
""")
code(r"""import numpy as np

q     = 10**6      # 모듈러스 (~10^6)
n     = 2          # LWE 차원
Delta = 100        # 스케일 인자 10^2
rng   = np.random.default_rng(42)

def center(x, mod=q):
    "값을 (-mod/2, mod/2] 범위로 옮김 (부호 있는 대표원)"
    return ((np.asarray(x, dtype=np.int64) + mod//2) % mod) - mod//2

print("q =", q, ", n =", n, ", Delta =", Delta)""")

md(r"""## 1. LWE 암호화 / phase / 복호화

비밀키 $\mathbf{s}\in\mathbb{Z}^n$, 확장키 $\bar{\mathbf{s}}=(1,s_1,s_2)$.

메시지 $m$ 암호화: 임의 $\mathbf a$, 작은 오류 $e$ 로
$$ b = \langle \mathbf a,\mathbf s\rangle + e + \Delta\, m \pmod q,\qquad
   \bar{\mathbf c}=(b,\,-a_1,\,-a_2). $$

그러면 **phase** 는 $\;\langle \bar{\mathbf c},\bar{\mathbf s}\rangle = b-\langle\mathbf a,\mathbf s\rangle = \Delta m + e$.
오류 $e$ 를 반올림으로 지우면 $m$ 이 복원됩니다.
""")
code(r"""def keygen():
    return rng.integers(-10, 11, size=n)          # sk ∈ [-10,10]

def sbar(s):
    return np.concatenate([[1], s]).astype(np.int64)   # (1, s1, s2)

def encrypt(m, s, delta=Delta):
    a = rng.integers(0, q, size=n).astype(np.int64)
    e = int(rng.integers(-10, 11))                # 오류 ∈ [-10,10]
    b = (int(a @ s) + e + delta*m) % q
    return np.concatenate([[b], (-a) % q]).astype(np.int64)   # (b, -a1, -a2)

def phase(c, s):
    return int(center(int(c @ sbar(s))))          # <c, sbar> 를 중심화

def decrypt(c, s, delta=Delta):
    return int(round(phase(c, s) / delta))

s = keygen()
print("비밀키 sk =", s, ", 확장키 sbar =", sbar(s))""")

code(r"""m1, m2 = 2, 3
c1 = encrypt(m1, s)
c2 = encrypt(m2, s)
print("암호문 c1 =", c1)
print("phase(c1) =", phase(c1, s), " (≈ Delta*m1 =", Delta*m1, ")  ->  복호:", decrypt(c1, s))
print("phase(c2) =", phase(c2, s), " (≈ Delta*m2 =", Delta*m2, ")  ->  복호:", decrypt(c2, s))
assert decrypt(c1, s) == m1 and decrypt(c2, s) == m2
print("OK: 암호화/복호화 동작")""")

md(r"""## 2. 덧셈 — 암호문을 그대로 더한다

$\bar{\mathbf c}_1+\bar{\mathbf c}_2$ 를 계산하면 phase 도 그대로 더해져
$\Delta(m_1+m_2)+(e_1+e_2)$. 복호하면 $m_1+m_2$.
""")
code(r"""c_add = (c1 + c2) % q
print("phase(c1+c2) =", phase(c_add, s), " (= phase(c1)+phase(c2))")
print("복호:", decrypt(c_add, s), " (기대값 m1+m2 =", m1+m2, ")")
assert decrypt(c_add, s) == m1 + m2
print("OK: 동형 덧셈")""")

md(r"""### ★ 실습 1. 메시지와 오류를 바꾸면?

아래 세 값만 바꿔 실행해 보세요. 실행 전에는 다음을 먼저 예상합니다.

- 두 암호문의 복호 결과와 덧셈 결과는 무엇일까?
- 오류 한계가 $\Delta/2$에 가까워지거나 넘어가면 언제 복호가 흔들릴까?

이 셀은 별도 난수 생성기를 사용하므로 값을 바꿔도 뒤의 예제에는 영향을 주지 않습니다.
기본값은 `Run All`에서 정상 동작하며, 실패 실험도 예외 대신 결과로 표시합니다.
""")
code(r"""# 바꿔 볼 값: 메시지 두 개와 오류 절댓값의 최대치
TRY_M1, TRY_M2 = 4, -1
TRY_ERROR_BOUND = 10

trial_rng = np.random.default_rng(2026)

def encrypt_trial(m, s, error_bound):
    a = trial_rng.integers(0, q, size=n).astype(np.int64)
    e = int(trial_rng.integers(-error_bound, error_bound + 1))
    b = (int(a @ s) + e + Delta*m) % q
    c = np.concatenate([[b], (-a) % q]).astype(np.int64)
    return c, e

tc1, te1 = encrypt_trial(TRY_M1, s, TRY_ERROR_BOUND)
tc2, te2 = encrypt_trial(TRY_M2, s, TRY_ERROR_BOUND)
tadd = (tc1 + tc2) % q

got1, got2, got_add = decrypt(tc1, s), decrypt(tc2, s), decrypt(tadd, s)
print("개별 오류 (e1, e2):", (te1, te2), " / 합산 오류 e1+e2:", te1 + te2)
print("반올림 기준: 개별은 |ei| <", Delta/2, ", 덧셈은 |e1+e2| <", Delta/2)
print("개별 복호:", (got1, got2), " / 예상:", (TRY_M1, TRY_M2))
print("덧셈 복호:", got_add, " / 예상:", TRY_M1 + TRY_M2)
print("결과:", "성공" if (got1, got2, got_add) == (TRY_M1, TRY_M2, TRY_M1 + TRY_M2)
      else "복호 실패 — 오류와 Delta의 상대적 크기를 확인하세요")""")

md(r"""## 3. 곱셈 — 비밀키와 암호문의 **텐서곱**

phase 는 $\bar{\mathbf s}$ 가 작용하는 **선형식** 이므로, 두 phase 의 곱은 자연스럽게 텐서곱이 됩니다:
$$ \langle\bar{\mathbf c}_1,\bar{\mathbf s}\rangle\cdot\langle\bar{\mathbf c}_2,\bar{\mathbf s}\rangle
 = \langle\, \bar{\mathbf c}_1\otimes\bar{\mathbf c}_2,\ \bar{\mathbf s}\otimes\bar{\mathbf s}\,\rangle. $$

- 새 암호문 = $\bar{\mathbf c}_1\otimes\bar{\mathbf c}_2$ (차원 $9$), 새 키 = $\bar{\mathbf s}\otimes\bar{\mathbf s}$ (차원 $9$).
- phase 는 $\approx \Delta^2 m_1 m_2$ 로 **스케일이 $10^2 \to 10^4$ 로 커집니다.**
""")
code(r"""sb    = sbar(s)
t     = np.outer(sb, sb).flatten().astype(np.int64)          # sbar ⊗ sbar (차원 9)
c_mul = np.outer(c1, c2).flatten().astype(np.int64) % q      # c1 ⊗ c2   (차원 9)

ph_mul = int(center(int(c_mul @ t)))
print("텐서곱 암호문 차원:", c_mul.shape[0], ", 텐서곱 키 차원:", t.shape[0])
print("phase(곱) =", ph_mul)
print("  ≈ Delta^2 * m1*m2 =", Delta**2 * m1*m2, "  <-- 스케일이 10^2에서 10^4로!")
print("  Delta^2 로 나눠 복호:", round(ph_mul / Delta**2), " (기대값", m1*m2, ")")
assert round(ph_mul / Delta**2) == m1*m2
print("OK: 동형 곱셈 (2차 암호문)")""")

md(r"""### 선택 심화 3-1. 왜 하필 '텐서'인가 — 곱셈의 선형대수

phase 는 **듀얼벡터 $\bar{\mathbf s}$ 가 암호문에 작용하는 1차식** $\mu=\bar{\mathbf c}^\top\bar{\mathbf s}$.
값을 곱하면 $\bar{\mathbf s}$ 가 **두 번** 들어가 **이차형식(quadratic form)** 이 됩니다:
$$ \mu_1\mu_2=(\bar{\mathbf c}_1^\top\bar{\mathbf s})(\bar{\mathbf s}^\top\bar{\mathbf c}_2)
   =\bar{\mathbf s}^\top\underbrace{(\bar{\mathbf c}_1\bar{\mathbf c}_2^\top)}_{C:\ \text{외적, rank }1}\bar{\mathbf s}
   =\langle \bar{\mathbf c}_1\otimes\bar{\mathbf c}_2,\ \bar{\mathbf s}\otimes\bar{\mathbf s}\rangle $$
즉 **텐서곱 = 이 이차형식(외적 행렬 $C$)을 1차 내적 꼴로 '펼친' 좌표표현**. 아래에서 셋이 같음을 확인합니다.
""")
code(r"""mu1, mu2 = phase(c1, s), phase(c2, s)
C = np.outer(c1, c2).astype(np.int64)                     # 두 암호문의 외적 -> d×d 행렬 (랭크 1)
print("외적 행렬 C = c1·c2^T  (3×3, 랭크 1):")
print(C)

qf   = int(center(int(sb @ C @ sb)))                      # (2) s^T C s   이차형식
tens = int(center(int(np.outer(c1, c2).flatten() @ t)))   # (3) <c1⊗c2, s⊗s>
print()
print("(1) mu1 * mu2          =", mu1*mu2)
print("(2) sbar^T C sbar      =", qf,   "  <- 키에 대한 이차형식")
print("(3) <c1⊗c2, sbar⊗sbar> =", tens, "  <- 텐서 내적 (vec(C)와 s⊗s)")
assert mu1*mu2 == qf == tens
print("=> 셋 다 동일! 텐서곱은 '키에 대한 이차형식'을 편 것.")
print("   외적 행렬을 벡터화하면 같은 이차식을 d^2차원 텐서 내적으로 표현할 수 있습니다.")""")

md(r"""### ★ 실습 2. 3개짜리(n=3)로 직접 해보기

지금까지는 **비밀키 2개(n=2)** 로 암호화·덧셈·곱셈(텐서곱)이 도는 것을 확인했습니다.
이제 **비밀키 3개(n=3)** 로 같은 파이프라인을 **직접 완성**해 보세요.

- 확장키는 $\bar{\mathbf s}=(1,s_1,s_2,s_3)$ 로 차원이 **4**, 텐서곱 키·암호문은 차원이 **16**이 됩니다.
- 아래 코드의 `None` 슬롯 세 곳(`sbar3`, `t3`, `cmul3`)을 채우면 자동 검증이 돌아갑니다.
- 나머지(암호화·중심화·복호)는 이미 임의의 $n$ 에서 동작합니다 — **차원만 늘렸을 뿐 원리는 그대로**임을 확인하세요.
""")
code(r"""# n=2 는 위에서 확인했습니다. 이제 n=3 (비밀키 3개)로 직접 완성해 보세요.
# 아래 None 슬롯 3개를 채우면 자동 검증이 실행됩니다. (채우기 전에는 안내만 출력)
n3   = 3
rng3 = np.random.default_rng(7)

def keygen3():
    return rng3.integers(-10, 11, size=n3)                 # sk ∈ [-10,10]^3

def encrypt3(m, sk, delta=Delta):
    a = rng3.integers(0, q, size=n3).astype(np.int64)
    e = int(rng3.integers(-10, 11))
    b = (int(a @ sk) + e + delta*m) % q
    return np.concatenate([[b], (-a) % q]).astype(np.int64) # (b, -a1, -a2, -a3)

s3   = keygen3()
c1_3 = encrypt3(2, s3)        # 메시지 2
c2_3 = encrypt3(3, s3)        # 메시지 3

# ---- 채워야 할 슬롯 3개 (None 을 지우고 채우기) --------------------------
sbar3 = None   # 확장키 (1, s1, s2, s3)            힌트: np.concatenate([[1], s3])
t3    = None   # 텐서곱 키 sbar3 ⊗ sbar3            힌트: np.outer(sbar3, sbar3).flatten()
cmul3 = None   # 암호문 텐서곱 c1_3 ⊗ c2_3 (mod q)  힌트: np.outer(c1_3, c2_3).flatten() % q
# ------------------------------------------------------------------------

if sbar3 is None or t3 is None or cmul3 is None:
    print("슬롯(None)을 채운 뒤 다시 실행하세요.  힌트는 각 줄 주석 참고.")
    print("기대값 -> 확장키 차원 4, 텐서 차원 16, phase(곱) ≈ Delta^2*2*3 =", Delta**2*6)
else:
    sbar3 = np.asarray(sbar3).astype(np.int64)
    t3    = np.asarray(t3).astype(np.int64)
    cmul3 = np.asarray(cmul3).astype(np.int64) % q
    ph_add = int(center(int(((c1_3 + c2_3) % q) @ sbar3)))
    ph_mul = int(center(int(cmul3 @ t3)))
    print("확장키 차원:", sbar3.shape[0], "(기대 4) / 텐서 차원:", t3.shape[0], "(기대 16)")
    print("덧셈 복호 :", round(ph_add / Delta),     "(기대 5)")
    print("곱셈 phase:", ph_mul, "≈ Delta^2*6 =", Delta**2*6, "-> 복호:", round(ph_mul / Delta**2), "(기대 6)")
    assert sbar3.shape[0] == n3 + 1 and t3.shape[0] == (n3 + 1)**2
    assert round(ph_add / Delta) == 5 and round(ph_mul / Delta**2) == 6
    print("OK: n=3 에서도 암호화·덧셈·텐서곱 동작 🎉")""")

md(r"""## 4. 키스위칭의 특수한 경우: 리니어라이제이션

곱셈 결과는 차원 9의 **2차 키** 아래 있습니다. 계속 연산(예: 덧셈)하려면 원래 키로 되돌려야 합니다.

지금처럼 $\bar{\mathbf s}\otimes\bar{\mathbf s}$ 아래의 곱셈 결과를 다시 같은
$\bar{\mathbf s}$ 아래로 줄이는 연산을 **리니어라이제이션(relinearization)** 이라고 합니다.
이는 키스위칭의 특수한 경우입니다.

**아이디어(가젯 분해)**: 큰 키의 각 성분 $t_j$ 를 미리 원래 키로 암호화해 둔
**키스위칭 키(KSK)** 를 준비하고, 암호문 성분 $c_j$ 를 **10진 자릿수**로 분해해 조합합니다.
phase 는 (작은 오류를 더한 채) **그대로 보존**됩니다.
""")
md(r"""### ★ 실습 3. 가젯 분해를 직접 확인하기

`TRY_DIGIT_VALUE`만 바꾸고 부호 있는 10진 자릿수를 먼저 예상해 보세요.
완성된 분해 함수가 자릿수를 다시 조합해 원래 값과 같은지도 자동으로 확인합니다.
""")
code(r"""B, L = 10, 6   # 10진 분해, 자릿수 6개 (10^6 = q)

def signed_digits(x):
    "x 를 부호 있는 10진 자릿수 L개로 분해"
    x = int(x) % q
    ds = []
    for _ in range(L):
        d = x % B
        if d > B//2:
            d -= B
        ds.append(d)
        x = (x - d) // B
    return ds

# ★ 실습 3: 이 값만 바꾸고, 출력될 부호 있는 10진 자릿수를 먼저 예상해 보세요.
TRY_DIGIT_VALUE = 314159
try_digits = signed_digits(TRY_DIGIT_VALUE)
try_reconstructed = sum(d * (B**l) for l, d in enumerate(try_digits))
print("원래 값 (mod q):", TRY_DIGIT_VALUE % q)
print("부호 있는 자릿수:", try_digits)
print("자릿수 재조합 (mod q):", try_reconstructed % q)
assert try_reconstructed % q == TRY_DIGIT_VALUE % q
print("OK: 가젯 분해 후 다시 같은 값")""")

md(r"""#### KSK를 만들고 리니어라이제이션 실행

아래 셀은 코드가 조금 길지만 하는 일은 두 단계뿐입니다.

1. 텐서 키의 각 성분과 각 자릿수 가중치 $B^\ell$을 원래 키 아래 암호화해 KSK를 만듭니다.
2. 큰 암호문의 각 성분을 위의 부호 있는 자릿수로 분해하고 KSK를 선형 결합합니다.
""")
code(r"""def encrypt_raw(value, s):
    "스케일 없이 값 자체를 암호화: phase ≈ value + e (키스위칭 키용)"
    a = rng.integers(0, q, size=n).astype(np.int64)
    e = int(rng.integers(-10, 11))
    b = (int(a @ s) + e + int(value)) % q
    return np.concatenate([[b], (-a) % q]).astype(np.int64)

# KSK: 큰 키 성분 t_j (j>=1) 를 각 자리 B^l 배로 암호화
d_big = t.shape[0]
KSK = {j: [encrypt_raw(int(t[j]) * (B**l), s) for l in range(L)] for j in range(1, d_big)}

def keyswitch(c_big):
    cprime = np.zeros(n+1, dtype=np.int64)
    cprime[0] = int(c_big[0]) % q          # t_0 = 1 (상수항)은 b-슬롯으로
    for j in range(1, d_big):
        ds = signed_digits(c_big[j])
        for l in range(L):
            cprime = (cprime + ds[l] * KSK[j][l]) % q
    return cprime % q

c_ks   = keyswitch(c_mul)
ph_ks  = int(center(int(c_ks @ sb)))
print("리니어라이제이션 후 차원:", c_ks.shape[0], " (다시 원래 키", sb.shape[0], "차원)")
print("phase(리니어라이제이션) =", ph_ks, " (곱 phase", ph_mul, "와 거의 같음, 오류만 약간 증가)")
assert round(ph_ks / Delta**2) == m1*m2
print("OK: 리니어라이제이션 (phase·메시지 보존)")""")

md(r"""## 5. 장난감 리스케일 — $1/\Delta$ 로 나눠 원래 스케일로

phase 스케일이 $\Delta^2(=10^4)$ 로 커져 있으니, $\Delta(=100)$ 로 나눠 원래 $\Delta(=10^2)$ 스케일로 되돌립니다.

**핵심**: 암호문을 $\Delta$ 로 나눌 때 **모듈러스도 $q\to q/\Delta$ 로 함께 줄입니다.**
(성분별 반올림이 phase 에 $q$ 의 배수 오프셋을 넣는데, 새 모듈러스 $q/\Delta$ 로 줄이면 그 오프셋이 사라집니다.)

이 단계는 CKKS의 리스케일 직관을 보여 주는 교육용 모형입니다.
BFV·BGV·CKKS의 실제 스케일 및 모듈러스 관리는 서로 다릅니다.
""")
code(r"""q2 = q // Delta        # 새 모듈러스 10^4
cc   = center(c_ks, q)                                # 중심화 (mod q)
c_rs = (np.round(cc / Delta).astype(np.int64)) % q2   # Delta로 나누고 새 모듈러스로

ph_rs = int(center(int(c_rs @ sb), q2))
print("리스케일 후 phase =", ph_rs, " (≈ Delta * m1*m2 =", Delta*m1*m2, ")  <-- 다시 10^2 스케일!")
print("복호:", round(ph_rs / Delta), " (기대값", m1*m2, ")")
assert round(ph_rs / Delta) == m1*m2
print("OK: 리스케일 -> 원래 스케일의 정상 암호문 (곱셈 결과 m1*m2 =", m1*m2, ")")""")

md(r"""### 정리 (1부)

| 단계 | phase | 스케일 |
|---|---|---|
| 암호화 $m$ | $\Delta m + e$ | $\Delta=10^2$ |
| 덧셈 | $\Delta(m_1{+}m_2)$ | $10^2$ |
| 곱셈(텐서) | $\Delta^2 m_1 m_2$ | $10^4$ (2차 키) |
| 리니어라이제이션 | $\Delta^2 m_1 m_2$ | $10^4$ (원래 키) |
| 리스케일 | $\Delta m_1 m_2$ | $10^2$ |

→ 이 예제는 **곱셈 → 리니어라이제이션 → 스케일·모듈러스 관리**라는 공통 흐름을 보여 줍니다.
정확한 암호문 형식과 마지막 단계의 의미는 BGV·BFV·CKKS마다 다릅니다.
""")

# ================= NTT =================
md(r"""# 2부. NTT — 다항식 곱셈을 빠르게

RLWE 기반 FHE의 암호문은 **다항식**으로 표현됩니다. 다항식 곱셈을 빠르게 하는 것이 NTT(수론 변환)입니다.

- 이 실습의 단순화된 링: $\mathbb{Z}_{17}[X]/(X^4-1)$  →  **순환 합성곱**
- $17$ 에서 $4$ 는 **원시 $4$차 단위근**: $4^2\equiv 16\equiv -1,\ 4^4\equiv 1 \pmod{17}$.

실제 RLWE 기반 FHE에서는 보통 $\mathbb{Z}_q[X]/(X^N+1)$의 **부호 반전 순환
합성곱(negacyclic convolution)** 을 사용합니다. 여기서는 NTT의 핵심 원리를 먼저 보기 위해
$X^N-1$의 순환 합성곱으로 단순화합니다.
""")
code(r"""P, N, w = 17, 4, 4
print("4^1..4^4 mod 17 =", [pow(w,k,P) for k in range(1,5)], " (order =", N, "인 원시근)")
a = np.array([1, 2, 3, 4]) % P
b = np.array([5, 6, 7, 8]) % P
print("a =", a, ", b =", b)""")

md(r"""## 6. 스쿨북 순환 합성곱 (곱하고 $X^4-1$ 로 나눈 나머지)

$X^4\equiv 1$ 이므로 지수는 $\bmod\,4$. 즉 인덱스 $(i+j)\bmod 4$ 에 더합니다.
""")
code(r"""def cyc_convol_schoolbook(a, b):
    res = np.zeros(N, dtype=np.int64)
    for i in range(N):
        for j in range(N):
            res[(i+j) % N] = (res[(i+j) % N] + a[i]*b[j]) % P
    return res % P

c_school = cyc_convol_schoolbook(a, b)
print("스쿨북 순환 합성곱 mod 17 =", c_school)""")

md(r"""## 7. FFT 로 같은 결과 (합성곱 정리)

$\text{IFFT}(\text{FFT}(a)\cdot\text{FFT}(b))$ 는 순환 합성곱과 같습니다.
여기서는 복소수 부동소수점 FFT의 결과를 반올림해 $\bmod 17$ 하면 위와 일치합니다.
작은 예제라 가능한 비교이며, 큰 정수 암호 연산에서는 반올림 오차 때문에 이 방법을 그대로 쓰지 않습니다.
""")
code(r"""c_fft = np.round(np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))).astype(np.int64) % P
print("FFT 순환 합성곱 mod 17   =", c_fft)
assert np.array_equal(c_school, c_fft)
print("OK: 스쿨북 == FFT")""")

md(r"""## 8. 원시근 4로 만든 **NTT 행렬**

FFT의 복소수 단위근 대신, $\mathbb{Z}_{17}$ 의 원시근 $w=4$ 를 씁니다.
$$ W^{(+)}_{ij}=w^{ij},\quad W^{(-)}_{ij}=w^{-ij},\qquad
   \text{NTT}(x)=W^{(+)}x,\quad \text{INTT}(X)=N^{-1}W^{(-)}X \pmod {17}. $$
포인트와이즈 곱 후 역변환하면 순환 합성곱이 됩니다 — FFT와 똑같은 원리, 다만 **정수 mod 17**.

아래는 원리를 눈으로 보기 위한 **행렬형 NTT**이므로 계산량은 $O(N^2)$입니다.
실제 구현은 같은 변환을 butterfly 구조로 계산하는 fast NTT를 사용해 $O(N\log N)$에 수행합니다.
""")
code(r"""winv = pow(w, -1, P)   # 4^{-1} mod 17
Ninv = pow(N, -1, P)   # 4^{-1} mod 17
Wm = np.array([[pow(w,    (i*j) % N, P) for j in range(N)] for i in range(N)], dtype=np.int64)
Wi = np.array([[pow(winv, (i*j) % N, P) for j in range(N)] for i in range(N)], dtype=np.int64)
print("w^-1 =", winv, ", N^-1 =", Ninv)
print("NTT 행렬 W =\n", Wm)

def ntt(x):  return (Wm @ (np.asarray(x) % P)) % P
def intt(X): return (Ninv * (Wi @ (np.asarray(X) % P))) % P

c_ntt = intt((ntt(a) * ntt(b)) % P) % P
print("NTT 순환 합성곱 mod 17   =", c_ntt)
assert np.array_equal(c_ntt, c_school)
print("OK: NTT == 스쿨북 == FFT")""")

md(r"""## 9. 주파수 영역에서 mod 17 왕복

NTT 는 $\mathbb{Z}_{17}$ 위의 FFT. 주파수 영역으로 갔다가($\bmod 17$) 되돌아오면 원래 계수가 그대로 복원됩니다.
""")
code(r"""A = ntt(a)
print("NTT(a)         =", A, "  (주파수 영역, mod 17)")
print("INTT(NTT(a))   =", intt(A), "  (원래 a =", a % P, ")")
assert np.array_equal(intt(A), a % P)
print("OK: NTT <-> INTT 왕복 항등 (mod 17)")""")

md(r"""### ★ 실습 4. 단위근을 바꾸면?

`1 <= TRY_W < 17` 범위에서 값을 바꿔 보세요. `TRY_W=4`일 때는 정확히 4번
거듭제곱해서 처음으로 1이 됩니다. `TRY_W=2`로 바꾸면 차수가 어떻게 되고,
왕복 변환은 유지될지 먼저 예상한 뒤 실행합니다.

원시 $N$차 단위근이 아닌 값을 넣어도 예외를 내지 않고 결과를 비교합니다.
""")
code(r"""TRY_W = 4

try_order = next((k for k in range(1, P) if pow(TRY_W, k, P) == 1), None)
try_winv = pow(TRY_W, -1, P)
try_W = np.array([[pow(TRY_W, i*j, P) for j in range(N)] for i in range(N)], dtype=np.int64)
try_Wi = np.array([[pow(try_winv, i*j, P) for j in range(N)] for i in range(N)], dtype=np.int64)
try_A = (try_W @ a) % P
try_back = (Ninv * (try_Wi @ try_A)) % P

print("TRY_W의 차수:", try_order, " / 필요한 차수:", N)
print("원시 N차 단위근인가?", try_order == N)
print("왕복 결과:", try_back, " / 원래 값:", a)
print("왕복 성공?", np.array_equal(try_back, a % P))""")

md(r"""### 정리 (2부)

- 다항식 곱셈(순환 합성곱)은 **스쿨북 = FFT = NTT** 로 모두 같은 결과입니다.
- NTT는 정수 모듈러 연산만 사용하므로 부동소수점 반올림 오차 없이 정확합니다.
- 이 노트북의 행렬형 구현은 $O(N^2)$, 실제 butterfly fast NTT는 $O(N\log N)$입니다.
- 실제 RLWE 기반 FHE 라이브러리는 보통 $X^N+1$에 맞춘 fast negacyclic NTT로 다항식 곱셈을 가속합니다.

**수고하셨습니다! 🎉**
""")

nb['cells'] = c
nb.metadata['kernelspec'] = {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'}
nb.metadata['language_info'] = {'name': 'python'}
with open('fhe_lwe_ntt_practice.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print("wrote fhe_lwe_ntt_practice.ipynb  (", len(c), "cells )")
