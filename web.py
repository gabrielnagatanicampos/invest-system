import streamlit as st 
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from regras import calcular_carteira
from mercado import obter_preco
from mercado import acoes
import auth
from invest_llm import invest_llm





obter_preco = st.cache_data(obter_preco)        #Melhora na resposta do site.                            

st.set_page_config(
    page_title="System Invest",
    page_icon="📊",
    layout= "wide",
    initial_sidebar_state="expanded",
)


@st.dialog('Alert')
def login_validation(username, password):
    if username == '' or password == '':
        st.error('digite seu nome de usuário e senha.')
    elif auth.login(username, password):
        st.session_state.logado = True 
        st.session_state.usuario = username
        st.success('Login validado')
        
        if st.button('Continuar', use_container_width= True):
            st.rerun()
    else: 
        st.error('Usuário ou senha inválidos.')

@st.dialog('Crir conta')
def cadastro():
    new_user = st.text_input('Usuário')
    new_psw = st.text_input('Senha', type = 'password' )
    new_psw2 = st.text_input('Confirme sua senha', type = 'password' )
    
    if st.button('Cadastrar', use_container_width= True):
        if new_user == '' or new_psw == '' or new_psw2 == '':
            st.error('digite seu nome de usuário e senha')
        elif new_psw != new_psw2:
            st.error('Senhas diferentes')
        else:
            try:
                auth.register_user(new_user, new_psw)
                st.success('Conta criada! Feche esta janela e faça login.')
            except auth.UsuarioJaExisteError:
                st.error('Esse usuário já existe.')
                             
    
def tela_login():        
    with st.form('sign_in'):
        st.title('Sign In')
        st.caption('Please enter your username and password.')
        st.divider()
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        submit_btn = st.form_submit_button(
            label="Submit",
            type="primary",
            use_container_width=True
        )
       
        col1, col2, col3, col4 = st.columns(4)
        with col3:
            remember_box = st.checkbox("Remember me")
        with col4:
            forgot_pass = st.html('<p style=margin-top:8px; color:#FFAC41><a href="https://www.google.com.br/?hl=pt-BR">Forgot password?</a></p>')
    
    create_acc_btn = st.button(
        label="Create an Account",
        type="secondary",
        use_container_width=True
    )
    
    if submit_btn:
        login_validation(username, password)
        
    if create_acc_btn:
        cadastro() 
    
    


def tela_principal():

    st.title("  Sistema de investimentos    ")
    st.header("Suas Ações:")
    st.text("Selecione o ativo para remover")
    #Memória
    if "lista_acoes" not in st.session_state:
        st.session_state["lista_acoes"] = {}

    #Adicionar Ações
    st.sidebar.header('Adicionar ações')

    ticker_input = st.sidebar.selectbox(
        'Selecione a ação:',
        acoes,
        index= None,
        placeholder= 'Digite ou Busque',
        accept_new_options=True
    )

    qnt_input = st.sidebar.number_input("Digite a Quantidade", min_value=0, step=1) #Faz o salto do click ser de 1 em 1.

    if st.sidebar.button('Adicionar'):

        st.session_state["lista_acoes"][ticker_input] = qnt_input

        st.sidebar.success(f"{ticker_input} adicionado!")

    st.sidebar.markdown("---") 


        



        
    soma_acoes = 0.0 
    lista_precos = []


    if st.session_state["lista_acoes"]: #Salava ações em caso de Rerun.
            
        
        for ticker, quantidade in st.session_state["lista_acoes"].items():
            preco = obter_preco(ticker)
            total_ativo = preco * quantidade
            soma_acoes += total_ativo

            lista_precos.append({
                "Ativo": ticker,
                "Quantidade": quantidade,
                "Preço": f"R${preco:.2f}",
                "Total(R$)": total_ativo
            })



        df = pd.DataFrame(lista_precos)
        tabela_acoes = df.sort_values(by='Total(R$)', ascending=False)
            
        event = st.dataframe(
        tabela_acoes,
        hide_index= True,
        use_container_width=True,
        key="tabela_acoes_select",
        on_select="rerun",
        selection_mode=["multi-row"],
    )
        linhas_selecionadas = event.selection["rows"]

        if linhas_selecionadas:
            tickers_selecionados = tabela_acoes.iloc[linhas_selecionadas]["Ativo"].tolist()
            st.write(f"Selecionado(s): {', '.join(tickers_selecionados)}")

            if st.button("Remover ação(ões) selecionada(s)"):
                for ticker in tickers_selecionados:
                    st.session_state["lista_acoes"].pop(ticker, None)
                st.rerun()

        
        col1,col2,col3,col4,col5,col6 = st.columns(6)

        col1.metric(
            "Total em ações",
            f"R${soma_acoes:.2f}",
            delta = None,
            border= True
        )
    else:
        st.sidebar.caption("Nenhuma ação adicionada ainda.")



    # Variáveis para receber metas e quantidades.
    meta = st.sidebar.number_input("Meta para Ações (%)", value = 0.0)

    #Adicionar Renda Fixa
    s_rf = st.sidebar.number_input("Saldo em Renda Fixa (R$)", value = 0.0)

    #Adicionar bitcoin 
    qnt_bit = st.sidebar.number_input("Quantidade em bitcoin", value = 0.0, format="%.6f")  #Formata quantidade de bitcoin

    meta_cripto = st.sidebar.number_input("Meta para Criptomoeda (%)", value = 0.0)


    
    # Botão para obter valores de ativos, calcular e apresentar 
    if st.button("Calcular Carteira"):                                              
                            
        #Convertendo de Dolar para Real
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

        #gerador dashboard. 
        col2.metric(
            'Total em Renda Fixa',
            f"R${s_rf:.2f}",
            border= True
        )

        col3.metric(
            'Total em Bitcoin',
            f"R${s_cripto:,.2f}",
            border= True
        )

        col4.metric(
            'Patrimônio Total(R$)',
            f"R${resultado['total']:,.2f}",
            border= True,
            delta = None,
            delta_color= 'normal'
        )

        

        df = pd.DataFrame(resultado['itens'])  #transforma o relatorio em uma tabela.

        df = df.set_index("nome") #Usa a coluna 'nome' como etiqueta e não dado.

        grafico = df[["saldo", "ideal"]] #Duplo colchetes para criar uma nova tabela somente com esses dados selecionador, removendo os outros.

        
        col1.bar_chart(
            grafico,
            color = [ "#0000FF","#FF0000"],
            horizontal= False,
            stack= False,
            use_container_width= True
        )


        donut_chart = go.Figure(data=[go.Pie(labels=grafico.reset_index()['nome'], values=grafico['saldo'], hole=.3)])

        col2.plotly_chart(
            donut_chart,
            theme= 'streamlit',
            use_container_width= True
        )
        
        with col3: 
            st.header('Recomendação:')


    
    
   
        for item in resultado['itens']:
            nome = item['nome']
            gap  = item['gap']
        
            with col3:   
            
             if gap > 0:
                st.info(f" {nome}: :green[COMPRAR R$] {gap:,.2f}")
             else:
                st.warning(f" {nome}: :red[VENDER R$] {abs(gap):,.2f}")
                
                
        
                
                
    

    
    

# Inicializa o histórico de mensagens na sessão, caso ainda não exista
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Exibe todas as mensagens anteriores armazenadas no estado da sessão
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#Verifica se o user está logado ou não.
if "logado" not in st.session_state:
    st.session_state.logado = False


if st.session_state.logado == True:
    tela_principal()
    invest_llm()
else:
    tela_login()

