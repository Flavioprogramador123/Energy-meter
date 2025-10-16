# Pieng Medidor - Plataforma Master

API em FastAPI para coleta, análise e encaminhamento de dados de medidores (Modbus RTU/RS485, Tuya API e outros), com armazenamento local em SQLite e opções de forward para uma plataforma slave.

## Requisitos

- Python 3.11+
- Windows com porta serial (para Modbus) ou gateways/bridges adequados

## Instalação

```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Endpoints

- GET / (healthcheck)
- GET /api/clients, POST /api/clients
- GET /api/devices, POST /api/devices
- POST /api/ingest (ingestão direta de medições)
- GET /api/metrics?device_id=...&metric=...
- GET /api/alarms/rules, POST /api/alarms/rules

## Configuração

Variáveis no `.env` (opcional):

```
APP_NAME=Pieng Medidor Master
API_PREFIX=/api
DATABASE_URL=sqlite:///./data/app.db
SCHEDULER_TIMEZONE=UTC
ENABLE_FORWARDING=true
FORWARDER_URL=http://localhost:9000
```

## Conectores

- Modbus RTU (via minimalmodbus): configurar cada device com `config` contendo `port`, `slave_id`, `baudrate`, `timeout`, `base`, `count`, `metrics`.
- Tuya API (via tinytuya): em breve.

## Observações

- O agendador (APS) executa `poll_modbus_devices` a cada 30s.
- Banco: SQLite local na pasta `data/`.

