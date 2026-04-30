from models import pedido_model, produto_model
from services import notification_service
from utils.validators import ValidationError

STATUS_VALIDOS = {"pendente", "aprovado", "enviado", "entregue", "cancelado"}


def criar_pedido(usuario_id, itens):
    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    if not itens or len(itens) == 0:
        raise ValidationError("Pedido deve ter pelo menos 1 item")

    produto_ids = []
    for item in itens:
        if not isinstance(item, dict) or "produto_id" not in item or "quantidade" not in item:
            raise ValidationError("Cada item precisa de produto_id e quantidade")
        quantidade = item["quantidade"]
        if not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade <= 0:
            raise ValidationError("Quantidade deve ser inteiro positivo")
        produto_ids.append(item["produto_id"])

    produtos = produto_model.get_many_by_ids(produto_ids)

    total = 0.0
    linhas = []
    for item in itens:
        produto = produtos.get(item["produto_id"])
        if produto is None:
            raise ValidationError(
                f"Produto {item['produto_id']} não encontrado"
            )
        if produto["estoque"] < item["quantidade"]:
            raise ValidationError(
                f"Estoque insuficiente para {produto['nome']}"
            )
        total += produto["preco"] * item["quantidade"]
        linhas.append(
            {
                "produto_id": item["produto_id"],
                "quantidade": item["quantidade"],
                "preco_unitario": produto["preco"],
            }
        )

    pedido_id = pedido_model.create(usuario_id, total)
    pedido_model.add_items(pedido_id, linhas)
    for linha in linhas:
        produto_model.adjust_estoque(linha["produto_id"], -linha["quantidade"])

    notification_service.send_order_created(pedido_id, usuario_id)
    return {"pedido_id": pedido_id, "total": total}


def atualizar_status(pedido_id, status):
    if status not in STATUS_VALIDOS:
        raise ValidationError("Status inválido")
    if pedido_model.get_by_id(pedido_id) is None:
        raise ValidationError("Pedido não encontrado")
    pedido_model.update_status(pedido_id, status)
    notification_service.send_status_changed(pedido_id, status)
