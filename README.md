# 🎵 YTMusic Commits

Automação que busca suas **3 músicas mais ouvidas no YouTube Music** no dia anterior e faz um commit no GitHub toda vez que você liga o PC.

---

## 📁 Estrutura

```
ytmusic-commits/
├── HISTÓRICO.md          ← gerado automaticamente
├── commit_music.sh       ← script principal (roda no boot)
├── ytmusic-commit.service← serviço systemd
└── scripts/
    ├── fetch_music.py    ← busca e filtra as músicas
    └── setup_auth.py     ← configuração única de autenticação
```

---

## 🚀 Instalação passo a passo

### 1. Clone ou crie o repositório no GitHub

Crie um repositório novo em https://github.com/new (pode ser privado), depois:

```bash
git clone git@github.com:SEU_USUARIO/ytmusic-commits.git
cd ytmusic-commits
```

Ou, se preferir iniciar do zero localmente:

```bash
mkdir ~/ytmusic-commits && cd ~/ytmusic-commits
git init
git remote add origin git@github.com:SEU_USUARIO/NOME_DO_REPO.git
```

Copie todos os arquivos deste projeto para dentro da pasta.

---

### 2. Instale as dependências

```bash
pip install ytmusicapi
```

---

### 3. Configure a autenticação (feito uma única vez)

```bash
python scripts/setup_auth.py
```

Siga as instruções na tela:
1. Abra o YouTube Music no navegador e faça login
2. Aperte **F12** → aba **Network**
3. Atualize a página (**F5**)
4. Clique em qualquer requisição para `music.youtube.com`
5. Copie o bloco de **Request Headers** e cole no terminal

Isso gera o arquivo `scripts/oauth.json` com seus cookies de autenticação.

> ⚠️ Não faça commit do `oauth.json`! Ele já está no `.gitignore`.

---

### 4. Teste o script manualmente

```bash
python scripts/fetch_music.py
```

Se tudo certo, o arquivo `HISTÓRICO.md` será criado/atualizado.

---

### 5. Ajuste o script shell

Abra `commit_music.sh` e verifique:

```bash
REPO_DIR="$HOME/ytmusic-commits"   # caminho do seu repositório
PYTHON="${HOME}/.local/bin/python3" # ou: which python3
```

Torne-o executável:

```bash
chmod +x commit_music.sh
```

Teste manualmente:

```bash
./commit_music.sh
```

---

### 6. Configure o autostart com systemd

```bash
# Substitua SEU_USUARIO pelo seu usuário real
sed -i 's/SEU_USUARIO/'"$USER"'/g' ytmusic-commit.service

# Copie o serviço para o systemd do usuário
mkdir -p ~/.config/systemd/user/
cp ytmusic-commit.service ~/.config/systemd/user/

# Ative e habilite o serviço
systemctl --user daemon-reload
systemctl --user enable ytmusic-commit.service

# (opcional) Teste sem reiniciar
systemctl --user start ytmusic-commit.service
systemctl --user status ytmusic-commit.service
```

A partir de agora, toda vez que você ligar o PC e a internet estiver disponível, o script roda automaticamente após 30 segundos (para garantir que a rede está pronta).

---

## 📋 Exemplo de HISTÓRICO.md gerado

```markdown
# 🎵 Histórico de Músicas — YouTube Music

## 📅 19/05/2025

🥇 Espiral de Ilusão — Djavan (4x)
🥈 Dreams — Fleetwood Mac (3x)
🥉 Anunciação — Alceu Valença (2x)

## 📅 18/05/2025

🥇 Aquarela — Toquinho (5x)
...
```

---

## 🔍 Ver os logs

```bash
tail -f ~/ytmusic-commits/commit_music.log
```

---

## ⚠️ Observações

- **Autenticação expira?** Se o ytmusicapi parar de funcionar, rode `setup_auth.py` novamente com headers frescos do navegador.
- **Push falha?** Configure SSH no GitHub: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
- **`.gitignore` recomendado:** adicione `scripts/oauth.json` e `*.log` para não expor seus cookies.
