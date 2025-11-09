import unittest
from .CryptoSystem import CryptoSystem
from .SignatureSystem import SignatureSystem
from typing import Generic, TypeVar

CryptoPublicKey = TypeVar("CryptoPublicKey")
CryptoPrivateKey = TypeVar("CryptoPrivateKey")
Ciphertext = TypeVar("Ciphertext")
SignatureSignerKey = TypeVar("SignatureSignerKey")
SignatureVerifierKey = TypeVar("SignatureVerifierKey")

class CryptoSystemAndSignatureSystemTest(unittest.TestCase, Generic[CryptoPublicKey, CryptoPrivateKey, Ciphertext, SignatureSignerKey, SignatureVerifierKey]):
    def create_crypto_system(self) -> CryptoSystem[CryptoPublicKey, CryptoPrivateKey, Ciphertext]:
        raise NotImplementedError
    
    def create_signature_system(self) -> SignatureSystem[SignatureSignerKey, SignatureVerifierKey]:
        raise NotImplementedError
    
    def setUp(self):
        try:
            self.crypto_system = self.create_crypto_system()
            self.signature_system = self.create_signature_system()
        except NotImplementedError:
            self.skipTest("create_crypto_system() or create_signature_system() is not implemented")

    def test_all(self):
        K1, K2 = self.crypto_system.generate_keypair()
        k1, k2 = self.signature_system.generate_keypair()

        x = "IT" # "ITCOULDBEANYTHINGWITHONLYTWENTYSIXLETTERSANDTHEFIRSTLETTERMUSTNOTBEA"

        signature_x = self.signature_system.sign(k1, self.signature_system.str2plaintext_signer(k1, x))

        encrypted_x = self.crypto_system.encrypt(K1, self.crypto_system.str2plaintext(K1, x))
        encrypted_signature_x = self.crypto_system.encrypt(K1, signature_x)

        decrypted_x = self.crypto_system.decrypt(K2, encrypted_x)
        decrypted_signature_x = self.crypto_system.decrypt(K2, encrypted_signature_x)

        self.assertTrue(self.signature_system.verify(k2, decrypted_x, decrypted_signature_x))
        self.assertEqual(self.crypto_system.str2plaintext(K1, x), decrypted_x)
        self.assertEqual(x.upper(), self.crypto_system.plaintext2str(K2, decrypted_x))

    def test_all_2(self):
        # print("TESTING...")
        x = "oq" # "HelloABCDEFGHIJKLMNOpqrstuvwxyz"

        # print("Generating crypto keypair...")
        K1, K2 = self.crypto_system.generate_keypair()
        # print("Generating signature keypair...")
        k1, k2 = self.signature_system.generate_keypair()

        # print("Signing")
        signature_x = self.signature_system.sign(k1, self.signature_system.str2plaintext_signer(k1, x))

        # print("Encrypting")
        encrypted_x = self.crypto_system.encrypt(K1, self.crypto_system.str2plaintext(K1, x))
        encrypted_signature_x = self.crypto_system.encrypt(K1, signature_x)

        # print("Decrypting")
        decrypted_x = self.crypto_system.decrypt(K2, encrypted_x)
        decrypted_signature_x = self.crypto_system.decrypt(K2, encrypted_signature_x)

        # print("Verifying")
        self.assertTrue(self.signature_system.verify(k2, decrypted_x, decrypted_signature_x))
        self.assertEqual(self.crypto_system.str2plaintext(K1, x), decrypted_x)
        self.assertEqual(x.upper(), self.crypto_system.plaintext2str(K2, decrypted_x))
        
if __name__ == "__main__":
    unittest.main()