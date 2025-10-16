# deploy_vercel.ps1
# Script para deploy automático no Vercel

Write-Host "🚀 Deploy Automático para Vercel - Energy Meter Master" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

# Verificar se está na pasta correta
$currentPath = Get-Location
Write-Host "📁 Pasta atual: $currentPath" -ForegroundColor Yellow

# Verificar se é a pasta do projeto
if (-not (Test-Path "app\main.py")) {
    Write-Host "❌ Erro: Não está na pasta do projeto!" -ForegroundColor Red
    Write-Host "   Execute este script na pasta: C:\Projetos\pieng-energy-meter" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Pasta do projeto encontrada!" -ForegroundColor Green

# Verificar se o Vercel CLI está instalado
Write-Host "`n🔍 Verificando Vercel CLI..." -ForegroundColor Yellow
try {
    $vercelVersion = vercel --version 2>$null
    if ($vercelVersion) {
        Write-Host "✅ Vercel CLI encontrado: $vercelVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Vercel CLI não encontrado!" -ForegroundColor Red
        Write-Host "   Instalando Vercel CLI..." -ForegroundColor Yellow
        
        # Instalar Vercel CLI
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
        
        # Fazer login no Vercel
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

# Verificar se o projeto já existe no Vercel
Write-Host "`n📋 Verificando projeto no Vercel..." -ForegroundColor Yellow
try {
    $vercelProjects = vercel ls 2>$null
    if ($vercelProjects -match "pieng-energy-meter") {
        Write-Host "✅ Projeto encontrado no Vercel!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Projeto não encontrado, será criado automaticamente" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Não foi possível verificar projetos existentes" -ForegroundColor Yellow
}

# Verificar arquivos necessários
Write-Host "`n📄 Verificando arquivos necessários..." -ForegroundColor Yellow
$requiredFiles = @(
    "app\main.py",
    "requirements.txt",
    "vercel.json",
    "api\index.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file não encontrado!" -ForegroundColor Red
        exit 1
    }
}

# Verificar se há alterações não commitadas
Write-Host "`n📝 Verificando status do Git..." -ForegroundColor Yellow
try {
    $gitStatus = git status --porcelain 2>$null
    if ($gitStatus) {
        Write-Host "⚠️ Há alterações não commitadas:" -ForegroundColor Yellow
        Write-Host $gitStatus -ForegroundColor Yellow
        
        $commit = Read-Host "Deseja fazer commit antes do deploy? (s/n)"
        if ($commit -eq "s" -or $commit -eq "S") {
            Write-Host "📝 Fazendo commit..." -ForegroundColor Yellow
            git add .
            git commit -m "Deploy automático para Vercel"
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Commit realizado!" -ForegroundColor Green
            } else {
                Write-Host "❌ Falha no commit!" -ForegroundColor Red
                exit 1
            }
        }
    } else {
        Write-Host "✅ Nenhuma alteração pendente" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Não foi possível verificar status do Git" -ForegroundColor Yellow
}

# Fazer push para GitHub (se necessário)
Write-Host "`n📤 Verificando push para GitHub..." -ForegroundColor Yellow
try {
    $gitRemote = git remote -v 2>$null
    if ($gitRemote -match "origin") {
        Write-Host "✅ Remote origin configurado" -ForegroundColor Green
        
        $push = Read-Host "Deseja fazer push para GitHub? (s/n)"
        if ($push -eq "s" -or $push -eq "S") {
            Write-Host "📤 Fazendo push..." -ForegroundColor Yellow
            git push origin master
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Push realizado!" -ForegroundColor Green
            } else {
                Write-Host "❌ Falha no push!" -ForegroundColor Red
                exit 1
            }
        }
    } else {
        Write-Host "⚠️ Remote origin não configurado" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Não foi possível verificar remote do Git" -ForegroundColor Yellow
}

# Deploy no Vercel
Write-Host "`n🚀 Iniciando deploy no Vercel..." -ForegroundColor Yellow
Write-Host "   Isso pode levar alguns minutos..." -ForegroundColor Yellow

try {
    # Deploy com confirmação automática
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
    } else {
        Write-Host "❌ Falha no deploy!" -ForegroundColor Red
        Write-Host "`n📊 Erro do Deploy:" -ForegroundColor Red
        Write-Host $deployOutput -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Erro durante o deploy: $_" -ForegroundColor Red
    exit 1
}

# Verificar status do deploy
Write-Host "`n🔍 Verificando status do deploy..." -ForegroundColor Yellow
try {
    $vercelStatus = vercel ls 2>$null
    Write-Host "📋 Projetos no Vercel:" -ForegroundColor Cyan
    Write-Host $vercelStatus -ForegroundColor White
} catch {
    Write-Host "⚠️ Não foi possível verificar status" -ForegroundColor Yellow
}

# Instruções finais
Write-Host "`n🎉 Deploy Concluído!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Configure as variáveis de ambiente no Vercel Dashboard" -ForegroundColor White
Write-Host "2. Teste os endpoints da API" -ForegroundColor White
Write-Host "3. Configure o Google Drive se necessário" -ForegroundColor White
Write-Host "4. Monitore os logs no Vercel Dashboard" -ForegroundColor White

Write-Host "`n🔗 Links úteis:" -ForegroundColor Yellow
Write-Host "• Vercel Dashboard: https://vercel.com/dashboard" -ForegroundColor White
Write-Host "• Documentação: https://vercel.com/docs" -ForegroundColor White
Write-Host "• Suporte: https://vercel.com/support" -ForegroundColor White

Write-Host "`n✨ Deploy realizado com sucesso!" -ForegroundColor Green