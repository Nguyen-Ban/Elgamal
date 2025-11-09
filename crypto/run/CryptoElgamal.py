from ..pubkey import PubKeyCryptoCommunication
from ..system import ElGamalCryptoSystem

def run_CryptoElGamal():
    driver = PubKeyCryptoCommunication(ElGamalCryptoSystem())
    driver.run()