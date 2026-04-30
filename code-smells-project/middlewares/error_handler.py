import logging

from flask import jsonify

from utils.validators import ValidationError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({"erro": str(e), "sucesso": False}), 400

    @app.errorhandler(404)
    def handle_not_found(_e):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(_e):
        return jsonify({"erro": "Método não permitido", "sucesso": False}), 405

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.exception("unhandled exception: %s", e)
        return jsonify(
            {"erro": "Erro interno do servidor", "sucesso": False}
        ), 500
