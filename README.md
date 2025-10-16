# Pieng Medidor - Plataforma Master

Plataforma de monitoramento energético com suporte para medidores Modbus (RTU/TCP), Tuya IoT e análise de consumo/injeção de energia. Backend FastAPI + Frontend web responsivo com gráficos em tempo real.

## 🚀 Quick Start

### 1. Instalação
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configurar Dispositivo (exemplo: SDM630 via EW11)
```bash
python setup_sdm630_device.py
```

### 3. Iniciar Servidor (Backend + Frontend)
```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Acessar Interface Web
- **Dashboard**: http://localhost:8000/api/dashboard
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/

## 📊 Dispositivos Suportados

### Medidores Modbus
- **Eastron SDM630-Modbus CT** (trifásico)
  - Driver: `sdm630`
  - Comunicação: Modbus TCP via EW11 ou RTU direto
  - Métricas: tensões, correntes, potências, energia, fator de potência
  - Detecta consumo e injeção de energia (geração solar)

- **PZEM-004T** (monofásico)
  - Driver: `pzem004t`
  - Comunicação: Modbus RTU (RS485) ou TCP via gateway
  - Métricas: tensão, corrente, potência, energia

### Gateways Suportados
- **Elfin EW11/EW11A** (RS485 para WiFi/Ethernet)
- **Conversor USB-RS485** (comunicação serial direta)

### IoT Cloud (em desenvolvimento)
- **Tuya Smart** (6 módulos configuráveis)

## 🔧 Configuração

### Variáveis de Ambiente (.env)
```env
APP_NAME=Pieng Medidor Master
API_PREFIX=/api
DATABASE_URL=sqlite:///./data/app.db
SCHEDULER_TIMEZONE=UTC
ENABLE_FORWARDING=true
FORWARDER_URL=http://localhost:9000
```

### Exemplo de Configuração de Dispositivo

**Modbus TCP (via EW11):**
```json
{
  "client_id": 1,
  "name": "SDM630 - Entrada Principal",
  "device_type": "modbus_tcp",
  "active": true,
  "config": {
    "host": "10.0.0.109",
    "port": 8899,
    "slave_id": 1,
    "driver": "sdm630",
    "timeout": 3.0
  }
}
```

**Modbus RTU (serial direto):**
```json
{
  "client_id": 1,
  "name": "PZEM-004T Sala",
  "device_type": "modbus",
  "active": true,
  "config": {
    "port": "COM3",
    "slave_id": 1,
    "baudrate": 9600,
    "driver": "pzem004t",
    "timeout": 0.5
  }
}
```

## 📡 API Endpoints

### Gestão
- `GET /` - Health check
- `GET /api/clients` - Listar clientes
- `POST /api/clients` - Criar cliente
- `GET /api/devices` - Listar dispositivos
- `POST /api/devices` - Registrar dispositivo

### Dados e Métricas
- `POST /api/ingest` - Ingestão direta de medições
- `GET /api/metrics?device_id={id}&metric={name}&limit={n}` - Consultar métricas
- `GET /api/metrics/summary` - Resumo estatístico + Six Sigma
- `GET /api/metrics/linreg` - Regressão linear

### Alarmes
- `GET /api/alarms/rules` - Listar regras
- `POST /api/alarms/rules` - Criar regra de alarme
- `GET /api/alarms/events` - Eventos disparados

### Interface Web
- `GET /api/dashboard` - Dashboard interativo com Chart.js

## 🛠️ Ferramentas de Teste

### Monitor em Tempo Real
```bash
python test_sdm630_realtime.py
```
Monitora SDM630 em tempo real (atualização a cada 2s) com alertas automáticos.

## ⚙️ Funcionamento

### Coleta Automática (Poller)
- **Modbus RTU**: Pool a cada 30s (dispositivos `device_type: "modbus"`)
- **Modbus TCP**: Pool a cada 30s (dispositivos `device_type: "modbus_tcp"`)
- **Tuya**: Configurável (em desenvolvimento)

### Regras de Alarme
Avaliadas automaticamente durante ingestão:
- Operadores: `>`, `<`, `>=`, `<=`, `==`, `!=`
- Escopo: por cliente e/ou dispositivo
- Eventos armazenados com timestamp e valor

### Encaminhamento Master → Slave
- Forward automático para plataforma slave (opcional)
- Configurável via `ENABLE_FORWARDING` e `FORWARDER_URL`

## 📦 Estrutura do Projeto

```
app/
├── connectors/          # Drivers para dispositivos
│   ├── modbus.py        # Cliente Modbus RTU e TCP
│   ├── pzem004t.py      # Driver PZEM-004T
│   ├── eastron_sdm630.py # Driver SDM630
│   └── tuya.py          # Cliente Tuya Cloud (WIP)
├── routers/             # Endpoints da API
├── services/            # Lógica de negócio
│   ├── pollers.py       # Coletores automáticos
│   ├── scheduler.py     # APScheduler
│   ├── analytics.py     # Análise estatística
│   └── forwarder.py     # Forward para slave
├── static/              # CSS/JS do frontend
└── templates/           # HTML (Jinja2)
```

## 🔐 Segurança

- Isolamento de dados por cliente (multi-tenant ready)
- Autenticação JWT (planejado)
- Validação de entrada com Pydantic

## 📈 Roadmap

- [x] Suporte SDM630 via Modbus TCP
- [x] Gateway EW11 (RS485 → WiFi)
- [x] Dashboard web responsivo
- [x] Detecção de consumo/injeção
- [ ] Poller Tuya Cloud
- [ ] Autenticação multi-tenant
- [ ] Exportação CSV/Excel
- [ ] Notificações (email/SMS)
- [ ] Deploy Docker
- [ ] Plataforma slave (dashboard público por cliente)

## 📝 Licença

Proprietário - Pieng Soluções

