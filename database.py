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

def insert_user(username, password_hash, salt):
    conexao = sqlite3.connect('banco.db')
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()
    sql =   """
            INSERT INTO usuarios(username, password_hash, salt)
            VALUES (?, ?, ?)
            """
    cursor.execute(sql, (username, password_hash, salt))
    conexao.commit()

def search_user(username):
    
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
    

def insert_ticker(usuario_id, ticker, qnt):
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
        
      
        
def read_ticker(usuario_id):
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
    
        ticker = cursor.fetchall()
    

        return ticker
    finally:
        conexao.close()
        
    


def delete_transaction():
    pass   


insert_ticker(1,'PETR3', 30)

print(read_ticker(1))