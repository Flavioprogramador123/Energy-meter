@echo off
REM deploy_vercel.bat
REM Script para deploy automático no Vercel

echo 🚀 Deploy Automático para Vercel - Energy Meter Master
echo ============================================================

REM Verificar se está na pasta correta
if not exist "app\main.py" (
    echo ❌ Erro: Não está na pasta do projeto!
    echo    Execute este script na pasta: C:\Projetos\pieng-energy-meter
    pause
    exit /b 1
)

echo ✅ Pasta do projeto encontrada!

REM Verificar se o Vercel CLI está instalado
echo.
echo 🔍 Verificando Vercel CLI...
vercel --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Vercel CLI não encontrado!
    echo    Instalando Vercel CLI...
    npm install -g vercel
    if %errorlevel% neq 0 (
        echo ❌ Falha ao instalar Vercel CLI!
        pause
        exit /b 1
    )
    echo ✅ Vercel CLI instalado com sucesso!
) else (
    echo ✅ Vercel CLI encontrado!
)

REM Verificar se está logado no Vercel
echo.
echo 🔐 Verificando login no Vercel...
vercel whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Não está logado no Vercel!
    echo    Fazendo login...
    vercel login
    if %errorlevel% neq 0 (
        echo ❌ Falha no login!
        pause
        exit /b 1
    )
    echo ✅ Login realizado com sucesso!
) else (
    echo ✅ Já está logado no Vercel!
)

REM Verificar arquivos necessários
echo.
echo 📄 Verificando arquivos necessários...
if not exist "app\main.py" (
    echo ❌ app\main.py não encontrado!
    pause
    exit /b 1
)
if not exist "requirements.txt" (
    echo ❌ requirements.txt não encontrado!
    pause
    exit /b 1
)
if not exist "vercel.json" (
    echo ❌ vercel.json não encontrado!
    pause
    exit /b 1
)
if not exist "api\index.py" (
    echo ❌ api\index.py não encontrado!
    pause
    exit /b 1
)

echo ✅ Todos os arquivos necessários encontrados!

REM Verificar se há alterações não commitadas
echo.
echo 📝 Verificando status do Git...
git status --porcelain >nul 2>&1
if %errorlevel% eq 0 (
    echo ⚠️ Há alterações não commitadas
    set /p commit="Deseja fazer commit antes do deploy? (s/n): "
    if /i "%commit%"=="s" (
        echo 📝 Fazendo commit...
        git add .
        git commit -m "Deploy automático para Vercel"
        if %errorlevel% neq 0 (
            echo ❌ Falha no commit!
            pause
            exit /b 1
        )
        echo ✅ Commit realizado!
    )
) else (
    echo ✅ Nenhuma alteração pendente
)

REM Fazer push para GitHub (se necessário)
echo.
echo 📤 Verificando push para GitHub...
git remote -v >nul 2>&1
if %errorlevel% eq 0 (
    echo ✅ Remote origin configurado
    set /p push="Deseja fazer push para GitHub? (s/n): "
    if /i "%push%"=="s" (
        echo 📤 Fazendo push...
        git push origin master
        if %errorlevel% neq 0 (
            echo ❌ Falha no push!
            pause
            exit /b 1
        )
        echo ✅ Push realizado!
    )
) else (
    echo ⚠️ Remote origin não configurado
)

REM Deploy no Vercel
echo.
echo 🚀 Iniciando deploy no Vercel...
echo    Isso pode levar alguns minutos...

vercel --prod --yes
if %errorlevel% neq 0 (
    echo ❌ Falha no deploy!
    pause
    exit /b 1
)

echo ✅ Deploy realizado com sucesso!

REM Verificar status do deploy
echo.
echo 🔍 Verificando status do deploy...
vercel ls

REM Instruções finais
echo.
echo 🎉 Deploy Concluído!
echo ============================================================
echo 📋 Próximos passos:
echo 1. Configure as variáveis de ambiente no Vercel Dashboard
echo 2. Teste os endpoints da API
echo 3. Configure o Google Drive se necessário
echo 4. Monitore os logs no Vercel Dashboard
echo.
echo 🔗 Links úteis:
echo • Vercel Dashboard: https://vercel.com/dashboard
echo • Documentação: https://vercel.com/docs
echo • Suporte: https://vercel.com/support
echo.
echo ✨ Deploy realizado com sucesso!
pause
