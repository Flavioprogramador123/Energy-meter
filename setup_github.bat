# Script para criar repositório no GitHub
# Execute estes comandos após reiniciar o terminal

# 1. Autenticar no GitHub CLI
gh auth login

# 2. Criar repositório no GitHub
gh repo create Pieng_medidor --public --description "Sistema de monitoramento energético com PZEM-004T" --source=. --remote=origin --push

# 3. Verificar se foi criado
git remote -v
