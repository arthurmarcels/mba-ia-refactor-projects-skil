import logging

from config.database import get_db_connection
from config.settings import Config
from utils.validators import ValidationError

logger = logging.getLogger(__name__)


def reset_db():
    if not Config.ADMIN_ENDPOINTS_ENABLED:
        return (
            {"erro": "Endpoint administrativo desabilitado", "sucesso": False},
            403,
        )
    conn = get_db_connection()
    for tabela in ("itens_pedido", "pedidos", "produtos", "usuarios"):
        conn.execute(f"DELETE FROM {tabela}")
    conn.commit()
    logger.warning("admin.reset_db executado")
    return {"mensagem": "Banco de dados resetado", "sucesso": True}, 200


def execute_query(dados):
    if not Config.ADMIN_ENDPOINTS_ENABLED:
        return (
            {"erro": "Endpoint administrativo desabilitado", "sucesso": False},
            403,
        )
    if not dados:
        raise ValidationError("Dados inválidos")
    sql = (dados.get("sql") or "").strip()
    if not sql:
        raise ValidationError("Query não informada")
    if not sql.upper().startswith("SELECT"):
        return (
            {"erro": "Apenas SELECT é permitido neste endpoint", "sucesso": False},
            403,
        )
    rows = get_db_connection().execute(sql).fetchall()
    return {"dados": [dict(r) for r in rows], "sucesso": True}, 200
