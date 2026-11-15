import pytest




@pytest.fixture
def a(banco):
    import auth
    return auth


def test_hash_gera_salt_quando_nao_informado(a):
    h, salt = a.generate_hash("senha-ficticia")
    assert salt and h


def test_mesma_senha_com_salts_diferentes_gera_hashes_diferentes(a):
    h1, s1 = a.generate_hash("senha-ficticia")
    h2, s2 = a.generate_hash("senha-ficticia")
    assert s1 != s2
    assert h1 != h2


def test_mesma_senha_e_mesmo_salt_gera_mesmo_hash(a):
    h1, salt = a.generate_hash("senha-ficticia")
    h2, _ = a.generate_hash("senha-ficticia", salt)
    assert h1 == h2


def test_hash_nao_contem_a_senha_em_texto(a):
    h, _ = a.generate_hash("senha-ficticia")
    assert "senha-ficticia" not in h


def test_check_password_aceita_senha_correta(a):
    h, salt = a.generate_hash("senha-ficticia")
    assert a.check_password("senha-ficticia", h, salt) is True


def test_check_password_recusa_senha_errada(a):
    h, salt = a.generate_hash("senha-ficticia")
    assert a.check_password("outra", h, salt) is False


def test_cadastro_guarda_hash_e_nao_a_senha(a, banco):
    a.register_user("ana", "senha-ficticia")
    user = banco.search_user("ana")
    assert user["password_hash"] != "senha-ficticia"
    assert user["salt"]


def test_login_com_senha_certa(a):
    a.register_user("ana", "senha-ficticia")
    assert a.login("ana", "senha-ficticia") is True


def test_login_com_senha_errada(a):
    a.register_user("ana", "senha-ficticia")
    assert a.login("ana", "errada") is False


def test_login_de_usuario_inexistente_devolve_falso(a):
    assert a.login("ninguem", "qualquer") is False


def test_cadastro_de_usuario_repetido_lanca_erro(a):
    a.register_user("ana", "senha-ficticia")
    with pytest.raises(a.UsuarioJaExisteError):
        a.register_user("ana", "outra-senha")


def test_usuario_repetido_nao_troca_a_senha_original(a):
    a.register_user("ana", "senha-ficticia")
    with pytest.raises(a.UsuarioJaExisteError):
        a.register_user("ana", "outra-senha")
    assert a.login("ana", "senha-ficticia") is True
