from . import *
from typing import Callable
CHOICES: dict[str, Callable[[], None]] = {
    "1": run_CryptoElGamal,
    "2": run_CryptoAndSignatureElGamal,
}

if __name__ == "__main__":
    print("Select the operation to run:")
    print("1. ElGamal Public Key Cryptography")
    print("2. ElGamal Public Key Cryptography with Digital Signatures")
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice in CHOICES:
        CHOICES[choice]()
    else:
        print("Invalid choice. Please select 1 or 2.")