# 🔐 Guia Prático - Configurar Chaves Seguras

## ✅ **Status de Segurança Atual**

### **Arquivo .env:**
- ✅ **Protegido pelo .gitignore** 
- ✅ **NÃO será commitado** no GitHub
- ✅ **Chaves seguras** no ambiente local

### **Verificação:**
```bash
git status --ignored
# Resultado: .env não aparece (está sendo ignorado)
```

## 🚀 **Configuração no Vercel**

### **1. Acessar Vercel Dashboard**
1. Acesse: https://vercel.com/dashboard
2. Selecione: `pieng-energy-meter`
3. **Settings** → **Environment Variables**

### **2. Adicionar Variáveis**

#### **Variables (Públicas):**
```
APP_NAME = Energy Meter Master
API_PREFIX = /api
DATABASE_URL = sqlite:///./data/app.db
SCHEDULER_TIMEZONE = America/Sao_Paulo
ENABLE_FORWARDING = false
FORWARDER_URL = 
PYTHONPATH = .
```

#### **Secrets (Privadas):**
```
GOOGLE_DRIVE_CREDENTIALS = {"type":"service_account",...}
GOOGLE_DRIVE_FOLDER_ID = 1ABC123DEF456GHI789JKL
TELEGRAM_BOT_TOKEN = 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID = 123456789
```

### **3. Configurar Ambientes**
- **Production:** ✅ Todas as variáveis
- **Preview:** ✅ Todas as variáveis  
- **Development:** ✅ Todas as variáveis

## 📋 **Checklist de Segurança**

### **Local:**
- [x] ✅ Arquivo `.env` no `.gitignore`
- [x] ✅ Arquivo `env.example` como template
- [x] ✅ Chaves não commitadas
- [x] ✅ Testes funcionando

### **Vercel:**
- [ ] 🔄 Variáveis públicas configuradas
- [ ] 🔄 Secrets configurados
- [ ] 🔄 Deploy testado

## 🛠️ **Exemplo de Uso no Código**

```python
# app/core/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Energy Meter Master"
    api_prefix: str = "/api"
    database_url: str = "sqlite:///./data/app.db"
    
    # Chaves privadas
    google_drive_credentials: str | None = None
    google_drive_folder_id: str | None = None
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## 🔍 **Verificação de Segurança**

### **Comandos para Verificar:**
```bash
# Verificar se .env está sendo ignorado
git status --ignored

# Verificar se há chaves no código
grep -r "sk-" . --exclude-dir=.git
grep -r "token" . --exclude-dir=.git
grep -r "key" . --exclude-dir=.git
```

### **Resultado Esperado:**
- ✅ `.env` não aparece no `git status`
- ✅ Nenhuma chave encontrada no código
- ✅ Apenas templates em `env.example`

## 🚨 **Em Caso de Vazamento**

### **Se uma chave vazar:**
1. **Revogar** a chave imediatamente
2. **Gerar** nova chave
3. **Atualizar** configurações
4. **Verificar** logs de uso
5. **Notificar** equipe

## 📝 **Próximos Passos**

1. **Criar arquivo .env** local com suas chaves
2. **Configurar variáveis** no Vercel
3. **Fazer deploy** e testar
4. **Verificar** se tudo funciona

---
*Guia prático criado em 16/10/2025*
