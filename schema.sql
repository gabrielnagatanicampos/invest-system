-- Schema Postgres (VPS com Docker ou Supabase: SQL Editor).
-- Idempotente: pode rodar mais de uma vez.
CREATE TABLE IF NOT EXISTS usuarios(
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email TEXT
);
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS email TEXT;

CREATE TABLE IF NOT EXISTS carteira(
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    ticker TEXT NOT NULL,
    quantidade INTEGER NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(usuario_id, ticker)
);

CREATE TABLE IF NOT EXISTS carteira_config(
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    saldo_renda_fixa NUMERIC,
    qnt_cripto NUMERIC,
    meta_acoes NUMERIC,
    meta_cripto NUMERIC,
    UNIQUE(usuario_id)
);
