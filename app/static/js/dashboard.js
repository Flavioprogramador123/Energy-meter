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
    // Detectar se é medidor trifásico (buscar métricas por fase)
    const voltage_l1_check = await fetchJSON(`/api/metrics?device_id=${deviceId}&metric=voltage_l1&limit=1`);
    const isThreePhase = voltage_l1_check.length > 0;

    let voltageData, currentData, powerData;

    let energyData, alarms;

    if (isThreePhase) {
      // Buscar métricas trifásicas
      const [v1, v2, v3, i1, i2, i3, p1, p2, p3, pTotal, eData, alarmsData] = await Promise.all([
        fetchJSON(`/api/metrics?device_id=${deviceId}&metric=voltage_l1&limit=100`),
        fetchJSON(`/api/metrics?device_id=${deviceId}&metric=voltage_l2&limit=100`),
        fetchJSON(`/api/metrics?device_id=${deviceId}&metric=voltage_l3&limit=100`),
        fetchJSON(`/api/metrics?device_id=${deviceId}&metric=current_l1&limit=100`),
        fetchJSON(`/api/metrics?device_id=${deviceId}&metric=current_l2&limit=100`),
        fetchJSON(`/api/metrics?device_id=${deviceId}&metric=current_l3&limit=100`),
        fetchJSON(`/api/metrics?device_id=${deviceId}&metric=power_l1&limit=100`),
        fetchJSON(`/api/metrics?device_id=${deviceId}&metric=power_l2&limit=100`),
        fetchJSON(`/api/metrics?device_id=${deviceId}&metric=power_l3&limit=100`),
        fetchJSON(`/api/metrics?device_id=${deviceId}&metric=power_total&limit=100`),
        fetchJSON(`/api/metrics?device_id=${deviceId}&metric=energy_wh&limit=100`),
        fetchJSON(`/api/alarms/events?device_id=${deviceId}&limit=20`)
      ]);

      // Armazenar dados por fase para uso posterior
      window.phaseData = { v1, v2, v3, i1, i2, i3, p1, p2, p3 };
      voltageData = v1; // usar L1 como referência para status
      currentData = i1;
      powerData = pTotal.length > 0 ? pTotal : p1;
      energyData = eData;
      alarms = alarmsData;

    } else {
      // Buscar métricas monofásicas (formato antigo)
      const [vData, iData, pData, eData, alarmsData] = await Promise.all([
        fetchJSON(`/api/metrics?device_id=${deviceId}&metric=voltage&limit=100`),
        fetchJSON(`/api/metrics?device_id=${deviceId}&metric=current&limit=100`),
        fetchJSON(`/api/metrics?device_id=${deviceId}&metric=power&limit=100`),
        fetchJSON(`/api/metrics?device_id=${deviceId}&metric=energy_wh&limit=100`),
        fetchJSON(`/api/alarms/events?device_id=${deviceId}&limit=20`)
      ]);
      voltageData = vData;
      currentData = iData;
      powerData = pData;
      energyData = eData;
      alarms = alarmsData;
      window.phaseData = null;
    }

    // Verificar status do dispositivo (dados nos últimos 60 segundos)
    const lastReading = voltageData[0] || currentData[0] || powerData[0];
    const isOnline = lastReading && (Date.now() - new Date(lastReading.timestamp)) < 60000;

    const statusEl = el('deviceStatus');
    if (isOnline) {
      statusEl.className = 'status-indicator status-online';
      statusEl.title = 'Dispositivo online (última leitura há ' + Math.round((Date.now() - new Date(lastReading.timestamp))/1000) + 's)';
    } else {
      statusEl.className = 'status-indicator status-offline';
      statusEl.title = lastReading ?
        'Dispositivo offline (última leitura: ' + new Date(lastReading.timestamp).toLocaleString() + ')' :
        'Sem dados disponíveis';
    }

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

    // Calcular potência aparente (trifásico vs monofásico)
    let apparent_power = 0;
    if (isThreePhase && window.phaseData) {
      // Trifásico: S = V1*I1 + V2*I2 + V3*I3
      const v1 = window.phaseData.v1[0]?.value || 0;
      const v2 = window.phaseData.v2[0]?.value || 0;
      const v3 = window.phaseData.v3[0]?.value || 0;
      const i1 = window.phaseData.i1[0]?.value || 0;
      const i2 = window.phaseData.i2[0]?.value || 0;
      const i3 = window.phaseData.i3[0]?.value || 0;
      apparent_power = (v1 * i1) + (v2 * i2) + (v3 * i3);
    } else {
      // Monofásico: S = V * I
      apparent_power = v * i;
    }

    const power_factor = apparent_power > 0 ? Math.abs(p) / apparent_power : 0;
    const cost = e_kwh * 0.65;

    // Médias
    const avgV = voltageData.reduce((sum, d) => sum + d.value, 0) / voltageData.length || 0;
    const avgI = currentData.reduce((sum, d) => sum + d.value, 0) / currentData.length || 0;
    const avgP = powerData.reduce((sum, d) => sum + d.value, 0) / powerData.length || 0;

    // Atualizar valores em tempo real
    if (isThreePhase && window.phaseData) {
      // Helper para formatar com indicador de inatividade
      const formatPhaseValue = (val, unit, decimals = 1) => {
        const value = val || 0;
        const isInactive = Math.abs(value) < 0.01;
        const color = isInactive ? '#999' : 'inherit';
        const label = isInactive ? '(inativo)' : '';
        return `<span style="color:${color}">${value.toFixed(decimals)}${unit} ${label}</span>`;
      };

      // Exibir valores por fase para trifásicos
      el('liveVoltage').innerHTML = `
        L1: ${formatPhaseValue(window.phaseData.v1[0]?.value, 'V', 1)}<br>
        L2: ${formatPhaseValue(window.phaseData.v2[0]?.value, 'V', 1)}<br>
        L3: ${formatPhaseValue(window.phaseData.v3[0]?.value, 'V', 1)}
      `;

      const i1 = window.phaseData.i1[0]?.value || 0;
      const i2 = window.phaseData.i2[0]?.value || 0;
      const i3 = window.phaseData.i3[0]?.value || 0;
      el('liveCurrent').innerHTML = `
        L1: ${formatPhaseValue(i1, 'A', 2)}<br>
        L2: ${formatPhaseValue(i2, 'A', 2)}<br>
        L3: ${formatPhaseValue(i3, 'A', 2)}
      `;

      const p1 = window.phaseData.p1[0]?.value || 0;
      const p2 = window.phaseData.p2[0]?.value || 0;
      const p3 = window.phaseData.p3[0]?.value || 0;
      el('livePower').innerHTML = `
        L1: ${formatPhaseValue(p1, 'W', 0)}<br>
        L2: ${formatPhaseValue(p2, 'W', 0)}<br>
        L3: ${formatPhaseValue(p3, 'W', 0)}<br>
        <strong>Total: ${p.toFixed(0)}W</strong>
      `;
    } else {
      // Exibir valores únicos para monofásicos
      el('liveVoltage').textContent = v.toFixed(1) + ' V';
      el('liveCurrent').textContent = i.toFixed(3) + ' A';
      el('livePower').textContent = p.toFixed(1) + ' W';
    }

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
    const eSeries = energyData.reverse();
    const eLabels = eSeries.map(x => new Date(x.timestamp).toLocaleTimeString());

    if (isThreePhase && window.phaseData) {
      // Gráficos trifásicos com as 3 fases
      const v1_series = window.phaseData.v1.slice().reverse();
      const v2_series = window.phaseData.v2.slice().reverse();
      const v3_series = window.phaseData.v3.slice().reverse();
      const i1_series = window.phaseData.i1.slice().reverse();
      const i2_series = window.phaseData.i2.slice().reverse();
      const i3_series = window.phaseData.i3.slice().reverse();
      const p1_series = window.phaseData.p1.slice().reverse();
      const p2_series = window.phaseData.p2.slice().reverse();
      const p3_series = window.phaseData.p3.slice().reverse();

      const vLabels = v1_series.map(x => new Date(x.timestamp).toLocaleTimeString());
      const iLabels = i1_series.map(x => new Date(x.timestamp).toLocaleTimeString());
      const pLabels = p1_series.map(x => new Date(x.timestamp).toLocaleTimeString());

      // Gráfico de Tensões (3 fases)
      if (!charts.voltage || !charts.voltage.data.datasets[1]) {
        if (charts.voltage) charts.voltage.destroy();
        charts.voltage = new Chart(el('chartVoltage'), {
          type: 'line',
          data: {
            labels: vLabels,
            datasets: [
              { label: 'L1', data: v1_series.map(x => x.value), borderColor: '#e63946', tension: 0.4, borderWidth: 2 },
              { label: 'L2', data: v2_series.map(x => x.value), borderColor: '#f77f00', tension: 0.4, borderWidth: 2 },
              { label: 'L3', data: v3_series.map(x => x.value), borderColor: '#06d6a0', tension: 0.4, borderWidth: 2 }
            ]
          },
          options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: false } } }
        });
      } else {
        charts.voltage.data.labels = vLabels;
        charts.voltage.data.datasets[0].data = v1_series.map(x => x.value);
        charts.voltage.data.datasets[1].data = v2_series.map(x => x.value);
        charts.voltage.data.datasets[2].data = v3_series.map(x => x.value);
        charts.voltage.update('none');
      }

      // Gráfico de Correntes (3 fases)
      if (!charts.current || !charts.current.data.datasets[1]) {
        if (charts.current) charts.current.destroy();
        charts.current = new Chart(el('chartCurrent'), {
          type: 'line',
          data: {
            labels: iLabels,
            datasets: [
              { label: 'L1', data: i1_series.map(x => x.value), borderColor: '#457b9d', tension: 0.4, borderWidth: 2 },
              { label: 'L2', data: i2_series.map(x => x.value), borderColor: '#1d3557', tension: 0.4, borderWidth: 2 },
              { label: 'L3', data: i3_series.map(x => x.value), borderColor: '#a8dadc', tension: 0.4, borderWidth: 2 }
            ]
          },
          options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
        });
      } else {
        charts.current.data.labels = iLabels;
        charts.current.data.datasets[0].data = i1_series.map(x => x.value);
        charts.current.data.datasets[1].data = i2_series.map(x => x.value);
        charts.current.data.datasets[2].data = i3_series.map(x => x.value);
        charts.current.update('none');
      }

      // Gráfico de Potências (3 fases)
      if (!charts.power || !charts.power.data.datasets[1]) {
        if (charts.power) charts.power.destroy();
        charts.power = new Chart(el('chartPower'), {
          type: 'line',
          data: {
            labels: pLabels,
            datasets: [
              { label: 'L1', data: p1_series.map(x => x.value), borderColor: '#2a9d8f', tension: 0.4, borderWidth: 2 },
              { label: 'L2', data: p2_series.map(x => x.value), borderColor: '#264653', tension: 0.4, borderWidth: 2 },
              { label: 'L3', data: p3_series.map(x => x.value), borderColor: '#80ed99', tension: 0.4, borderWidth: 2 }
            ]
          },
          options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: false } } }
        });
      } else {
        charts.power.data.labels = pLabels;
        charts.power.data.datasets[0].data = p1_series.map(x => x.value);
        charts.power.data.datasets[1].data = p2_series.map(x => x.value);
        charts.power.data.datasets[2].data = p3_series.map(x => x.value);
        charts.power.update('none');
      }

    } else {
      // Gráficos monofásicos (formato original)
      const vSeries = voltageData.reverse();
      const iSeries = currentData.reverse();
      const pSeries = powerData.reverse();

      const vLabels = vSeries.map(x => new Date(x.timestamp).toLocaleTimeString());
      const iLabels = iSeries.map(x => new Date(x.timestamp).toLocaleTimeString());
      const pLabels = pSeries.map(x => new Date(x.timestamp).toLocaleTimeString());

      if (!charts.voltage) {
        charts.voltage = createChart('chartVoltage', 'Tensão (V)', '#e63946');
        charts.current = createChart('chartCurrent', 'Corrente (A)', '#457b9d');
        charts.power = createChart('chartPower', 'Potência (W)', '#2a9d8f');
      }

      updateChart(charts.voltage, vLabels, vSeries.map(x => x.value));
      updateChart(charts.current, iLabels, iSeries.map(x => x.value));
      updateChart(charts.power, pLabels, pSeries.map(x => x.value));
    }

    // Gráfico de Energia (igual para ambos)
    if (!charts.energy) {
      charts.energy = createChart('chartEnergy', 'Energia (Wh)', '#f77f00');
    }
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

async function openAlarmModal() {
  el('alarmModal').style.display = 'block';
}

function closeAlarmModal() {
  el('alarmModal').style.display = 'none';
  el('alarmForm').reset();
}

async function createAlarmRule(e) {
  e.preventDefault();
  const deviceId = el('deviceSelect').value;

  const payload = {
    client_id: null,  // será inferido do dispositivo no backend
    device_id: parseInt(deviceId),
    name: el('alarmName').value,
    metric: el('alarmMetric').value,
    operator: el('alarmOperator').value,
    threshold: parseFloat(el('alarmThreshold').value),
    enabled: el('alarmEnabled').checked
  };

  try {
    const response = await fetch('/api/alarms/rules', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      alert('✅ Regra de alarme criada com sucesso!');
      closeAlarmModal();
      loadAlarmRules();
      loadData();
    } else {
      const error = await response.json();
      alert('❌ Erro ao criar alarme: ' + JSON.stringify(error));
    }
  } catch (error) {
    alert('❌ Erro: ' + error.message);
  }
}

async function loadAlarmRules() {
  const deviceId = el('deviceSelect').value;
  if (!deviceId) return;

  try {
    const rules = await fetchJSON(`/api/alarms/rules?device_id=${deviceId}`);
    const container = el('alarmRulesList');

    if (rules.length === 0) {
      container.innerHTML = '<em style="color:#888">Nenhuma regra configurada</em>';
      return;
    }

    container.innerHTML = '<strong>Regras ativas:</strong><br>' + rules.map(r => {
      const status = r.enabled ? '🟢' : '🔴';
      return `${status} ${r.name}: ${r.metric} ${r.operator} ${r.threshold}`;
    }).join('<br>');
  } catch (error) {
    console.error('Erro ao carregar regras de alarme:', error);
  }
}

async function deleteAlarmRule(ruleId) {
  if (!confirm('Tem certeza que deseja remover esta regra de alarme?')) return;

  try {
    const response = await fetch(`/api/alarms/rules/${ruleId}`, { method: 'DELETE' });
    if (response.ok) {
      alert('✅ Regra removida!');
      loadAlarmRules();
    } else {
      alert('❌ Erro ao remover regra');
    }
  } catch (error) {
    alert('❌ Erro: ' + error.message);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  el('refreshBtn').addEventListener('click', loadData);
  el('deviceSelect').addEventListener('change', () => {
    updateDeviceStatus();
    loadAlarmRules();
    loadData();
  });
  el('configBtn').addEventListener('click', openConfigModal);
  el('configModal').querySelector('.close').addEventListener('click', closeConfigModal);
  el('testBtn').addEventListener('click', testConnection);
  el('configForm').addEventListener('submit', saveConfig);

  el('addAlarmBtn').addEventListener('click', openAlarmModal);
  el('alarmForm').addEventListener('submit', createAlarmRule);

  window.onclick = (e) => {
    if (e.target === el('configModal')) closeConfigModal();
    if (e.target === el('alarmModal')) closeAlarmModal();
  };

  updateDeviceStatus();
  loadAlarmRules();
  loadData();
  setInterval(loadData, 30000);
});


