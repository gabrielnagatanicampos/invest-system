"""Acesso ao banco. Usa Postgres (Supabase ou VPS) se DATABASE_URL existir;
senão usa o SQLite local 'banco.db'. Nenhuma conexão é aberta no import."""
import os
import sqlite3

from dotenv import load_dotenv

try:
    import psycopg2
    import psycopg2.extras
except ImportError:  # sem psycopg2 só o SQLite funciona
    psycopg2 = None

load_dotenv()

_inicializado = False


def _usa_postgres() -> bool:
    return bool(os.getenv("DATABASE_URL")) and psycopg2 is not None


def _abrir():
    if _usa_postgres():
        return psycopg2.connect(
            os.environ["DATABASE_URL"],
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
    conexao = sqlite3.connect("banco.db")
    conexao.row_factory = sqlite3.Row
    return conexao


def _conectar():
    """Abre uma conexão nova (cria as tabelas na primeira vez).
    Quem chama é responsável por fechar."""
    if not _inicializado:
        init_db()
    return _abrir()


def _sql(sql: str) -> str:
    """Troca ? por %s quando o banco é Postgres."""
    return sql.replace("?", "%s") if _usa_postgres() else sql


def _executar(sql, params=(), *, resultado=None):
    """Executa uma consulta e fecha a conexão. resultado: None, 'um' ou 'todos'."""
    conexao = _conectar()
    try:
        cursor = conexao.cursor()
        cursor.execute(_sql(sql), params)
        dados = None
        if resultado == "um":
            dados = cursor.fetchone()
        elif resultado == "todos":
            dados = cursor.fetchall()
        conexao.commit()
        return dados
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def init_db():
    """Cria as tabelas (se não existirem) e a coluna email (migração segura)."""
    global _inicializado
    pg = _usa_postgres()
    pk = ("INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY" if pg
          else "INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT")
    ts = "TIMESTAMP" if pg else "DATETIME"

    conexao = _abrir()
    try:
        cursor = conexao.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS usuarios(
                id {pk},
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_on {ts} DEFAULT CURRENT_TIMESTAMP
            )""")
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS carteira(
                id {pk},
                usuario_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                criado_em {ts} DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                UNIQUE(usuario_id, ticker)
            )""")
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS carteira_config(
                id {pk},
                usuario_id INTEGER NOT NULL,
                saldo_renda_fixa NUMERIC,
                qnt_cripto NUMERIC,
                meta_acoes NUMERIC,
                meta_cripto NUMERIC,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                UNIQUE(usuario_id)
            )""")
        if pg:
            cursor.execute(
                "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS email TEXT")
        else:
            cursor.execute("PRAGMA table_info(usuarios)")
            colunas = [c["name"] for c in cursor.fetchall()]
            if "email" not in colunas:
                cursor.execute("ALTER TABLE usuarios ADD COLUMN email TEXT")
        conexao.commit()
        _inicializado = True
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def insert_user(username: str, password_hash: str, salt):
    sql = """
        INSERT INTO usuarios(username, password_hash, salt)
        VALUES (?, ?, ?)
        """
    try:
        _executar(sql, (username, password_hash, salt))
    except Exception as erro:
        # auth.py captura sqlite3.IntegrityError; traduz o erro do Postgres.
        if psycopg2 is not None and isinstance(erro, psycopg2.IntegrityError):
            raise sqlite3.IntegrityError(str(erro)) from erro
        raise


def search_user(username: str):
    return _executar(
        "SELECT * FROM usuarios WHERE username = ?",
        (username,), resultado="um")


def salvar_email(usuario_id: int, email: str):
    _executar("UPDATE usuarios SET email = ? WHERE id = ?",
              (email, usuario_id))


def listar_usuarios_com_email():
    linhas = _executar(
        """
        SELECT id, username, email
        FROM usuarios
        WHERE email IS NOT NULL AND email <> ''
        """, resultado="todos")
    return [{"id": l["id"], "username": l["username"], "email": l["email"]}
            for l in linhas]


def insert_ticker(usuario_id: int, ticker: str, qnt: int):
    _executar(
        """
        INSERT INTO carteira(usuario_id, ticker, quantidade)
        VALUES (?, ?, ?)
        ON CONFLICT(usuario_id, ticker) DO UPDATE SET
            quantidade = excluded.quantidade
        """, (usuario_id, ticker, qnt))


def read_ticker(usuario_id: int):
    return _executar(
        "SELECT ticker, quantidade FROM carteira WHERE usuario_id = ?",
        (usuario_id,), resultado="todos")


def delete_ticker(usuario_id: int, ticker: str):
    _executar(
        "DELETE FROM carteira WHERE usuario_id = ? AND ticker = ?",
        (usuario_id, ticker))


def update_ticker(quantidade: int, usuario_id: int, ticker: str):
    _executar(
        """
        UPDATE carteira SET quantidade = ?
        WHERE usuario_id = ? AND ticker = ?
        """, (quantidade, usuario_id, ticker))


def save_config(usuario_id: int, s_rf: float, qnt_bit: float,
                meta_acoes: float, meta_cripto: float):
    _executar(
        """
        INSERT INTO carteira_config(usuario_id, saldo_renda_fixa, qnt_cripto, meta_acoes, meta_cripto)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(usuario_id) DO UPDATE SET
            saldo_renda_fixa = excluded.saldo_renda_fixa,
            qnt_cripto = excluded.qnt_cripto,
            meta_acoes = excluded.meta_acoes,
            meta_cripto = excluded.meta_cripto
        """, (usuario_id, s_rf, qnt_bit, meta_acoes, meta_cripto))


def load_config(usuario_id):
    return _executar(
        """
        SELECT saldo_renda_fixa, qnt_cripto, meta_acoes, meta_cripto
        FROM carteira_config WHERE usuario_id = ?
        """, (usuario_id,), resultado="um")


def load_carteira(usuario_id):
    config = load_config(usuario_id)
    if config is None:
        return None
    ativos = read_ticker(usuario_id)
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
