from config.database import get_db_connection
from config.settings import Config


def index():
    return (
        {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": Config.VERSAO,
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        },
        200,
    )


def health():
    conn = get_db_connection()
    conn.execute("SELECT 1")
    counts = {
        "produtos": conn.execute(
            "SELECT COUNT(*) AS c FROM produtos"
        ).fetchone()["c"],
        "usuarios": conn.execute(
            "SELECT COUNT(*) AS c FROM usuarios"
        ).fetchone()["c"],
        "pedidos": conn.execute(
            "SELECT COUNT(*) AS c FROM pedidos"
        ).fetchone()["c"],
    }
    return (
        {
            "status": "ok",
            "database": "connected",
            "counts": counts,
            "versao": Config.VERSAO,
            "ambiente": Config.AMBIENTE,
        },
        200,
    )
