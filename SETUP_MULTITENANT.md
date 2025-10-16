# Guia de Configuração Multi-Cliente e Múltiplos Dispositivos

## Arquitetura

```
Plataforma Master (Pieng Medidor)
  ├── Cliente 1
  │   ├── PZEM-004T (WiFi via Elfin)
  │   ├── Eastron SDM630 (WiFi via Elfin)
  │   └── Medidor Tuya WiFi
  ├── Cliente 2
  │   ├── PZEM-004T (Serial COM3)
  │   └── Eastron SDM630 (RS485)
  └── Cliente 3
      └── Medidores Tuya WiFi (múltiplos)
```

---

## 1. Configuração RS485 → WiFi (Elfin-EW11A)

### Para cada dispositivo Modbus:

**A. Conexão Física:**
```
Dispositivo         Elfin-EW11A
  A+ (TX+)    →→→   A+
  B- (RX-)    →→→   B-
  VCC         →→→   5-24V
  GND         →→→   GND
```

**B. Configurar Elfin (primeira vez):**

1. **Conectar ao AP:**
   - SSID: `Elfin-EW11-XXXX`
   - IP: `192.168.16.254`
   - Login: `admin/admin`

2. **Configurar WiFi Station:**
   ```
   Network → WiFi Mode: Station
   SSID: SUA_REDE_WIFI
   Password: SUA_SENHA
   IP Mode: DHCP (anotar IP obtido)
   ```

3. **Configurar Serial:**
   - PZEM-004T: `9600 8N1`
   - SDM630: `9600 8N1` ou `19200 8N1` (verificar DIP switches)

4. **Configurar Modbus TCP:**
   ```
   Protocol: Modbus TCP
   Mode: TCP Server
   Local Port: 502
   ```

5. **Salvar e reiniciar**

**C. Anotar configurações:**
```
Device: PZEM-004T Cliente 1
IP: 192.168.1.100
Port: 502
Slave ID: 1
```

---

## 2. Adicionar Clientes

### Via API:

```bash
# Cliente 1 - Residencial
curl -X POST http://localhost:8000/api/clients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva - Residencial",
    "external_id": "cliente_001"
  }'

# Cliente 2 - Comercial
curl -X POST http://localhost:8000/api/clients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Loja ABC - Comercial",
    "external_id": "cliente_002"
  }'

# Cliente 3 - Industrial
curl -X POST http://localhost:8000/api/clients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fábrica XYZ - Industrial",
    "external_id": "cliente_003"
  }'
```

---

## 3. Adicionar Dispositivos

### 3.1. PZEM-004T via WiFi (Elfin)

```bash
curl -X POST http://localhost:8000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "name": "PZEM-004T Quadro Principal",
    "device_type": "modbus_tcp",
    "active": true,
    "config": {
      "host": "192.168.1.100",
      "port": 502,
      "slave_id": 1,
      "driver": "pzem004t",
      "base": 0,
      "timeout": 3.0
    }
  }'
```

### 3.2. Eastron SDM630 via WiFi (Elfin)

```bash
curl -X POST http://localhost:8000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "name": "SDM630 Entrada Principal",
    "device_type": "modbus_tcp",
    "active": true,
    "config": {
      "host": "192.168.1.101",
      "port": 502,
      "slave_id": 1,
      "driver": "sdm630",
      "base": 0,
      "timeout": 3.0
    }
  }'
```

**Métricas coletadas do SDM630:**
- `voltage_l1`, `voltage_l2`, `voltage_l3` - Tensões por fase
- `current_l1`, `current_l2`, `current_l3` - Correntes por fase
- `power_l1`, `power_l2`, `power_l3` - Potências por fase
- `power_total` - Potência total trifásica
- `energy_kwh` - Energia acumulada
- `frequency` - Frequência da rede
- `power_factor` - Fator de potência total

### 3.3. PZEM-004T Serial (COM3)

```bash
curl -X POST http://localhost:8000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 2,
    "name": "PZEM-004T Local",
    "device_type": "modbus",
    "active": true,
    "config": {
      "port": "COM3",
      "slave_id": 1,
      "baudrate": 9600,
      "driver": "pzem004t",
      "base": 0,
      "timeout": 0.5
    }
  }'
```

### 3.4. Medidor Tuya WiFi

```bash
curl -X POST http://localhost:8000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 3,
    "name": "Medidor Tuya Sala",
    "device_type": "tuya",
    "active": true,
    "config": {
      "device_id": "bf123abc456def",
      "local_key": "1234567890abcdef",
      "ip": "192.168.1.50",
      "version": "3.3"
    }
  }'
```

---

## 4. Configuração Tuya Cloud

### Obter credenciais:

1. **Criar conta em:** https://iot.tuya.com
2. **Cloud → Development:**
   - Criar projeto
   - Obter: `Access ID`, `Access Secret`
3. **Link dispositivos:** Smart Home → Devices
4. **Obter Device ID e Local Key:** via App Tuya ou debug mode

### Adicionar no código (futuro):

```python
# app/.env
TUYA_REGION=us
TUYA_ACCESS_ID=seu_access_id
TUYA_ACCESS_SECRET=seu_secret
TUYA_UID=seu_user_id
```

---

## 5. Topologia de Rede Recomendada

```
Internet
   ↓
Router WiFi (192.168.1.1)
   ├── Elfin #1 (192.168.1.100) → PZEM Cliente 1
   ├── Elfin #2 (192.168.1.101) → SDM630 Cliente 1
   ├── Elfin #3 (192.168.1.102) → PZEM Cliente 2
   ├── Tuya Device (192.168.1.50)
   └── Servidor Master (192.168.1.10)
```

**IPs Sugeridos:**
- `192.168.1.10` - Servidor Pieng Medidor
- `192.168.1.100-119` - Conversores Elfin
- `192.168.1.120-149` - Medidores Tuya
- `192.168.1.150-199` - Reserva

---

## 6. Dashboard Multi-Cliente

### Acessar por cliente:

```bash
# Dashboard geral
http://localhost:8000/api/dashboard

# Filtrar por cliente (futuro)
http://localhost:8000/api/dashboard?client_id=1

# Analytics
http://localhost:8000/api/analytics
```

### Exemplo de dados por cliente:

```bash
# Ver dispositivos do Cliente 1
curl "http://localhost:8000/api/devices?client_id=1"

# Ver métricas de um dispositivo específico
curl "http://localhost:8000/api/metrics?device_id=4&limit=10"
```

---

## 7. Checklist de Instalação por Cliente

### Cliente Novo:

- [ ] Criar cliente na plataforma
- [ ] Instalar dispositivos físicos
- [ ] Configurar Elfin-EW11A (se RS485)
- [ ] Testar conectividade (ping IP)
- [ ] Adicionar dispositivos na plataforma
- [ ] Verificar coleta de dados (30s)
- [ ] Configurar alarmes (opcional)
- [ ] Treinar cliente no dashboard
- [ ] Fornecer acesso (futuro: login segregado)

---

## 8. Configuração SDM630 Específica

### DIP Switches (verificar no medidor):
- **Baudrate:** Geralmente `19200` (verificar manual)
- **Slave ID:** Padrão `1` (ajustar se múltiplos na mesma linha)

### Parâmetros Elfin para SDM630:
```
Baudrate: 19200
Data: 8
Parity: None
Stop: 1
```

### Config JSON:
```json
{
  "host": "192.168.1.101",
  "port": 502,
  "slave_id": 1,
  "driver": "sdm630",
  "baudrate": 19200,
  "timeout": 3.0
}
```

---

## 9. Troubleshooting Multi-Dispositivo

### Dispositivo não coleta:
```bash
# Verificar conectividade
ping 192.168.1.100

# Testar Modbus TCP manualmente
python -c "from pymodbus.client import ModbusTcpClient; c = ModbusTcpClient('192.168.1.100', 502); c.connect(); print(c.read_input_registers(0, 5, slave=1).registers)"
```

### Conflito de IPs:
- Usar DHCP Reservation no router
- Documentar IPs em planilha

### Performance:
- Máximo 30 dispositivos por servidor
- Intervalo mínimo: 30s por dispositivo
- Usar múltiplos Elfins (1 por barramento RS485)

---

## 10. Roadmap Multi-Tenant

### Fase 1 (Atual):
✅ Múltiplos clientes
✅ Múltiplos dispositivos
✅ Modbus RTU + TCP
✅ PZEM-004T + SDM630

### Fase 2 (Próximo):
- [ ] Integração Tuya completa
- [ ] Autenticação por cliente (JWT)
- [ ] Dashboard isolado por cliente
- [ ] Notificações por email/SMS
- [ ] Relatórios automáticos

### Fase 3 (Futuro):
- [ ] Plataforma Slave para clientes
- [ ] Billing/assinaturas
- [ ] API pública
- [ ] Mobile app
