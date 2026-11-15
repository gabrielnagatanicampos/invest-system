"""Regras de alerta de rebalanceamento (função pura, sem Streamlit nem banco)."""
from regras import calcular_carteira

LIMITE_PADRAO_PP = 5.0


def avaliar_alertas(carteira: list, limite_pp: float = LIMITE_PADRAO_PP) -> dict:
    """Devolve as classes fora da meta por mais de limite_pp pontos percentuais.

    carteira: lista de {"nome", "saldo", "meta"} (meta em %).
    Retorno: {"total", "alertas": [...], "sugestao_aporte": nome ou None}.
    """
    resultado = calcular_carteira(carteira)
    total = resultado["total"]
    if total <= 0:
        return {"total": total, "alertas": [], "sugestao_aporte": None}

    metas = {a["nome"]: a["meta"] for a in carteira}
    desvios = []
    for item in resultado["itens"]:
        atual = item["saldo"] / total * 100
        desvios.append({
            "nome": item["nome"],
            "percentual_atual": atual,
            "meta": metas[item["nome"]],
            "desvio_pp": atual - metas[item["nome"]],
            "gap": item["gap"],
        })

    alertas = []
    for d in desvios:
        if abs(d["desvio_pp"]) > limite_pp:
            d["acao"] = "comprar" if d["gap"] > 0 else "vender"
            d["valor"] = abs(d["gap"])
            alertas.append(d)

    sugestao = None
    if alertas:
        sugestao = min(desvios, key=lambda d: d["desvio_pp"])["nome"]

    return {"total": total, "alertas": alertas, "sugestao_aporte": sugestao}
