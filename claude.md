# Pieng Medidor — Guia de Arquitetura (para IA)

Documento de referência para evolução automática. Contém visão, árvore, modelos, endpoints, conectores, regras e analytics.

## Visão e Objetivo
- Plataforma master para coletar dados (Modbus RTU/RS485, Modbus TCP, Tuya API e outros), analisar e gerar alarmes por cliente.
- **APENAS DADOS REAIS**: Sistema trabalha exclusivamente com dados auditáveis de hardware físico
- Logs de auditoria em `data/audit.log` registram todas as leituras com timestamp, device_id, driver e métricas
- Encaminhamento opcional para plataforma slave (cliente acompanha a planta).
- Armazenamento local (SQLite); possível expansão para Firebase/Cloud.

## Stack
- API: FastAPI + Jinja2 (templates)
- ORM/DB: SQLAlchemy + SQLite
- Agendador: APScheduler
- Conectores: minimalmodbus (RTU), pymodbus (TCP), tinytuya (Tuya Cloud)
- Analytics: pandas, numpy (regressão linear via polyfit)
- Auditoria: logging em arquivo estruturado (data/audit.log)
- Frontend: Chart.js (CDN) + CSS responsivo

## Árvore do Projeto
```
app/
  __init__.py
  connectors/
    __init__.py
    modbus.py
    pzem004t.py
    tuya.py
  core/
    __init__.py
    config.py
    db.py
  crud.py
  main.py
  models.py
  routers/
    __init__.py
    alarms.py
    clients.py
    dashboard.py
    devices.py
    ingest.py
    metrics.py
  schemas.py
  services/
    __init__.py
    alarms.py
    analytics.py
    forwarder.py
    pollers.py
    scheduler.py
  static/
    css/
      styles.css
    js/
      dashboard.js
  templates/
    dashboard.html
data/
claude.md
pzem_004T.md
README.md
requirements.txt
```

## Configuração (.env)
- APP_NAME (default: Pieng Medidor Master)
- API_PREFIX (default: /api)
- DATABASE_URL (default: sqlite:///./data/app.db)
- SCHEDULER_TIMEZONE (default: UTC)
- ENABLE_FORWARDING (default: true)
- FORWARDER_URL (ex.: http://localhost:9000)

## Modelos (SQLAlchemy)
- Client(id, name, external_id, created_at)
- Device(id, client_id, name, device_type[modbus|tuya|...], active, config JSON, created_at)
- Measurement(id, device_id, timestamp, metric, value, extra JSON)
- AlarmRuleModel(id, client_id, device_id?, name, metric, operator {>,<,>=,<=,==,!=}, threshold, enabled, created_at)
- AlarmEvent(id, rule_id, device_id, timestamp, metric, value, details, acknowledged)

## Schemas (Pydantic)
- ClientCreate/Read, DeviceCreate/Read
- MeasurementCreate/Read
- AlarmRuleCreate/Read, AlarmEventRead

## Endpoints
- GET `/` — healthcheck
- Clients: GET `/api/clients`, POST `/api/clients`
- Devices: GET `/api/devices?client_id?`, POST `/api/devices`
- Ingest: POST `/api/ingest` — persiste, avalia regras, forward opcional
- Metrics: GET `/api/metrics?device_id&metric?&limit?`
  - GET `/api/metrics/summary` — resumo estatístico + six sigma
  - GET `/api/metrics/linreg` — regressão linear x vs y
- Alarms: GET `/api/alarms/rules`, POST `/api/alarms/rules`
  - GET `/api/alarms/events` — eventos de alarme por dispositivo
- Dashboard: GET `/api/dashboard` — interface web com gráficos
- Dev: POST `/api/dev/demo` — popula dados de teste (cliente + dispositivo + 40 amostras)

## Conectores e Pollers
- Modbus RTU (`app/connectors/modbus.py`)
  - `ModbusRTUClient(port, slave_id, baudrate=9600, timeout=0.5)`
  - Poller: `services/pollers.py::poll_modbus_devices` (30s)
  - `Device.config`: `{port, slave_id, baudrate, timeout, base, count, metrics}` ou `{driver: "pzem004t", ...}`
- PZEM-004T (`app/connectors/pzem004t.py`)
  - Driver específico: `read_pzem004t_metrics()` lê 5 registradores e monta voltage/current/power/energy_wh
  - Energia como U32 (regs 3+4), escalas conforme manual
- Tuya API (`app/connectors/tuya.py`)
  - `TuyaAPIClient(region, key, secret, uid)` com `list_devices`, `get_status`, `get_energy_data`
  - Agendamento Tuya: pendente (similar ao Modbus)

## Regras de Alarme
- Avaliadas na ingestão; cria `AlarmEvent` quando `operator(value, threshold)` é verdadeiro.
- Escopo por cliente e/ou dispositivo; habilitável por regra.

## Analytics
- Resumo: count, mean, std, min, max
- Six Sigma (básico): mean, std, cpk (LSL/USL = mean ± 3σ)
- Regressão linear: slope, intercept, r2

## Encaminhamento Master → Slave
- `services/forwarder.py`: POST para `/api/ingest` do slave.
- Controlado por `ENABLE_FORWARDING` e `FORWARDER_URL`.

## Notas PZEM-004T (Modbus)
- 9600 8N1; energia 32 bits (2 registradores). Preferir leitura de 5 regs desde 0x0000.
- Padronizar bytes `0xNN`; CRC calculado pela biblioteca.

## Como rodar
1. `python -m venv .venv && .\.venv\Scripts\activate`
2. `pip install -r requirements.txt`
3. `uvicorn app.main:app --reload --port 8000`
4. Testar: `POST /api/dev/demo` para popular dados
5. Dashboard: `http://localhost:8000/api/dashboard`
6. Docs: `http://localhost:8000/docs`

## Roadmap - Próximos Passos

### Curto Prazo (Próxima Sessão)
1. **Poller Tuya**: Implementar `poll_tuya_devices()` no scheduler
2. **Dashboard Melhorias**:
   - Cards de resumo por cliente (total dispositivos, alarmes ativos)
   - Modo dark/light toggle
   - Filtros por período (hoje, semana, mês)
   - Gráficos múltiplas métricas simultâneas
3. **Testes com Hardware Real**:
   - Conectar PZEM-004T físico
   - Validar escalas e registradores
   - Ajustar timeout e retry logic

### Médio Prazo
4. **Autenticação Multi-tenant**:
   - JWT tokens por cliente
   - Isolamento de dados por tenant
   - Login/logout no dashboard
5. **Exportações**:
   - CSV/Excel por período
   - Relatórios PDF automáticos
   - Backup/restore do SQLite
6. **Notificações**:
   - Email/SMS para alarmes críticos
   - Webhooks para integrações externas
   - Dashboard de notificações

### Longo Prazo
7. **Plataforma Slave**:
   - API separada para clientes
   - Dashboard público por cliente
   - Assinaturas e billing
8. **Analytics Avançados**:
   - Detecção de anomalias (Isolation Forest)
   - Previsão de consumo (ARIMA/LSTM)
   - Relatórios de eficiência energética
9. **Integrações**:
   - Firebase/Cloud SQL para escala
   - APIs de terceiros (Enel, CPFL)
   - IoT platforms (AWS IoT, Azure IoT)

### Melhorias Técnicas
10. **Performance**:
    - Cache Redis para consultas frequentes
    - Paginação em endpoints grandes
    - Compressão de dados históricos
11. **Monitoramento**:
    - Logs estruturados (JSON)
    - Métricas de performance
    - Health checks avançados
12. **DevOps**:
    - Docker containers
    - CI/CD pipeline
    - Deploy automatizado

### Configurações Pendentes
- Ajustar `.env` com credenciais reais
- Configurar firewall para portas Modbus
- Backup automático do SQLite
- Logs de auditoria para compliance
