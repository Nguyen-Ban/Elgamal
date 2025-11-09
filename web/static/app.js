// Chờ DOM tải xong
document.addEventListener('DOMContentLoaded', () => {

    // === Lấy các phần tử DOM ===
    const btnGenerateKeys = document.getElementById('btn-generate-keys');
    const keyDisplayArea = document.getElementById('key-display-area');
    
    // Khóa mã hóa
    const keyEncryptPub = document.getElementById('key-encrypt-pub');
    const keyEncryptPriv = document.getElementById('key-encrypt-priv');
    // Khóa ký
    const keySignVerify = document.getElementById('key-sign-verify');
    const keySignSigner = document.getElementById('key-sign-signer');

    // Mã hóa
    const btnEncrypt = document.getElementById('btn-encrypt');
    const encryptKey = document.getElementById('encrypt-key');
    const encryptMessage = document.getElementById('encrypt-message');
    const encryptResult = document.getElementById('encrypt-result');

    // Giải mã
    const btnDecrypt = document.getElementById('btn-decrypt');
    const decryptKey = document.getElementById('decrypt-key');
    const decryptCiphertext = document.getElementById('decrypt-ciphertext');
    const decryptResult = document.getElementById('decrypt-result');

    // Ký
    const btnSign = document.getElementById('btn-sign');
    const signKey = document.getElementById('sign-key');
    const signMessage = document.getElementById('sign-message');
    const signResult = document.getElementById('sign-result');

    // Xác thực
    const btnVerify = document.getElementById('btn-verify');
    const verifyKey = document.getElementById('verify-key');
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
     * Helper kiểm tra JSON hợp lệ
     * @param {string} str - Chuỗi JSON
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
    btnGenerateKeys.addEventListener('click', async () => {
        const data = await apiCall('/api/generate-keys', {});
        
        if (data) {
            // Hiển thị khóa (đã được định dạng JSON đẹp)
            keyEncryptPub.value = JSON.stringify(data.encryptionPublicKey, null, 2);
            keyEncryptPriv.value = JSON.stringify(data.encryptionPrivateKey, null, 2);
            keySignVerify.value = JSON.stringify(data.signatureVerifierKey, null, 2);
            keySignSigner.value = JSON.stringify(data.signatureSignerKey, null, 2);
            
            keyDisplayArea.classList.remove('hidden');
            showNotification('Tạo khóa thành công!', 'success');

            // Tự động điền khóa vào các trường bên dưới
            encryptKey.value = keyEncryptPub.value;
            decryptKey.value = keyEncryptPriv.value;
            signKey.value = keySignSigner.value;
            verifyKey.value = keySignVerify.value;
        }
    });

    // 2. Mã Hóa
    btnEncrypt.addEventListener('click', async () => {
        const key = parseJSON(encryptKey.value, 'Khóa Mã Hóa');
        if (!key) return;

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
        const key = parseJSON(decryptKey.value, 'Khóa Giải Mã');
        if (!key) return;

        const ciphertext = parseJSON(decryptCiphertext.value, 'Bản Mã');
        if (!ciphertext) return;

        const data = await apiCall('/api/decrypt', { ciphertext, key });
        if (data) {
            decryptResult.value = data.message;
            showNotification('Giải mã thành công!', 'success');
        } else {
            // apiCall đã hiển thị lỗi, nhưng chúng ta có thể xóa kết quả
            decryptResult.value = 'GIẢI MÃ THẤT BẠI';
        }
    });

    // 4. Ký
    btnSign.addEventListener('click', async () => {
        const key = parseJSON(signKey.value, 'Khóa Ký');
        if (!key) return;
        
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
        const key = parseJSON(verifyKey.value, 'Khóa Xác Thực');
        if (!key) return;
        
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