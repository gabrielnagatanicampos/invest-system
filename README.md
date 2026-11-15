# 📈 Invest System

Sistema de gestão e rebalanceamento de carteira de investimentos desenvolvido em Python com Streamlit. O objetivo é ajudar o investidor a manter o portfólio alinhado com as metas percentuais de alocação, com carteira salva por usuário e um assistente de IA para tirar dúvidas.

## Funcionalidades

- **Cotações em tempo real:** integração com o Yahoo Finance para obter preços de ações (B3) e criptomoedas.
- **Cálculo de gap:** identifica quanto falta comprar ou vender de cada ativo para atingir a meta ideal.
- **Gestão de carteira:** interface interativa para adicionar e remover ativos.
- **Login de usuários:** cada pessoa acessa a própria conta e enxerga só a sua carteira.
- **Persistência com SQLite:** a carteira de cada usuário fica salva no banco (tabela `carteira`, com usuário, ticker e quantidade), então os ativos continuam lá quando você volta ao app.
- **Assistente com IA:** chat integrado ao Streamlit que usa um modelo de linguagem via Groq (`openai/gpt-oss-120b`) para responder perguntas sobre investimentos.
- **Blindagem:** tratamento de erros para tickers inválidos e validação de campo vazio ao adicionar um ativo.

## Tecnologias utilizadas

- **Python** (backend)
- **Streamlit** (frontend)
- **Pandas** (dados)
- **yfinance** (cotações)
- **SQLite** (persistência)
- **Groq API** (modelo de linguagem)

## Estrutura do projeto

| Arquivo | Função |
| --- | --- |
| `web.py` | Interface em Streamlit: login, tela principal e chat com a IA |
| `mercado.py` | Busca de cotações |
| `regras.py` | Regras de negócio e cálculo do gap de rebalanceamento |
| `database.py` | Acesso ao banco SQLite: inserir, ler, atualizar e remover ativos da carteira |
| `invest_llm.py` | Integração com a LLM: monta o prompt e gera as respostas exibidas no app |

## Como rodar o projeto

Abra o terminal e execute os comandos abaixo na ordem:

```bash
# 1. Clone o repositório
git clone https://github.com/gabrielnagatanicampos/invest-system.git

# 2. Entre na pasta do projeto
cd invest-system

# 3. Instale as dependências
pip install -r requirements.txt
```

### Configurando a IA

O assistente precisa de uma chave da API da Groq. Crie uma conta em [console.groq.com](https://console.groq.com), gere uma chave e salve em um arquivo `.env` na raiz do projeto:

```
GROQ_API_KEY=sua_chave_aqui
```

O `.env` e o banco de dados (`banco.db`) não são versionados, então cada pessoa usa os seus.

### Executando

```bash
streamlit run web.py
```

## Como publicar na VPS

Guia para uma VPS gratuita da Oracle Cloud (Ubuntu) usando Docker. Tudo roda em containers: app (Streamlit), banco (Postgres), job de alertas e, se houver domínio, o Caddy (HTTPS automático).

### Pré-requisitos

- VPS Ubuntu com acesso SSH (por exemplo, pelo MobaXterm) e usuário com `sudo`.
- Repositório clonado na VPS (`git clone <url-do-repositorio>`).
- Descubra a arquitetura com `uname -m`: `x86_64` (x86) ou `aarch64` (ARM). As imagens usadas (`python:3.11-slim`, `postgres:16`, `caddy:2`) funcionam nas duas.
- Opcional: um domínio com o DNS (registro A) apontando para o IP da VPS, para ter HTTPS.

### Portas e firewall

Libere em dois lugares, senão o site não abre:

1. Painel da Oracle: Rede > VCN > Lista de segurança (ou NSG) > regra de entrada TCP para as portas 80 e 443 (e 8501 se for acessar sem domínio), origem `0.0.0.0/0`.
2. Firewall do Ubuntu na própria VPS (as imagens da Oracle costumam bloquear por padrão):

```bash
# se usa iptables (padrão nas imagens da Oracle)
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8501 -j ACCEPT   # só sem domínio
sudo netfilter-persistent save

# ou, se usa ufw
sudo ufw allow 80/tcp && sudo ufw allow 443/tcp && sudo ufw allow 8501/tcp
```

O Postgres não é exposto: não abra a porta 5432.

### Configurar o .env

```bash
cp .env.example .env
nano .env    # preencha senha do banco, GROQ_API_KEY, SMTP_*, DOMINIO
```

Deixe `DOMINIO` vazio para acessar em `http://IP-DA-VPS:8501`. Com domínio, o app fica em `https://seu-dominio`. Se o `.env` estiver no seu computador, copie com o painel de arquivos do MobaXterm ou `scp .env usuario@IP-DA-VPS:~/invest-system/`.

### Publicar

```bash
./scripts/deploy.sh
```

O script instala o Docker se faltar, confere o `.env`, faz `git pull`, sobe tudo com `docker compose up -d --build` e mostra o `docker compose ps`. Pode rodar de novo a qualquer momento. Se o Docker acabou de ser instalado, saia e entre de novo no SSH para o grupo `docker` valer.

### Dia a dia

```bash
docker compose logs -f app    # logs (troque por db, job-alertas ou caddy)
docker compose ps             # estado dos containers
./scripts/deploy.sh           # atualizar para a versão mais nova
./scripts/backup.sh           # backup em backups/invest_DATA.sql.gz
```

Backup diário automático (`crontab -e`):

```
0 3 * * * /home/ubuntu/invest-system/scripts/backup.sh >> /home/ubuntu/backup.log 2>&1
```

Restaurar um backup:

```bash
gunzip -c backups/invest_AAAAMMDD_HHMMSS.sql.gz | docker compose exec -T db psql -U USUARIO_DO_ENV -d NOME_DO_BANCO
```

### Checklist de verificação

- [ ] `docker compose ps` mostra app, db e job-alertas rodando (e caddy, se houver domínio).
- [ ] A página abre (`http://IP:8501` ou `https://dominio`) e, com domínio, o cadeado do HTTPS aparece.
- [ ] Cadastro de um usuário de teste e login funcionam.
- [ ] Depois de `docker compose restart` (ou reiniciar a VPS), o login do usuário de teste continua valendo: os dados persistem no volume `pgdata`.
- [ ] Teste o e-mail primeiro sem enviar: `docker compose exec job-alertas python job_alertas.py --dry-run`; só depois sem `--dry-run`.
- [ ] O intervalo do job vem de `ALERTA_INTERVALO_MIN` (padrão 1440 minutos).

### Trocar para o Supabase

Crie o projeto no Supabase, copie a string de conexão do Postgres e coloque no `.env` como `DATABASE_URL=...`. Nenhuma outra mudança é necessária: o compose usa essa variável no lugar da montada para o container `db`. Depois, se quiser, remova o serviço `db` do `docker-compose.yml`.

## Próximos passos

- Fazer a IA ler e interpretar os dados da carteira do usuário.
- Importar a carteira por arquivo CSV.
