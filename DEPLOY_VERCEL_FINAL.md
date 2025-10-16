# 🚀 Deploy no Vercel - pieng-energy-meter

## ✅ Status Atual
- **GitHub:** ✅ Push realizado com sucesso
- **Repositório:** https://github.com/Flavioprogramador123/pieng-energy-meter/
- **vercel.json:** ✅ Corrigido (removido conflito builds/functions)

## 🌐 Deploy no Vercel

### 1. Acessar Vercel
1. Acesse: https://vercel.com/new
2. **Import Git Repository:** Selecione `pieng-energy-meter`
3. Clique em **"Import"**

### 2. Configurar Build Settings
- **Framework Preset:** Other
- **Root Directory:** `./` (raiz)
- **Build Command:** (deixe vazio)
- **Output Directory:** (deixe vazio)
- **Install Command:** `pip install -r requirements.txt`

### 3. Environment Variables
Adicione estas variáveis no Vercel:

```
APP_NAME=Energy Meter Master
API_PREFIX=/api
DATABASE_URL=sqlite:///./data/app.db
SCHEDULER_TIMEZONE=America/Sao_Paulo
ENABLE_FORWARDING=false
FORWARDER_URL=
PYTHONPATH=.
```

### 4. Deploy
- Clique em **"Deploy"**
- Aguarde o build (pode levar 2-3 minutos)

## 🔧 Configuração Corrigida

### vercel.json (Corrigido)
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "50mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "PYTHONPATH": "."
  }
}
```

### ❌ Erro Corrigido
**Problema:** `The functions property cannot be used in conjunction with the builds property`

**Solução:** Removida a propriedade `functions` e integrada a configuração no `builds`

## 🔗 URLs Após Deploy
- **App:** `https://pieng-energy-meter.vercel.app`
- **API:** `https://pieng-energy-meter.vercel.app/api/`
- **Dashboard:** `https://pieng-energy-meter.vercel.app/api/dashboard`
- **Docs:** `https://pieng-energy-meter.vercel.app/docs`
- **Health:** `https://pieng-energy-meter.vercel.app/`

## 📁 Estrutura para Deploy
```
pieng-energy-meter/
├── api/
│   └── index.py          # ✅ Entry point Vercel
├── app/
│   ├── main.py           # ✅ FastAPI app
│   ├── core/
│   ├── routers/
│   ├── services/
│   ├── connectors/
│   ├── templates/
│   └── static/
├── vercel.json           # ✅ Configuração corrigida
├── requirements.txt      # ✅ Dependências Python
└── README.md
```

## 🚀 Melhorias Futuras

### 📊 Persistência de Dados
- **Problema:** SQLite é temporário no Vercel
- **Soluções:**
  - **Supabase** (PostgreSQL gratuito)
  - **Railway** (PostgreSQL com 5GB grátis)
  - **Neon** (PostgreSQL serverless)
  - **PlanetScale** (MySQL serverless)

### ⏰ Scheduler Alternativo
- **Problema:** APScheduler não funciona bem em serverless
- **Soluções:**
  - **Cron-job.org** (gratuito, até 3 jobs)
  - **GitHub Actions** (para tarefas periódicas)
  - **Raspberry Pi local** (script Python + API)
  - **Vercel Cron** (funções agendadas)

### 📝 Logs e Monitoramento
- **Integrações sugeridas:**
  - **Logtail** (logs estruturados)
  - **Sentry** (monitoramento de erros)
  - **Telegram Bot** (notificações)
  - **Discord Webhook** (alertas)

### 📚 Documentação Automática
- **FastAPI Swagger:** `/docs` já disponível
- **Melhorias:**
  - Adicionar descrições detalhadas nos endpoints
  - Exemplos de request/response
  - Validação de schemas

### 🔐 Segurança
- **Autenticação JWT** para API
- **Rate limiting** para endpoints
- **CORS** configurado adequadamente
- **Validação de entrada** robusta

### 🌐 Escalabilidade
- **Multi-tenant** completo
- **Cache Redis** para performance
- **CDN** para assets estáticos
- **Load balancing** para alta disponibilidade

## ⚠️ Notas Importantes
- **SQLite:** Funciona no Vercel, mas dados são temporários
- **Scheduler:** Pode não funcionar em ambiente serverless
- **Modbus:** Requer conexão física (não funciona em cloud)
- **Tuya API:** Funcionará normalmente

## 🎯 Próximos Passos
1. ✅ Push para GitHub
2. 🔄 Deploy no Vercel
3. 🔄 Configurar environment variables
4. 🔄 Testar URLs

---
*Guia atualizado em 16/10/2025*
