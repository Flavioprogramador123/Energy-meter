# 🚀 Plano de Melhorias - pieng-energy-meter

## 📋 Prioridades de Implementação

### 🔥 **Alta Prioridade (Implementar Primeiro)**

#### 1. **Persistência de Dados - Supabase**
```bash
# Instalar dependências
pip install supabase psycopg2-binary

# Configurar variáveis de ambiente
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
DATABASE_URL=postgresql://user:pass@host:port/db
```

**Benefícios:**
- ✅ Dados persistentes
- ✅ 500MB gratuito
- ✅ API REST automática
- ✅ Real-time subscriptions

#### 2. **Scheduler Alternativo - Vercel Cron**
```python
# api/cron.py
from app.services.pollers import poll_all_devices

def handler(request):
    """Função chamada pelo Vercel Cron"""
    poll_all_devices()
    return {"status": "success"}
```

**Configuração no vercel.json:**
```json
{
  "crons": [
    {
      "path": "/api/cron",
      "schedule": "*/30 * * * *"
    }
  ]
}
```

#### 3. **Logs Estruturados - Logtail**
```python
# app/core/logging.py
import structlog
from logtail import LogtailHandler

logger = structlog.get_logger()
logger.addHandler(LogtailHandler("your-source-token"))
```

### 🟡 **Média Prioridade**

#### 4. **Notificações - Telegram Bot**
```python
# app/services/notifications.py
import requests

def send_telegram_alert(message: str):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    requests.post(url, data=data)
```

#### 5. **Autenticação JWT**
```python
# app/core/auth.py
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

#### 6. **Rate Limiting**
```python
# app/core/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/ingest")
@limiter.limit("10/minute")
async def ingest_data(request: Request, ...):
    # endpoint logic
```

### 🟢 **Baixa Prioridade (Futuro)**

#### 7. **Cache Redis**
```python
# app/core/cache.py
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiry=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiry, json.dumps(result))
            return result
        return wrapper
    return decorator
```

#### 8. **Multi-tenant Completo**
```python
# app/core/tenant.py
from sqlalchemy import event
from sqlalchemy.orm import Session

def add_tenant_filter(query, tenant_id):
    return query.filter(Client.id == tenant_id)

# Middleware para extrair tenant_id do header
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    tenant_id = request.headers.get("X-Tenant-ID")
    request.state.tenant_id = tenant_id
    response = await call_next(request)
    return response
```

## 🛠️ **Implementação Passo a Passo**

### **Fase 1: Infraestrutura (Semana 1)**
1. ✅ Migrar para Supabase PostgreSQL
2. ✅ Configurar Vercel Cron para scheduler
3. ✅ Implementar logs estruturados

### **Fase 2: Segurança (Semana 2)**
1. ✅ Implementar autenticação JWT
2. ✅ Adicionar rate limiting
3. ✅ Configurar CORS adequadamente

### **Fase 3: Notificações (Semana 3)**
1. ✅ Integrar Telegram Bot
2. ✅ Configurar Discord Webhook
3. ✅ Implementar alertas por email

### **Fase 4: Performance (Semana 4)**
1. ✅ Implementar cache Redis
2. ✅ Otimizar queries do banco
3. ✅ Configurar CDN para assets

## 📊 **Métricas de Sucesso**

### **Performance**
- ⏱️ Tempo de resposta < 200ms
- 📈 Uptime > 99.9%
- 💾 Uso de memória < 512MB

### **Segurança**
- 🔐 Autenticação obrigatória
- 🛡️ Rate limiting ativo
- 📝 Logs de auditoria completos

### **Usabilidade**
- 📱 Interface responsiva
- 🔔 Notificações em tempo real
- 📊 Dashboard intuitivo

## 🔗 **Recursos Úteis**

### **Documentação**
- [Supabase Docs](https://supabase.com/docs)
- [Vercel Cron](https://vercel.com/docs/cron-jobs)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

### **Ferramentas**
- [Logtail](https://logtail.com/) - Logs estruturados
- [Sentry](https://sentry.io/) - Monitoramento de erros
- [Telegram Bot API](https://core.telegram.org/bots/api)

### **Tutoriais**
- [JWT com FastAPI](https://testdriven.io/blog/fastapi-jwt-auth/)
- [Redis com Python](https://redis-py.readthedocs.io/)
- [Multi-tenant Architecture](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)

---
*Plano criado em 16/10/2025 - Atualize conforme necessário*
