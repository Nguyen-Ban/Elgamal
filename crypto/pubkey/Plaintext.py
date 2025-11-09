# Plaintext.py
from .strint import str_chunk_to_int, int_to_str_chunk
from typing import List

GRANULARITY = 15  # bạn có thể điều chỉnh; đây là số ký tự (not bytes) mỗi block

class Plaintext:
    def __init__(self, numbers: List[int]):
        # mỗi phần tử là số nguyên được tạo từ 1 chunk UTF-8 của chuỗi gốc
        self.numbers = list(numbers)
    
    def to_string(self) -> str:
        """
        Chuyển danh sách số về chuỗi: mỗi số -> bytes -> decode -> nối lại.
        Lưu ý: các chunk sẽ ghép lại, trả về chuỗi gốc (nếu từ_string dùng cùng GRANULARITY).
        """
        result = ""
        for number in self.numbers:
            result += int_to_str_chunk(number)
        return result
    
    def __repr__(self) -> str:
        return f"Plaintext({self.numbers})"
    
    def __str__(self) -> str:
        return str(self.numbers)
    
    def _compare_numbers_only(self, other: 'Plaintext') -> bool:
        N = len(self.numbers)
        if N != len(other.numbers):
            return False
        for i in range(0, N):
            if self.numbers[i] != other.numbers[i]:
                return False
        return True

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Plaintext):
            return False
        # nếu các block giống nhau -> bằng
        if self._compare_numbers_only(other):
            return True
        # nếu các block không giống nhưng tái tạo chuỗi giống nhau -> cũng bằng
        return self.to_string() == other.to_string()
    
    @staticmethod
    def from_string(s: str) -> "Plaintext":
        """
        Tạo Plaintext từ chuỗi bất kỳ (Unicode):
        - chia chuỗi thành các chunk mỗi GRANULARITY ký tự (không phải bytes)
        - mỗi chunk encode utf-8 -> bytes -> int
        - lưu list số nguyên
        """
        numbers: List[int] = []
        if s == "":
            return Plaintext([])
        
        # chia theo số ký tự (GRANULARITY)
        accumulation = ""
        for ch in s:
            accumulation += ch
            if len(accumulation) == GRANULARITY:
                numbers.append(str_chunk_to_int(accumulation))
                accumulation = ""
        if len(accumulation) > 0:
            numbers.append(str_chunk_to_int(accumulation))
        return Plaintext(numbers)

if __name__ == "__main__":
    # test nhanh
    s = "Xin chào thế giới! Đây là một chuỗi dài hơn 15 ký tự."
    pt = Plaintext.from_string(s)
    print("Plaintext numbers:", pt.numbers)
    s_reconstructed = pt.to_string()
    print("Reconstructed string:", s_reconstructed)
    print("Equal to original?", s == s_reconstructed)