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
    

def insert_transaction():
    pass

def list_transaction():
    pass   
