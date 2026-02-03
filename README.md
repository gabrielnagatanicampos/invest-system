# 📈 Invest System

Sistema de gestão e rebalanceamento de carteira de investimentos desenvolvido em Python. O objetivo é auxiliar investidores a manterem seu portfólio alinhado com suas metas percentuais de alocação.

## 🚀 Funcionalidades
- **Cotações em Tempo Real:** Integração com Yahoo Finance para obter preços de Ações (B3) e Criptomoedas.
- **Cálculo de Gap:** Algoritmo que identifica quanto falta comprar ou vender de cada ativo para atingir a meta ideal.
- **Gestão de Carteira:** Interface interativa para adicionar e remover ativos.
- **Blindagem:** Tratamento de erros para tickers inválidos.

## 🛠️ Tecnologias Utilizadas
- **Python** (Backend)
- **Streamlit** (Frontend)
- **Pandas** (Dados)
- **yfinance** (API)

## 📦 Como rodar o projeto

Abra o seu terminal e execute os comandos abaixo na ordem:

```bash
# 1. Clone o repositório
git clone [https://github.com/gabrielnagatanicampos/invest-system.git](https://github.com/gabrielnagatanicampos/invest-system.git)

# 2. Entre na pasta do projeto
cd invest-system

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute a aplicação
streamlit run web.py
