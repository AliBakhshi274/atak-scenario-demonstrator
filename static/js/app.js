document.addEventListener('DOMContentLoaded', () => {
    const startButton = document.getElementById('startButton');
    const stopButton = document.getElementById('stopButton');
    const resetButton = document.getElementById('resetButton');
    const statusMessage = document.getElementById('statusMessage');
    const logArea = document.getElementById('logArea');
    const API_URL = '/api';


    const sendCommand = async (endpoint, method = 'POST') => {
        logArea.textContent += `\n> Sending command: ${endpoint}...`;
        try {
            const response = await fetch(API_URL + endpoint, { method: method });
            const data = await response.json();

            if (response.ok) {
                statusMessage.textContent = `status: ${data.status}`;
                logArea.textContent += `\n[SUCCESS] ${data.message}`;
            } else {
                logArea.textContent += `\n[ERROR] ${data.message || 'response without any message! or response not OK'}`;
            }
        } catch (error) {
            logArea.textContent += `\n[FATAL ERROR] FATAL ERROR`;
            console.error('Fetch error:', error);
        }
        logArea.scrollTop = logArea.scrollHeight;
    };

    startButton.addEventListener('click', () => {
        console.log("JS. START BTN")
        sendCommand('/start');
        startButton.disabled = true;
        stopButton.disabled = false;
        resetButton.disabled = false
    });

    stopButton.addEventListener('click', () => {
        console.log("JS. STOP BTN")
        sendCommand('/stop');
        startButton.disabled = false;
        stopButton.disabled = true;
        resetButton.disabled = false
    });

    resetButton.addEventListener('click', () => {
        console.log("JS. RST BTN")
        sendCommand('/reset');
        startButton.disabled = false;
        stopButton.disabled = true;
        resetButton.disabled = false
    });

});