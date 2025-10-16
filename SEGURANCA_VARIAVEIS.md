# 🔐 Configuração Segura de Variáveis de Ambiente

## ✅ **Status Atual - Segurança Garantida**

### **Arquivo .env Local:**
- ✅ **Protegido pelo .gitignore** (linha 25)
- ✅ **NÃO será commitado** no GitHub
- ✅ **Chaves seguras** no ambiente local

### **Arquivo env.example:**
- ✅ **Template público** sem chaves reais
- ✅ **Exemplo seguro** para outros desenvolvedores

## 🚀 **Configuração no Vercel**

### **1. Acessar Configurações do Projeto**
1. Acesse: https://vercel.com/dashboard
2. Selecione o projeto `pieng-energy-meter`
3. **Settings** → **Environment Variables**

### **2. Adicionar Variáveis de Ambiente**

#### **Variáveis Públicas (Variables):**
```
APP_NAME=Energy Meter Master
API_PREFIX=/api
DATABASE_URL=sqlite:///./data/app.db
SCHEDULER_TIMEZONE=America/Sao_Paulo
ENABLE_FORWARDING=false
FORWARDER_URL=
PYTHONPATH=.
```

#### **Variáveis Privadas (Secrets):**
```
GOOGLE_DRIVE_CREDENTIALS={"type":"service_account",...}
GOOGLE_DRIVE_FOLDER_ID=1ABC123DEF456GHI789JKL
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **3. Configurar Ambientes**
- **Production:** ✅ Todas as variáveis
- **Preview:** ✅ Todas as variáveis
- **Development:** ✅ Todas as variáveis

## 🔒 **Boas Práticas de Segurança**

### **✅ O que FAZER:**
- ✅ Usar **Secrets** para chaves sensíveis
- ✅ Usar **Variables** para configurações públicas
- ✅ **Nunca** commitar arquivos `.env`
- ✅ **Sempre** usar `env.example` como template
- ✅ **Rotacionar** chaves periodicamente
- ✅ **Monitorar** uso das APIs

### **❌ O que NÃO FAZER:**
- ❌ **Nunca** commitar arquivos `.env`
- ❌ **Nunca** colocar chaves no código
- ❌ **Nunca** usar chaves em logs
- ❌ **Nunca** compartilhar chaves por email/chat
- ❌ **Nunca** usar chaves de produção em desenvolvimento

## 📋 **Checklist de Segurança**

### **Local (Desenvolvimento):**
- [ ] ✅ Arquivo `.env` no `.gitignore`
- [ ] ✅ Arquivo `env.example` atualizado
- [ ] ✅ Chaves não commitadas
- [ ] ✅ Testes funcionando localmente

### **Vercel (Produção):**
- [ ] 🔄 Variáveis públicas configuradas
- [ ] 🔄 Secrets configurados
- [ ] 🔄 Ambientes configurados
- [ ] 🔄 Deploy testado

## 🛠️ **Exemplo de Configuração**

### **Arquivo .env (Local - NÃO COMMITAR):**
```env
# Configurações públicas
APP_NAME=Energy Meter Master
API_PREFIX=/api
DATABASE_URL=sqlite:///./data/app.db
SCHEDULER_TIMEZONE=America/Sao_Paulo
ENABLE_FORWARDING=false
FORWARDER_URL=
PYTHONPATH=.

# Chaves privadas (NUNCA COMMITAR)
GOOGLE_DRIVE_CREDENTIALS={"type":"service_account",...}
GOOGLE_DRIVE_FOLDER_ID=1ABC123DEF456GHI789JKL
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

### **Arquivo env.example (Público - COMMITAR):**
```env
# Configurações públicas
APP_NAME=Energy Meter Master
API_PREFIX=/api
DATABASE_URL=sqlite:///./data/app.db
SCHEDULER_TIMEZONE=America/Sao_Paulo
ENABLE_FORWARDING=false
FORWARDER_URL=
PYTHONPATH=.

# Chaves privadas (substituir por valores reais)
GOOGLE_DRIVE_CREDENTIALS=your-google-drive-credentials-json
GOOGLE_DRIVE_FOLDER_ID=your-google-drive-folder-id
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
```

## 🔍 **Verificação de Segurança**

### **Comando para Verificar:**
```bash
# Verificar se .env está sendo ignorado
git status --ignored

# Verificar se há chaves no código
grep -r "sk-" .
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
3. **Atualizar** todas as configurações
4. **Verificar** logs de uso suspeito
5. **Notificar** equipe se necessário

---
*Guia de segurança criado em 16/10/2025*
