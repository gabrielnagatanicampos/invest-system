import yfinance as yf 

def obter_preco(ticker):
    try:
        acao = yf.Ticker(ticker)
        dados = acao.history(period="1d")
        
        
        if dados.empty: #Se a tabela estiver vazia (ticker errado), retorna nada.
            return 0.0
            
        
        return float(dados['Close'].iloc[-1])
        
    except Exception:
        return 0.0
