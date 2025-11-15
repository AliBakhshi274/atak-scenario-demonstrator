document.addEventListener('DOMContentLoaded', () => {
  const startButton = document.getElementById('startButton');
  const stopButton = document.getElementById('stopButton');
  const resetButton = document.getElementById('resetButton');
  //   const statusMessage = document.getElementById('statusMessage');
  const speedSlider = document.getElementById('speedSlider');
  const speedValueDisplay = document.getElementById('speedValDisplay');
  const API_URL = '/api';

  const sendCommand = async (endpoint, method = 'POST', requestData = null) => {
    try {
      const response = await fetch(API_URL + endpoint, {
        method: method,
        headers: requestData
          ? { 'Content-Type': 'application/json' }
          : undefined,
        body: requestData ? JSON.stringify(requestData) : undefined,
      });

      return await response.json();
      //   const responseData = await response.json();
      //   if (response.ok) {
      //     statusMessage.textContent = `status: ${responseData.status}`;
      //   } else {
      //     statusMessage.textContent = `Error: ${responseData.status}`;
      //   }
    } catch (error) {
      console.error('Fetch error:', error);
    }
  };

  const setSpeed = async (speedValue) => {
    const d = { speed: speedValue };
    const result = await sendCommand(
      (endpoint = '/set-speed'),
      (method = 'POST'),
      (requestData = d)
    );
    console.log('Speed set to:', result, 'x');
  };

  startButton.addEventListener('click', () => {
    console.log('JS. START BTN');
    sendCommand('/start');
    startButton.disabled = true;
    stopButton.disabled = false;
    resetButton.disabled = false;
  });

  stopButton.addEventListener('click', () => {
    console.log('JS. STOP BTN');
    sendCommand('/stop');
    startButton.disabled = false;
    stopButton.disabled = true;
    resetButton.disabled = true;
  });

  resetButton.addEventListener('click', () => {
    console.log('JS. RST BTN');
    sendCommand('/reset');
    startButton.disabled = false;
    stopButton.disabled = true;
    resetButton.disabled = true;
  });

  speedSlider.addEventListener('input', () => {
    const speedValue = parseFloat(speedSlider.value);
    console.log('Speed slider input:', speedValue);
    setSpeed(speedValue);
    speedValueDisplay.textContent = speedValue;
  });
});
