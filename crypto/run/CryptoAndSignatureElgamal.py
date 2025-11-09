from ..pubkey import PubKeyCryptoSignatureCommunication
from ..pubkey.CryptoAndSignatureSystemTest import CryptoSystemAndSignatureSystemTest

from ..system import ElGamalCryptoSystem, ElGamalSignatureSystem, ElGamalCryptoPublicKey, ElGamalCryptoPrivateKey, ElGamalCiphertext, ElGamalSignatureSignerKey, ElGamalSignatureVerifierKey

class CryptoAndSignatureElgamal(CryptoSystemAndSignatureSystemTest[ElGamalCryptoPublicKey, ElGamalCryptoPrivateKey, ElGamalCiphertext, ElGamalSignatureSignerKey, ElGamalSignatureVerifierKey]):
    def create_crypto_system(self) -> ElGamalCryptoSystem:
        return ElGamalCryptoSystem()
    
    def create_signature_system(self) -> ElGamalSignatureSystem:
        return ElGamalSignatureSystem()
    
def run_CryptoAndSignatureElGamal():
    driver = PubKeyCryptoSignatureCommunication(ElGamalCryptoSystem(), ElGamalSignatureSystem())
    driver.run()