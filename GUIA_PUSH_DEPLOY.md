# 🚀 Guia para Push e Deploy - pieng-energy-meter

## 📋 Passos para Push no GitHub

### 1. Criar Repositório no GitHub
1. Acesse: https://github.com/new
2. **Repository name:** `pieng-energy-meter`
3. **Description:** `Energy Meter Master Platform - Sistema de monitoramento de energia com Modbus RTU/RS485, Tuya API e análise de dados`
4. **Visibility:** Public ✅
5. **NÃO marque:** "Add a README file" (já temos)
6. **NÃO marque:** "Add .gitignore" (já temos)
7. **NÃO marque:** "Choose a license" (opcional)
8. Clique em **"Create repository"**

### 2. Configurar Remote (Execute no terminal)
```bash
# Substitua USERNAME pelo seu usuário do GitHub
git remote set-url origin https://github.com/USERNAME/pieng-energy-meter.git
```

### 3. Fazer Push
```bash
git push -u origin master
```

## 🌐 Deploy no Vercel

### 1. Conectar Repositório
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
```

### 4. Deploy
- Clique em **"Deploy"**
- Aguarde o build (pode levar alguns minutos)

## 📁 Estrutura do Projeto
```
pieng-energy-meter/
├── api/
│   └── index.py          # Entry point para Vercel
├── app/
│   ├── main.py           # FastAPI app
│   ├── core/
│   ├── routers/
│   ├── services/
│   ├── connectors/
│   ├── templates/
│   └── static/
├── vercel.json           # Configuração Vercel
├── requirements.txt      # Dependências Python
└── README.md
```

## ✅ Checklist
- [ ] Repositório criado no GitHub
- [ ] Remote configurado
- [ ] Push realizado
- [ ] Projeto conectado no Vercel
- [ ] Environment variables configuradas
- [ ] Deploy realizado

## 🔗 URLs Importantes
- **GitHub:** https://github.com/USERNAME/pieng-energy-meter
- **Vercel:** https://pieng-energy-meter.vercel.app
- **API Docs:** https://pieng-energy-meter.vercel.app/docs
- **Dashboard:** https://pieng-energy-meter.vercel.app/api/dashboard

---
*Guia criado em 16/10/2025*
