// Chờ DOM tải xong
document.addEventListener('DOMContentLoaded', () => {

    // === Lấy các phần tử DOM ===
    const btnGenerateEncryption = document.getElementById('btn-generate-encryption');
    const btnGenerateSignature = document.getElementById('btn-generate-signature');
    const keyDisplayArea = document.getElementById('key-display-area');
    const bitsEncryptionInput = document.getElementById('bits-encryption');
    const bitsSignatureInput = document.getElementById('bits-signature');
    
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
    // const encryptResult = document.getElementById('encrypt-result');
    const encryptResultY1 = document.getElementById('encrypt-result-y1');
    const encryptResultY2 = document.getElementById('encrypt-result-y2');

    // Phần 2: Giải mã
    const btnDecrypt = document.getElementById('btn-decrypt');
    const decryptKeyP = document.getElementById('decrypt-key-p');
    const decryptKeyA = document.getElementById('decrypt-key-a');
    // const decryptCiphertext = document.getElementById('decrypt-ciphertext');
    const decryptCiphertextY1 = document.getElementById('decrypt-ciphertext-y1');
    const decryptCiphertextY2 = document.getElementById('decrypt-ciphertext-y2');
    const decryptResult = document.getElementById('decrypt-result');

    // Phần 3: Ký
    const btnSign = document.getElementById('btn-sign');
    const signKeyP = document.getElementById('sign-key-p');
    const signKeyG = document.getElementById('sign-key-g');
    const signKeyA = document.getElementById('sign-key-a');
    const signMessage = document.getElementById('sign-message');
    const signResultGamma = document.getElementById('sign-result-gamma');
    const signResultDelta = document.getElementById('sign-result-delta');

    // Phần 3: Xác thực
    const btnVerify = document.getElementById('btn-verify');
    const verifyKeyP = document.getElementById('verify-key-p');
    const verifyKeyG = document.getElementById('verify-key-g');
    const verifyKeyBeta = document.getElementById('verify-key-beta');
    const verifyMessage = document.getElementById('verify-message');
    const verifySignatureGamma = document.getElementById('verify-signature-gamma');
    const verifySignatureDelta = document.getElementById('verify-signature-delta');

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
        const bits = parseInt(bitsEncryptionInput.value, 10);
        if (isNaN(bits) || bits < 256) {
            showNotification('Vui lòng nhập số bit hợp lệ (ít nhất 256).', 'error');
            return;
        }
        const data = await apiCall('/api/generate-encryption-keys', {bits: bits});
        
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
        const bits = parseInt(bitsSignatureInput.value, 10);
        if (isNaN(bits) || bits < 256) {
            showNotification('Vui lòng nhập số bit hợp lệ (ít nhất 256).', 'error');
            return;
        }
        const data = await apiCall('/api/generate-signature-keys', {bits: bits});
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
            const y1_list = data.ciphertext.map(pair => pair.y1);
            const y2_list = data.ciphertext.map(pair => pair.y2);

            // Hiển thị mỗi giá trị trên một dòng
            encryptResultY1.value = y1_list.join('\n');
            encryptResultY2.value = y2_list.join('\n');
            showNotification('Mã hóa thành công.', 'success');

            // Tự động điền bản mã vào trường giải mã
            decryptCiphertextY1.value = encryptResultY1.value;
            decryptCiphertextY2.value = encryptResultY2.value;
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

        const y1_text = decryptCiphertextY1.value;
        const y2_text = decryptCiphertextY2.value;

        if (!y1_text || !y2_text) {
            showNotification('Vui lòng nhập đủ danh sách y1 và y2.', 'error');
            return;
        }

            // Tách chuỗi bằng ký tự xuống dòng, lọc bỏ các dòng rỗng
            const y1_list = y1_text.split('\n').filter(Boolean);
            const y2_list = y2_text.split('\n').filter(Boolean);

        if (y1_list.length !== y2_list.length) {
            showNotification('Lỗi: Số lượng y1 và y2 không khớp nhau.', 'error');
            return;
        }

        // Tái tạo lại cấu trúc list[dict] mà backend mong đợi
        const ciphertext = [];
        for (let i = 0; i < y1_list.length; i++) {
        ciphertext.push({
            y1: y1_list[i].trim(), // .trim() để xóa khoảng trắng thừa
            y2: y2_list[i].trim()
        });
        }

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
            const gamma_list = [];
            const delta_list = [];

            for (let i = 0; i < data.signature.length; i += 2) {
                if(data.signature[i]) gamma_list.push(data.signature[i]);
                if(data.signature[i+1]) delta_list.push(data.signature[i+1]);
            }

            signResultGamma.value = gamma_list.join('\n');
            signResultDelta.value = delta_list.join('\n');
            showNotification('Tạo chữ ký thành công.', 'success');
            
            // Tự động điền tin nhắn và chữ ký vào trường xác thực
            verifyMessage.value = message;
            verifySignatureGamma.value = signResultGamma.value;
            verifySignatureDelta.value = signResultDelta.value;
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

        const gamma_text = verifySignatureGamma.value;
        const delta_text = verifySignatureDelta.value;

        if (!gamma_text || !delta_text) {
            showNotification('Vui lòng nhập đủ danh sách Gamma và Delta của chữ ký.', 'error');
            return;
        }

        // Tách chuỗi bằng ký tự xuống dòng, lọc bỏ các dòng rỗng
        const gamma_list = gamma_text.split('\n').filter(Boolean);
        const delta_list = delta_text.split('\n').filter(Boolean);

        if (gamma_list.length !== delta_list.length) {
            showNotification('Lỗi: Số lượng Gamma và Delta không khớp nhau.', 'error');
            return;
        }

        // Tái tạo lại cấu trúc list[dict] mà backend mong đợi
        const signature = [];
        for (let i = 0; i < gamma_list.length; i++) {
            signature.push(gamma_list[i].trim()); // gamma
            signature.push(delta_list[i].trim()); // delta
        }

        if (signature.length === 0) {
            showNotification('Lỗi: Chữ ký không được để trống.', 'error');
            return;
        }

        const data = await apiCall('/api/verify', { message, signature, key });
        if (data) {
            let verifyResultBox = document.getElementById('verify-result');
        if (!verifyResultBox) {
            const resultBox = document.createElement('div');
            resultBox.id = 'verify-result';
            resultBox.className = 'mt-4 p-3 rounded-md text-center font-semibold';
            verifyMessage.parentNode.appendChild(resultBox); // chèn sau vùng message
            verifyResultBox = resultBox;
        }

        if (data.isValid) {
            verifyResultBox.textContent = 'XÁC THỰC HỢP LỆ';
            verifyResultBox.className = 'mt-4 p-3 rounded-md text-center font-semibold bg-green-800 text-green-100';
            showNotification('XÁC THỰC THÀNH CÔNG: Chữ ký hợp lệ!', 'success');
        } else {
            verifyResultBox.textContent = 'XÁC THỰC KHÔNG HỢP LỆ';
            verifyResultBox.className = 'mt-4 p-3 rounded-md text-center font-semibold bg-red-800 text-red-100';
            showNotification('XÁC THỰC THẤT BẠI: Chữ ký KHÔNG hợp lệ!', 'error');
        }

        verifyResultBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
        setTimeout(() => {
            verifyResultBox.style.opacity = '0';
            setTimeout(() => verifyResultBox.classList.add('hidden'), 700); // đợi hiệu ứng fade out
        }, 5000);
        }
    });

});