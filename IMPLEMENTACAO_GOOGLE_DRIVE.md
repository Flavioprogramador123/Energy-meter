# 🚀 Implementação Prática - Google Drive

## 📋 **Exemplo de Uso**

### **1. Configurar Credenciais**
```python
# config/google_drive_setup.py
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

def setup_google_drive():
    """Configurar Google Drive API"""
    
    # Credenciais do service account
    credentials_info = {
        "type": "service_account",
        "project_id": "pieng-energy-meter",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
        "client_email": "pieng-energy-meter@pieng-energy-meter.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/pieng-energy-meter%40pieng-energy-meter.iam.gserviceaccount.com"
    }
    
    # Salvar credenciais
    with open('credentials.json', 'w') as f:
        json.dump(credentials_info, f)
    
    print("✅ Credenciais configuradas!")

if __name__ == "__main__":
    setup_google_drive()
```

### **2. Testar Conexão**
```python
# test_google_drive.py
import os
from app.connectors.google_drive import GoogleDriveStorage
from datetime import datetime

def test_google_drive():
    """Testar integração com Google Drive"""
    
    # Configurar variáveis de ambiente
    os.environ['GOOGLE_DRIVE_CREDENTIALS_FILE'] = 'credentials.json'
    os.environ['GOOGLE_DRIVE_FOLDER_ID'] = '1ABC123DEF456GHI789JKL'  # Substitua pelo ID da sua pasta
    
    try:
        # Inicializar storage
        storage = GoogleDriveStorage()
        
        # Testar salvamento
        storage.save_measurement(
            device_id=1,
            metric='voltage',
            value=220.5,
            timestamp=datetime.now()
        )
        
        print("✅ Teste de salvamento realizado!")
        
        # Testar busca
        measurements = storage.get_measurements(
            device_id=1,
            metric='voltage',
            days=1
        )
        
        print(f"✅ Encontradas {len(measurements)} medições!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    test_google_drive()
```

### **3. Integrar com FastAPI**
```python
# app/routers/storage.py
from fastapi import APIRouter, HTTPException
from app.services.storage import HybridStorage
from app.schemas import MeasurementCreate
from datetime import datetime

router = APIRouter(prefix="/api/storage", tags=["storage"])
storage = HybridStorage()

@router.post("/backup")
async def backup_to_google_drive():
    """Fazer backup de todos os dados para Google Drive"""
    try:
        # Implementar lógica de backup
        # ...
        return {"status": "success", "message": "Backup realizado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/restore")
async def restore_from_google_drive():
    """Restaurar dados do Google Drive"""
    try:
        # Implementar lógica de restauração
        # ...
        return {"status": "success", "message": "Dados restaurados com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def storage_status():
    """Verificar status do armazenamento"""
    try:
        # Verificar conexão com Google Drive
        # ...
        return {
            "local_db": "connected",
            "google_drive": "connected",
            "last_backup": "2025-10-16T10:30:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### **4. Atualizar Ingestão de Dados**
```python
# app/routers/ingest.py (atualizado)
from app.services.storage import HybridStorage

# ... código existente ...

@router.post("/ingest")
async def ingest_measurement(measurement: MeasurementCreate):
    """Ingerir medição com armazenamento híbrido"""
    try:
        # Salvar usando storage híbrido
        storage.save_measurement(
            device_id=measurement.device_id,
            metric=measurement.metric,
            value=measurement.value
        )
        
        # Avaliar alarmes
        await evaluate_alarms(measurement)
        
        # Encaminhar para slave (se habilitado)
        if settings.enable_forwarding:
            await forward_measurement(measurement)
        
        return {"status": "success", "message": "Medição salva com sucesso!"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 🔧 **Configuração no Vercel**

### **1. Environment Variables**
```
GOOGLE_DRIVE_CREDENTIALS={"type":"service_account",...}
GOOGLE_DRIVE_FOLDER_ID=1ABC123DEF456GHI789JKL
APP_NAME=Energy Meter Master
API_PREFIX=/api
DATABASE_URL=sqlite:///./data/app.db
SCHEDULER_TIMEZONE=America/Sao_Paulo
ENABLE_FORWARDING=false
FORWARDER_URL=
```

### **2. Deploy**
```bash
# Fazer commit das alterações
git add .
git commit -m "feat: Integrar Google Drive para persistência de dados"
git push origin master

# Deploy automático no Vercel
```

## 📊 **Monitoramento**

### **Dashboard de Status**
```html
<!-- app/templates/storage_status.html -->
<div class="card">
    <h3>📁 Status do Armazenamento</h3>
    <div class="status-grid">
        <div class="status-item">
            <span class="status-label">Banco Local:</span>
            <span class="status-value" id="localStatus">Verificando...</span>
        </div>
        <div class="status-item">
            <span class="status-label">Google Drive:</span>
            <span class="status-value" id="gdriveStatus">Verificando...</span>
        </div>
        <div class="status-item">
            <span class="status-label">Último Backup:</span>
            <span class="status-value" id="lastBackup">--</span>
        </div>
    </div>
    <button onclick="checkStorageStatus()">🔄 Verificar Status</button>
</div>
```

## 🎯 **Vantagens da Solução Google Drive:**

- ✅ **15GB gratuito** (vs 500MB Supabase)
- ✅ **Backup automático** (Google cuida)
- ✅ **Sincronização** entre dispositivos
- ✅ **Histórico** de versões
- ✅ **API robusta** e confiável
- ✅ **Sem custos** adicionais
- ✅ **Integração** com ecossistema Google

## ⚠️ **Considerações:**

- **Rate Limits:** 100 requests/100s
- **Latência:** Maior que banco tradicional
- **Estrutura:** Arquivos CSV (não relacional)
- **Dependência:** Internet obrigatória

---
*Implementação criada em 16/10/2025*
