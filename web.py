import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from regras import calcular_carteira
from mercado import obter_preco, acoes
import auth
from invest_llm import invest_llm
import database


obter_preco = st.cache_data(obter_preco)


st.set_page_config(
    page_title="System Invest",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown(
    """
    <style>
    .stApp {
        background: #0e1117;
    }

    [data-testid="stSidebar"] {
        background: #11151d;
        border-right: 1px solid #262c36;
    }

    [data-testid="stMetric"] {
        background: #151a23;
        border: 1px solid #262c36;
        border-radius: 12px;
        padding: 16px;
    }

    [data-testid="stMetricLabel"] {
        color: #9ca3af;
    }

    [data-testid="stMetricValue"] {
        color: #f3f4f6;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    .dashboard-card {
        background: #151a23;
        border: 1px solid #262c36;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 16px;
    }

    .section-title {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .section-subtitle {
        color: #9ca3af;
        font-size: 14px;
        margin-bottom: 16px;
    }

    .positive {
        color: #22c55e;
        font-weight: 600;
    }

    .negative {
        color: #ef4444;
        font-weight: 600;
    }

    .neutral {
        color: #9ca3af;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def inicializar_estado():
    if "logado" not in st.session_state:
        st.session_state.logado = False

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "lista_acoes" not in st.session_state:
        st.session_state.lista_acoes = {}

    if "resultado_carteira" not in st.session_state:
        st.session_state.resultado_carteira = None

    if "dados_carteira" not in st.session_state:
        st.session_state.dados_carteira = None

    if "usuario_id" not in st.session_state:
        st.session_state.usuario_id = None

    if "usuario" not in st.session_state:
        st.session_state.usuario = None


def limpar_sessao():
    st.session_state.logado = False
    st.session_state.usuario = None
    st.session_state.usuario_id = None
    st.session_state.lista_acoes = {}
    st.session_state.resultado_carteira = None
    st.session_state.dados_carteira = None
    st.session_state.messages = []


@st.dialog("Login")
def login_validation(username: str, password: str):
    if not username.strip() or not password:
        st.error("Digite seu nome de usuário e senha.")
        return

    if auth.login(username, password):
        user = database.search_user(username)

        if user is None:
            st.error("Não foi possível carregar os dados do usuário.")
            return

        st.session_state.logado = True
        st.session_state.usuario = username
        st.session_state.usuario_id = user["id"]

        st.success("Login validado.")

        if st.button(
            "Continuar",
            use_container_width=True,
            key="continuar_login"
        ):
            st.rerun()
    else:
        st.error("Usuário ou senha inválidos.")


@st.dialog("Criar conta")
def cadastro():
    new_user = st.text_input(
        "Usuário",
        key="cadastro_usuario"
    )

    new_psw = st.text_input(
        "Senha",
        type="password",
        key="cadastro_senha"
    )

    new_psw2 = st.text_input(
        "Confirme sua senha",
        type="password",
        key="cadastro_confirmacao"
    )

    if st.button(
        "Cadastrar",
        use_container_width=True,
        type="primary",
        key="cadastrar_usuario"
    ):
        if not new_user.strip() or not new_psw or not new_psw2:
            st.error("Preencha todos os campos.")
            return

        if new_psw != new_psw2:
            st.error("As senhas são diferentes.")
            return

        try:
            auth.register_user(new_user.strip(), new_psw)
            st.success("Conta criada. Feche esta janela e faça login.")
        except auth.UsuarioJaExisteError:
            st.error("Esse usuário já existe.")


def tela_login():
    st.markdown(
        """
        <div style="text-align:center; margin-top:70px;">
            <div style="font-size:48px;">📊</div>
            <h1>System Invest</h1>
            <p style="color:#9ca3af;">
                Gestão e análise da sua carteira de investimentos
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("sign_in"):
            st.subheader("Entrar")

            username = st.text_input(
                "Usuário",
                key="login_usuario"
            )

            password = st.text_input(
                "Senha",
                type="password",
                key="login_senha"
            )

            submit_btn = st.form_submit_button(
                "Entrar",
                type="primary",
                use_container_width=True
            )

        if submit_btn:
            login_validation(username, password)

        st.write("")

        if st.button(
            "Criar uma conta",
            use_container_width=True,
            key="abrir_cadastro"
        ):
            cadastro()


def carregar_acoes(usuario_id):
    registros = database.read_ticker(usuario_id)

    return {
        row["ticker"]: row["quantidade"]
        for row in registros
    }


def carregar_dados_acoes():
    lista_precos = []
    soma_acoes = 0.0

    for ticker, quantidade in st.session_state["lista_acoes"].items():
        preco = obter_preco(ticker)
        total_ativo = preco * quantidade

        soma_acoes += total_ativo

        lista_precos.append(
            {
                "Ativo": ticker,
                "Quantidade": quantidade,
                "Preço": preco,
                "Total(R$)": total_ativo
            }
        )

    if not lista_precos:
        return pd.DataFrame(
            columns=[
                "Ativo",
                "Quantidade",
                "Preço",
                "Total(R$)"
            ]
        ), 0.0

    df = pd.DataFrame(lista_precos)

    df = df.sort_values(
        by="Total(R$)",
        ascending=False
    ).reset_index(drop=True)

    return df, soma_acoes


def sidebar_acoes(usuario_id):
    st.sidebar.markdown("## Carteira")

    st.sidebar.markdown("### Adicionar ação")

    ticker_input = st.sidebar.selectbox(
        "Ativo",
        acoes,
        index=None,
        placeholder="Digite ou busque",
        accept_new_options=True,
        key="ticker_input"
    )

    qnt_input = st.sidebar.number_input(
        "Quantidade",
        min_value=0,
        step=1,
        value=0,
        key="quantidade_input"
    )

    if st.sidebar.button(
        "Adicionar ativo",
        use_container_width=True,
        type="primary",
        key="adicionar_ativo"
    ):
        if ticker_input is None or not str(ticker_input).strip():
            st.sidebar.error("Digite ou selecione um ativo.")
        elif qnt_input <= 0:
            st.sidebar.error("A quantidade deve ser maior que zero.")
        else:
            ticker = str(ticker_input).strip().upper()

            st.session_state["lista_acoes"][ticker] = qnt_input

            database.insert_ticker(
                usuario_id,
                ticker,
                qnt_input
            )

            st.session_state["resultado_carteira"] = None

            st.sidebar.success(
                f"{ticker} adicionado."
            )

            st.rerun()

    st.sidebar.divider()

    st.sidebar.markdown("### Configuração da carteira")


def tabela_acoes(usuario_id, tabela_acoes):
    if tabela_acoes.empty:
        st.info("Nenhuma ação adicionada à carteira.")
        return

    tabela_visual = tabela_acoes.copy()

    tabela_visual["Preço"] = tabela_visual["Preço"].map(
        lambda x: f"R$ {x:,.2f}"
    )

    tabela_visual["Total(R$)"] = tabela_visual["Total(R$)"].map(
        lambda x: f"R$ {x:,.2f}"
    )

    event = st.dataframe(
        tabela_visual,
        hide_index=True,
        use_container_width=True,
        key="tabela_acoes_select",
        on_select="rerun",
        selection_mode=["multi-row"]
    )

    linhas_selecionadas = event.selection["rows"]

    if linhas_selecionadas:
        tickers_selecionados = tabela_acoes.iloc[
            linhas_selecionadas
        ]["Ativo"].tolist()

        st.caption(
            f"Selecionado(s): {', '.join(tickers_selecionados)}"
        )

        if st.button(
            "Remover selecionados",
            key="remover_acoes"
        ):
            for ticker in tickers_selecionados:
                database.delete_ticker(
                    usuario_id,
                    ticker
                )

                st.session_state["lista_acoes"].pop(
                    ticker,
                    None
                )

            st.session_state["resultado_carteira"] = None

            st.rerun()


def configuracao_carteira(usuario_id, config):
    saldo_renda_fixa = (
        config["saldo_renda_fixa"]
        if config
        else 0.0
    )

    qnt_cripto = (
        config["qnt_cripto"]
        if config
        else 0.0
    )

    meta_acoes = (
        config["meta_acoes"]
        if config
        else 0.0
    )

    meta_cripto = (
        config["meta_cripto"]
        if config
        else 0.0
    )

    meta = st.sidebar.number_input(
        "Meta para ações (%)",
        min_value=0.0,
        max_value=100.0,
        value=float(meta_acoes),
        step=1.0,
        key="meta_acoes"
    )

    saldo_renda_fixa = st.sidebar.number_input(
        "Saldo em renda fixa (R$)",
        min_value=0.0,
        value=float(saldo_renda_fixa),
        step=100.0,
        key="saldo_renda_fixa"
    )

    qnt_bit = st.sidebar.number_input(
        "Quantidade de Bitcoin",
        min_value=0.0,
        value=float(qnt_cripto),
        step=0.0001,
        format="%.8f",
        key="quantidade_bitcoin"
    )

    meta_cripto = st.sidebar.number_input(
        "Meta para criptomoeda (%)",
        min_value=0.0,
        max_value=100.0,
        value=float(meta_cripto),
        step=1.0,
        key="meta_cripto"
    )

    meta_rf = 100.0 - meta - meta_cripto

    if meta_rf < 0:
        st.sidebar.error(
            "As metas de ações e criptomoeda ultrapassam 100%."
        )
    else:
        st.sidebar.caption(
            f"Meta de renda fixa: {meta_rf:.1f}%"
        )

    database.save_config(
        usuario_id,
        saldo_renda_fixa,
        qnt_bit,
        meta,
        meta_cripto
    )

    return {
        "saldo_renda_fixa": saldo_renda_fixa,
        "qnt_cripto": qnt_bit,
        "meta_acoes": meta,
        "meta_cripto": meta_cripto,
        "meta_renda_fixa": meta_rf
    }


def calcular_resultado(
    soma_acoes,
    configuracao
):
    meta = configuracao["meta_acoes"]
    meta_cripto = configuracao["meta_cripto"]
    meta_rf = configuracao["meta_renda_fixa"]

    if meta_rf < 0:
        st.error(
            "A soma das metas de ações e criptomoeda não pode ultrapassar 100%."
        )
        return None

    qnt_bit = configuracao["qnt_cripto"]
    saldo_renda_fixa = configuracao["saldo_renda_fixa"]

    valor_bitcoin_dolar = obter_preco("BTC-USD")
    preco_dolar = obter_preco("BRL=X")

    valor_bitcoin = (
        valor_bitcoin_dolar * preco_dolar
    )

    saldo_cripto = qnt_bit * valor_bitcoin

    carteira = [
        {
            "nome": "Ações",
            "saldo": soma_acoes,
            "meta": meta
        },
        {
            "nome": "Renda Fixa",
            "saldo": saldo_renda_fixa,
            "meta": meta_rf
        },
        {
            "nome": "CriptoMoeda",
            "saldo": saldo_cripto,
            "meta": meta_cripto
        }
    ]

    resultado = calcular_carteira(carteira)

    st.session_state["resultado_carteira"] = resultado

    st.session_state["dados_carteira"] = {
        "saldo_renda_fixa": saldo_renda_fixa,
        "saldo_cripto": saldo_cripto,
        "valor_bitcoin": valor_bitcoin,
        "meta_acoes": meta,
        "meta_renda_fixa": meta_rf,
        "meta_cripto": meta_cripto
    }

    return resultado


def cards_patrimonio(resultado):
    dados = st.session_state.get(
        "dados_carteira",
        {}
    )

    total = resultado.get("total", 0.0)

    saldo_renda_fixa = dados.get(
        "saldo_renda_fixa",
        0.0
    )

    saldo_cripto = dados.get(
        "saldo_cripto",
        0.0
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Patrimônio total",
            f"R$ {total:,.2f}"
        )

    with col2:
        st.metric(
            "Total em ações",
            f"R$ {next((x['saldo'] for x in resultado['itens'] if x['nome'] == 'Ações'), 0):,.2f}"
        )

    with col3:
        st.metric(
            "Renda fixa",
            f"R$ {saldo_renda_fixa:,.2f}"
        )

    with col4:
        st.metric(
            "Cripto",
            f"R$ {saldo_cripto:,.2f}"
        )


def preparar_alocacao(resultado):
    itens = resultado.get("itens", [])
    total = resultado.get("total", 0.0)

    if not itens:
        return pd.DataFrame()

    df = pd.DataFrame(itens)

    if total > 0:
        df["atual_pct"] = (
            df["saldo"] / total * 100
        )

        df["meta_pct"] = (
            df["ideal"] / total * 100
        )
    else:
        df["atual_pct"] = 0.0
        df["meta_pct"] = 0.0

    return df


def grafico_alocacao(resultado):
    df = preparar_alocacao(resultado)

    if df.empty:
        return

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df["nome"],
            y=df["atual_pct"],
            name="Atual"
        )
    )

    fig.add_trace(
        go.Bar(
            x=df["nome"],
            y=df["meta_pct"],
            name="Meta"
        )
    )

    fig.update_layout(
        title="Alocação atual x meta",
        barmode="group",
        height=380,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        ),
        xaxis_title="",
        yaxis_title="Percentual (%)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="grafico_alocacao_unico"
    )


def tabela_alocacao(resultado):
    df = preparar_alocacao(resultado)

    if df.empty:
        return

    tabela = df[
        [
            "nome",
            "saldo",
            "ideal",
            "atual_pct",
            "meta_pct",
            "gap"
        ]
    ].copy()

    tabela.columns = [
        "Categoria",
        "Atual",
        "Ideal",
        "Atual (%)",
        "Meta (%)",
        "Gap"
    ]

    tabela["Atual"] = tabela["Atual"].map(
        lambda x: f"R$ {x:,.2f}"
    )

    tabela["Ideal"] = tabela["Ideal"].map(
        lambda x: f"R$ {x:,.2f}"
    )

    tabela["Gap"] = tabela["Gap"].map(
        lambda x: f"R$ {x:,.2f}"
    )

    tabela["Atual (%)"] = tabela["Atual (%)"].map(
        lambda x: f"{x:.2f}%"
    )

    tabela["Meta (%)"] = tabela["Meta (%)"].map(
        lambda x: f"{x:.2f}%"
    )

    st.dataframe(
        tabela,
        hide_index=True,
        use_container_width=True,
        key="tabela_alocacao"
    )


def painel_rebalanceamento(resultado):
    st.subheader("Rebalanceamento")

    df = preparar_alocacao(resultado)

    if df.empty:
        return

    for _, item in df.iterrows():
        nome = item["nome"]
        gap = item["gap"]
        atual_pct = item["atual_pct"]
        meta_pct = item["meta_pct"]

        col1, col2, col3 = st.columns(
            [2, 2, 3]
        )

        with col1:
            st.markdown(
                f"**{nome}**"
            )

        with col2:
            st.caption(
                f"{atual_pct:.2f}% atual → {meta_pct:.2f}% meta"
            )

        with col3:
            if gap > 0:
                st.success(
                    f"Comprar R$ {gap:,.2f}"
                )
            elif gap < 0:
                st.warning(
                    f"Reduzir R$ {abs(gap):,.2f}"
                )
            else:
                st.info(
                    "Carteira alinhada"
                )


def dashboard(resultado):
    if resultado is None:
        st.info(
            "Clique em **Calcular Carteira** para atualizar o dashboard."
        )
        return

    total = resultado.get(
        "total",
        0.0
    )

    if total <= 0:
        st.warning(
            "A carteira ainda não possui patrimônio para calcular a alocação."
        )
        return

    st.markdown("## Dashboard")

    cards_patrimonio(resultado)

    st.write("")

    col1, col2 = st.columns(
        [1.6, 1]
    )

    with col1:
        st.markdown(
            "### Alocação da carteira"
        )

        st.caption(
            "Comparação entre a distribuição atual e a distribuição ideal."
        )

        grafico_alocacao(resultado)

    with col2:
        st.markdown(
            "### Resumo"
        )

        tabela_alocacao(resultado)

    st.divider()

    painel_rebalanceamento(resultado)


def tela_principal():
    usuario_id = st.session_state.usuario_id

    if usuario_id is None:
        limpar_sessao()
        st.rerun()

    config = database.load_config(
        usuario_id
    )

    if not st.session_state["lista_acoes"]:
        st.session_state["lista_acoes"] = carregar_acoes(
            usuario_id
        )

    sidebar_acoes(
        usuario_id
    )

    configuracao = configuracao_carteira(
        usuario_id,
        config
    )

    st.sidebar.divider()

    if st.sidebar.button(
        "Calcular carteira",
        use_container_width=True,
        type="primary",
        key="calcular_carteira_sidebar"
    ):
        tabela_acoes, soma_acoes = carregar_dados_acoes()

        resultado = calcular_resultado(
            soma_acoes,
            configuracao
        )

        if resultado is not None:
            st.rerun()

    if st.sidebar.button(
        "Sair",
        use_container_width=True,
        key="logout"
    ):
        limpar_sessao()
        st.rerun()

    st.title("Sistema de Investimentos")

    st.caption(
        f"Carteira de {st.session_state.usuario}"
    )

    tabela_acoes, soma_acoes = carregar_dados_acoes()

    if not tabela_acoes.empty:
        st.markdown("### Seus ativos")

        tabela_acoes_com_participacao = tabela_acoes.copy()

        if soma_acoes > 0:
            tabela_acoes_com_participacao[
                "Participação"
            ] = (
                tabela_acoes_com_participacao["Total(R$)"]
                / soma_acoes
                * 100
            )
        else:
            tabela_acoes_com_participacao[
                "Participação"
            ] = 0.0

        tabela_visual = tabela_acoes_com_participacao[
            [
                "Ativo",
                "Quantidade",
                "Preço",
                "Total(R$)",
                "Participação"
            ]
        ].copy()

        tabela_visual["Preço"] = tabela_visual["Preço"].map(
            lambda x: f"R$ {x:,.2f}"
        )

        tabela_visual["Total(R$)"] = tabela_visual["Total(R$)"].map(
            lambda x: f"R$ {x:,.2f}"
        )

        tabela_visual["Participação"] = tabela_visual[
            "Participação"
        ].map(
            lambda x: f"{x:.2f}%"
        )

        event = st.dataframe(
            tabela_visual,
            hide_index=True,
            use_container_width=True,
            key="tabela_principal_acoes",
            on_select="rerun",
            selection_mode=["multi-row"]
        )

        linhas_selecionadas = event.selection["rows"]

        if linhas_selecionadas:
            tickers_selecionados = tabela_acoes.iloc[
                linhas_selecionadas
            ]["Ativo"].tolist()

            st.caption(
                f"Selecionado(s): {', '.join(tickers_selecionados)}"
            )

            if st.button(
                "Remover selecionados",
                key="remover_acoes_principal"
            ):
                for ticker in tickers_selecionados:
                    database.delete_ticker(
                        usuario_id,
                        ticker
                    )

                    st.session_state[
                        "lista_acoes"
                    ].pop(
                        ticker,
                        None
                    )

                st.session_state[
                    "resultado_carteira"
                ] = None

                st.rerun()

        st.metric(
            "Total em ações",
            f"R$ {soma_acoes:,.2f}"
        )

    else:
        st.info(
            "Adicione ações pela barra lateral para começar."
        )

    resultado = st.session_state.get(
        "resultado_carteira"
    )

    st.divider()

    dashboard(
        resultado
    )


inicializar_estado()


if st.session_state.logado:
    tela_principal()
    invest_llm()
else:
    tela_login()