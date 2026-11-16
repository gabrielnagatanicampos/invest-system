"""Guarda contra o erro de colocar código entre @st.dialog e a função da janela.

Já aconteceu: uma função auxiliar foi inserida entre o decorador e o cadastro(),
o decorador passou a valer para ela e o formulário saiu da janela.
Não importa o web.py (ele precisa do Streamlit rodando): lê o arquivo como texto.
"""
import ast
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / "web.py"


def _funcoes():
    arvore = ast.parse(WEB.read_text(encoding="utf-8"))
    return {n.name: n for n in arvore.body if isinstance(n, ast.FunctionDef)}


def _titulo_dialog(funcao):
    for d in funcao.decorator_list:
        if (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                and d.func.attr == "dialog" and d.args):
            return d.args[0].value
    return None


def test_janelas_estao_nas_funcoes_certas():
    f = _funcoes()
    assert _titulo_dialog(f["cadastro"]) == "Criar conta"
    assert _titulo_dialog(f["login_validation"]) == "Login"


def test_so_as_janelas_tem_decorador_de_dialog():
    for nome, funcao in _funcoes().items():
        if nome not in ("cadastro", "login_validation"):
            assert _titulo_dialog(funcao) is None, f"{nome} virou janela por engano"


def _email_valido():
    codigo = ast.get_source_segment(WEB.read_text(encoding="utf-8"), _funcoes()["email_valido"])
    escopo = {}
    exec(codigo, escopo)  # a função não usa Streamlit
    return escopo["email_valido"]


def test_email_valido():
    ok = _email_valido()
    assert ok("")  # opcional
    assert ok("exemplo@example.com")
    assert not ok("sem-arroba")
    assert not ok("a b@example.com")
    assert not ok("a@semponto")
