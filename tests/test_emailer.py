from unittest.mock import patch

import pytest

import emailer

ENV = {
    "SMTP_HOST": "smtp.example.com", "SMTP_PORT": "587",
    "SMTP_USER": "usuario-ficticio", "SMTP_PASSWORD": "senha-ficticia",
    "SMTP_FROM": "remetente@example.com",
}


def test_envia_com_starttls(monkeypatch):
    for k, v in ENV.items():
        monkeypatch.setenv(k, v)
    with patch("emailer.smtplib.SMTP") as smtp_cls:
        smtp = smtp_cls.return_value.__enter__.return_value
        emailer.enviar_email("exemplo@example.com", "Assunto", "Corpo")
    smtp_cls.assert_called_once_with("smtp.example.com", 587, timeout=30)
    smtp.starttls.assert_called_once()
    smtp.login.assert_called_once_with("usuario-ficticio", "senha-ficticia")
    msg = smtp.send_message.call_args[0][0]
    assert msg["To"] == "exemplo@example.com"
    assert msg["Subject"] == "Assunto"


def test_credenciais_ausentes(monkeypatch):
    for k in ENV:
        monkeypatch.delenv(k, raising=False)
    with patch("emailer.smtplib.SMTP") as smtp_cls:
        with pytest.raises(emailer.ConfigEmailErro, match="SMTP_HOST"):
            emailer.enviar_email("exemplo@example.com", "a", "b")
    smtp_cls.assert_not_called()


def test_porta_invalida(monkeypatch):
    for k, v in ENV.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setenv("SMTP_PORT", "abc")
    with pytest.raises(emailer.ConfigEmailErro):
        emailer.ler_config()
