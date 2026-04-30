from werkzeug.security import generate_password_hash

from models import usuario_model
from utils.validators import ValidationError, validate_usuario_payload


def listar():
    return {"dados": usuario_model.get_all(), "sucesso": True}, 200


def buscar(usuario_id):
    usuario = usuario_model.get_by_id(usuario_id)
    if usuario is None:
        return {"erro": "Usuário não encontrado", "sucesso": False}, 404
    return {"dados": usuario, "sucesso": True}, 200


def criar(dados):
    validate_usuario_payload(dados)
    if usuario_model.get_by_email_with_credentials(dados["email"]):
        raise ValidationError("Email já cadastrado")
    usuario_id = usuario_model.create(
        dados["nome"],
        dados["email"],
        generate_password_hash(dados["senha"]),
    )
    return {"dados": {"id": usuario_id}, "sucesso": True}, 201
