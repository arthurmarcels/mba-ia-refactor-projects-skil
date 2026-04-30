from flask import Blueprint, jsonify, request

from controllers import produto_controller
from middlewares.auth import auth_required

produto_bp = Blueprint("produtos", __name__)


@produto_bp.get("/produtos")
def listar_produtos():
    body, status = produto_controller.listar()
    return jsonify(body), status


@produto_bp.get("/produtos/busca")
def buscar_produtos():
    body, status = produto_controller.buscar_filtrados(
        request.args.get("q", ""),
        request.args.get("categoria"),
        request.args.get("preco_min"),
        request.args.get("preco_max"),
    )
    return jsonify(body), status


@produto_bp.get("/produtos/<int:produto_id>")
def buscar_produto(produto_id):
    body, status = produto_controller.buscar(produto_id)
    return jsonify(body), status


@produto_bp.post("/produtos")
@auth_required(role="admin")
def criar_produto():
    body, status = produto_controller.criar(request.get_json(silent=True))
    return jsonify(body), status


@produto_bp.put("/produtos/<int:produto_id>")
@auth_required(role="admin")
def atualizar_produto(produto_id):
    body, status = produto_controller.atualizar(
        produto_id, request.get_json(silent=True)
    )
    return jsonify(body), status


@produto_bp.delete("/produtos/<int:produto_id>")
@auth_required(role="admin")
def deletar_produto(produto_id):
    body, status = produto_controller.deletar(produto_id)
    return jsonify(body), status
