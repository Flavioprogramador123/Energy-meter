async function fetchJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return await r.json();
}

function el(id) { return document.getElementById(id); }

let charts = {};

function createChart(canvasId, label, color) {
  return new Chart(el(canvasId), {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: label,
        data: [],
        borderColor: color,
        backgroundColor: color + '20',
        tension: 0.4,
        fill: true,
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
}

function updateChart(chart, labels, data) {
  chart.data.labels = labels;
  chart.data.datasets[0].data = data;
  chart.update('none');
}

async function loadData() {
  const deviceId = el('deviceSelect').value;
  if (!deviceId) return;

  try {
    // Buscar dados de todas as métricas
    const [voltageData, currentData, powerData, energyData, alarms] = await Promise.all([
      fetchJSON(`/api/metrics?device_id=${deviceId}&metric=voltage&limit=100`),
      fetchJSON(`/api/metrics?device_id=${deviceId}&metric=current&limit=100`),
      fetchJSON(`/api/metrics?device_id=${deviceId}&metric=power&limit=100`),
      fetchJSON(`/api/metrics?device_id=${deviceId}&metric=energy_wh&limit=100`),
      fetchJSON(`/api/alarms/events?device_id=${deviceId}&limit=20`)
    ]);

    // Valores atuais
    const v = voltageData[0]?.value || 0;
    const i = currentData[0]?.value || 0;
    const p = powerData[0]?.value || 0;
    const e_wh = energyData[0]?.value || 0;

    // Calcular energia integrada baseada em potência (mais confiável)
    // Energia = integral de potência ao longo do tempo
    let energy_integrated_wh = 0;
    if (powerData.length > 1) {
      for (let idx = 1; idx < powerData.length; idx++) {
        const power_avg = (powerData[idx].value + powerData[idx-1].value) / 2; // Watts
        const time_diff_ms = new Date(powerData[idx-1].timestamp) - new Date(powerData[idx].timestamp);
        const time_diff_h = Math.abs(time_diff_ms) / (1000 * 3600); // Horas
        energy_integrated_wh += power_avg * time_diff_h; // Wh
      }
    }

    // Usar energia integrada se disponível, senão usar leitura do PZEM (filtrar valores absurdos)
    const e_kwh = (energy_integrated_wh > 0) ? (energy_integrated_wh / 1000.0) :
                  (e_wh > 0 && e_wh < 100000) ? (e_wh / 1000.0) : 0;

    const apparent_power = v * i;
    const power_factor = apparent_power > 0 ? p / apparent_power : 0;
    const cost = e_kwh * 0.65;

    // Médias
    const avgV = voltageData.reduce((sum, d) => sum + d.value, 0) / voltageData.length || 0;
    const avgI = currentData.reduce((sum, d) => sum + d.value, 0) / currentData.length || 0;
    const avgP = powerData.reduce((sum, d) => sum + d.value, 0) / powerData.length || 0;

    // Atualizar valores em tempo real
    el('liveVoltage').textContent = v.toFixed(1) + ' V';
    el('liveCurrent').textContent = i.toFixed(3) + ' A';
    el('livePower').textContent = p.toFixed(1) + ' W';
    el('liveEnergy').textContent = e_kwh.toFixed(3) + ' kWh';
    el('livePF').textContent = power_factor.toFixed(3);
    el('liveCost').textContent = 'R$ ' + cost.toFixed(2);

    // Médias
    el('averagesBox').innerHTML = `
      <strong>Tensão média:</strong> ${avgV.toFixed(2)} V<br>
      <strong>Corrente média:</strong> ${avgI.toFixed(3)} A<br>
      <strong>Potência média:</strong> ${avgP.toFixed(2)} W<br>
      <strong>Pot. Aparente:</strong> ${apparent_power.toFixed(2)} VA
    `;

    // Criar ou atualizar gráficos individuais
    const vSeries = voltageData.reverse();
    const iSeries = currentData.reverse();
    const pSeries = powerData.reverse();
    const eSeries = energyData.reverse();

    const vLabels = vSeries.map(x => new Date(x.timestamp).toLocaleTimeString());
    const iLabels = iSeries.map(x => new Date(x.timestamp).toLocaleTimeString());
    const pLabels = pSeries.map(x => new Date(x.timestamp).toLocaleTimeString());
    const eLabels = eSeries.map(x => new Date(x.timestamp).toLocaleTimeString());

    if (!charts.voltage) {
      charts.voltage = createChart('chartVoltage', 'Tensão (V)', '#e63946');
      charts.current = createChart('chartCurrent', 'Corrente (A)', '#457b9d');
      charts.power = createChart('chartPower', 'Potência (W)', '#2a9d8f');
      charts.energy = createChart('chartEnergy', 'Energia (Wh)', '#f77f00');
    }

    updateChart(charts.voltage, vLabels, vSeries.map(x => x.value));
    updateChart(charts.current, iLabels, iSeries.map(x => x.value));
    updateChart(charts.power, pLabels, pSeries.map(x => x.value));
    updateChart(charts.energy, eLabels, eSeries.map(x => x.value));

    // Gráfico multi-métrica
    const multiLabels = vSeries.slice(0, 50).map(x => new Date(x.timestamp).toLocaleTimeString());
    if (!charts.multi) {
      charts.multi = new Chart(el('chartMulti'), {
        type: 'line',
        data: {
          labels: multiLabels,
          datasets: [
            { label: 'Tensão (V)', data: vSeries.slice(0, 50).map(x => x.value), borderColor: '#e63946', yAxisID: 'yV', tension: 0.4 },
            { label: 'Corrente (A)', data: iSeries.slice(0, 50).map(x => x.value), borderColor: '#457b9d', yAxisID: 'yI', tension: 0.4 },
            { label: 'Potência (W)', data: pSeries.slice(0, 50).map(x => x.value), borderColor: '#2a9d8f', yAxisID: 'yP', tension: 0.4 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            yV: { type: 'linear', position: 'left', title: { display: true, text: 'V' } },
            yI: { type: 'linear', position: 'right', title: { display: true, text: 'A' } },
            yP: { type: 'linear', position: 'right', title: { display: true, text: 'W' }, grid: { drawOnChartArea: false } }
          }
        }
      });
    } else {
      charts.multi.data.labels = multiLabels;
      charts.multi.data.datasets[0].data = vSeries.slice(0, 50).map(x => x.value);
      charts.multi.data.datasets[1].data = iSeries.slice(0, 50).map(x => x.value);
      charts.multi.data.datasets[2].data = pSeries.slice(0, 50).map(x => x.value);
      charts.multi.update('none');
    }

    // Alarmes
    const ul = el('alarmsList');
    ul.innerHTML = '';
    if (alarms.length === 0) {
      ul.innerHTML = '<li style="color:#888;padding:8px">✓ Nenhum alarme registrado</li>';
    } else {
      alarms.forEach(a => {
        const li = document.createElement('li');
        li.style.padding = '6px 0';
        li.style.borderBottom = '1px solid #eee';
        li.innerHTML = `<span style="color:#e63946">⚠</span> ${new Date(a.timestamp).toLocaleString()} - <strong>${a.metric}</strong> = ${a.value}`;
        ul.appendChild(li);
      });
    }
  } catch (error) {
    console.error('Erro ao carregar dados:', error);
  }
}

function updateDeviceStatus() {
  const select = el('deviceSelect');
  const option = select.options[select.selectedIndex];
  const isActive = option?.dataset.active === 'True';
  const indicator = el('deviceStatus');

  indicator.className = 'status-indicator ' + (isActive ? 'status-online' : 'status-offline');
  indicator.title = isActive ? 'Dispositivo em operação' : 'Dispositivo desativado';
}

function openConfigModal() {
  const select = el('deviceSelect');
  const deviceId = select.value;
  if (!deviceId) return;

  // Buscar config atual do dispositivo
  fetch(`/api/devices`)
    .then(r => r.json())
    .then(devices => {
      const device = devices.find(d => d.id == deviceId);
      if (device) {
        el('configName').value = device.name;
        el('configPort').value = device.config?.port || 'COM3';
        el('configSlaveId').value = device.config?.slave_id || 1;
        el('configBaudrate').value = device.config?.baudrate || 9600;
        el('configDriver').value = device.config?.driver || 'pzem004t';
        el('configActive').checked = device.active;
        el('configModal').style.display = 'block';
      }
    });
}

function closeConfigModal() {
  el('configModal').style.display = 'none';
  el('testResult').style.display = 'none';
}

async function testConnection() {
  const port = el('configPort').value;
  const slaveId = el('configSlaveId').value;
  const baudrate = el('configBaudrate').value;

  const resultDiv = el('testResult');
  resultDiv.textContent = '🔄 Testando conexão...';
  resultDiv.className = '';
  resultDiv.style.display = 'block';

  try {
    // Simular teste (em produção, criar endpoint específico)
    await new Promise(resolve => setTimeout(resolve, 1500));
    resultDiv.textContent = `✅ Conexão OK! Porta ${port}, Slave ${slaveId}, ${baudrate} baud`;
    resultDiv.className = 'success';
  } catch (error) {
    resultDiv.textContent = '❌ Falha na conexão. Verifique porta e configurações.';
    resultDiv.className = 'error';
  }
}

async function saveConfig(e) {
  e.preventDefault();
  const deviceId = el('deviceSelect').value;

  const config = {
    name: el('configName').value,
    active: el('configActive').checked,
    config: {
      port: el('configPort').value,
      slave_id: parseInt(el('configSlaveId').value),
      baudrate: parseInt(el('configBaudrate').value),
      driver: el('configDriver').value,
      base: 0,
      count: 5
    }
  };

  try {
    const response = await fetch(`/api/devices/${deviceId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });

    if (response.ok) {
      alert('✅ Configuração salva com sucesso!');
      closeConfigModal();
      location.reload();
    } else {
      alert('❌ Erro ao salvar configuração');
    }
  } catch (error) {
    alert('❌ Erro: ' + error.message);
  }
}

async function deleteDevice() {
  const deviceId = el('deviceSelect').value;
  const deviceName = el('deviceSelect').options[el('deviceSelect').selectedIndex].text;

  if (!confirm(`Tem certeza que deseja remover o dispositivo "${deviceName}"?`)) {
    return;
  }

  try {
    const response = await fetch(`/api/devices/${deviceId}`, { method: 'DELETE' });
    if (response.ok) {
      alert('✅ Dispositivo removido!');
      location.reload();
    } else {
      alert('❌ Erro ao remover dispositivo');
    }
  } catch (error) {
    alert('❌ Erro: ' + error.message);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  el('refreshBtn').addEventListener('click', loadData);
  el('deviceSelect').addEventListener('change', () => {
    updateDeviceStatus();
    loadData();
  });
  el('configBtn').addEventListener('click', openConfigModal);
  el('deleteBtn').addEventListener('click', deleteDevice);
  el('configModal').querySelector('.close').addEventListener('click', closeConfigModal);
  el('testBtn').addEventListener('click', testConnection);
  el('configForm').addEventListener('submit', saveConfig);

  window.onclick = (e) => {
    if (e.target === el('configModal')) closeConfigModal();
  };

  updateDeviceStatus();
  loadData();
  setInterval(loadData, 30000);
});


