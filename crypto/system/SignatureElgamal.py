from sympy import gcd
from ..pubkey import SignatureSystem, Plaintext, SignatureSystemTest
from .CryptoElgamal import ElGamal_generate_keys
import random

SIGNATURE_BITS = 512

class ElGamalSignatureSignerKey:
    def __init__(self, p: int, g: int, a: int):
        self.p = p
        self.g = g 
        self.a = a
        
    def __repr__(self) -> str:
        return f"ElGamalSignatureSignerKey(p={self.p}, g={self.g}, a={self.a})"
    
class ElGamalSignatureVerifierKey:
    def __init__(self, p: int, g: int, beta: int):
        self.p = p
        self.g = g
        self.beta = beta
        
    def __repr__(self) -> str:
        return f"ElGamalSignatureVerifierKey(p={self.p}, g={self.g}, beta={self.beta})"
    
class ElGamalSignatureSystem(SignatureSystem[ElGamalSignatureVerifierKey, ElGamalSignatureSignerKey]):
    def generate_keypair(self, bits: int = SIGNATURE_BITS) -> tuple[ElGamalSignatureSignerKey, ElGamalSignatureVerifierKey]:
        public_key_dict, private_key_dict = ElGamal_generate_keys(bits)
        verifier_key = ElGamalSignatureVerifierKey(**public_key_dict)
        signer_key = ElGamalSignatureSignerKey(
            p=private_key_dict["p"],
            g=public_key_dict["g"],
            a=private_key_dict["a"]
        )
        return signer_key, verifier_key
    
    def ask_verification_key_interactively(self, prompt: str|None = None) -> ElGamalSignatureVerifierKey:
        print(prompt or "Enter Verification Key:")
        p = int(input("Enter prime p: "))
        g = int(input("Enter primitive root g: "))
        beta = int(input("Enter beta: "))
        return ElGamalSignatureVerifierKey(p, g, beta)
    
    def sign(self, signer_key: ElGamalSignatureSignerKey, plain_text: Plaintext) -> Plaintext:
        p = signer_key.p
        g = signer_key.g
        a = signer_key.a
        
        signature_numbers = []
        for m in plain_text.numbers:
            while True:
                k = random.randint(2, p - 2)
                if gcd(k, p - 1) == 1:
                    break
            gamma = pow(g, k, p)
            k_inv = pow(k, -1, p - 1)
            delta = (k_inv * (m - a * gamma)) % (p - 1)
            signature_numbers.append(gamma)
            signature_numbers.append(delta)
        return Plaintext(signature_numbers)
    
    def verify(self, verifier_key: ElGamalSignatureVerifierKey, plain_text: Plaintext, signature: Plaintext) -> bool:
        p = verifier_key.p
        g = verifier_key.g
        beta = verifier_key.beta
        
        sig_nums = signature.numbers
        if len(sig_nums) != 2 * len(plain_text.numbers):
            return False
        for i, m in enumerate(plain_text.numbers):
            gamma, delta = sig_nums[2 * i], sig_nums[2 * i + 1]
            left = (pow(beta, gamma, p) * pow(gamma, delta, p)) % p
            right = pow(g, m, p)
            if left != right:
                return False
        return True
    
    def str2plaintext_signer(self, signer_key: ElGamalSignatureSignerKey, string: str) -> Plaintext:
        plain_text = Plaintext.from_string(string)
        return plain_text
    
    def str2plaintext_verifier(self, verifier_key: ElGamalSignatureVerifierKey, string: str) -> Plaintext:
        plain_text = Plaintext.from_string(string)
        return plain_text
    
class ElGamalSignatureSystemTest(SignatureSystemTest[ElGamalSignatureSignerKey, ElGamalSignatureVerifierKey]):
    def create_signature_system(self) -> SignatureSystem[ElGamalSignatureSignerKey, ElGamalSignatureVerifierKey]:
        return ElGamalSignatureSystem()
if __name__ == "__main__":
    import unittest
    unittest.main()