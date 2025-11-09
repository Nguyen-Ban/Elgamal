import gmpy2
import secrets

from .generate_prime import generate_prime
import time

from typing import Dict, List, Optional

def find_primitive_root_safe_prime(p: int) -> int:
    """
    Trả về phần tử sinh g cho safe prime p (p = 2q + 1)
    - Chỉ cần kiểm tra bậc 2 và q
    - Rất nhanh, dùng cho p 1024–4096 bit
    """
    if not gmpy2.is_prime(p):
        raise ValueError("p phải là số nguyên tố")

    q = (p - 1) // 2
    if not gmpy2.is_prime(q):
        raise ValueError("p không phải safe prime (p = 2q + 1 với q nguyên tố)")

    while True:
        g = secrets.randbelow(p - 2) + 2  # chọn ngẫu nhiên [2, p-2]
        if gmpy2.powmod(g, 2, p) == 1:
            continue
        if gmpy2.powmod(g, q, p) == 1:
            continue
        return g

def _is_probable_prime(n: int) -> bool:
    # wrapper, gmpy2.is_prime returns 0/1/2 (0 composite, 1 probable, 2 provable for small n)
    return bool(gmpy2.is_prime(n))

def _trial_division(n: int, small_primes: List[int]) -> Dict[int, int]:
    """Chia hết n bởi small_primes trước, trả về dict factors và n reduced."""
    factors: Dict[int, int] = {}
    for p in small_primes:
        if p * p > n:
            break
        while n % p == 0:
            factors[p] = factors.get(p, 0) + 1
            n //= p
    return factors, n

def _pollard_rho(n: int) -> int:
    """Returns a non-trivial factor of n (n composite, odd)."""
    if n % 2 == 0:
        return 2
    # choose random polynomial x^2 + c
    while True:
        x = secrets.randbelow(n - 2) + 2
        y = x
        c = secrets.randbelow(n - 1) + 1
        d = 1
        while d == 1:
            x = (gmpy2.powmod(x, 2, n) + c) % n
            y = (gmpy2.powmod(y, 2, n) + c) % n
            y = (gmpy2.powmod(y, 2, n) + c) % n
            d = gmpy2.gcd(abs(x - y), n)
            if d == n:
                break
        if d > 1 and d < n:
            return d
        # else retry

def _factor(n: int, out: Dict[int, int]) -> None:
    """Recursively factor n into out dict using Pollard-Rho & trial division."""
    if n == 1:
        return
    if _is_probable_prime(n):
        out[n] = out.get(n, 0) + 1
        return
    # small trial division with simple wheel / small primes list
    small_primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
    for p in small_primes:
        if n % p == 0:
            cnt = 0
            while n % p == 0:
                n //= p
                cnt += 1
            out[p] = out.get(p, 0) + cnt
            _factor(n, out)
            return
    # otherwise Pollard-Rho
    d = _pollard_rho(n)
    _factor(d, out)
    _factor(n // d, out)

def factorize(n: int) -> Dict[int, int]:
    """Return factorization dict for n (using Pollard-Rho)."""
    if n <= 1:
        return {}
    out: Dict[int, int] = {}
    _factor(n, out)
    return out

def is_primitive_root(p: int, g: int, fact_p_minus_1: Optional[Dict[int,int]] = None) -> bool:
    """Kiểm tra g là primitive root mod p (p prime).
       fact_p_minus_1: có thể truyền trước phân tích p-1 để tiết kiệm.
    """
    if p == 2:
        return g % p == 1
    if not fact_p_minus_1:
        fact_p_minus_1 = factorize(p - 1)
    phi = p - 1
    # unique primes
    for q in fact_p_minus_1.keys():
        if gmpy2.powmod(g, phi // q, p) == 1:
            return False
    return True


def find_primitive_root_general(p: int, max_tries: int = 1000) -> int:
    """Tìm primitive root cho prime bất kỳ.
       - factorize p-1 (Pollard-Rho)
       - thử candidates (small rồi random)
    """
    if not _is_probable_prime(p):
        raise ValueError("p phải là số nguyên tố")

    fact = factorize(p - 1)
    primes = list(fact.keys())
    # try small ints first (cheap)
    small_candidates = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    for g in small_candidates:
        if g >= p:
            continue
        good = True
        for q in primes:
            if gmpy2.powmod(g, (p - 1)//q, p) == 1:
                good = False
                break
        if good:
            return g
    # random trials
    for _ in range(max_tries):
        g = secrets.randbelow(p - 3) + 2
        good = True
        for q in primes:
            if gmpy2.powmod(g, (p - 1)//q, p) == 1:
                good = False
                break
        if good:
            return g
    raise RuntimeError("Không tìm được primitive root trong số lần thử cho trước. Hãy tăng max_tries hoặc kiểm tra p.")

def find_primitive_root(p: int, safe: bool) -> int:
    if safe:
        return find_primitive_root_safe_prime(p)
    else:
        return find_primitive_root_general(p)

if __name__ == "__main__":

    print("🔹 Tạo safe prime n-bit ...")
    safe_mode = False
    p = generate_prime(200, safe=safe_mode)
    print("p =", p)

    print("🔹 Tìm primitive root ...")
    t0 = time.time()
    g = find_primitive_root(p, safe=safe_mode)
    print(f"✅ g = {g}\n⏱️ Thời gian: {time.time()-t0:.2f}s")
