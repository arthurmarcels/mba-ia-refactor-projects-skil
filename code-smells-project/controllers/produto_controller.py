from models import produto_model
from utils.validators import ValidationError, validate_produto_payload


def listar():
    return {"dados": produto_model.get_all(), "sucesso": True}, 200


def buscar(produto_id):
    produto = produto_model.get_by_id(produto_id)
    if produto is None:
        return {"erro": "Produto não encontrado", "sucesso": False}, 404
    return {"dados": produto, "sucesso": True}, 200


def criar(dados):
    validate_produto_payload(dados)
    produto_id = produto_model.create(
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral"),
    )
    return (
        {"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"},
        201,
    )


def atualizar(produto_id, dados):
    if produto_model.get_by_id(produto_id) is None:
        return {"erro": "Produto não encontrado", "sucesso": False}, 404
    validate_produto_payload(dados)
    produto_model.update(
        produto_id,
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral"),
    )
    return {"sucesso": True, "mensagem": "Produto atualizado"}, 200


def deletar(produto_id):
    if produto_model.get_by_id(produto_id) is None:
        return {"erro": "Produto não encontrado", "sucesso": False}, 404
    produto_model.delete(produto_id)
    return {"sucesso": True, "mensagem": "Produto deletado"}, 200


def buscar_filtrados(termo, categoria, preco_min, preco_max):
    if preco_min is not None:
        try:
            preco_min = float(preco_min)
        except (TypeError, ValueError):
            raise ValidationError("preco_min inválido")
    if preco_max is not None:
        try:
            preco_max = float(preco_max)
        except (TypeError, ValueError):
            raise ValidationError("preco_max inválido")
    resultados = produto_model.search(termo, categoria, preco_min, preco_max)
    return (
        {"dados": resultados, "total": len(resultados), "sucesso": True},
        200,
    )
