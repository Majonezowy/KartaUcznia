document.addEventListener('DOMContentLoaded', () => {
    const useNPButton = document.getElementById('useNP');
    const npStatus = document.getElementById('status');
    const studentName = document.getElementById('name');
    const avatar = document.getElementById('avatar');

    let isCountdownActive = false;
    const queryParams = new URLSearchParams(window.location.search);
    const serialNumber = queryParams.get('serialNumber');

    if (!serialNumber) {
        console.error('Serial number not found in URL parameters.');
        window.location.href = '/404.html';
        return;
    }

    const updateTimer = () => {
        const now = new Date();
        const targetTime = new Date();
        targetTime.setHours(24, 0, 0, 0);

        const diff = targetTime - now;
        const hours = String(Math.floor(diff / (1000 * 60 * 60))).padStart(2, '0');
        const minutes = String(Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))).padStart(2, '0');
        const seconds = String(Math.floor((diff % (1000 * 60)) / 1000)).padStart(2, '0');

        npStatus.textContent = `Aktywna przez ${hours}:${minutes}:${seconds}`;
    }

    const setNPStatus = (data) => {
        studentName.textContent = data.name || 'Nieznany uczeń';
        npStatus.textContent = data.valid ? 'Aktywna' : 'Nieaktywna';
        npStatus.classList.toggle('available', data.valid);
        npStatus.classList.toggle('disabled', !data.valid);

        useNPButton.style.display = 'none';
        useNPButton.disabled = !data.valid;

        if (data.user_role === 'teacher') {
            localStorage.setItem('role', data.user_role);
            avatar.classList.add('colorful');
        }

        if (data.user_role === 'student' && localStorage.getItem('role') === 'teacher') {
            useNPButton.style.display = 'block';
        }

        if (data.used) {
            isCountdownActive = true;
            npStatus.classList.toggle('disabled', !data.valid);
            useNPButton.disabled = true;
        }
    }

    const getStudentStatus = async (serialNumber) => {
        try {
            const response = await axios.get('http://localhost:8000/check-validity', { params: { serialNumber } });

            if (response.status === 200) {
                setNPStatus(response.data);
            } else {
                npStatus.textContent = 'Nieznany status';
            }
        } catch (e) {
            npStatus.textContent = 'Error fetching status';
            if (e.response && e.response.status === 429) {
                npStatus.textContent = 'Limit zapytań przekroczony';
            }
            console.error('Error fetching NP status:', e);
        }
    }

    const handleNPButtonClick = async () => {
        if (localStorage.getItem('role') !== 'teacher') {
            return;
        }

        try {
            await axios.post('http://localhost:8000/useNP', { serialNumber });
            window.location.reload();
        } catch (e) {
            console.error('Error while sending serial number:', e);
        }
    }

    useNPButton.addEventListener('click', handleNPButtonClick);

    getStudentStatus(serialNumber);

    setInterval(() => {
        if (isCountdownActive) {
            updateTimer();
        }
    }, 1000);
});
