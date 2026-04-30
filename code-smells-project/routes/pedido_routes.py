from flask import Blueprint, jsonify, request

from controllers import pedido_controller
from middlewares.auth import auth_required

pedido_bp = Blueprint("pedidos", __name__)


@pedido_bp.post("/pedidos")
@auth_required()
def criar_pedido():
    body, status = pedido_controller.criar(request.get_json(silent=True))
    return jsonify(body), status


@pedido_bp.get("/pedidos")
@auth_required(role="admin")
def listar_todos_pedidos():
    body, status = pedido_controller.listar_todos()
    return jsonify(body), status


@pedido_bp.get("/pedidos/usuario/<int:usuario_id>")
@auth_required()
def listar_pedidos_usuario(usuario_id):
    body, status = pedido_controller.listar_por_usuario(usuario_id)
    return jsonify(body), status


@pedido_bp.put("/pedidos/<int:pedido_id>/status")
@auth_required(role="admin")
def atualizar_status_pedido(pedido_id):
    body, status = pedido_controller.atualizar_status(
        pedido_id, request.get_json(silent=True)
    )
    return jsonify(body), status
