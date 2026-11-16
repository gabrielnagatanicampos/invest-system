"""Job de alertas: calcula a carteira de cada usuário e envia e-mail se precisar.

Uso: python job_alertas.py [--dry-run] [--limite 5]
"""
import argparse
import logging

from alertas import LIMITE_PADRAO_PP, avaliar_alertas

log = logging.getLogger("job_alertas")


def montar_carteira(dados: dict, obter_preco) -> list:
    """Monta a carteira como o dashboard (ações, renda fixa, cripto).

    Se faltar cotação de algo que o usuário possui, levanta ValueError:
    melhor não enviar nada do que mandar um alerta calculado com preço zero.
    """
    def preco(ticker):
        valor = obter_preco(ticker)
        if not valor or valor <= 0:
            raise ValueError(f"sem cotação para {ticker}")
        return valor

    soma_acoes = sum(preco(a["ticker"]) * a["quantidade"] for a in dados["ativos"])
    qnt_cripto = dados["quantidade_de_criptomoeda"]
    saldo_cripto = qnt_cripto * preco("BTC-USD") * preco("BRL=X") if qnt_cripto else 0.0
    meta_acoes = dados["percentual_meta_acoes"]
    meta_cripto = dados["percentual_meta_cripto"]
    return [
        {"nome": "Ações", "saldo": soma_acoes, "meta": meta_acoes},
        {"nome": "Renda Fixa", "saldo": dados["saldo_renda_fixa"],
         "meta": 100 - meta_acoes - meta_cripto},
        {"nome": "CriptoMoeda", "saldo": saldo_cripto, "meta": meta_cripto},
    ]


def _brl(valor: float) -> str:
    """4650.5 -> '4.650,50' (formato brasileiro)."""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(valor: float) -> str:
    """6.5 -> '6,5'."""
    return f"{valor:.1f}".replace(".", ",")


def montar_email(username: str, avaliacao: dict, limite_pp: float):
    assunto = "Invest System: pontos de atenção na sua carteira"
    linhas = [
        f"Olá, {username}.",
        "",
        f"Estas classes estão a mais de {_pct(limite_pp).rstrip('0').rstrip(',')} pontos percentuais da meta:",
        "",
    ]
    for a in avaliacao["alertas"]:
        linhas.append(
            f"- {a['nome']}: {_pct(a['percentual_atual'])}% (meta {_pct(a['meta'])}%). "
            f"Sugestão: {a['acao']} R$ {_brl(a['valor'])}."
        )
    linhas += [
        "",
        f"Para o próximo aporte, priorize: {avaliacao['sugestao_aporte']}.",
        "",
        "Esta é uma mensagem automática do Invest System.",
    ]
    return assunto, "\n".join(linhas)


def executar(limite_pp=LIMITE_PADRAO_PP, dry_run=False, listar_usuarios=None,
             load_carteira=None, obter_preco=None, enviar=None) -> dict:
    if listar_usuarios is None or load_carteira is None:
        import database
        listar_usuarios = listar_usuarios or database.listar_usuarios_com_email
        load_carteira = load_carteira or database.load_carteira
    if obter_preco is None:
        from mercado import obter_preco
    if enviar is None:
        from emailer import enviar_email as enviar

    resumo = {"enviados": 0, "sem_alerta": 0, "falhas": 0}
    for u in listar_usuarios():
        try:
            dados = load_carteira(u["id"])
            if dados is None:
                resumo["sem_alerta"] += 1
                continue
            avaliacao = avaliar_alertas(montar_carteira(dados, obter_preco), limite_pp)
            if not avaliacao["alertas"]:
                resumo["sem_alerta"] += 1
                continue
            assunto, corpo = montar_email(u["username"], avaliacao, limite_pp)
            if dry_run:
                print(f"[dry-run] Para usuário id={u['id']}\n{assunto}\n{corpo}\n")
            else:
                enviar(u["email"], assunto, corpo)
            resumo["enviados"] += 1
        except Exception:
            resumo["falhas"] += 1
            log.exception("Falha ao processar usuário id=%s", u.get("id"))
    return resumo


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--limite", type=float, default=LIMITE_PADRAO_PP)
    args = p.parse_args()
    print(executar(limite_pp=args.limite, dry_run=args.dry_run))
