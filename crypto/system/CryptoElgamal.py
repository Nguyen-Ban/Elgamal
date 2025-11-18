from ..pubkey import CryptoSystem, Plaintext, CryptoSystemTest
from ..prime.generate_prime import generate_prime
from ..prime.prime_root import find_primitive_root
import random
import unittest

CRYPTO_BITS  = 2048

class ElGamalCiphertextPair:
    def __init__(self, y1: int, y2: int):
        self.y1 = y1
        self.y2 = y2
        
    def __repr__(self):
        return f"ElGamalCiphertextPair(y1={self.y1}, y2={self.y2})"
    
class ElGamalCiphertext:
    def __init__(self, cipher_pairs: list[ElGamalCiphertextPair]):
        self.cipher_pairs = cipher_pairs
        
    def __repr__(self):
        return f"ElGamalCiphertext(cipher_pairs={self.cipher_pairs})"
    
def ElGamal_generate_keys(bit_length: int) -> tuple[dict, dict]:
    p = generate_prime(bit_length, safe=True)
    g = find_primitive_root(p, safe=True)
    
    a = random.randint(2, p - 2)  # Private key
    beta = pow(g, a, p)  # Public key component
    
    private_key = {"p": p, "a": a}
    public_key = {"p": p, "g": g, "beta": beta}
    
    return public_key, private_key

class ElGamalCryptoPublicKey:
    def __init__(self, p: int, g: int, beta: int):
        self.p = p
        self.g = g
        self.beta = beta
    
    def __repr__(self) -> str:
        return f"ElGamalCryptoPublicKey(p={self.p}, g={self.g}, beta={self.beta})"
    
class ElGamalCryptoPrivateKey:
    def __init__(self, p: int, a: int):
        self.p = p
        self.a = a
    
    def __repr__(self) -> str:
        return f"ElGamalCryptoPrivateKey(p={self.p}, a={self.a})"
    
class ElGamalCryptoSystem(CryptoSystem[ElGamalCryptoPublicKey, ElGamalCryptoPrivateKey, ElGamalCiphertext]):
    def generate_keypair(self, bits: int = CRYPTO_BITS):
        public_key_dict, private_key_dict = ElGamal_generate_keys(bits)
        public_key = ElGamalCryptoPublicKey(**public_key_dict)
        private_key = ElGamalCryptoPrivateKey(**private_key_dict)
        return public_key, private_key
    
    def ask_public_key_interactively(self, prompt: str|None = None) -> ElGamalCryptoPublicKey:
        print(prompt or "Enter ElGamal Public Key parameters:")
        p = int(input("Enter prime p: "))
        g = int(input("Enter primitive root g: "))
        beta = int(input("Enter beta: "))
        return ElGamalCryptoPublicKey(p, g, beta)
    
    def ask_plain_text_interactively(self, public_key: ElGamalCryptoPublicKey, prompt: str|None = None) -> Plaintext:
        s = input((prompt or "Enter plaintext") + " (as string): ")
        return Plaintext.from_string(s)
    
    def ask_cipher_text_interactively(self, private_key: ElGamalCryptoPrivateKey, prompt: str|None = None) -> ElGamalCiphertext:
        print(prompt or "Enter ElGamal Ciphertext pairs:")
        N = int(input("Enter number of ciphertext pairs: "))
        cipher_pairs: list[ElGamalCiphertextPair] = []
        for i in range(N):
            y1 = int(input(f"Enter y1 for pair {i+1}: "))
            y2 = int(input(f"Enter y2 for pair {i+1}: "))
            cipher_pairs.append(ElGamalCiphertextPair(y1, y2))
        return ElGamalCiphertext(cipher_pairs)
    
    def encrypt(self, public_key: ElGamalCryptoPublicKey, plain_text: Plaintext) -> ElGamalCiphertext:
        p, g, beta = public_key.p, public_key.g, public_key.beta
        cipher_pairs: list[ElGamalCiphertextPair] = []
        
        for m in plain_text.numbers:
            k = random.randint(2, p - 2)
            y1 = pow(g, k, p)
            y2 = (m * pow(beta, k, p)) % p
            cipher_pairs.append(ElGamalCiphertextPair(y1, y2))
        
        return ElGamalCiphertext(cipher_pairs)
    
    def decrypt(self, private_key: ElGamalCryptoPrivateKey, cipher_text: ElGamalCiphertext) -> Plaintext:
        p, a = private_key.p, private_key.a
        numbers: list[int] = []
        
        for pair in cipher_text.cipher_pairs:
            y1, y2 = pair.y1, pair.y2
            s = pow(y1, a, p)
            s_inv = pow(s, p - 2, p)  # Modular inverse using Fermat's little theorem
            m = (y2 * s_inv) % p
            numbers.append(m)
        
        return Plaintext(numbers)
    
    def str2plaintext(self, public_key: ElGamalCryptoPublicKey, string: str) -> Plaintext:
        return Plaintext.from_string(string)
    
    def plaintext2str(self, private_key: ElGamalCryptoPrivateKey, plain_text: Plaintext) -> str:
        return plain_text.to_string()
    
class ElGamalCryptoSystemTest(CryptoSystemTest[ElGamalCryptoPublicKey, ElGamalCryptoPrivateKey, ElGamalCiphertext]):
    def create_crypto_system(self) -> ElGamalCryptoSystem:
        return ElGamalCryptoSystem()
    
if __name__ == "__main__":
    unittest.main()