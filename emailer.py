"""Envio de e-mail por SMTP. Credenciais apenas por variáveis de ambiente."""
import os
import smtplib
from email.message import EmailMessage

VARIAVEIS = ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM")


class ConfigEmailErro(Exception):
    pass


def ler_config() -> dict:
    faltando = [v for v in VARIAVEIS if not os.environ.get(v)]
    if faltando:
        raise ConfigEmailErro(
            "Variáveis de ambiente ausentes: " + ", ".join(faltando)
        )
    config = {v: os.environ[v] for v in VARIAVEIS}
    try:
        config["SMTP_PORT"] = int(config["SMTP_PORT"])
    except ValueError:
        raise ConfigEmailErro("SMTP_PORT deve ser um número inteiro")
    return config


def enviar_email(destinatario: str, assunto: str, corpo: str) -> None:
    config = ler_config()
    msg = EmailMessage()
    msg["From"] = config["SMTP_FROM"]
    msg["To"] = destinatario
    msg["Subject"] = assunto
    msg.set_content(corpo)

    with smtplib.SMTP(config["SMTP_HOST"], config["SMTP_PORT"], timeout=30) as smtp:
        smtp.starttls()
        smtp.login(config["SMTP_USER"], config["SMTP_PASSWORD"])
        smtp.send_message(msg)
