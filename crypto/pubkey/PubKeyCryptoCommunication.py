from .CryptoSystem import CryptoSystem
from typing import TypeVar, Generic

CryptoPublicKey = TypeVar("CryptoPublicKey")
CryptoPrivateKey = TypeVar("CryptoPrivateKey")
Ciphertext = TypeVar("Ciphertext")

class PubKeyCryptoCommunication(Generic[CryptoPublicKey, CryptoPrivateKey, Ciphertext]):
    def __init__(
        self,
        crypto_system: CryptoSystem[CryptoPublicKey, CryptoPrivateKey, Ciphertext],
    ):
        self.crypto_system = crypto_system
    
    def run(self):
        print("Generating crypto keypair...")
        K1, K2 = self.crypto_system.generate_keypair()

        myName = input("Your Name: ")
        friendName = input("Your Friend's Name: ")

        print(f"{myName}'s Public Key for Encryption (PKE):")
        print(f"      K1 = {K1}")
        print()

        F1 = self.crypto_system.ask_public_key_interactively(f"Please enter {friendName}'s PKE")

        m = input("Text message to send: ")
        x = self.crypto_system.str2plaintext(K1, m)
        encrypted_x = self.crypto_system.encrypt(F1, x)
        print("SEND:")
        print(f"Send encrypted message: {encrypted_x}")

        print("RECEIVE:")

        encrypted_x = self.crypto_system.ask_cipher_text_interactively(K2, "Enter received encrypted message")
        decrypted_x = self.crypto_system.decrypt(K2, encrypted_x)
        decrypted_m = self.crypto_system.plaintext2str(K2, decrypted_x)

        print()
        print("=" * 79)
        print()

        print(f"OK, message is: {decrypted_m} ; plaintext number(s): {decrypted_x}")

        print()
        print("=" * 79)
        print()
        print("REVEAL PRIVATE KEY:")
        print(f"{myName}'s Private Key for Decryption (pKD):")
        print(f"      K2 = {K2}")