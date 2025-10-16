# deploy_complete.ps1
# Script completo para deploy no Vercel (incluindo configuração de variáveis)

Write-Host "🚀 Deploy Completo para Vercel - Energy Meter Master" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan

# Verificar se está na pasta correta
$currentPath = Get-Location
Write-Host "📁 Pasta atual: $currentPath" -ForegroundColor Yellow

if (-not (Test-Path "app\main.py")) {
    Write-Host "❌ Erro: Não está na pasta do projeto!" -ForegroundColor Red
    Write-Host "   Execute este script na pasta: C:\Projetos\pieng-energy-meter" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Pasta do projeto encontrada!" -ForegroundColor Green

# Função para verificar e instalar Vercel CLI
function Install-VercelCLI {
    Write-Host "🔍 Verificando Vercel CLI..." -ForegroundColor Yellow
    try {
        $vercelVersion = vercel --version 2>$null
        if ($vercelVersion) {
            Write-Host "✅ Vercel CLI encontrado: $vercelVersion" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Vercel CLI não encontrado!" -ForegroundColor Red
            Write-Host "   Instalando Vercel CLI..." -ForegroundColor Yellow
            npm install -g vercel
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Vercel CLI instalado com sucesso!" -ForegroundColor Green
                return $true
            } else {
                Write-Host "❌ Falha ao instalar Vercel CLI!" -ForegroundColor Red
                return $false
            }
        }
    } catch {
        Write-Host "❌ Erro ao verificar Vercel CLI: $_" -ForegroundColor Red
        return $false
    }
}

# Função para fazer login no Vercel
function Login-Vercel {
    Write-Host "🔐 Verificando login no Vercel..." -ForegroundColor Yellow
    try {
        $vercelWho = vercel whoami 2>$null
        if ($vercelWho) {
            Write-Host "✅ Logado como: $vercelWho" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Não está logado no Vercel!" -ForegroundColor Red
            Write-Host "   Fazendo login..." -ForegroundColor Yellow
            vercel login
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Login realizado com sucesso!" -ForegroundColor Green
                return $true
            } else {
                Write-Host "❌ Falha no login!" -ForegroundColor Red
                return $false
            }
        }
    } catch {
        Write-Host "❌ Erro ao verificar login: $_" -ForegroundColor Red
        return $false
    }
}

# Função para configurar variáveis de ambiente
function Configure-EnvironmentVariables {
    Write-Host "`n🔧 Configurando variáveis de ambiente..." -ForegroundColor Yellow
    
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
        "LOG_LEVEL" = "INFO"
        "LOG_FORMAT" = "json"
        "SECRET_KEY" = "sua_chave_secreta_muito_longa_e_complexa"
        "JWT_SECRET_KEY" = "sua_jwt_secret_key"
        "JWT_ALGORITHM" = "HS256"
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES" = "30"
        "RATE_LIMIT_REQUESTS" = "100"
        "RATE_LIMIT_WINDOW" = "60"
        "CORS_ORIGINS" = "https://seu-frontend.com,https://localhost:3000"
        "CORS_METHODS" = "GET,POST,PUT,DELETE"
        "CORS_HEADERS" = "*"
        "DEBUG" = "false"
        "ENVIRONMENT" = "production"
    }
    
    $configureEnv = Read-Host "Deseja configurar as variáveis de ambiente? (s/n)"
    if ($configureEnv -eq "s" -or $configureEnv -eq "S") {
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
        Write-Host "✅ Variáveis de ambiente configuradas!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Configuração de variáveis cancelada!" -ForegroundColor Yellow
    }
}

# Função para fazer deploy
function Deploy-Vercel {
    Write-Host "`n🚀 Iniciando deploy no Vercel..." -ForegroundColor Yellow
    Write-Host "   Isso pode levar alguns minutos..." -ForegroundColor Yellow
    
    try {
        $deployResult = vercel --prod --yes 2>&1
        $deployOutput = $deployResult | Out-String
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Deploy realizado com sucesso!" -ForegroundColor Green
            Write-Host "`n📊 Resultado do Deploy:" -ForegroundColor Cyan
            Write-Host $deployOutput -ForegroundColor White
            
            # Extrair URL do deploy
            if ($deployOutput -match "https://[^\s]+") {
                $deployUrl = $matches[0]
                Write-Host "`n🌐 URL do Deploy: $deployUrl" -ForegroundColor Green
                Write-Host "   Abra no navegador para testar!" -ForegroundColor Yellow
            }
            return $true
        } else {
            Write-Host "❌ Falha no deploy!" -ForegroundColor Red
            Write-Host "`n📊 Erro do Deploy:" -ForegroundColor Red
            Write-Host $deployOutput -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Erro durante o deploy: $_" -ForegroundColor Red
        return $false
    }
}

# Executar o processo completo
Write-Host "`n🔄 Iniciando processo de deploy completo..." -ForegroundColor Yellow

# 1. Instalar Vercel CLI
if (-not (Install-VercelCLI)) {
    exit 1
}

# 2. Fazer login
if (-not (Login-Vercel)) {
    exit 1
}

# 3. Verificar arquivos necessários
Write-Host "`n📄 Verificando arquivos necessários..." -ForegroundColor Yellow
$requiredFiles = @("app\main.py", "requirements.txt", "vercel.json", "api\index.py")
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file não encontrado!" -ForegroundColor Red
        exit 1
    }
}

# 4. Configurar variáveis de ambiente
Configure-EnvironmentVariables

# 5. Fazer deploy
if (-not (Deploy-Vercel)) {
    exit 1
}

# 6. Verificar status final
Write-Host "`n🔍 Verificando status final..." -ForegroundColor Yellow
try {
    $vercelStatus = vercel ls 2>$null
    Write-Host "📋 Projetos no Vercel:" -ForegroundColor Cyan
    Write-Host $vercelStatus -ForegroundColor White
} catch {
    Write-Host "⚠️ Não foi possível verificar status" -ForegroundColor Yellow
}

# Instruções finais
Write-Host "`n🎉 Deploy Completo Concluído!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Teste os endpoints da API" -ForegroundColor White
Write-Host "2. Configure o Google Drive se necessário" -ForegroundColor White
Write-Host "3. Monitore os logs no Vercel Dashboard" -ForegroundColor White
Write-Host "4. Configure notificações se necessário" -ForegroundColor White

Write-Host "`n🔗 Links úteis:" -ForegroundColor Yellow
Write-Host "• Vercel Dashboard: https://vercel.com/dashboard" -ForegroundColor White
Write-Host "• Documentação: https://vercel.com/docs" -ForegroundColor White
Write-Host "• Suporte: https://vercel.com/support" -ForegroundColor White

Write-Host "`n✨ Deploy completo realizado com sucesso!" -ForegroundColor Green
