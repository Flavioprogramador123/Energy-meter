# configure_vercel_env.ps1
# Script para configurar variáveis de ambiente no Vercel

Write-Host "🔐 Configuração de Variáveis de Ambiente no Vercel" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

# Verificar se o Vercel CLI está instalado
Write-Host "🔍 Verificando Vercel CLI..." -ForegroundColor Yellow
try {
    $vercelVersion = vercel --version 2>$null
    if ($vercelVersion) {
        Write-Host "✅ Vercel CLI encontrado: $vercelVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Vercel CLI não encontrado!" -ForegroundColor Red
        Write-Host "   Instalando Vercel CLI..." -ForegroundColor Yellow
        npm install -g vercel
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Vercel CLI instalado com sucesso!" -ForegroundColor Green
        } else {
            Write-Host "❌ Falha ao instalar Vercel CLI!" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "❌ Erro ao verificar Vercel CLI: $_" -ForegroundColor Red
    exit 1
}

# Verificar se está logado no Vercel
Write-Host "`n🔐 Verificando login no Vercel..." -ForegroundColor Yellow
try {
    $vercelWho = vercel whoami 2>$null
    if ($vercelWho) {
        Write-Host "✅ Logado como: $vercelWho" -ForegroundColor Green
    } else {
        Write-Host "❌ Não está logado no Vercel!" -ForegroundColor Red
        Write-Host "   Fazendo login..." -ForegroundColor Yellow
        vercel login
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Login realizado com sucesso!" -ForegroundColor Green
        } else {
            Write-Host "❌ Falha no login!" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "❌ Erro ao verificar login: $_" -ForegroundColor Red
    exit 1
}

# Lista de variáveis de ambiente
$envVars = @{
    "APP_NAME" = "Energy Meter Master"
    "API_PREFIX" = "/api"
    "DATABASE_URL" = "sqlite:///./data/app.db"
    "SCHEDULER_TIMEZONE" = "America/Sao_Paulo"
    "GOOGLE_DRIVE_CREDENTIALS_FILE" = "credentials.json"
    "GOOGLE_DRIVE_FOLDER_ID" = "1ABC123DEF456GHI789JKL"
    "ENABLE_FORWARDING" = "true"
    "FORWARDER_URL" = "https://seu-slave-platform.com/api/ingest"
    "MODBUS_SERIAL_PORT" = "COM3"
    "MODBUS_BAUDRATE" = "9600"
    "MODBUS_TIMEOUT" = "1.0"
    "MODBUS_RETRIES" = "3"
    "MODBUS_TCP_HOST" = "192.168.1.100"
    "MODBUS_TCP_PORT" = "502"
    "MODBUS_TCP_UNIT_ID" = "1"
    "TUYA_API_KEY" = "sua_tuya_api_key"
    "TUYA_API_SECRET" = "sua_tuya_api_secret"
    "TUYA_API_REGION" = "us"
    "TUYA_API_BASE_URL" = "https://openapi.tuyaus.com"
    "LOG_LEVEL" = "INFO"
    "LOG_FORMAT" = "json"
    "LOG_FILE" = "logs/app.log"
    "SECRET_KEY" = "sua_chave_secreta_muito_longa_e_complexa"
    "JWT_SECRET_KEY" = "sua_jwt_secret_key"
    "JWT_ALGORITHM" = "HS256"
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES" = "30"
    "RATE_LIMIT_REQUESTS" = "100"
    "RATE_LIMIT_WINDOW" = "60"
    "CORS_ORIGINS" = "https://seu-frontend.com,https://localhost:3000"
    "CORS_METHODS" = "GET,POST,PUT,DELETE"
    "CORS_HEADERS" = "*"
    "TELEGRAM_BOT_TOKEN" = "seu_telegram_bot_token"
    "TELEGRAM_CHAT_ID" = "seu_chat_id"
    "DISCORD_WEBHOOK_URL" = "https://discord.com/api/webhooks/..."
    "SENTRY_DSN" = "https://sua_sentry_dsn"
    "LOGTAIL_TOKEN" = "seu_logtail_token"
    "BACKUP_ENABLED" = "true"
    "BACKUP_INTERVAL_HOURS" = "24"
    "BACKUP_RETENTION_DAYS" = "30"
    "DEBUG" = "false"
    "ENVIRONMENT" = "production"
}

Write-Host "`n📋 Variáveis de Ambiente Disponíveis:" -ForegroundColor Yellow
Write-Host "Total: $($envVars.Count) variáveis" -ForegroundColor White

# Mostrar variáveis críticas
$criticalVars = @("APP_NAME", "API_PREFIX", "DATABASE_URL", "SCHEDULER_TIMEZONE")
Write-Host "`n🚨 Variáveis Críticas (Obrigatórias):" -ForegroundColor Red
foreach ($var in $criticalVars) {
    Write-Host "   $var = $($envVars[$var])" -ForegroundColor White
}

# Mostrar variáveis do Google Drive
$gdriveVars = @("GOOGLE_DRIVE_CREDENTIALS_FILE", "GOOGLE_DRIVE_FOLDER_ID")
Write-Host "`n☁️ Variáveis do Google Drive:" -ForegroundColor Blue
foreach ($var in $gdriveVars) {
    Write-Host "   $var = $($envVars[$var])" -ForegroundColor White
}

# Mostrar variáveis do Modbus
$modbusVars = @("MODBUS_SERIAL_PORT", "MODBUS_BAUDRATE", "MODBUS_TIMEOUT")
Write-Host "`n🔌 Variáveis do Modbus:" -ForegroundColor Cyan
foreach ($var in $modbusVars) {
    Write-Host "   $var = $($envVars[$var])" -ForegroundColor White
}

# Perguntar se quer configurar todas as variáveis
Write-Host "`n❓ Deseja configurar todas as variáveis de ambiente?" -ForegroundColor Yellow
$configureAll = Read-Host "Digite 's' para sim, 'n' para não"

if ($configureAll -eq "s" -or $configureAll -eq "S") {
    Write-Host "`n🔧 Configurando variáveis de ambiente..." -ForegroundColor Yellow
    
    foreach ($var in $envVars.Keys) {
        Write-Host "   Configurando $var..." -ForegroundColor White
        try {
            vercel env add $var --value $envVars[$var] --scope production
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   ✅ $var configurada!" -ForegroundColor Green
            } else {
                Write-Host "   ❌ Falha ao configurar $var" -ForegroundColor Red
            }
        } catch {
            Write-Host "   ❌ Erro ao configurar $var: $_" -ForegroundColor Red
        }
    }
    
    Write-Host "`n✅ Configuração concluída!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️ Configuração cancelada!" -ForegroundColor Yellow
    Write-Host "   Você pode configurar manualmente no Vercel Dashboard" -ForegroundColor White
}

# Instruções finais
Write-Host "`n📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Configure as variáveis específicas do seu ambiente" -ForegroundColor White
Write-Host "2. Faça o deploy do projeto" -ForegroundColor White
Write-Host "3. Teste os endpoints da API" -ForegroundColor White
Write-Host "4. Monitore os logs no Vercel Dashboard" -ForegroundColor White

Write-Host "`n🔗 Links úteis:" -ForegroundColor Yellow
Write-Host "• Vercel Dashboard: https://vercel.com/dashboard" -ForegroundColor White
Write-Host "• Documentação: https://vercel.com/docs" -ForegroundColor White
Write-Host "• Suporte: https://vercel.com/support" -ForegroundColor White

Write-Host "`n✨ Configuração concluída!" -ForegroundColor Green
