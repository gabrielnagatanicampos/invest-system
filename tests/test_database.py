import sqlite3

import pytest


@pytest.fixture
def ids(banco):
    banco.insert_user("ana", "h1", "s1")
    banco.insert_user("bia", "h2", "s2")
    return banco.search_user("ana")["id"], banco.search_user("bia")["id"]


def _dict(linhas):
    return {l["ticker"]: l["quantidade"] for l in linhas}


def test_search_user_devolve_none_se_nao_existe(banco):
    assert banco.search_user("fantasma") is None


def test_insert_e_read_ticker(banco, ids):
    ana, _ = ids
    banco.insert_ticker(ana, "PETR4.SA", 10)
    assert _dict(banco.read_ticker(ana)) == {"PETR4.SA": 10}


def test_read_ticker_sem_ativos_devolve_lista_vazia(banco, ids):
    assert banco.read_ticker(ids[0]) == []


def test_insert_ticker_repetido_atualiza_quantidade(banco, ids):
    ana, _ = ids
    banco.insert_ticker(ana, "PETR4.SA", 10)
    banco.insert_ticker(ana, "PETR4.SA", 25)
    assert _dict(banco.read_ticker(ana)) == {"PETR4.SA": 25}


def test_update_ticker_muda_quantidade(banco, ids):
    ana, _ = ids
    banco.insert_ticker(ana, "VALE3.SA", 5)
    banco.update_ticker(7, ana, "VALE3.SA")
    assert _dict(banco.read_ticker(ana)) == {"VALE3.SA": 7}


def test_update_ticker_nao_cria_ativo_inexistente(banco, ids):
    ana, _ = ids
    banco.update_ticker(7, ana, "VALE3.SA")
    assert banco.read_ticker(ana) == []


def test_delete_ticker_remove_so_o_ativo_indicado(banco, ids):
    ana, _ = ids
    banco.insert_ticker(ana, "PETR4.SA", 10)
    banco.insert_ticker(ana, "VALE3.SA", 5)
    banco.delete_ticker(ana, "PETR4.SA")
    assert _dict(banco.read_ticker(ana)) == {"VALE3.SA": 5}


def test_usuarios_nao_veem_ativos_um_do_outro(banco, ids):
    ana, bia = ids
    banco.insert_ticker(ana, "PETR4.SA", 10)
    banco.insert_ticker(bia, "VALE3.SA", 3)
    assert _dict(banco.read_ticker(ana)) == {"PETR4.SA": 10}
    assert _dict(banco.read_ticker(bia)) == {"VALE3.SA": 3}


def test_mesmo_ticker_em_dois_usuarios_sao_independentes(banco, ids):
    ana, bia = ids
    banco.insert_ticker(ana, "PETR4.SA", 10)
    banco.insert_ticker(bia, "PETR4.SA", 99)
    banco.update_ticker(11, ana, "PETR4.SA")
    assert _dict(banco.read_ticker(bia)) == {"PETR4.SA": 99}


def test_delete_de_um_usuario_nao_afeta_o_outro(banco, ids):
    ana, bia = ids
    banco.insert_ticker(ana, "PETR4.SA", 10)
    banco.insert_ticker(bia, "PETR4.SA", 99)
    banco.delete_ticker(ana, "PETR4.SA")
    assert _dict(banco.read_ticker(bia)) == {"PETR4.SA": 99}


def test_save_e_load_config(banco, ids):
    ana, _ = ids
    banco.save_config(ana, 1000.0, 0.5, 60.0, 40.0)
    c = banco.load_config(ana)
    assert (c["saldo_renda_fixa"], c["qnt_cripto"], c["meta_acoes"], c["meta_cripto"]) == (1000.0, 0.5, 60.0, 40.0)


def test_load_config_sem_registro_devolve_none(banco, ids):
    assert banco.load_config(ids[0]) is None


def test_save_config_repetido_atualiza(banco, ids):
    ana, _ = ids
    banco.save_config(ana, 1000.0, 0.5, 60.0, 40.0)
    banco.save_config(ana, 2000.0, 1.0, 70.0, 30.0)
    assert banco.load_config(ana)["saldo_renda_fixa"] == 2000.0
    assert banco.load_config(ana)["meta_acoes"] == 70.0


def test_config_de_um_usuario_nao_aparece_para_outro(banco, ids):
    ana, bia = ids
    banco.save_config(ana, 1000.0, 0.5, 60.0, 40.0)
    assert banco.load_config(bia) is None


def test_load_carteira_sem_config_devolve_none(banco, ids):
    assert banco.load_carteira(ids[0]) is None


def test_load_carteira_junta_config_e_ativos(banco, ids):
    ana, _ = ids
    banco.save_config(ana, 1000.0, 0.5, 60.0, 40.0)
    banco.insert_ticker(ana, "PETR4.SA", 10)
    c = banco.load_carteira(ana)
    assert c["saldo_renda_fixa"] == 1000.0
    assert c["quantidade_de_criptomoeda"] == 0.5
    assert c["percentual_meta_acoes"] == 60.0
    assert c["percentual_meta_cripto"] == 40.0
    assert c["ativos"] == [{"ticker": "PETR4.SA", "quantidade": 10}]


def test_load_carteira_nao_mistura_ativos_de_outro_usuario(banco, ids):
    ana, bia = ids
    banco.save_config(ana, 1000.0, 0.5, 60.0, 40.0)
    banco.save_config(bia, 50.0, 0.0, 80.0, 20.0)
    banco.insert_ticker(ana, "PETR4.SA", 10)
    banco.insert_ticker(bia, "VALE3.SA", 3)
    assert banco.load_carteira(ana)["ativos"] == [{"ticker": "PETR4.SA", "quantidade": 10}]
    assert banco.load_carteira(bia)["ativos"] == [{"ticker": "VALE3.SA", "quantidade": 3}]


def test_nome_de_usuario_e_unico(banco, ids):
    with pytest.raises(sqlite3.IntegrityError):
        banco.insert_user("ana", "x", "y")


def test_salvar_email_e_search_user(banco, ids):
    banco.salvar_email(ids[0], "exemplo@example.com")
    assert banco.search_user("ana")["email"] == "exemplo@example.com"
    assert banco.search_user("bia")["email"] is None


def test_listar_usuarios_com_email_so_de_quem_tem(banco, ids):
    banco.salvar_email(ids[0], "exemplo@example.com")
    assert banco.listar_usuarios_com_email() == [
        {"id": ids[0], "username": "ana", "email": "exemplo@example.com"}
    ]


def test_listar_usuarios_com_email_vazio(banco, ids):
    assert banco.listar_usuarios_com_email() == []


def test_migracao_de_banco_antigo_sem_coluna_email(banco, tmp_path):
    import importlib
    antigo = tmp_path / "banco.db"
    antigo.unlink()
    con = sqlite3.connect(antigo)
    con.execute("""CREATE TABLE usuarios(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
        salt TEXT NOT NULL, created_on DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    con.execute("INSERT INTO usuarios(username, password_hash, salt) VALUES ('ana','h','s')")
    con.commit()
    con.close()
    importlib.reload(banco)
    banco.init_db()
    banco.init_db()  # rodar duas vezes não pode falhar
    assert banco.search_user("ana")["email"] is None
    banco.salvar_email(1, "exemplo@example.com")
    assert banco.listar_usuarios_com_email()[0]["username"] == "ana"


def test_banco_de_teste_fica_na_pasta_temporaria(banco, tmp_path):
    assert (tmp_path / "banco.db").exists()
