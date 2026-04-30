from flask import Blueprint, jsonify, request

from controllers import usuario_controller
from middlewares.auth import auth_required

usuario_bp = Blueprint("usuarios", __name__)


@usuario_bp.get("/usuarios")
@auth_required(role="admin")
def listar_usuarios():
    body, status = usuario_controller.listar()
    return jsonify(body), status


@usuario_bp.get("/usuarios/<int:usuario_id>")
@auth_required()
def buscar_usuario(usuario_id):
    body, status = usuario_controller.buscar(usuario_id)
    return jsonify(body), status


@usuario_bp.post("/usuarios")
def criar_usuario():
    body, status = usuario_controller.criar(request.get_json(silent=True))
    return jsonify(body), status
