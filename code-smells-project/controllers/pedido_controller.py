from models import pedido_model
from services import pedido_service
from utils.validators import ValidationError


def criar(dados):
    if not dados:
        raise ValidationError("Dados inválidos")
    resultado = pedido_service.criar_pedido(
        dados.get("usuario_id"), dados.get("itens", [])
    )
    return (
        {
            "dados": resultado,
            "sucesso": True,
            "mensagem": "Pedido criado com sucesso",
        },
        201,
    )


def listar_todos():
    return {"dados": pedido_model.list_with_items(), "sucesso": True}, 200


def listar_por_usuario(usuario_id):
    return (
        {"dados": pedido_model.list_with_items(usuario_id=usuario_id), "sucesso": True},
        200,
    )


def atualizar_status(pedido_id, dados):
    if not dados:
        raise ValidationError("Dados inválidos")
    pedido_service.atualizar_status(pedido_id, dados.get("status", ""))
    return {"sucesso": True, "mensagem": "Status atualizado"}, 200
