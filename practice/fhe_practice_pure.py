#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
동형암호(FHE) 원리 실습 — 순수 파이썬(표준 라이브러리)만 사용.
numpy·아나콘다·pip 설치 전혀 필요 없음.  실행:  python3 fhe_practice_pure.py

토이 파라미터라 numpy 없이도 충분합니다. (import는 random, cmath 뿐 — 둘 다 파이썬 기본 내장)
"""
import random
import cmath

# ===== 0. 파라미터 =====
q     = 10**6      # 모듈러스
n     = 2          # LWE 차원
Delta = 100        # 스케일 인자
random.seed(42)

def center(x, mod=q):
    "값을 (-mod/2, mod/2] 범위로 (부호 있는 대표원)"
    return ((int(x) + mod // 2) % mod) - mod // 2

def dot(u, v):
    return sum(a * b for a, b in zip(u, v))

print("q =", q, ", n =", n, ", Delta =", Delta)

# ===== 1. LWE 암호화 / phase / 복호화 =====
def keygen():
    return [random.randint(-10, 10) for _ in range(n)]

def sbar(s):
    return [1] + list(s)                       # (1, s1, s2)

def encrypt(m, s, delta=Delta):
    a = [random.randint(0, q - 1) for _ in range(n)]
    e = random.randint(-10, 10)
    b = (dot(a, s) + e + delta * m) % q
    return [b] + [(-ai) % q for ai in a]        # (b, -a1, -a2)

def phase(c, s):
    return center(dot(c, sbar(s)))

def decrypt(c, s, delta=Delta):
    return round(phase(c, s) / delta)

s = keygen()
print("\n[1] 비밀키 sk =", s, ", 확장키 sbar =", sbar(s))
m1, m2 = 2, 3
c1, c2 = encrypt(m1, s), encrypt(m2, s)
print("phase(c1) =", phase(c1, s), "-> 복호:", decrypt(c1, s))
print("phase(c2) =", phase(c2, s), "-> 복호:", decrypt(c2, s))
assert decrypt(c1, s) == m1 and decrypt(c2, s) == m2
print("OK: 암호화/복호화")

# ===== 2. 덧셈 =====
c_add = [(x + y) % q for x, y in zip(c1, c2)]
print("\n[2] phase(c1+c2) =", phase(c_add, s), "-> 복호:", decrypt(c_add, s), "(기대", m1 + m2, ")")
assert decrypt(c_add, s) == m1 + m2
print("OK: 동형 덧셈")

# ===== 3. 곱셈 = 텐서곱 =====
sb    = sbar(s)
t     = [sb[i] * sb[j] for i in range(len(sb)) for j in range(len(sb))]   # sbar ⊗ sbar (차원 9)
c_mul = [(c1[i] * c2[j]) % q for i in range(len(c1)) for j in range(len(c2))]  # c1 ⊗ c2
ph_mul = center(dot(c_mul, t))
print("\n[3] 텐서곱 차원:", len(c_mul), "/ phase(곱) =", ph_mul,
      "≈ Delta^2*m1*m2 =", Delta**2 * m1 * m2)
print("Delta^2로 나눠 복호:", round(ph_mul / Delta**2), "(기대", m1 * m2, ")")
assert round(ph_mul / Delta**2) == m1 * m2
print("OK: 동형 곱셈 (2차 암호문)")

# ---- 왜 '텐서'인가: 외적행렬 이차형식 = 텐서 내적 ----
d = len(sb)
C = [[c1[i] * c2[j] for j in range(len(c2))] for i in range(len(c1))]        # 외적 행렬
qf   = center(sum(sb[i] * C[i][j] * sb[j] for i in range(d) for j in range(d)))
tens = center(dot([C[i][j] for i in range(d) for j in range(d)], t))
print("(1) mu1*mu2          =", phase(c1, s) * phase(c2, s))
print("(2) sbar^T C sbar    =", qf)
print("(3) <c1⊗c2, s⊗s>     =", tens)
assert phase(c1, s) * phase(c2, s) == qf == tens
print("OK: 외적 이차형식 = 텐서 내적 (셋 다 동일)")

# ===== 4. 키스위칭(리니어라이제이션) — 가젯 분해 =====
Bg, L = 10, 6
def signed_digits(x):
    x = int(x) % q
    ds = []
    for _ in range(L):
        dgt = x % Bg
        if dgt > Bg // 2:
            dgt -= Bg
        ds.append(dgt)
        x = (x - dgt) // Bg
    return ds

def encrypt_raw(value, s):
    a = [random.randint(0, q - 1) for _ in range(n)]
    e = random.randint(-10, 10)
    b = (dot(a, s) + e + int(value)) % q
    return [b] + [(-ai) % q for ai in a]

d_big = len(t)
KSK = {j: [encrypt_raw(t[j] * (Bg**l), s) for l in range(L)] for j in range(1, d_big)}

def keyswitch(c_big):
    cprime = [0] * (n + 1)
    cprime[0] = int(c_big[0]) % q
    for j in range(1, d_big):
        ds = signed_digits(c_big[j])
        for l in range(L):
            cprime = [(cprime[k] + ds[l] * KSK[j][l][k]) % q for k in range(n + 1)]
    return cprime

c_ks = keyswitch(c_mul)
ph_ks = center(dot(c_ks, sb))
print("\n[4] 리니어라이제이션 후 차원:", len(c_ks), "/ phase =", ph_ks, "(곱 phase", ph_mul, "와 유사)")
assert round(ph_ks / Delta**2) == m1 * m2
print("OK: 리니어라이제이션 (phase·메시지 보존)")

# ===== 5. 리스케일 =====
q2 = q // Delta
c_rs = [round(center(x) / Delta) % q2 for x in c_ks]
ph_rs = center(dot(c_rs, sb), q2)
print("\n[5] 리스케일 후 phase =", ph_rs, "≈ Delta*m1*m2 =", Delta * m1 * m2,
      "-> 복호:", round(ph_rs / Delta), "(기대", m1 * m2, ")")
assert round(ph_rs / Delta) == m1 * m2
print("OK: 리스케일 -> 정상 스케일 (곱셈 결과", m1 * m2, ")")

# ===== 6~9. NTT (다항식 곱셈 가속) =====
P, N, w = 17, 4, 4
a = [1, 2, 3, 4]
b = [5, 6, 7, 8]
print("\n[6] 4^1..4^4 mod 17 =", [pow(w, k, P) for k in range(1, 5)], "(원시 4차 단위근)")

def cyc_convol(a, b):
    res = [0] * N
    for i in range(N):
        for j in range(N):
            res[(i + j) % N] = (res[(i + j) % N] + a[i] * b[j]) % P
    return res
c_school = cyc_convol(a, b)
print("스쿨북 순환 합성곱 mod 17 =", c_school)

# FFT (복소 DFT, 표준 cmath)
def dft(x):
    M = len(x)
    return [sum(x[j] * cmath.exp(-2j * cmath.pi * k * j / M) for j in range(M)) for k in range(M)]
def idft(X):
    M = len(X)
    return [sum(X[k] * cmath.exp(2j * cmath.pi * k * j / M) for k in range(M)) / M for j in range(M)]
prod = [A * Bv for A, Bv in zip(dft(a), dft(b))]
c_fft = [round(v.real) % P for v in idft(prod)]
print("[7] FFT 순환 합성곱 mod 17   =", c_fft)
assert c_fft == c_school
print("OK: 스쿨북 == FFT")

# NTT 행렬 (Z_17 위)
winv = pow(w, -1, P)
Ninv = pow(N, -1, P)
Wm = [[pow(w,    (i * j) % N, P) for j in range(N)] for i in range(N)]
Wi = [[pow(winv, (i * j) % N, P) for j in range(N)] for i in range(N)]
def ntt(x):  return [sum(Wm[i][j] * x[j] for j in range(N)) % P for i in range(N)]
def intt(X): return [(Ninv * sum(Wi[i][j] * X[j] for j in range(N))) % P for i in range(N)]
c_ntt = intt([(A * Bv) % P for A, Bv in zip(ntt(a), ntt(b))])
print("[8] NTT 순환 합성곱 mod 17   =", c_ntt)
assert c_ntt == c_school
print("OK: NTT == 스쿨북 == FFT")

A = ntt(a)
print("[9] NTT(a) =", A, "/ INTT(NTT(a)) =", intt(A), "(원래 a =", a, ")")
assert intt(A) == [x % P for x in a]
print("OK: NTT <-> INTT 왕복 항등")

print("\n===== 전부 통과: numpy 없이 순수 파이썬만으로 동작 확인 🎉 =====")
