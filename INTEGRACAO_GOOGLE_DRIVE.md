# 📁 Integração com Google Drive - pieng-energy-meter

## 🎯 **Por que Google Drive?**

### ✅ **Vantagens:**
- **15GB gratuito** (muito mais que Supabase)
- **Backup automático** (Google cuida da redundância)
- **Acesso via API** (Google Drive API)
- **Sincronização** com outros dispositivos
- **Histórico de versões** automático
- **Já tem conta** (sem necessidade de cadastros extras)

### ⚠️ **Considerações:**
- **Rate limits** da API (100 requests/100s)
- **Latência** maior que banco tradicional
- **Estrutura** de arquivos (não banco relacional)

## 🛠️ **Implementação**

### 1. **Configurar Google Drive API**

#### **Passo 1: Criar Projeto no Google Cloud**
1. Acesse: https://console.cloud.google.com/
2. **New Project** → `pieng-energy-meter`
3. **APIs & Services** → **Library**
4. Busque: **Google Drive API**
5. **Enable** a API

#### **Passo 2: Criar Credenciais**
1. **APIs & Services** → **Credentials**
2. **Create Credentials** → **Service Account**
3. **Name:** `pieng-energy-meter-service`
4. **Role:** `Editor`
5. **Create Key** → **JSON**
6. **Download** o arquivo JSON

#### **Passo 3: Compartilhar Pasta**
1. Crie uma pasta no Google Drive: `pieng-energy-meter-data`
2. **Compartilhar** com o email do service account
3. **Permissão:** `Editor`

### 2. **Instalar Dependências**
```bash
pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
```

### 3. **Configurar Variáveis de Ambiente**
```env
# .env
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
GOOGLE_DRIVE_FOLDER_ID=1ABC123DEF456GHI789JKL
APP_NAME=Energy Meter Master
API_PREFIX=/api
DATABASE_URL=sqlite:///./data/app.db
SCHEDULER_TIMEZONE=America/Sao_Paulo
ENABLE_FORWARDING=false
FORWARDER_URL=
```

### 4. **Implementar Driver Google Drive**
```python
# app/connectors/google_drive.py
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
import pandas as pd

class GoogleDriveStorage:
    def __init__(self):
        self.credentials_file = os.getenv("GOOGLE_DRIVE_CREDENTIALS_FILE")
        self.folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Autenticar com Google Drive API"""
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_file,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        return build('drive', 'v3', credentials=credentials)
    
    def save_measurement(self, device_id: int, metric: str, value: float, timestamp: datetime):
        """Salvar medição no Google Drive"""
        try:
            # Criar arquivo CSV com a medição
            data = {
                'device_id': device_id,
                'metric': metric,
                'value': value,
                'timestamp': timestamp.isoformat()
            }
            
            # Nome do arquivo baseado na data
            filename = f"measurements_{timestamp.strftime('%Y-%m-%d')}.csv"
            
            # Verificar se arquivo já existe
            file_id = self._get_file_id(filename)
            
            if file_id:
                # Atualizar arquivo existente
                self._append_to_csv(file_id, data)
            else:
                # Criar novo arquivo
                self._create_csv_file(filename, data)
                
        except HttpError as error:
            print(f"Erro ao salvar no Google Drive: {error}")
    
    def _get_file_id(self, filename: str):
        """Buscar ID do arquivo no Google Drive"""
        try:
            results = self.service.files().list(
                q=f"name='{filename}' and parents in '{self.folder_id}'",
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            return files[0]['id'] if files else None
            
        except HttpError as error:
            print(f"Erro ao buscar arquivo: {error}")
            return None
    
    def _create_csv_file(self, filename: str, data: dict):
        """Criar novo arquivo CSV"""
        import io
        
        # Criar CSV em memória
        df = pd.DataFrame([data])
        csv_content = df.to_csv(index=False)
        
        # Upload para Google Drive
        file_metadata = {
            'name': filename,
            'parents': [self.folder_id]
        }
        
        media = io.BytesIO(csv_content.encode('utf-8'))
        
        self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
    
    def _append_to_csv(self, file_id: str, data: dict):
        """Adicionar dados ao CSV existente"""
        import io
        
        # Baixar arquivo atual
        content = self.service.files().get_media(fileId=file_id).execute()
        
        # Converter para DataFrame
        existing_df = pd.read_csv(io.BytesIO(content))
        
        # Adicionar nova linha
        new_df = pd.DataFrame([data])
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        
        # Upload do arquivo atualizado
        csv_content = combined_df.to_csv(index=False)
        media = io.BytesIO(csv_content.encode('utf-8'))
        
        self.service.files().update(
            fileId=file_id,
            media_body=media
        ).execute()
    
    def get_measurements(self, device_id: int, metric: str, days: int = 7):
        """Buscar medições dos últimos N dias"""
        try:
            measurements = []
            
            # Buscar arquivos dos últimos N dias
            for i in range(days):
                date = datetime.now() - timedelta(days=i)
                filename = f"measurements_{date.strftime('%Y-%m-%d')}.csv"
                
                file_id = self._get_file_id(filename)
                if file_id:
                    # Baixar e processar arquivo
                    content = self.service.files().get_media(fileId=file_id).execute()
                    df = pd.read_csv(io.BytesIO(content))
                    
                    # Filtrar por device_id e metric
                    filtered_df = df[
                        (df['device_id'] == device_id) & 
                        (df['metric'] == metric)
                    ]
                    
                    measurements.extend(filtered_df.to_dict('records'))
            
            return measurements
            
        except HttpError as error:
            print(f"Erro ao buscar medições: {error}")
            return []
```

### 5. **Integrar com o Sistema**
```python
# app/services/storage.py
from app.connectors.google_drive import GoogleDriveStorage
from app.core.db import SessionLocal
from app.models import Measurement
from datetime import datetime

class HybridStorage:
    def __init__(self):
        self.db = SessionLocal()
        self.gdrive = GoogleDriveStorage()
    
    def save_measurement(self, device_id: int, metric: str, value: float):
        """Salvar medição em ambos os locais"""
        timestamp = datetime.now()
        
        # Salvar no banco local (SQLite)
        measurement = Measurement(
            device_id=device_id,
            metric=metric,
            value=value,
            timestamp=timestamp
        )
        self.db.add(measurement)
        self.db.commit()
        
        # Salvar no Google Drive (backup)
        self.gdrive.save_measurement(device_id, metric, value, timestamp)
    
    def get_measurements(self, device_id: int, metric: str, limit: int = 100):
        """Buscar medições (prioridade: banco local)"""
        try:
            # Tentar banco local primeiro
            measurements = self.db.query(Measurement).filter(
                Measurement.device_id == device_id,
                Measurement.metric == metric
            ).order_by(Measurement.timestamp.desc()).limit(limit).all()
            
            if measurements:
                return measurements
            else:
                # Fallback para Google Drive
                return self.gdrive.get_measurements(device_id, metric)
                
        except Exception as e:
            print(f"Erro ao buscar medições: {e}")
            return []
```

### 6. **Atualizar requirements.txt**
```txt
# Adicionar estas linhas
google-api-python-client==2.108.0
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
pandas==2.1.3
```

## 🔄 **Estratégia Híbrida**

### **Armazenamento Duplo:**
1. **SQLite Local** - Performance e cache
2. **Google Drive** - Backup e persistência

### **Vantagens:**
- ✅ **Performance** (SQLite local)
- ✅ **Persistência** (Google Drive)
- ✅ **Backup automático** (Google Drive)
- ✅ **Sincronização** entre dispositivos
- ✅ **Histórico** de versões

## 📊 **Estrutura de Arquivos no Google Drive**

```
pieng-energy-meter-data/
├── measurements_2025-10-16.csv
├── measurements_2025-10-15.csv
├── measurements_2025-10-14.csv
├── devices_backup.json
├── clients_backup.json
└── alarm_rules_backup.json
```

## 🚀 **Deploy com Google Drive**

### **Environment Variables no Vercel:**
```
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
GOOGLE_DRIVE_FOLDER_ID=1ABC123DEF456GHI789JKL
APP_NAME=Energy Meter Master
API_PREFIX=/api
DATABASE_URL=sqlite:///./data/app.db
SCHEDULER_TIMEZONE=America/Sao_Paulo
ENABLE_FORWARDING=false
FORWARDER_URL=
```

### **Upload do credentials.json:**
1. **Vercel Dashboard** → **Settings** → **Environment Variables**
2. **Add** → **Name:** `GOOGLE_DRIVE_CREDENTIALS`
3. **Value:** (cole o conteúdo do arquivo JSON)
4. **Type:** `Secret`

## 🎯 **Benefícios da Solução:**

- ✅ **15GB gratuito** (vs 500MB Supabase)
- ✅ **Backup automático** (Google cuida)
- ✅ **Sincronização** entre dispositivos
- ✅ **Histórico** de versões
- ✅ **API robusta** e confiável
- ✅ **Sem custos** adicionais

---
*Guia criado em 16/10/2025*
