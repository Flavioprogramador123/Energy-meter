# 🗄️ Migração para Supabase - Exemplo Prático

## 📋 Passo a Passo

### 1. **Criar Projeto no Supabase**
1. Acesse: https://supabase.com/dashboard
2. Clique em "New Project"
3. **Name:** `pieng-energy-meter`
4. **Database Password:** (anote bem!)
5. **Region:** escolha mais próxima
6. Clique em "Create new project"

### 2. **Obter Credenciais**
No dashboard do Supabase:
- **Project URL:** `https://your-project.supabase.co`
- **API Key:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- **Database URL:** `postgresql://postgres:[password]@db.your-project.supabase.co:5432/postgres`

### 3. **Instalar Dependências**
```bash
pip install supabase psycopg2-binary
```

### 4. **Configurar Variáveis de Ambiente**
```env
# .env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_URL=postgresql://postgres:[password]@db.your-project.supabase.co:5432/postgres
```

### 5. **Criar Tabelas no Supabase**
```sql
-- SQL Editor no Supabase Dashboard
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    name VARCHAR(255) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    config JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE measurements (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    metric VARCHAR(100) NOT NULL,
    value DECIMAL(10,4) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE alarm_rules (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    name VARCHAR(255) NOT NULL,
    metric VARCHAR(100) NOT NULL,
    operator VARCHAR(10) NOT NULL,
    threshold DECIMAL(10,4) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE alarm_events (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES alarm_rules(id),
    device_id INTEGER REFERENCES devices(id),
    message TEXT NOT NULL,
    value DECIMAL(10,4) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

### 6. **Atualizar app/core/db.py**
```python
# app/core/db.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Usar PostgreSQL do Supabase
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")

if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(DATABASE_URL)
else:
    # Fallback para SQLite local
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

### 7. **Atualizar requirements.txt**
```txt
# Adicionar estas linhas
supabase==2.3.4
psycopg2-binary==2.9.9
```

### 8. **Testar Conexão**
```python
# test_supabase.py
import os
from supabase import create_client, Client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url, key)

# Testar inserção
result = supabase.table('clients').insert({
    "name": "Cliente Teste",
    "email": "teste@example.com"
}).execute()

print("✅ Conexão com Supabase funcionando!")
```

## 🔄 **Migração de Dados**

### **Script de Migração**
```python
# migrate_to_supabase.py
import sqlite3
import os
from supabase import create_client, Client

# Conectar ao SQLite local
sqlite_conn = sqlite3.connect('data/app.db')
sqlite_cursor = sqlite_conn.cursor()

# Conectar ao Supabase
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Migrar clientes
sqlite_cursor.execute("SELECT * FROM clients")
clients = sqlite_cursor.fetchall()

for client in clients:
    supabase.table('clients').insert({
        "id": client[0],
        "name": client[1],
        "email": client[2],
        "created_at": client[3]
    }).execute()

print("✅ Migração concluída!")
```

## 🚀 **Deploy com Supabase**

### **Environment Variables no Vercel**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_URL=postgresql://postgres:[password]@db.your-project.supabase.co:5432/postgres
```

### **Benefícios da Migração**
- ✅ **Dados persistentes** (não se perdem)
- ✅ **Backup automático** (diário)
- ✅ **Escalabilidade** (até 500MB gratuito)
- ✅ **API REST** automática
- ✅ **Real-time** subscriptions
- ✅ **Dashboard** web para gerenciar dados

## ⚠️ **Considerações**

### **Limitações do Plano Gratuito**
- 500MB de armazenamento
- 2GB de transferência/mês
- 50MB de upload de arquivos

### **Alternativas**
- **Railway:** 5GB gratuito
- **Neon:** 3GB gratuito
- **PlanetScale:** 1GB gratuito (MySQL)

---
*Guia criado em 16/10/2025*
