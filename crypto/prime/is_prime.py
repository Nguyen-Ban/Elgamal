import random
from gmpy2 import powmod

_small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43,
                 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

def _trail_division(n: int) -> bool:
    if n < 2:
        return False
    for p in _small_primes:
        if n % p == 0:
            return False
    return True

def _miller_rabin(n: int, rounds: int = 10) -> bool:
    if n < 2:
        return False
    if n in _small_primes:
        return True
    if any(n % p == 0 for p in _small_primes):
        return False

    d, s = 0, n - 1
    while s % 2 == 0:
        d += 1
        s //= 2

    for _ in range(rounds):
        a = random.randint(2, n - 2)
        x = powmod(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(d - 1):
            x = powmod(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def _jacobi(a: int, n: int) -> int:
    if n <= 0 or n % 2 == 0:
        return 0
    a = a % n
    result = 1
    while a != 0:
        while a % 2 == 0:
            a //= 2
            if n % 8 in [3, 5]:
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a %= n
    if n == 1:
        return result
    return 0

def _lucas_prp(n: int) -> bool:
    """Kiểm tra nguyên tố theo Lucas probable prime."""
    # Tìm P sao cho D = P^2 - 4 có Jacobi(D/n) = -1
    for P in range(3, 100):
        D = P * P - 4
        if _jacobi(D, n) == -1:
            break
    else:
        return False

    # Dãy Lucas
    def lucas_uv(P, D, k, n):
        U, V = 0, 2
        inv2 = powmod(2, -1, n)
        for bit in bin(k)[2:]:
            U, V = (U * V) % n, (V * V - 2) % n
            if bit == "1":
                U, V = (P * U + V) * inv2 % n, (D * U + P * V) * inv2 % n
        return U, V

    U, V = lucas_uv(P, D, n + 1, n)
    return U == 0

def is_prime(n: int) -> bool:
    """Kiểm tra số nguyên tố sử dụng kết hợp các phương pháp."""
    if n < 2:
        return False
    if n in _small_primes:
        return True
    if not _trail_division(n):
        return False
    if not _miller_rabin(n):
        return False
    if not _lucas_prp(n):
        return False
    return True