# strint.py
# Chuyển string <-> integer bằng cách encode UTF-8 và dùng base-256 (int.from_bytes / int.to_bytes)
from typing import Tuple

def str_chunk_to_int(s: str) -> int:
    """
    Chuyển một chuỗi (chunk) thành số nguyên:
    - encode UTF-8 -> bytes
    - int.from_bytes(bytes, 'big')
    """
    if s == "":
        return 0
    b = s.encode("utf-8")
    return int.from_bytes(b, "big")

def int_to_str_chunk(n: int) -> str:
    """
    Chuyển số nguyên (đã được tạo từ bytes) về chuỗi:
    - tìm số byte cần thiết: (n.bit_length()+7)//8
    - int.to_bytes -> decode('utf-8')
    """
    if n == 0:
        return ""
    length = (n.bit_length() + 7) // 8
    b = n.to_bytes(length, "big")
    return b.decode("utf-8")

if __name__ == "__main__":
    # test nhanh
    original = "Xin chào!"
    n = str_chunk_to_int(original)
    reconstructed = int_to_str_chunk(n)
    print("Original string:", original)
    print("Converted to int:", n)
    print("Reconstructed string:", reconstructed)
    print("Equal to original?", original == reconstructed)