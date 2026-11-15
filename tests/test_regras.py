import pytest

from regras import calcular_carteira


def _carteira():
    return [
        {"nome": "Ações", "saldo": 300, "meta": 50},
        {"nome": "Renda fixa", "saldo": 700, "meta": 50},
    ]


def test_total_e_a_soma_dos_saldos():
    assert calcular_carteira(_carteira())["total"] == 1000


def test_ideal_e_meta_percentual_do_total():
    itens = calcular_carteira(_carteira())["itens"]
    assert itens[0]["ideal"] == 500


def test_gap_e_ideal_menos_saldo():
    itens = calcular_carteira(_carteira())["itens"]
    assert itens[0]["gap"] == 500 - 300


def test_gap_positivo_significa_comprar():
    assert calcular_carteira(_carteira())["itens"][0]["gap"] > 0


def test_gap_negativo_significa_vender():
    assert calcular_carteira(_carteira())["itens"][1]["gap"] < 0


def test_carteira_balanceada_tem_gap_zero():
    carteira = [
        {"nome": "A", "saldo": 500, "meta": 50},
        {"nome": "B", "saldo": 500, "meta": 50},
    ]
    gaps = [i["gap"] for i in calcular_carteira(carteira)["itens"]]
    assert gaps == [0, 0]


def test_gaps_somam_zero_quando_metas_somam_100():
    gaps = [i["gap"] for i in calcular_carteira(_carteira())["itens"]]
    assert sum(gaps) == pytest.approx(0)


def test_relatorio_preserva_nome_e_saldo():
    item = calcular_carteira(_carteira())["itens"][0]
    assert item["nome"] == "Ações"
    assert item["saldo"] == 300


def test_total_zero_gera_ideal_e_gap_zero():
    carteira = [
        {"nome": "A", "saldo": 0, "meta": 60},
        {"nome": "B", "saldo": 0, "meta": 40},
    ]
    resultado = calcular_carteira(carteira)
    assert resultado["total"] == 0
    assert all(i["ideal"] == 0 and i["gap"] == 0 for i in resultado["itens"])


def test_lista_vazia_devolve_total_zero_e_sem_itens():
    assert calcular_carteira([]) == {"total": 0, "itens": []}


def test_metas_abaixo_de_100_nao_geram_aviso_hoje():
    # Comportamento atual: calcula normalmente, sem erro nem aviso.
    carteira = [
        {"nome": "A", "saldo": 500, "meta": 30},
        {"nome": "B", "saldo": 500, "meta": 30},
    ]
    resultado = calcular_carteira(carteira)
    assert [i["ideal"] for i in resultado["itens"]] == [300, 300]
    assert "aviso" not in resultado


def test_metas_acima_de_100_nao_geram_aviso_hoje():
    carteira = [
        {"nome": "A", "saldo": 500, "meta": 80},
        {"nome": "B", "saldo": 500, "meta": 80},
    ]
    resultado = calcular_carteira(carteira)
    assert sum(i["gap"] for i in resultado["itens"]) == pytest.approx(600)
    assert "aviso" not in resultado


@pytest.mark.xfail(
    reason="regras.py não valida metas que não somam 100%: deveria avisar ou lançar erro",
    strict=True,
)
def test_metas_que_nao_somam_100_deveriam_ser_rejeitadas():
    carteira = [
        {"nome": "A", "saldo": 500, "meta": 30},
        {"nome": "B", "saldo": 500, "meta": 30},
    ]
    with pytest.raises(ValueError):
        calcular_carteira(carteira)
