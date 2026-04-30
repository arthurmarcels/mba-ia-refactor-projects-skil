from werkzeug.security import check_password_hash

from middlewares.auth import issue_token
from models import usuario_model
from utils.validators import ValidationError


def login(dados):
    if not dados:
        raise ValidationError("Dados inválidos")
    email = (dados.get("email") or "").strip()
    senha = dados.get("senha") or ""
    if not email or not senha:
        raise ValidationError("Email e senha são obrigatórios")

    credenciais = usuario_model.get_by_email_with_credentials(email)
    if credenciais is None or not check_password_hash(
        credenciais["senha_hash"], senha
    ):
        return {"erro": "Email ou senha inválidos", "sucesso": False}, 401

    token = issue_token(credenciais)
    return (
        {
            "dados": {
                "id": credenciais["id"],
                "nome": credenciais["nome"],
                "email": credenciais["email"],
                "tipo": credenciais["tipo"],
                "token": token,
            },
            "sucesso": True,
            "mensagem": "Login OK",
        },
        200,
    )
