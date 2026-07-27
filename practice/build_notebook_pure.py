#!/usr/bin/env python3
# fhe_lwe_ntt_practice_pure.ipynb 생성기 — numpy 없이 순수 파이썬(random, cmath)만 사용.
# 실행:  python3 build_notebook_pure.py
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

nb = new_notebook()
c = []
def md(t): c.append(new_markdown_cell(t))
def code(t): c.append(new_code_cell(t))

md(r"""# 동형암호(FHE) 원리 실습 — 순수 파이썬(설치 필요 없음)

**서울여대 GSPP Privacy Scholar Camp · 이승환 (waLLLnut / LatticA)**

이 노트북은 **numpy조차 필요 없이** 파이썬 표준 라이브러리(`random`, `cmath`)만으로 동형암호의 핵심을 돌려봅니다.
아나콘다·pip 설치 없이 파이썬만 있으면 됩니다. (토이 파라미터라 numpy 없이 충분)

> **두 가지 사용법**
> 1. 설명을 들으며 **Run All** — 기본값에서 모든 셀이 처음부터 끝까지 실행됩니다.
> 2. `★ 실습` 셀의 `TRY_...`/`None` 슬롯을 바꿔 다시 실행 — 결과를 예측하며 실험합니다.
>
> **주의:** 차원 $n=2$와 $[-10,10]$ 균등 샘플은 원리를 보기 위한 장난감 설정입니다. 실제 보안 파라미터가 아닙니다.
> (곱셈 절 뒤 **★ 실습 2** 에서 같은 파이프라인을 $n=3$ 으로 직접 채워 봅니다.)

**1부 — LWE 암호와 동형연산** · **2부 — NTT (다항식 곱셈 가속)**
""")

md(r"""## 0. 파라미터 설정

- 차원 $n=2$, 모듈러스 $q=10^6$, 스케일 인자 $\Delta=10^2$
- 비밀키·오류는 $[-10,10]$ 균등 샘플, 시드 고정(`random.seed(42)`)
- numpy 배열 대신 **파이썬 리스트**, 행렬곱/텐서곱은 리스트 내포로 직접 계산합니다.
""")
code(r"""import random, cmath   # 둘 다 파이썬 기본 내장 (설치 불필요)

q     = 10**6      # 모듈러스
n     = 2          # LWE 차원
Delta = 100        # 스케일 인자 10^2
random.seed(42)

def center(x, mod=q):
    "값을 (-mod/2, mod/2] 범위로 (부호 있는 대표원)"
    return ((int(x) + mod//2) % mod) - mod//2

def dot(u, v):
    "두 벡터(리스트)의 내적"
    return sum(a*b for a, b in zip(u, v))

print("q =", q, ", n =", n, ", Delta =", Delta)""")

md(r"""## 1. LWE 암호화 / phase / 복호화

비밀키 $\mathbf s$, 확장키 $\bar{\mathbf s}=(1,s_1,s_2)$. 암호문 $\bar{\mathbf c}=(b,-a_1,-a_2)$ 에서
**phase** $=\langle\bar{\mathbf c},\bar{\mathbf s}\rangle=\Delta m+e$. 반올림으로 잡음 $e$ 를 지우면 $m$ 복원.
""")
code(r"""def keygen():
    return [random.randint(-10, 10) for _ in range(n)]      # sk ∈ [-10,10]^n

def sbar(s):
    return [1] + list(s)                                    # (1, s1, s2)

def encrypt(m, s, delta=Delta):
    a = [random.randint(0, q-1) for _ in range(n)]
    e = random.randint(-10, 10)
    b = (dot(a, s) + e + delta*m) % q
    return [b] + [(-ai) % q for ai in a]                    # (b, -a1, -a2)

def phase(c, s):
    return center(dot(c, sbar(s)))

def decrypt(c, s, delta=Delta):
    return round(phase(c, s) / delta)

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

$\bar{\mathbf c}_1+\bar{\mathbf c}_2$ 를 계산하면 phase 도 그대로 더해져 $\Delta(m_1+m_2)+(e_1+e_2)$. 복호하면 $m_1+m_2$.
""")
code(r"""c_add = [(x + y) % q for x, y in zip(c1, c2)]
print("phase(c1+c2) =", phase(c_add, s), " (= phase(c1)+phase(c2))")
print("복호:", decrypt(c_add, s), " (기대값 m1+m2 =", m1+m2, ")")
assert decrypt(c_add, s) == m1 + m2
print("OK: 동형 덧셈")""")

md(r"""### ★ 실습 1. 메시지와 오류를 바꾸면?

아래 세 값만 바꿔 실행해 보세요. 오류 한계가 $\Delta/2=50$ 에 가까워지면 언제 복호가 흔들릴까요?
(이 셀은 별도 난수기를 써서 뒤 예제에 영향을 주지 않습니다.)
""")
code(r"""TRY_M1, TRY_M2 = 4, -1
TRY_ERROR_BOUND = 10

trial_rng = random.Random(2026)

def encrypt_trial(m, s, error_bound):
    a = [trial_rng.randint(0, q-1) for _ in range(n)]
    e = trial_rng.randint(-error_bound, error_bound)
    b = (dot(a, s) + e + Delta*m) % q
    return ([b] + [(-ai) % q for ai in a]), e

tc1, te1 = encrypt_trial(TRY_M1, s, TRY_ERROR_BOUND)
tc2, te2 = encrypt_trial(TRY_M2, s, TRY_ERROR_BOUND)
tadd = [(x + y) % q for x, y in zip(tc1, tc2)]

got1, got2, got_add = decrypt(tc1, s), decrypt(tc2, s), decrypt(tadd, s)
print("개별 오류 (e1, e2):", (te1, te2), " / 합산 오류 e1+e2:", te1 + te2)
print("반올림 기준: |ei| <", Delta/2, ", |e1+e2| <", Delta/2)
print("개별 복호:", (got1, got2), " / 예상:", (TRY_M1, TRY_M2))
print("덧셈 복호:", got_add, " / 예상:", TRY_M1 + TRY_M2)
print("결과:", "성공" if (got1, got2, got_add) == (TRY_M1, TRY_M2, TRY_M1 + TRY_M2)
      else "복호 실패 — 오류와 Delta의 상대적 크기를 확인하세요")""")

md(r"""## 3. 곱셈 — 비밀키와 암호문의 **텐서곱**

두 phase 의 곱은 자연스럽게 텐서곱이 됩니다:
$\langle\bar{\mathbf c}_1,\bar{\mathbf s}\rangle\langle\bar{\mathbf c}_2,\bar{\mathbf s}\rangle
=\langle\bar{\mathbf c}_1\otimes\bar{\mathbf c}_2,\ \bar{\mathbf s}\otimes\bar{\mathbf s}\rangle$.
새 암호문·키는 차원 $9$, phase 는 $\approx\Delta^2 m_1m_2$ 로 스케일이 $10^2\to10^4$ 로 커집니다.
""")
code(r"""sb    = sbar(s)
t     = [sb[i]*sb[j] for i in range(len(sb)) for j in range(len(sb))]          # sbar ⊗ sbar (차원 9)
c_mul = [(c1[i]*c2[j]) % q for i in range(len(c1)) for j in range(len(c2))]    # c1 ⊗ c2   (차원 9)

ph_mul = center(dot(c_mul, t))
print("텐서곱 암호문 차원:", len(c_mul), ", 텐서곱 키 차원:", len(t))
print("phase(곱) =", ph_mul)
print("  ≈ Delta^2 * m1*m2 =", Delta**2 * m1*m2, "  <-- 스케일이 10^2에서 10^4로!")
print("  Delta^2 로 나눠 복호:", round(ph_mul / Delta**2), " (기대값", m1*m2, ")")
assert round(ph_mul / Delta**2) == m1*m2
print("OK: 동형 곱셈 (2차 암호문)")""")

md(r"""### 선택 심화 3-1. 왜 하필 '텐서'인가 — 곱셈의 선형대수

$\mu_1\mu_2=\bar{\mathbf s}^\top(\bar{\mathbf c}_1\bar{\mathbf c}_2^\top)\bar{\mathbf s}
=\langle\bar{\mathbf c}_1\otimes\bar{\mathbf c}_2,\ \bar{\mathbf s}\otimes\bar{\mathbf s}\rangle$.
외적 행렬 $C$ 의 이차형식과 텐서 내적이 같음을 확인합니다.
""")
code(r"""mu1, mu2 = phase(c1, s), phase(c2, s)
C = [[c1[i]*c2[j] for j in range(len(c2))] for i in range(len(c1))]   # 외적 행렬 (랭크 1)
print("외적 행렬 C = c1·c2^T (3×3, 랭크 1):")
for row in C:
    print("  ", row)

d = len(sb)
qf   = center(sum(sb[i]*C[i][j]*sb[j] for i in range(d) for j in range(d)))   # (2) s^T C s
tens = center(dot([C[i][j] for i in range(d) for j in range(d)], t))          # (3) <c1⊗c2, s⊗s>
print()
print("(1) mu1 * mu2          =", mu1*mu2)
print("(2) sbar^T C sbar      =", qf,   "  <- 키에 대한 이차형식")
print("(3) <c1⊗c2, sbar⊗sbar> =", tens, "  <- 텐서 내적")
assert mu1*mu2 == qf == tens
print("=> 셋 다 동일! 텐서곱은 '키에 대한 이차형식'을 편 것.")""")

md(r"""### ★ 실습 2. 3개짜리(n=3)로 직접 해보기

지금까지 **비밀키 2개(n=2)** 로 확인했습니다. 이제 **n=3** 으로 같은 파이프라인을 **직접 완성**해 보세요.
아래 `None` 슬롯 세 곳을 채우면 자동 검증이 돕니다. (확장키 차원 4, 텐서 차원 16)
""")
code(r"""# n=2 는 위에서 확인했습니다. 이제 n=3 (비밀키 3개)로 직접 완성해 보세요.
n3   = 3
rng3 = random.Random(7)

def keygen3():
    return [rng3.randint(-10, 10) for _ in range(n3)]

def encrypt3(m, sk, delta=Delta):
    a = [rng3.randint(0, q-1) for _ in range(n3)]
    e = rng3.randint(-10, 10)
    b = (dot(a, sk) + e + delta*m) % q
    return [b] + [(-ai) % q for ai in a]        # (b, -a1, -a2, -a3)

s3   = keygen3()
c1_3 = encrypt3(2, s3)        # 메시지 2
c2_3 = encrypt3(3, s3)        # 메시지 3

# ---- 채워야 할 슬롯 3개 (None 을 지우고 채우기) --------------------------
sbar3 = None   # 확장키 [1, s1, s2, s3]           힌트: [1] + s3
t3    = None   # 텐서곱 키 sbar3 ⊗ sbar3           힌트: [sbar3[i]*sbar3[j] for i in range(4) for j in range(4)]
cmul3 = None   # 암호문 텐서곱 c1_3 ⊗ c2_3 (mod q)  힌트: [(c1_3[i]*c2_3[j])%q for i in range(4) for j in range(4)]
# ------------------------------------------------------------------------

if sbar3 is None or t3 is None or cmul3 is None:
    print("슬롯(None)을 채운 뒤 다시 실행하세요.  힌트는 각 줄 주석 참고.")
    print("기대값 -> 확장키 차원 4, 텐서 차원 16, phase(곱) ≈ Delta^2*2*3 =", Delta**2*6)
else:
    ph_add = center(dot([(x + y) % q for x, y in zip(c1_3, c2_3)], sbar3))
    ph_mul3 = center(dot(cmul3, t3))
    print("확장키 차원:", len(sbar3), "(기대 4) / 텐서 차원:", len(t3), "(기대 16)")
    print("덧셈 복호 :", round(ph_add / Delta),     "(기대 5)")
    print("곱셈 phase:", ph_mul3, "-> 복호:", round(ph_mul3 / Delta**2), "(기대 6)")
    assert len(sbar3) == n3 + 1 and len(t3) == (n3 + 1)**2
    assert round(ph_add / Delta) == 5 and round(ph_mul3 / Delta**2) == 6
    print("OK: n=3 에서도 암호화·덧셈·텐서곱 동작 🎉")""")

md(r"""## 4. 키스위칭의 특수한 경우: 리니어라이제이션

곱셈 결과는 차원 9의 **2차 키** 아래 있습니다. **가젯 분해**로 큰 키 성분 $t_j$ 를 원래 키로 재암호화한
**키스위칭 키(KSK)** 를 이용해 다시 원래 $\bar{\mathbf s}$ 아래로 줄입니다(리니어라이제이션).
""")
md(r"""### ★ 실습 3. 가젯 분해를 직접 확인하기

`TRY_DIGIT_VALUE`만 바꾸고, 부호 있는 10진 자릿수를 먼저 예상해 보세요. 재조합이 원래 값과 같은지 자동 확인합니다.
""")
code(r"""Bg, L = 10, 6   # 10진 분해, 자릿수 6개 (10^6 = q)

def signed_digits(x):
    "x 를 부호 있는 10진 자릿수 L개로 분해"
    x = int(x) % q
    ds = []
    for _ in range(L):
        dgt = x % Bg
        if dgt > Bg // 2:
            dgt -= Bg
        ds.append(dgt)
        x = (x - dgt) // Bg
    return ds

# ★ 실습 3: 이 값만 바꾸고, 출력될 부호 있는 10진 자릿수를 먼저 예상해 보세요.
TRY_DIGIT_VALUE = 314159
try_digits = signed_digits(TRY_DIGIT_VALUE)
try_reconstructed = sum(dgt * (Bg**l) for l, dgt in enumerate(try_digits))
print("원래 값 (mod q):", TRY_DIGIT_VALUE % q)
print("부호 있는 자릿수:", try_digits)
print("자릿수 재조합 (mod q):", try_reconstructed % q)
assert try_reconstructed % q == TRY_DIGIT_VALUE % q
print("OK: 가젯 분해 후 다시 같은 값")""")

md(r"""#### KSK를 만들고 리니어라이제이션 실행

1. 텐서 키의 각 성분 $t_j$ 를 각 자리 $B^\ell$ 배로 원래 키 아래 암호화 → KSK.
2. 큰 암호문의 각 성분을 부호 있는 자릿수로 분해하고 KSK를 선형 결합.
""")
code(r"""def encrypt_raw(value, s):
    "스케일 없이 값 자체를 암호화: phase ≈ value + e (KSK용)"
    a = [random.randint(0, q-1) for _ in range(n)]
    e = random.randint(-10, 10)
    b = (dot(a, s) + e + int(value)) % q
    return [b] + [(-ai) % q for ai in a]

d_big = len(t)
KSK = {j: [encrypt_raw(t[j] * (Bg**l), s) for l in range(L)] for j in range(1, d_big)}

def keyswitch(c_big):
    cprime = [0] * (n + 1)
    cprime[0] = int(c_big[0]) % q          # 상수항(=1)은 b-슬롯으로
    for j in range(1, d_big):
        ds = signed_digits(c_big[j])
        for l in range(L):
            cprime = [(cprime[k] + ds[l] * KSK[j][l][k]) % q for k in range(n + 1)]
    return cprime

c_ks  = keyswitch(c_mul)
ph_ks = center(dot(c_ks, sb))
print("리니어라이제이션 후 차원:", len(c_ks), " (다시 원래 키", len(sb), "차원)")
print("phase(리니어라이제이션) =", ph_ks, " (곱 phase", ph_mul, "와 유사, 오류만 약간 증가)")
assert round(ph_ks / Delta**2) == m1*m2
print("OK: 리니어라이제이션 (phase·메시지 보존)")""")

md(r"""## 5. 장난감 리스케일 — $1/\Delta$ 로 나눠 원래 스케일로

phase 스케일이 $\Delta^2(=10^4)$ 이니 $\Delta(=100)$ 로 나눠 원래 $\Delta$ 스케일로 되돌립니다.
암호문을 $\Delta$ 로 나눌 때 **모듈러스도 $q\to q/\Delta$ 로 함께** 줄입니다. (CKKS 리스케일 직관의 교육용 모형)
""")
code(r"""q2 = q // Delta        # 새 모듈러스 10^4
c_rs = [round(center(x) / Delta) % q2 for x in c_ks]   # Delta로 나누고 새 모듈러스로

ph_rs = center(dot(c_rs, sb), q2)
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

→ **곱셈 → 리니어라이제이션 → 스케일·모듈러스 관리** 라는 공통 흐름. 정확한 형식은 BGV·BFV·CKKS마다 다릅니다.
""")

# ================= NTT =================
md(r"""# 2부. NTT — 다항식 곱셈을 빠르게

RLWE 기반 FHE의 암호문은 **다항식**입니다. 다항식 곱셈을 빠르게 하는 것이 NTT(수론 변환).

- 단순화 링: $\mathbb Z_{17}[X]/(X^4-1)$ → **순환 합성곱**
- $17$ 에서 $4$ 는 **원시 4차 단위근**: $4^2\equiv-1,\ 4^4\equiv1$.
""")
code(r"""P, N, w = 17, 4, 4
print("4^1..4^4 mod 17 =", [pow(w, k, P) for k in range(1, 5)], " (order =", N, "인 원시근)")
a = [1, 2, 3, 4]
b = [5, 6, 7, 8]
print("a =", a, ", b =", b)""")

md(r"""## 6. 스쿨북 순환 합성곱 ($X^4\equiv1$ 이므로 인덱스 $\bmod 4$)""")
code(r"""def cyc_convol_schoolbook(a, b):
    res = [0]*N
    for i in range(N):
        for j in range(N):
            res[(i+j) % N] = (res[(i+j) % N] + a[i]*b[j]) % P
    return res

c_school = cyc_convol_schoolbook(a, b)
print("스쿨북 순환 합성곱 mod 17 =", c_school)""")

md(r"""## 7. FFT 로 같은 결과 (합성곱 정리)

복소 DFT를 `cmath` 로 직접 구현합니다. $\text{IDFT}(\text{DFT}(a)\cdot\text{DFT}(b))$ 를 반올림해 $\bmod17$ 하면 위와 일치.
작은 예제라 가능한 비교이며, 큰 정수 연산에서는 반올림 오차 때문에 그대로 쓰지 않습니다.
""")
code(r"""def dft(x):
    M = len(x)
    return [sum(x[j]*cmath.exp(-2j*cmath.pi*k*j/M) for j in range(M)) for k in range(M)]

def idft(X):
    M = len(X)
    return [sum(X[k]*cmath.exp(2j*cmath.pi*k*j/M) for k in range(M))/M for j in range(M)]

prod = [A*Bv for A, Bv in zip(dft(a), dft(b))]
c_fft = [round(v.real) % P for v in idft(prod)]
print("FFT 순환 합성곱 mod 17   =", c_fft)
assert c_fft == c_school
print("OK: 스쿨북 == FFT")""")

md(r"""## 8. 원시근 4로 만든 **NTT 행렬**

복소 단위근 대신 $\mathbb Z_{17}$ 의 원시근 $w=4$: $W^{(+)}_{ij}=w^{ij}$, $\text{NTT}(x)=W^{(+)}x$,
$\text{INTT}(X)=N^{-1}W^{(-)}X\pmod{17}$. 포인트와이즈 곱 후 역변환 = 순환 합성곱 — FFT와 같은 원리, 다만 **정수 mod 17**.
""")
code(r"""winv = pow(w, -1, P)   # 4^{-1} mod 17
Ninv = pow(N, -1, P)
Wm = [[pow(w,    (i*j) % N, P) for j in range(N)] for i in range(N)]
Wi = [[pow(winv, (i*j) % N, P) for j in range(N)] for i in range(N)]
print("w^-1 =", winv, ", N^-1 =", Ninv)
print("NTT 행렬 W =")
for row in Wm:
    print("  ", row)

def ntt(x):  return [sum(Wm[i][j]*x[j] for j in range(N)) % P for i in range(N)]
def intt(X): return [(Ninv*sum(Wi[i][j]*X[j] for j in range(N))) % P for i in range(N)]

c_ntt = intt([(A*Bv) % P for A, Bv in zip(ntt(a), ntt(b))])
print("NTT 순환 합성곱 mod 17   =", c_ntt)
assert c_ntt == c_school
print("OK: NTT == 스쿨북 == FFT")""")

md(r"""## 9. 주파수 영역에서 mod 17 왕복

NTT 는 $\mathbb Z_{17}$ 위의 FFT. 주파수 영역으로 갔다가 되돌아오면 원래 계수가 그대로 복원됩니다.
""")
code(r"""A = ntt(a)
print("NTT(a)         =", A, "  (주파수 영역, mod 17)")
print("INTT(NTT(a))   =", intt(A), "  (원래 a =", [x % P for x in a], ")")
assert intt(A) == [x % P for x in a]
print("OK: NTT <-> INTT 왕복 항등 (mod 17)")""")

md(r"""### ★ 실습 4. 단위근을 바꾸면?

`1 <= TRY_W < 17` 에서 값을 바꿔 보세요. `TRY_W=4`는 4번 거듭제곱해 처음 1이 됩니다(원시 4차 근).
`TRY_W=2`면 차수가 어떻게 되고 왕복이 유지될지 먼저 예상한 뒤 실행하세요.
""")
code(r"""TRY_W = 4

try_order = next((k for k in range(1, P) if pow(TRY_W, k, P) == 1), None)
try_winv = pow(TRY_W, -1, P)
try_W  = [[pow(TRY_W,   i*j, P) for j in range(N)] for i in range(N)]
try_Wi = [[pow(try_winv, i*j, P) for j in range(N)] for i in range(N)]
try_A    = [sum(try_W[i][j]*a[j] for j in range(N)) % P for i in range(N)]
try_back = [(Ninv*sum(try_Wi[i][j]*try_A[j] for j in range(N))) % P for i in range(N)]

print("TRY_W의 차수:", try_order, " / 필요한 차수:", N)
print("원시 N차 단위근인가?", try_order == N)
print("왕복 결과:", try_back, " / 원래 값:", [x % P for x in a])
print("왕복 성공?", try_back == [x % P for x in a])""")

md(r"""### 정리 (2부)

- 순환 합성곱은 **스쿨북 = FFT = NTT** 로 모두 같은 결과.
- NTT는 정수 모듈러 연산만 써서 반올림 오차 없이 정확.
- 이 노트북은 **numpy 없이 순수 파이썬**(random, cmath)만으로 전 과정을 돌렸습니다.

**수고하셨습니다! 🎉**
""")

nb['cells'] = c
nb.metadata['kernelspec'] = {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'}
nb.metadata['language_info'] = {'name': 'python'}
with open('fhe_lwe_ntt_practice_pure.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print("wrote fhe_lwe_ntt_practice_pure.ipynb  (", len(c), "cells )")
