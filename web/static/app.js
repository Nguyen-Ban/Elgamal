// Chờ DOM tải xong
document.addEventListener('DOMContentLoaded', () => {

    // === Lấy các phần tử DOM ===
    const btnGenerateEncryption = document.getElementById('btn-generate-encryption');
    const btnGenerateSignature = document.getElementById('btn-generate-signature');
    const keyDisplayArea = document.getElementById('key-display-area');
    
    // Phần 1: Hiển thị khóa
    const keyEncryptPubP = document.getElementById('key-encrypt-pub-p');
    const keyEncryptPubG = document.getElementById('key-encrypt-pub-g');
    const keyEncryptPubBeta = document.getElementById('key-encrypt-pub-beta');
    const keyEncryptPrivP = document.getElementById('key-encrypt-priv-p');
    const keyEncryptPrivA = document.getElementById('key-encrypt-priv-a');
    const keyVerifyP = document.getElementById('key-verify-p');
    const keyVerifyG = document.getElementById('key-verify-g');
    const keyVerifyBeta = document.getElementById('key-verify-beta');
    const keySignP = document.getElementById('key-sign-p');
    const keySignG = document.getElementById('key-sign-g');
    const keySignA = document.getElementById('key-sign-a');

    // Phần 2: Mã hóa
    const btnEncrypt = document.getElementById('btn-encrypt');
    const encryptKeyP = document.getElementById('encrypt-key-p');
    const encryptKeyG = document.getElementById('encrypt-key-g');
    const encryptKeyBeta = document.getElementById('encrypt-key-beta');
    const encryptMessage = document.getElementById('encrypt-message');
    const encryptResult = document.getElementById('encrypt-result');

    // Phần 2: Giải mã
    const btnDecrypt = document.getElementById('btn-decrypt');
    const decryptKeyP = document.getElementById('decrypt-key-p');
    const decryptKeyA = document.getElementById('decrypt-key-a');
    const decryptCiphertext = document.getElementById('decrypt-ciphertext');
    const decryptResult = document.getElementById('decrypt-result');

    // Phần 3: Ký
    const btnSign = document.getElementById('btn-sign');
    const signKeyP = document.getElementById('sign-key-p');
    const signKeyG = document.getElementById('sign-key-g');
    const signKeyA = document.getElementById('sign-key-a');
    const signMessage = document.getElementById('sign-message');
    const signResult = document.getElementById('sign-result');

    // Phần 3: Xác thực
    const btnVerify = document.getElementById('btn-verify');
    const verifyKeyP = document.getElementById('verify-key-p');
    const verifyKeyG = document.getElementById('verify-key-g');
    const verifyKeyBeta = document.getElementById('verify-key-beta');
    const verifyMessage = document.getElementById('verify-message');
    const verifySignature = document.getElementById('verify-signature');

    // Tiện ích
    const loadingSpinner = document.getElementById('loading-spinner');
    const notificationBox = document.getElementById('notification-box');
    const notificationMessage = document.getElementById('notification-message');

    // === Helper Functions ===

    /**
     * Hiển thị loading spinner
     * @param {boolean} show 
     */
    function showLoading(show) {
        loadingSpinner.classList.toggle('hidden', !show);
    }

    /**
     * Hiển thị thông báo (thành công, lỗi, thông tin)
     * @param {string} message - Nội dung thông báo
     * @param {'success' | 'error' | 'info'} type - Loại thông báo
     */
    function showNotification(message, type = 'info') {
        notificationMessage.textContent = message;
        
        // Reset classes
        notificationBox.className = 'p-4 rounded-md mb-6 transition-all duration-300';
        
        if (type === 'success') {
            notificationBox.classList.add('bg-green-800', 'text-green-100');
        } else if (type === 'error') {
            notificationBox.classList.add('bg-red-800', 'text-red-100');
        } else {
            notificationBox.classList.add('bg-blue-800', 'text-blue-100');
        }

        notificationBox.classList.remove('hidden');

        // Tự động ẩn sau 5 giây
        setTimeout(() => {
            notificationBox.classList.add('hidden');
        }, 5000);
    }

    /**
     * Helper gọi API (fetch)
     * @param {string} endpoint - API endpoint (ví dụ: '/api/generate-keys')
     * @param {object} body - Nội dung JSON để gửi
     * @returns {Promise<object>} - Dữ liệu JSON trả về
     */
    async function apiCall(endpoint, body) {
        showLoading(true);
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(body),
            });

            const data = await response.json();

            if (!response.ok) {
                // Lỗi từ server (4xx, 5xx)
                throw new Error(data.error || 'Có lỗi xảy ra từ server');
            }
            
            if (data.success === false) {
                // Lỗi logic từ ứng dụng
                throw new Error(data.error || 'Yêu cầu không thành công');
            }
            
            return data; // Thành công
        } catch (error) {
            console.error(`Lỗi khi gọi ${endpoint}:`, error);
            showNotification(error.message, 'error');
            return null; // Trả về null nếu lỗi
        } finally {
            showLoading(false);
        }
    }

    /**
     * Helper kiểm tra JSON hợp lệ (cho bản mã / chữ ký)
     * @param {string} str - Chuỗi JSON
     * @param {string} fieldName - Tên trường để báo lỗi
     * @returns {object | null} - Object nếu hợp lệ, null nếu không
     */
    function parseJSON(str, fieldName) {
        try {
            const obj = JSON.parse(str);
            return obj;
        } catch (e) {
            showNotification(`Lỗi: Dữ liệu JSON không hợp lệ trong trường "${fieldName}".`, 'error');
            return null;
        }
    }


    // === Gắn Sự Kiện ===

    // 1. Tạo Khóa
    btnGenerateEncryption.addEventListener('click', async () => {
        const data = await apiCall('/api/generate-encryption-keys', {});
        
        if (data) {
            // Hiển thị khóa (vào các ô input riêng lẻ)
            
            // Khóa mã hóa (Public)
            keyEncryptPubP.value = data.encryptionPublicKey.p;
            keyEncryptPubG.value = data.encryptionPublicKey.g;
            keyEncryptPubBeta.value = data.encryptionPublicKey.beta;
            
            // Khóa giải mã (Private)
            keyEncryptPrivP.value = data.encryptionPrivateKey.p;
            keyEncryptPrivA.value = data.encryptionPrivateKey.a;
            
            keyDisplayArea.classList.remove('hidden');
            showNotification('Tạo khóa thành công!', 'success');

            // Tự động điền khóa vào các trường bên dưới
            // Mã hóa
            encryptKeyP.value = data.encryptionPublicKey.p;
            encryptKeyG.value = data.encryptionPublicKey.g;
            encryptKeyBeta.value = data.encryptionPublicKey.beta;
            
            // Giải mã
            decryptKeyP.value = data.encryptionPrivateKey.p;
            decryptKeyA.value = data.encryptionPrivateKey.a;
        }
    });

    btnGenerateSignature.addEventListener('click', async () => {
        const data = await apiCall('/api/generate-signature-keys', {});
        if (data) {
            keyVerifyP.value = data.signatureVerifierKey.p;
            keyVerifyG.value = data.signatureVerifierKey.g;
            keyVerifyBeta.value = data.signatureVerifierKey.beta;

            keySignP.value = data.signatureSignerKey.p;
            keySignG.value = data.signatureSignerKey.g;
            keySignA.value = data.signatureSignerKey.a;
            keyDisplayArea.classList.remove('hidden');
            showNotification('Tạo khóa chữ ký thành công!', 'success');

            signKeyP.value = data.signatureSignerKey.p;
            signKeyG.value = data.signatureSignerKey.g;
            signKeyA.value = data.signatureSignerKey.a;
            verifyKeyP.value = data.signatureVerifierKey.p;
            verifyKeyG.value = data.signatureVerifierKey.g;
            verifyKeyBeta.value = data.signatureVerifierKey.beta;
        }
    });

    // 2. Mã Hóa
    btnEncrypt.addEventListener('click', async () => {
        const key = {
            p: encryptKeyP.value,
            g: encryptKeyG.value,
            beta: encryptKeyBeta.value
        };
        
        if (!key.p || !key.g || !key.beta) {
            showNotification('Vui lòng nhập đủ (p, g, beta) của Khóa Công Khai.', 'error');
            return;
        }

        const message = encryptMessage.value;
        if (!message) {
            showNotification('Vui lòng nhập tin nhắn để mã hóa.', 'error');
            return;
        }

        const data = await apiCall('/api/encrypt', { message, key });
        if (data) {
            encryptResult.value = JSON.stringify(data.ciphertext, null, 2);
            showNotification('Mã hóa thành công.', 'success');
            // Tự động điền bản mã vào trường giải mã
            decryptCiphertext.value = encryptResult.value;
        }
    });

    // 3. Giải Mã
    btnDecrypt.addEventListener('click', async () => {
        const key = {
            p: decryptKeyP.value,
            a: decryptKeyA.value
        };
        
        if (!key.p || !key.a) {
            showNotification('Vui lòng nhập đủ (p, a) của Khóa Bí Mật.', 'error');
            return;
        }

        const ciphertext = parseJSON(decryptCiphertext.value, 'Bản Mã');
        if (!ciphertext) return;

        const data = await apiCall('/api/decrypt', { ciphertext, key });
        if (data) {
            decryptResult.value = data.message;
            showNotification('Giải mã thành công!', 'success');
        } else {
            decryptResult.value = 'GIẢI MÃ THẤT BẠI';
        }
    });

    // 4. Ký
    btnSign.addEventListener('click', async () => {
        const key = {
            p: signKeyP.value,
            g: signKeyG.value,
            a: signKeyA.value
        };

        if (!key.p || !key.g || !key.a) {
            showNotification('Vui lòng nhập đủ (p, g, a) của Khóa Ký.', 'error');
            return;
        }
        
        const message = signMessage.value;
        if (!message) {
            showNotification('Vui lòng nhập tin nhắn để ký.', 'error');
            return;
        }

        const data = await apiCall('/api/sign', { message, key });
        if (data) {
            signResult.value = JSON.stringify(data.signature, null, 2);
            showNotification('Tạo chữ ký thành công.', 'success');
            
            // Tự động điền tin nhắn và chữ ký vào trường xác thực
            verifyMessage.value = message;
            verifySignature.value = signResult.value;
        }
    });

    // 5. Xác thực
    btnVerify.addEventListener('click', async () => {
        const key = {
            p: verifyKeyP.value,
            g: verifyKeyG.value,
            beta: verifyKeyBeta.value
        };
        
        if (!key.p || !key.g || !key.beta) {
            showNotification('Vui lòng nhập đủ (p, g, beta) của Khóa Xác Thực.', 'error');
            return;
        }
        
        const message = verifyMessage.value;
        if (!message) {
            showNotification('Vui lòng nhập tin nhắn gốc.', 'error');
            return;
        }

        const signature = parseJSON(verifySignature.value, 'Chữ Ký');
        if (!signature) return;

        const data = await apiCall('/api/verify', { message, signature, key });
        if (data) {
            if (data.isValid) {
                showNotification('XÁC THỰC THÀNH CÔNG: Chữ ký hợp lệ!', 'success');
            } else {
                showNotification('XÁC THỰC THẤT BẠI: Chữ ký KHÔNG hợp lệ!', 'error');
            }
        }
    });

});