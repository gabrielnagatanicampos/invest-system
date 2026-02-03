
def calcular_carteira(carteira):
    total = 0


    for ativo in carteira:
        total += ativo['saldo'] #Vai adicionar os valores recebidos em um valor total (Patrimônio )

    relatorio = []

    for ativo in carteira:
        ideal = total * (ativo['meta'] / 100)

        gap = ideal - ativo['saldo']  # difernca entre a meta 

        relatorio.append({
        "nome": ativo["nome"],
        "saldo": ativo["saldo"],   #Guardar os dados para o Gráfico 
        "ideal": ideal,
        "gap": gap 
        })

    return {
        "total": total,
        "itens": relatorio
        }

