from .CryptoSystem import CryptoSystem
from .SignatureSystem import SignatureSystem
from typing import TypeVar, Generic

CryptoPublicKey = TypeVar("CryptoPublicKey")
CryptoPrivateKey = TypeVar("CryptoPrivateKey")
Ciphertext = TypeVar("Ciphertext")
SignatureSignerKey = TypeVar("SignatureSignerKey")
SignatureVerifierKey = TypeVar("SignatureVerifierKey")

class PubKeyCryptoSignatureCommunication(Generic[CryptoPublicKey, CryptoPrivateKey, Ciphertext, SignatureSignerKey, SignatureVerifierKey]):
    def __init__(
        self,
        crypto_system: CryptoSystem[CryptoPublicKey, CryptoPrivateKey, Ciphertext],
        signature_system: SignatureSystem[SignatureSignerKey, SignatureVerifierKey],
    ):
        self.crypto_system = crypto_system
        self.signature_system = signature_system
    
    def run(self):
        print("Generating crypto keypair...")
        K1, K2 = self.crypto_system.generate_keypair()
        print("Generating signature keypair...")
        k1, k2 = self.signature_system.generate_keypair()

        myName = input("Your Name: ")
        friendName = input("Your Friend's Name: ")

        print(f"{myName}'s Public Key for Encryption (PKE):")
        print(f"      K1 = {K1}")
        print(f"{myName}'s Public Key for Verification (PKV):")
        print(f"      k2 = {k2}")
        print()

        F1 = self.crypto_system.ask_public_key_interactively(f"Please enter {friendName}'s PKE")

        f2 = self.signature_system.ask_verification_key_interactively(f"Please enter {friendName}'s PKV")

        x = input("Text message to send: ")
        cx = self.crypto_system.str2plaintext(K1, x)
        sx = self.signature_system.str2plaintext_signer(k1, x)

        # print("Signing")
        signature_x = self.signature_system.sign(k1, sx)

        # print("Encrypting")
        encrypted_x = self.crypto_system.encrypt(F1, cx)
        encrypted_signature_x = self.crypto_system.encrypt(F1, signature_x)

        print("SEND:")
        print(f"Send encrypted message: {encrypted_x}")
        print(f"Send encrypted signature: {encrypted_signature_x}")

        print("RECEIVE:")

        encrypted_x = self.crypto_system.ask_cipher_text_interactively(K2, "Enter received encrypted message")
        encrypted_signature_x = self.crypto_system.ask_cipher_text_interactively(K2, "Enter received encrypted signature")
        decrypted_x = self.crypto_system.decrypt(K2, encrypted_x)
        decrypted_signature_x = self.crypto_system.decrypt(K2, encrypted_signature_x)
        SUCCESS = self.signature_system.verify(f2, decrypted_x, decrypted_signature_x)

        print()
        print("=" * 79)
        print()
        if not SUCCESS:
            print(f"WRONG, message not authentic.")
            print(f"Message is: {self.crypto_system.plaintext2str(K2, decrypted_x)} ; plaintext number(s): {decrypted_x}")
        else:
            print(f"OK, message is: {self.crypto_system.plaintext2str(K2, decrypted_x)} ; plaintext number(s): {decrypted_x}")
        
        print()
        print("=" * 79)
        print()
        print("REVEAL PRIVATE/SIGNER KEYS:")
        print(f"{myName}'s Private Key for Decryption (pKD):")
        print(f"      K2 = {K2}")
        print(f"{myName}'s Private Key for Signing (pKS):")
        print(f"      k1 = {k1}")
        print()
        print("=" * 79)
        print()
        print("REVEAL SIGNATURE(S):")
        print(f"{signature_x}")
        print()
        
if __name__ == "__main__":
    print("This is a module containing PubKeyCryptoSignatureCommunication class.")