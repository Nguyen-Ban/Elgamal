from .Plaintext import Plaintext, Plaintext as Signature
import unittest
from typing import Generic, TypeVar

SignatureSignerKey = TypeVar("SignatureSignerKey")
SignatureVerifierKey = TypeVar("SignatureVerifierKey")

class SignatureSystem(Generic[SignatureSignerKey, SignatureVerifierKey]):
    def generate_keypair(self) -> tuple[SignatureSignerKey, SignatureVerifierKey]:
        raise NotImplementedError
    
    def ask_verification_key_interactively(self, prompt: str|None = None) -> SignatureVerifierKey:
        raise NotImplementedError
    
    def sign(self, signer_key: SignatureSignerKey, plain_text: Plaintext) -> Signature:
        raise NotImplementedError
    
    def verify(self, verifier_key: SignatureVerifierKey, plain_text: Plaintext, signature: Signature) -> bool:
        raise NotImplementedError
    
    def str2plaintext_signer(self, signer_key: SignatureSignerKey, string: str) -> Plaintext:
        raise NotImplementedError
    
    def str2plaintext_verifier(self, verifier_key: SignatureVerifierKey, string: str) -> Plaintext:
        raise NotImplementedError

class SignatureSystemTest(unittest.TestCase, Generic[SignatureSignerKey, SignatureVerifierKey]):
    def create_signature_system(self) -> SignatureSystem[SignatureSignerKey, SignatureVerifierKey]:
        raise NotImplementedError
    
    def setUp(self):
        try:
            self.signature_system = self.create_signature_system()
        except NotImplementedError:
            self.skipTest("create_signature_system() is not implemented")

    def test_sign(self):
        k1, k2 = self.signature_system.generate_keypair()
        x = "HE"
        signature_x = self.signature_system.sign(k1, self.signature_system.str2plaintext_signer(k1, x))
        self.assertTrue(self.signature_system.verify(k2, self.signature_system.str2plaintext_verifier(k2, x), signature_x))