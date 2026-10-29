import sqlite3

conexao = sqlite3.connect('banco.db')
conexao.row_factory = sqlite3.Row
cursor = conexao.cursor()

cursor.execute("""
               CREATE TABLE IF NOT EXISTS usuarios(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_on DATETIME DEFAULT CURRENT_TIMESTAMP      
            
               )""")

conexao.commit()


cursor.execute("""
            CREATE TABLE IF NOT EXISTS carteira(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            UNIQUE(usuario_id, ticker)          
            )  """)


conexao.commit()

cursor.execute("""
           CREATE TABLE IF NOT EXISTS carteira_config(
           id INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
           usuario_id INTEGER NOT NULL, 
           saldo_renda_fixa NUMERIC,
           qnt_cripto NUMERIC,
           meta_acoes NUMERIC,
           meta_cripto NUMERIC,
           FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
           UNIQUE(usuario_id)   
           )""")

conexao.commit()


def insert_user(username:str, password_hash: str, salt):
    conexao = sqlite3.connect('banco.db')
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()
    sql =   """
            INSERT INTO usuarios(username, password_hash, salt)
            VALUES (?, ?, ?)
            """
    cursor.execute(sql, (username, password_hash, salt))
    conexao.commit()

def search_user(username: str):
    
    conexao = sqlite3.connect('banco.db')
    conexao.row_factory = sqlite3.Row
    
    try:
        cursor = conexao.cursor()

        sql = """
            SELECT *
            FROM usuarios
            WHERE username = ?
            """
        
        cursor.execute(sql, (username,))
    
        user = cursor.fetchone()
    

        return user
    finally:
        conexao.close()
    

def insert_ticker(usuario_id: int, ticker: str, qnt: int):
    conexao = sqlite3.connect('banco.db')
    conexao.row_factory = sqlite3.Row
    
    
    
    try:
        cursor = conexao.cursor()
    
        sql = """
           INSERT INTO carteira(usuario_id, ticker, quantidade)
           VALUES (?, ?, ?)
           ON CONFLICT(usuario_id, ticker) DO UPDATE SET 
                quantidade = excluded.quantidade
        """
            
        cursor.execute(sql, (usuario_id, ticker, qnt))
        conexao.commit()
    finally:
        conexao.close()
        
      
        
def read_ticker(usuario_id: int):
    conexao = sqlite3.connect('banco.db')
    conexao.row_factory = sqlite3.Row
    try:
        cursor = conexao.cursor()

        sql = """
            SELECT ticker, quantidade
            FROM carteira
            WHERE usuario_id = ?
            """
        
        cursor.execute(sql, (usuario_id,))
    
        read = cursor.fetchall()
    

        return read
    finally:
        conexao.close()
        
    


def delete_ticker(usuario_id: int, ticker: str):
    conexao = sqlite3.connect('banco.db')
    conexao.row_factory = sqlite3.Row
    
    try:
        cursor = conexao.cursor()
        sql = """
            DELETE FROM carteira
            WHERE usuario_id = ? AND ticker = ?    
            """
            
        cursor.execute(sql, (usuario_id, ticker))
        conexao.commit()
        
    finally:
        conexao.close()   

def update_ticker(quantidade: int, usuario_id: int,ticker: str):
    conexao = sqlite3.connect('banco.db')
    conexao.row_factory = sqlite3.Row    
    try:
        cursor = conexao.cursor()
        sql = """
            UPDATE carteira
            SET quantidade = ?
            WHERE usuario_id = ? AND ticker = ?    
            """
        
        cursor.execute(sql, (quantidade, usuario_id,ticker))
        conexao.commit()
        
        
    finally:
        conexao.close()
        
        
        
def save_config(usuario_id:int, s_rf: float, qnt_bit: float,meta_acoes:float, meta_cripto: float ):
    conexao = sqlite3.connect('banco.db')
    conexao.row_factory = sqlite3.Row
    
    
    
    try:
        cursor = conexao.cursor()
    
        sql = """
           INSERT INTO carteira_config(usuario_id, saldo_renda_fixa, qnt_cripto, meta_acoes, meta_cripto)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(usuario_id) DO UPDATE SET
                saldo_renda_fixa = excluded.saldo_renda_fixa,
                qnt_cripto = excluded.qnt_cripto,
                meta_acoes = excluded.meta_acoes,
                meta_cripto = excluded.meta_cripto
        """
            
        cursor.execute(sql, (usuario_id, s_rf, qnt_bit, meta_acoes, meta_cripto))
        conexao.commit()
    finally:
        conexao.close()


def load_config(usuario_id):
    conexao = sqlite3.connect('banco.db')
    conexao.row_factory = sqlite3.Row
    try:
        cursor = conexao.cursor()

        sql = """
            SELECT saldo_renda_fixa, qnt_cripto, meta_acoes, meta_cripto
            FROM carteira_config
            WHERE usuario_id = ?
            """
        
        cursor.execute(sql, (usuario_id,))
    
        load = cursor.fetchone()
    

        return load
    finally:
        conexao.close()


def load_carteira(usuario_id):
    conexao = sqlite3.connect('banco.db')
    conexao.row_factory = sqlite3.Row
    try:
        cursor = conexao.cursor()

        cursor.execute(
            """
            SELECT saldo_renda_fixa, qnt_cripto, meta_acoes, meta_cripto
            FROM carteira_config
            WHERE usuario_id = ?
            """,
            (usuario_id,),
        )
        config = cursor.fetchone()

        if config is None:
            return None

        cursor.execute(
            """
            SELECT ticker, quantidade
            FROM carteira
            WHERE usuario_id = ?
            """,
            (usuario_id,),
        )
        ativos = cursor.fetchall()

        return {
            "saldo_renda_fixa": config["saldo_renda_fixa"],
            "quantidade_de_criptomoeda": config["qnt_cripto"],
            "percentual_meta_acoes": config["meta_acoes"],
            "percentual_meta_cripto": config["meta_cripto"],
            "ativos": [
                {"ticker": a["ticker"], "quantidade": a["quantidade"]}
                for a in ativos
            ],
        }
    finally:
        conexao.close()
        
        
        
print(load_carteira(5))