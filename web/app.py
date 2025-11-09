import sys
import os
from flask import Flask, render_template, request, jsonify
import logging

# --- Thêm thư mục `crypto` (ở thư mục cha) vào Python Path ---
# Điều này là BẮT BUỘC để import thư viện crypto của bạn
script_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(parent_dir)

try:
    from crypto.system.CryptoElgamal import (
        ElGamalCryptoSystem, ElGamalCryptoPublicKey, ElGamalCryptoPrivateKey,
        ElGamalCiphertext, ElGamalCiphertextPair
    )
    from crypto.system.SignatureElgamal import (
        ElGamalSignatureSystem, ElGamalSignatureSignerKey, ElGamalSignatureVerifierKey
    )
    from crypto.pubkey.Plaintext import Plaintext
except ImportError as e:
    print(f"LỖI QUAN TRỌNG: Không thể import thư viện crypto.")
    print(f"Đảm bảo bạn có cấu trúc thư mục đúng và các file __init__.py.")
    print(f"Thư mục cha đã được thêm vào path: {parent_dir}")
    print(f"Lỗi: {e}")
    sys.exit(1)

# -------------------------------------------------------------------

app = Flask(__name__)

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# Khởi tạo các hệ thống crypto
# Chúng ta có thể tạo chúng một lần ở đây nếu chúng thread-safe
# Hoặc tạo instance mới trong mỗi_lần_gọi_api để an toàn hơn.
# Tạm thời, chúng ta tạo một lần.
try:
    crypto_system = ElGamalCryptoSystem()
    signature_system = ElGamalSignatureSystem()
except Exception as e:
    app.logger.error(f"Không thể khởi tạo crypto systems: {e}", exc_info=True)
    sys.exit(1)


# === Helper Functions để chuyển đổi Object <-> JSON ===
# (Những hàm này giúp chuyển đổi các đối tượng khóa và bản mã
#  thành JSON và ngược lại, vì chúng chứa các số nguyên lớn)

def serialize_public_key(key: ElGamalCryptoPublicKey) -> dict:
    """Chuyển Public Key thành dict an toàn cho JSON (dùng string)."""
    return {"p": str(key.p), "g": str(key.g), "beta": str(key.beta)}

def serialize_private_key(key: ElGamalCryptoPrivateKey) -> dict:
    """Chuyển Private Key thành dict an toàn cho JSON (dùng string)."""
    return {"p": str(key.p), "a": str(key.a)}

def serialize_verifier_key(key: ElGamalSignatureVerifierKey) -> dict:
    """Chuyển Verifier Key thành dict an toàn cho JSON (dùng string)."""
    return {"p": str(key.p), "g": str(key.g), "beta": str(key.beta)}

def serialize_signer_key(key: ElGamalSignatureSignerKey) -> dict:
    """Chuyển Signer Key thành dict an toàn cho JSON (dùng string)."""
    return {"p": str(key.p), "g": str(key.g), "a": str(key.a)}

def serialize_ciphertext(cipher: ElGamalCiphertext) -> list[dict]:
    """Chuyển Ciphertext (list các cặp) thành list an toàn cho JSON."""
    return [{"y1": str(pair.y1), "y2": str(pair.y2)} for pair in cipher.cipher_pairs]

def deserialize_public_key(data: dict) -> ElGamalCryptoPublicKey:
    """Tạo lại Public Key từ dict (chuyển string về int)."""
    return ElGamalCryptoPublicKey(p=int(data['p']), g=int(data['g']), beta=int(data['beta']))

def deserialize_private_key(data: dict) -> ElGamalCryptoPrivateKey:
    """Tạo lại Private Key từ dict (chuyển string về int)."""
    return ElGamalCryptoPrivateKey(p=int(data['p']), a=int(data['a']))

def deserialize_verifier_key(data: dict) -> ElGamalSignatureVerifierKey:
    """Tạo lại Verifier Key từ dict (chuyển string về int)."""
    return ElGamalSignatureVerifierKey(p=int(data['p']), g=int(data['g']), beta=int(data['beta']))

def deserialize_signer_key(data: dict) -> ElGamalSignatureSignerKey:
    """Tạo lại Signer Key từ dict (chuyển string về int)."""
    return ElGamalSignatureSignerKey(p=int(data['p']), g=int(data['g']), a=int(data['a']))

def deserialize_ciphertext(data: list[dict]) -> ElGamalCiphertext:
    """Tạo lại Ciphertext từ list dict (chuyển string về int)."""
    pairs = [ElGamalCiphertextPair(y1=int(p['y1']), y2=int(p['y2'])) for p in data]
    return ElGamalCiphertext(cipher_pairs=pairs)

# === Routes ===

@app.route('/')
def index():
    """Phục vụ file HTML giao diện chính."""
    return render_template('index.html')

# === API Endpoints ===

@app.route('/api/generate-keys', methods=['POST'])
def generate_keys():
    """
    API endpoint để tạo tất cả các cặp khóa (Mã hóa và Chữ ký).
    """
    app.logger.info("Yêu cầu /api/generate-keys")
    try:
        # 1. Tạo khóa mã hóa
        pub_key, priv_key = crypto_system.generate_keypair()
        
        # 2. Tạo khóa chữ ký
        signer_key, verifier_key = signature_system.generate_keypair()
        
        app.logger.info("Tạo khóa thành công.")
        return jsonify({
            "success": True,
            "encryptionPublicKey": serialize_public_key(pub_key),
            "encryptionPrivateKey": serialize_private_key(priv_key),
            "signatureSignerKey": serialize_signer_key(signer_key),
            "signatureVerifierKey": serialize_verifier_key(verifier_key),
        })
    except Exception as e:
        app.logger.error(f"Lỗi khi tạo khóa: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/encrypt', methods=['POST'])
def encrypt_message():
    """
    API endpoint để mã hóa tin nhắn.
    Nhận: { "message": "...", "key": { ...public_key... } }
    """
    app.logger.info("Yêu cầu /api/encrypt")
    try:
        data = request.json
        message_str = data['message']
        key_dict = data['key']
        
        public_key = deserialize_public_key(key_dict)
        # Chuyển chuỗi đầu vào thành đối tượng Plaintext (list các số)
        plain_text = Plaintext.from_string(message_str)
        
        cipher_text_obj = crypto_system.encrypt(public_key, plain_text)
        
        app.logger.info("Mã hóa thành công.")
        return jsonify({
            "success": True,
            "ciphertext": serialize_ciphertext(cipher_text_obj)
        })
    except Exception as e:
        app.logger.error(f"Lỗi khi mã hóa: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/decrypt', methods=['POST'])
def decrypt_message():
    """
    API endpoint để giải mã tin nhắn.
    Nhận: { "ciphertext": [ ... ], "key": { ...private_key... } }
    """
    app.logger.info("Yêu cầu /api/decrypt")
    try:
        data = request.json
        cipher_list = data['ciphertext']
        key_dict = data['key']
        
        private_key = deserialize_private_key(key_dict)
        cipher_text_obj = deserialize_ciphertext(cipher_list)
        
        decrypted_plaintext = crypto_system.decrypt(private_key, cipher_text_obj)
        # Chuyển đối tượng Plaintext (list các số) về chuỗi gốc
        decrypted_message = decrypted_plaintext.to_string()
        
        app.logger.info("Giải mã thành công.")
        return jsonify({
            "success": True,
            "message": decrypted_message
        })
    except Exception as e:
        # Lỗi giải mã (ví dụ: sai khóa) thường gây ra lỗi toán học hoặc decode
        app.logger.warning(f"Lỗi khi giải mã: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Không thể giải mã. Sai khóa hoặc dữ liệu hỏng."}), 400

@app.route('/api/sign', methods=['POST'])
def sign_message():
    """
    API endpoint để ký tin nhắn.
    Nhận: { "message": "...", "key": { ...signer_key... } }
    """
    app.logger.info("Yêu cầu /api/sign")
    try:
        data = request.json
        message_str = data['message']
        key_dict = data['key']

        signer_key = deserialize_signer_key(key_dict)
        plain_text = Plaintext.from_string(message_str)
        
        signature_obj = signature_system.sign(signer_key, plain_text)
        
        # Chữ ký (Plaintext) được trả về dưới dạng list các con số (dạng string)
        app.logger.info("Ký thành công.")
        return jsonify({
            "success": True,
            "signature": [str(num) for num in signature_obj.numbers]
        })
    except Exception as e:
        app.logger.error(f"Lỗi khi ký: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/verify', methods=['POST'])
def verify_signature():
    """
    API endpoint để xác thực chữ ký.
    Nhận: { "message": "...", "signature": [ ... ], "key": { ...verifier_key... } }
    """
    app.logger.info("Yêu cầu /api/verify")
    try:
        data = request.json
        message_str = data['message']
        signature_list = data['signature'] # List of strings
        key_dict = data['key']
        
        verifier_key = deserialize_verifier_key(key_dict)
        
        # Chuyển message string và signature list về Plaintext object
        message_plaintext = Plaintext.from_string(message_str)
        signature_plaintext = Plaintext([int(num) for num in signature_list])
        
        is_valid = signature_system.verify(verifier_key, message_plaintext, signature_plaintext)
        
        app.logger.info(f"Xác thực hoàn tất. Hợp lệ: {is_valid}")
        return jsonify({
            "success": True,
            "isValid": is_valid
        })
    except Exception as e:
        # Lỗi (ví dụ: chữ ký sai định dạng) có thể xảy ra ở đây
        app.logger.warning(f"Lỗi khi xác thực: {e}", exc_info=True)
        # Trả về isValid: False nếu có lỗi trong quá trình xác thực
        return jsonify({"success": True, "isValid": False, "error": "Lỗi khi xử lý xác thực."})

if __name__ == '__main__':
    """Chạy app ở chế độ debug."""
    app.run(debug=True, port=5000)