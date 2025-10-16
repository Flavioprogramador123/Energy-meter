# 🚀 Guia Completo - Criar Repositório no GitHub

## 📋 **Opção 1: Via Interface Web (Mais Simples)**

### **Passo a Passo:**

1. **Acesse**: [github.com](https://github.com)
2. **Faça login** na sua conta GitHub
3. **Clique no botão verde**: "New" ou "+" → "New repository"
4. **Configure o repositório**:
   ```
   Repository name: Pieng_medidor
   Description: Sistema de monitoramento energético com PZEM-004T
   Visibility: Public (recomendado)
   ✅ Add a README file: NÃO marcar (já temos)
   ✅ Add .gitignore: NÃO marcar (já temos)
   ✅ Choose a license: Opcional
   ```
5. **Clique em**: "Create repository"

### **Após criar, execute estes comandos:**

```bash
# Conectar repositório local ao GitHub
git remote add origin https://github.com/SEU_USUARIO/Pieng_medidor.git

# Fazer push do código
git branch -M main
git push -u origin main
```

---

## 📋 **Opção 2: Via GitHub CLI (Após reiniciar terminal)**

### **Após reiniciar o terminal:**

```bash
# 1. Autenticar
gh auth login

# 2. Criar repositório e fazer push
gh repo create Pieng_medidor --public --description "Sistema de monitoramento energético com PZEM-004T" --source=. --remote=origin --push
```

---

## 📋 **Opção 3: Comandos Manuais**

### **Se preferir fazer manualmente:**

```bash
# 1. Adicionar remote (substitua SEU_USUARIO)
git remote add origin https://github.com/SEU_USUARIO/Pieng_medidor.git

# 2. Renomear branch para main
git branch -M main

# 3. Fazer push
git push -u origin main
```

---

## ✅ **Verificação Final:**

Após qualquer opção, verifique:

```bash
# Verificar remotes
git remote -v

# Verificar status
git status

# Verificar branches
git branch -a
```

---

## 🎯 **URLs do Repositório:**

Após criar, você terá:
- **Repositório**: `https://github.com/SEU_USUARIO/Pieng_medidor`
- **Clone**: `git clone https://github.com/SEU_USUARIO/Pieng_medidor.git`

---

## 🚀 **Deploy no Vercel:**

Após criar o repositório:

1. **Acesse**: [vercel.com](https://vercel.com)
2. **Import Project** → **GitHub**
3. **Selecione**: `Pieng_medidor`
4. **Configure** conforme `DEPLOY_VERCEL.md`
5. **Deploy automático**!

---

## ❓ **Dúvidas?**

- **Não tem conta GitHub?**: Crie em [github.com](https://github.com)
- **Esqueceu usuário?**: Verifique em [github.com/settings](https://github.com/settings)
- **Problemas com push?**: Verifique permissões do repositório
