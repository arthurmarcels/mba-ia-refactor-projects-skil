import logging
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import g, jsonify, request

from config.settings import Config

logger = logging.getLogger(__name__)


def issue_token(usuario):
    payload = {
        "user_id": usuario["id"],
        "tipo": usuario.get("tipo", "cliente"),
        "exp": datetime.now(timezone.utc)
        + timedelta(hours=Config.JWT_EXPIRES_HOURS),
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")


def _decode_token(token):
    return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])


def auth_required(role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not Config.AUTH_ENABLED:
                logger.warning(
                    "auth bypass: AUTH_ENABLED=false (rota=%s método=%s)",
                    request.path,
                    request.method,
                )
                g.current_user = None
                return fn(*args, **kwargs)

            header = request.headers.get("Authorization", "")
            if not header.startswith("Bearer "):
                return jsonify({"erro": "Token ausente", "sucesso": False}), 401
            token = header[len("Bearer ") :].strip()
            if not token:
                return jsonify({"erro": "Token ausente", "sucesso": False}), 401

            try:
                payload = _decode_token(token)
            except jwt.ExpiredSignatureError:
                return jsonify({"erro": "Token expirado", "sucesso": False}), 401
            except jwt.InvalidTokenError:
                return jsonify({"erro": "Token inválido", "sucesso": False}), 401

            if role and payload.get("tipo") != role:
                return jsonify({"erro": "Acesso negado", "sucesso": False}), 403

            g.current_user = payload
            return fn(*args, **kwargs)

        return wrapper

    return decorator
