import streamlit as st 
import pandas as pd
from regras import calcular_carteira
from mercado import obter_preco

obter_preco = st.cache_data(obter_preco)        #Melhora na resposta do site.                            

st.title("  Sistema de investimentos    ")

#Memória
if "lista_acoes" not in st.session_state:
    st.session_state["lista_acoes"] = {}

#Adicionar Ações
st.sidebar.header('Adicionar ações')
ticker_input = st.sidebar.text_input('Nome da Ação (EX: PETR4.SA)')
qnt_input = st.sidebar.number_input("Digite a Quantidade", min_value=0, step=1) #Faz o salto do click ser de 1 em 1.

if st.sidebar.button('Adicionar'):
    st.session_state["lista_acoes"][ticker_input] = qnt_input
    st.sidebar.success(f"{ticker_input} adicionado!")

st.sidebar.markdown("---") 

st.sidebar.write("**Sua Ações Atual:**")
    
soma_acoes = 0.0 
   
lista_precos = []

if st.session_state["lista_acoes"]: 
        
    
    for ticker, quantidade in st.session_state["lista_acoes"].items():
        preco = obter_preco(ticker)
        total_ativo = preco * quantidade
        soma_acoes += total_ativo

        lista_precos.append({
            "Ativo": ticker,
            "Qnt": quantidade,
            "Preço": f"R${preco:.2f}"
        })

    tabela_acoes = pd.DataFrame(lista_precos)
        
    st.sidebar.dataframe(tabela_acoes, hide_index=True, use_container_width=True)     
    
    st.sidebar.metric("Total em ações", f"R${soma_acoes:.2f}")
else:
    st.sidebar.caption("Nenhuma ação adicionada ainda.")

meta = st.sidebar.number_input("Meta para Ações (%)", value = 0.0)

#Adicionar Renda Fixa
s_rf = st.sidebar.number_input("Saldo em Renda Fixa (R$)", value = 0.0)

#Adicionar bitcoin 
qnt_bit = st.sidebar.number_input("Quantidade em bitcoin", value = 0.0, format="%.6f")  #Formata quantidade de bitcoin

meta_cripto = st.sidebar.number_input("Meta para Criptomoeda (%)", value = 0.0)

# Condicional para obter valores de ativos, calcular e apresentar 
if st.button("Calcular Carteira"):                                              

    obter_preco = st.cache_data(obter_preco)        #Melhora na resposta do site.                            

    valor_bitcoin_dolar = obter_preco("BTC-USD")

    preco_dolar = obter_preco("BRL=X")

    valor_bitcoin = valor_bitcoin_dolar * preco_dolar

    s_cripto = qnt_bit * valor_bitcoin

   
    


    meta_rf = 100 - meta - meta_cripto   # Meta da Renda Fixa.

    carteira = [] 

    carteira.append({
        "nome": "Ações",
        "saldo": soma_acoes,
        "meta": meta
    })

    carteira.append({
        "nome": "Renda Fixa",
        "saldo": s_rf,
        "meta": meta_rf
    })

    carteira.append({
        "nome": "CriptoMoeda",
        "saldo": s_cripto,
        "meta": meta_cripto
    })


    resultado = calcular_carteira(carteira)

    st.write("   Relatório  ")
    st.write(f" Patrimônio Total: R$ {resultado['total']:,.2f}")
    st.write(f" Valor do Bitcoin Atual:{valor_bitcoin:,.2f}")
    df = pd.DataFrame(resultado['itens'])  #transforma o relatorio em uma tabela.

    df = df.set_index("nome") #Usa a coluna 'nome' como etiqueta e não dado.

    grafico = df[["saldo", "ideal"]] #Duplo colchetes para criar uma nova tabela somente com esses dados selecionador, removendo os outros.

    st.bar_chart(grafico)





    for item in resultado['itens']:
        nome = item['nome']
        gap  = item['gap']
        
        if gap > 0:
            st.info(f" {nome}: COMPRAR R$ {gap:,.2f}")
        else:
         st.warning(f" {nome}: VENDER R$ {abs(gap):,.2f}")


    