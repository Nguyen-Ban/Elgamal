import secrets
import multiprocessing as mp
import time

try:
    import gmpy2
except ImportError:
    raise ImportError("Bạn cần cài đặt gmpy2 trước: pip install gmpy2")

from functools import partial


# Sinh số nguyên tố cơ bản
def _generate_candidate(bits: int):
    """Sinh số lẻ ngẫu nhiên có đúng 'bits' bit."""
    n = secrets.randbits(bits)
    n |= (1 << bits - 1) | 1   # đảm bảo có đúng bit độ dài và là số lẻ
    return gmpy2.mpz(n)


def _next_prime(n):
    """Lấy số nguyên tố kế tiếp >= n (dựa vào gmpy2, cực nhanh)."""
    return gmpy2.next_prime(n)


def _worker(bits, safe=False, *args):
    """Tiến trình con: sinh prime (hoặc safe prime)."""
    while True:
        p = _next_prime(_generate_candidate(bits))
        if not safe:
            return p
        q = _next_prime(_generate_candidate(bits - 1))
        p = 2*q + 1
        if gmpy2.is_prime(p):
            return p


# Hàm chính
def generate_prime(bits=1024, safe=False, workers=4):
    """
    Sinh số nguyên tố 'bits'-bit nhanh bằng cách chạy song song nhiều tiến trình.
    - bits: độ dài bit (512, 1024, 2048, ...)
    - safe: True → sinh safe prime (p và (p-1)/2 đều prime)
    - workers: số CPU core sử dụng
    """
    with mp.Pool(workers) as pool:
        # results = [pool.apply_async(_worker, (bits, safe)) for _ in range(workers)]
        # for r in results:
        #     p = r.get()
        #     if p:
        #         pool.terminate()
        #         return p
        func = partial(_worker, bits, safe)
        for p in pool.imap_unordered(func, range(workers)):
            if p:
                pool.terminate()
                return p


# Kiểm tra chạy thử
if __name__ == "__main__":

    bits = 1024
    safe_mode = True
    print(f"🔹 Sinh {'safe ' if safe_mode else ''}prime {bits}-bit ...")

    t0 = time.time()
    prime = generate_prime(bits=bits, safe=safe_mode, workers=4)
    t1 = time.time()

    print(f"Prime = {prime}")
    print(f"Thời gian: {t1 - t0:.3f} giây")