import job_alertas

PRECOS = {"AAAA3.SA": 10.0, "BTC-USD": 1.0, "BRL=X": 1.0}


def preco(t):
    return PRECOS[t]


def dados(qtd_acoes, rf, cripto):
    return {
        "saldo_renda_fixa": rf,
        "quantidade_de_criptomoeda": cripto,
        "percentual_meta_acoes": 50,
        "percentual_meta_cripto": 20,
        "ativos": [{"ticker": "AAAA3.SA", "quantidade": qtd_acoes}],
    }


USUARIOS = [
    {"id": 1, "username": "ana", "email": "exemplo@example.com"},
    {"id": 2, "username": "bia", "email": "exemplo2@example.com"},
    {"id": 3, "username": "caio", "email": "exemplo3@example.com"},
]
CARTEIRAS = {
    1: dados(70, 200, 100),  # fora da meta
    2: dados(50, 300, 200),  # na meta
    3: dados(70, 200, 100),  # fora da meta
}


def rodar(enviar, **kw):
    return job_alertas.executar(
        listar_usuarios=lambda: USUARIOS,
        load_carteira=lambda i: CARTEIRAS[i],
        obter_preco=preco, enviar=enviar, **kw)


def test_envia_so_para_quem_precisa():
    enviados = []
    r = rodar(lambda d, a, c: enviados.append((d, a, c)))
    assert [e[0] for e in enviados] == ["exemplo@example.com", "exemplo3@example.com"]
    assert r == {"enviados": 2, "sem_alerta": 1, "falhas": 0}
    assert "Ações" in enviados[0][2] and "próximo aporte" in enviados[0][2]


def test_ninguem_fora_da_meta_nao_envia():
    enviados = []
    r = rodar(lambda *a: enviados.append(a), limite_pp=50)
    assert enviados == [] and r["enviados"] == 0


def test_falha_de_um_nao_derruba_os_outros():
    enviados = []

    def enviar(dest, a, c):
        if dest == "exemplo@example.com":
            raise RuntimeError("smtp fora do ar")
        enviados.append(dest)

    r = rodar(enviar)
    assert enviados == ["exemplo3@example.com"]
    assert r["falhas"] == 1


def test_dry_run_nao_envia(capsys):
    def enviar(*a):
        raise AssertionError("não deveria enviar")

    r = rodar(enviar, dry_run=True)
    assert r["enviados"] == 2
    assert "exemplo@example.com" not in capsys.readouterr().out


def test_preco_zero_nao_gera_alerta_falso():
    import job_alertas

    dados = {
        "ativos": [{"ticker": "PETR4.SA", "quantidade": 10}],
        "quantidade_de_criptomoeda": 0,
        "percentual_meta_acoes": 50,
        "percentual_meta_cripto": 0,
        "saldo_renda_fixa": 1000,
    }
    try:
        job_alertas.montar_carteira(dados, lambda t: 0.0)
    except ValueError as erro:
        assert "PETR4.SA" in str(erro)
    else:
        raise AssertionError("deveria recusar preço zero")


def test_email_usa_formato_brasileiro():
    import job_alertas

    avaliacao = {
        "alertas": [{"nome": "Ações", "percentual_atual": 6.5, "meta": 50.0,
                     "acao": "comprar", "valor": 4650.5}],
        "sugestao_aporte": "Ações",
    }
    _, corpo = job_alertas.montar_email("teste", avaliacao, 5.0)
    assert "R$ 4.650,50" in corpo
    assert "6,5% (meta 50,0%)" in corpo
    assert "mais de 5 pontos" in corpo
