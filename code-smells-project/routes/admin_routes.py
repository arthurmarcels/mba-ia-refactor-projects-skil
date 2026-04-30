from flask import Blueprint, jsonify, request

from controllers import admin_controller
from middlewares.auth import auth_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.post("/admin/reset-db")
@auth_required(role="admin")
def reset_database():
    body, status = admin_controller.reset_db()
    return jsonify(body), status


@admin_bp.post("/admin/query")
@auth_required(role="admin")
def executar_query():
    body, status = admin_controller.execute_query(request.get_json(silent=True))
    return jsonify(body), status
