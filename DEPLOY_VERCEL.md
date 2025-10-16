# 🚀 Deploy no Vercel - Pieng Medidor Master

## 📋 Pré-requisitos

1. **Conta no Vercel**: [vercel.com](https://vercel.com)
2. **GitHub/GitLab**: Repositório do projeto
3. **Python 3.8+**: Suportado pelo Vercel

## 🔧 Configuração

### 1. Conectar Repositório

```bash
# No Vercel Dashboard:
# 1. Import Project
# 2. Conectar GitHub/GitLab
# 3. Selecionar repositório
```

### 2. Configurações do Build

- **Framework Preset**: Other
- **Build Command**: `pip install -r requirements.txt`
- **Output Directory**: `api`
- **Install Command**: `pip install -r requirements.txt`

### 3. Variáveis de Ambiente

Configure no Vercel Dashboard:

```env
APP_NAME=Pieng Medidor Master
API_PREFIX=/api
DATABASE_URL=sqlite:///./pieng_medidor.db
SCHEDULER_TIMEZONE=America/Sao_Paulo
ENABLE_FORWARDING=false
FORWARDER_URL=
```

## 📁 Estrutura para Vercel

```
├── api/
│   └── index.py          # Entry point do Vercel
├── app/                  # Código da aplicação
├── vercel.json          # Configuração do Vercel
├── requirements.txt     # Dependências Python
└── README.md
```

## 🌐 URLs de Deploy

Após o deploy, você terá:

- **API**: `https://seu-projeto.vercel.app/api/`
- **Dashboard**: `https://seu-projeto.vercel.app/api/dashboard`
- **Docs**: `https://seu-projeto.vercel.app/docs`

## ⚠️ Limitações do Vercel

1. **Serverless**: Não mantém estado entre requests
2. **Timeout**: 30s máximo por função
3. **Banco de dados**: SQLite não persistente
4. **Polling**: Não funciona em ambiente serverless

## 🔄 Alternativas para Produção

Para uso em produção com hardware real:

1. **Railway**: Suporte completo a Python
2. **Heroku**: Deploy tradicional
3. **DigitalOcean**: VPS dedicado
4. **AWS/GCP**: Infraestrutura completa

## 📝 Comandos Úteis

```bash
# Deploy local para teste
vercel dev

# Deploy para produção
vercel --prod

# Ver logs
vercel logs
```

## 🎯 Próximos Passos

1. Configurar banco de dados persistente (PostgreSQL)
2. Implementar WebSockets para tempo real
3. Configurar CI/CD automático
4. Adicionar monitoramento e alertas
