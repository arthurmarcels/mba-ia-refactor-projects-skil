from flask import Blueprint, jsonify

from controllers import relatorio_controller
from middlewares.auth import auth_required

relatorio_bp = Blueprint("relatorios", __name__)


@relatorio_bp.get("/relatorios/vendas")
@auth_required(role="admin")
def relatorio_vendas():
    body, status = relatorio_controller.relatorio_vendas()
    return jsonify(body), status
