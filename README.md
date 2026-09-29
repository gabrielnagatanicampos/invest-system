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

## Próximos passos

- Fazer a IA ler e interpretar os dados da carteira do usuário.
- Importar a carteira por arquivo CSV.
