# Configuração Elfin-EW11A - Conversor RS485 para WiFi/Ethernet

## Visão Geral
O Elfin-EW11A é um conversor industrial RS485 para WiFi/Ethernet que permite comunicação Modbus TCP com dispositivos seriais remotos (como PZEM-004T).

## Especificações
- **Interface**: RS485 ⟷ WiFi/Ethernet
- **Protocolo**: Modbus TCP (porta padrão 502)
- **Tensão**: 5-24V DC
- **Baudrate RS485**: 1200-115200 bps (padrão 9600 para PZEM-004T)
- **Modo**: TCP Server ou TCP Client

## Configuração Inicial

### 1. Conexão Física

**RS485 (Lado PZEM-004T):**
```
Elfin A+ ←→ PZEM TX+
Elfin B- ←→ PZEM RX-
```

**Alimentação:**
```
VCC: 5-24V DC
GND: Ground comum
```

### 2. Acesso ao WebUI

1. Conecte o Elfin na rede via Ethernet ou WiFi (AP mode padrão: `Elfin-EW11-XXXX`)
2. Acesse: `http://192.168.16.254` (IP padrão em modo AP)
3. Login: `admin` / `admin`

### 3. Configuração de Rede

**Modo Station (conectar ao WiFi existente):**
- **Network Settings** → **WiFi Mode**: `Station`
- **SSID**: Nome da rede WiFi
- **Password**: Senha WiFi
- **DHCP**: Habilitado (ou configurar IP estático)

Anote o IP obtido (ex: `192.168.1.100`)

### 4. Configuração Serial (RS485)

**Serial Settings:**
- **Baudrate**: `9600` (para PZEM-004T)
- **Data Bits**: `8`
- **Parity**: `None`
- **Stop Bits**: `1`
- **Flow Control**: `None`

### 5. Configuração Modbus TCP

**Network Protocol:**
- **Protocol**: `Modbus TCP`
- **Mode**: `TCP Server`
- **Local Port**: `502` (porta padrão Modbus)
- **Timeout**: `3000ms`

**Salvar e reiniciar o dispositivo.**

## Configuração no Pieng Medidor

### Criar Dispositivo via Dashboard

1. Acesse: http://localhost:8000/api/dashboard
2. Clique em **⚙️ Configurações**
3. Preencha:
   - **Nome**: `PZEM-004T via Elfin`
   - **Tipo**: `modbus_tcp`
   - **Host/IP**: `192.168.1.100` (IP do Elfin)
   - **Porta TCP**: `502`
   - **Slave ID**: `1` (ID do PZEM-004T)
   - **Driver**: `pzem004t`
   - **Ativo**: ✓

### Criar Dispositivo via API

```bash
curl -X POST http://localhost:8000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "name": "PZEM-004T via Elfin",
    "device_type": "modbus_tcp",
    "active": true,
    "config": {
      "host": "192.168.1.100",
      "port": 502,
      "slave_id": 1,
      "driver": "pzem004t",
      "base": 0,
      "count": 5,
      "timeout": 3.0
    }
  }'
```

## Configuração JSON Completa

```json
{
  "host": "192.168.1.100",      // IP do Elfin-EW11A
  "port": 502,                   // Porta Modbus TCP
  "slave_id": 1,                 // ID do PZEM-004T
  "driver": "pzem004t",          // Driver específico
  "base": 0,                     // Endereço base (0x0000)
  "count": 5,                    // 5 registradores
  "timeout": 3.0                 // Timeout em segundos
}
```

## Validação de Comunicação

### Teste de Ping
```bash
ping 192.168.1.100
```

### Teste Modbus TCP (via Python)
```python
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient(host='192.168.1.100', port=502, timeout=3)
client.connect()
result = client.read_input_registers(address=0, count=5, slave=1)
print(result.registers)
client.close()
```

Deve retornar 5 valores do PZEM-004T.

## Troubleshooting

### Problema: Não conecta ao Elfin
- Verificar se o IP está correto (`ipconfig` / `arp -a`)
- Verificar firewall (porta 502 TCP)
- Testar com `telnet 192.168.1.100 502`

### Problema: Timeout Modbus
- Aumentar `timeout` no config (ex: 5.0)
- Verificar baudrate RS485 (deve ser 9600 para PZEM-004T)
- Verificar conexões físicas A+/B-

### Problema: Dados incorretos
- Verificar `slave_id` (padrão PZEM-004T = 1)
- Verificar endereço base (deve ser 0 para PZEM-004T)
- Verificar ordem dos bytes (little-endian vs big-endian)

### Problema: Conexão instável
- Reduzir intervalo de polling (aumentar de 30s para 60s)
- Adicionar resistor terminador 120Ω na linha RS485
- Verificar comprimento do cabo RS485 (máx 1200m)

## Logs de Depuração

Os logs aparecem no console do servidor FastAPI:
```
Erro ao ler dispositivo Modbus TCP 4 (PZEM via Elfin): Timeout
```

## Vantagens Modbus TCP vs Serial

✅ **Sem ocupar porta USB/COM local**
✅ **Alcance ilimitado via rede**
✅ **Múltiplos clientes simultâneos**
✅ **Fácil expansão (vários Elfins)**
✅ **Monitoramento remoto via internet**

## Referências
- Manual Elfin-EW11A: http://www.hi-flying.com/elfin-ew10-elfin-ew11
- Modbus TCP Spec: https://modbus.org/specs.php
- PyModbus Docs: https://pymodbus.readthedocs.io/
