document.addEventListener('DOMContentLoaded', () => {

    // Lấy các phần tử DOM
    // Công cụ
    const loadingSpinner = document.getElementById('loading-spinner');
    const notificationBox = document.getElementById('notification-box');
    const notificationMessage = document.getElementById('notification-message');

    // 1. Generate Prime
    const primeBits = document.getElementById('prime-bits');
    const primeSafe = document.getElementById('prime-safe');
    const btnGeneratePrime = document.getElementById('btn-generate-prime');
    const primeResult = document.getElementById('prime-result');
    const primeTime = document.getElementById('prime-time');

    // 2. Check Prime
    const checkNumber = document.getElementById('check-number');
    const btnCheckPrime = document.getElementById('btn-check-prime');
    const checkResult = document.getElementById('check-result');

    // 3. Find Root
    const rootP = document.getElementById('root-p');
    const rootSafe = document.getElementById('root-safe');
    const btnFindRoot = document.getElementById('btn-find-root');
    const rootResult = document.getElementById('root-result');


    // Helper Functions
    function showLoading(show) {
        loadingSpinner.classList.toggle('hidden', !show);
    }

    function showNotification(message, type = 'info') {
        notificationMessage.textContent = message;
        notificationBox.className = 'p-4 rounded-md mb-6 transition-all duration-300';
        if (type === 'success') {
            notificationBox.classList.add('bg-green-800', 'text-green-100');
        } else if (type === 'error') {
            notificationBox.classList.add('bg-red-800', 'text-red-100');
        } else {
            notificationBox.classList.add('bg-blue-800', 'text-blue-100');
        }
        notificationBox.classList.remove('hidden');
        setTimeout(() => { notificationBox.classList.add('hidden'); }, 5000);
    }

    async function apiCall(endpoint, body) {
        showLoading(true);
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Có lỗi xảy ra từ server');
            }
            if (data.success === false) {
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

    //Gắn Sự Kiện

    // 1. Tạo số nguyên tố
    btnGeneratePrime.addEventListener('click', async () => {
        const bits = parseInt(primeBits.value, 10);
        const safe = primeSafe.checked;
        
        if (safe && bits < 512) {
             showNotification('Tạo Safe Prime nên dùng số bits lớn (>= 512) để đảm bảo thành công.', 'info');
        }

        primeResult.value = "Đang tạo...";
        primeTime.textContent = "";

        const data = await apiCall('/api/tools/generate-prime', { bits, safe });
        
        if (data) {
            primeResult.value = data.prime;
            primeTime.textContent = `Thời gian tạo: ${data.time} giây`;
            showNotification('Tạo số nguyên tố thành công!', 'success');
            // Tự động điền vào các ô bên dưới
            checkNumber.value = data.prime;
            rootP.value = data.prime;
            rootSafe.checked = safe; // Đồng bộ trạng thái safe
        } else {
             primeResult.value = "Thất bại. Xem thông báo lỗi.";
        }
    });

    // 2. Kiểm tra số nguyên tố
    btnCheckPrime.addEventListener('click', async () => {
        const number = checkNumber.value;
        if (!number) {
            showNotification('Vui lòng nhập số.', 'error');
            return;
        }

        checkResult.textContent = "Đang kiểm tra...";
        checkResult.className = 'result-box'; // Reset class

        const data = await apiCall('/api/tools/check-prime', { number });
        
        if (data) {
            if (data.isPrime) {
                checkResult.textContent = `Hợp lệ: ${data.number} LÀ số nguyên tố.`;
                checkResult.classList.add('success');
            } else {
                checkResult.textContent = `Không hợp lệ: ${data.number} KHÔNG phải là số nguyên tố.`;
                checkResult.classList.add('error');
            }
        } else {
             checkResult.textContent = "Lỗi kiểm tra. Định dạng số sai?";
             checkResult.classList.add('error');
        }
    });

    // 3. Tìm phần tử sinh (g)
    btnFindRoot.addEventListener('click', async () => {
        const p = rootP.value;
        const safe = rootSafe.checked;
        if (!p) {
            showNotification('Vui lòng nhập số nguyên tố p.', 'error');
            return;
        }

        rootResult.value = "Đang tìm...";
        const data = await apiCall('/api/tools/find-root', { p, safe });

        if (data) {
            rootResult.value = data.g;
            showNotification('Tìm thấy g thành công!', 'success');
        } else {
            rootResult.value = "Thất bại. (p không phải SNT hoặc không phải Safe Prime?)";
        }
    });
});