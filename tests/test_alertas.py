from alertas import avaliar_alertas


def cart(a, rf, c):
    return [
        {"nome": "Ações", "saldo": a, "meta": 50},
        {"nome": "Renda Fixa", "saldo": rf, "meta": 30},
        {"nome": "CriptoMoeda", "saldo": c, "meta": 20},
    ]


def test_dentro_da_meta_sem_alerta():
    r = avaliar_alertas(cart(500, 300, 200))
    assert r["alertas"] == [] and r["sugestao_aporte"] is None


def test_fora_da_meta_compra_e_vende():
    r = avaliar_alertas(cart(700, 100, 200))
    por_nome = {a["nome"]: a for a in r["alertas"]}
    assert por_nome["Ações"]["acao"] == "vender"
    assert por_nome["Ações"]["valor"] == 200
    assert por_nome["Renda Fixa"]["acao"] == "comprar"
    assert r["sugestao_aporte"] == "Renda Fixa"


def test_limite_customizado():
    c = cart(560, 270, 170)  # desvios de 6, -3 e -3
    assert len(avaliar_alertas(c)["alertas"]) == 1
    assert avaliar_alertas(c, limite_pp=10)["alertas"] == []


def test_carteira_vazia():
    assert avaliar_alertas(cart(0, 0, 0))["alertas"] == []
