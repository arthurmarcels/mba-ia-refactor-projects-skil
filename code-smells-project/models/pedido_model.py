from collections import OrderedDict

from config.database import get_db_connection


def create(usuario_id, total):
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total),
    )
    conn.commit()
    return cursor.lastrowid


def add_items(pedido_id, items):
    conn = get_db_connection()
    conn.executemany(
        "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
        [
            (pedido_id, i["produto_id"], i["quantidade"], i["preco_unitario"])
            for i in items
        ],
    )
    conn.commit()


def get_by_id(pedido_id):
    row = (
        get_db_connection()
        .execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,))
        .fetchone()
    )
    if row is None:
        return None
    return {
        "id": row["id"],
        "usuario_id": row["usuario_id"],
        "status": row["status"],
        "total": row["total"],
        "criado_em": row["criado_em"],
    }


def update_status(pedido_id, status):
    conn = get_db_connection()
    conn.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (status, pedido_id),
    )
    conn.commit()


def list_with_items(usuario_id=None):
    sql = """
        SELECT
            p.id AS pedido_id, p.usuario_id, p.status, p.total, p.criado_em,
            ip.produto_id, ip.quantidade, ip.preco_unitario,
            pr.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido ip ON p.id = ip.pedido_id
        LEFT JOIN produtos pr ON ip.produto_id = pr.id
    """
    params = ()
    if usuario_id is not None:
        sql += " WHERE p.usuario_id = ?"
        params = (usuario_id,)
    sql += " ORDER BY p.id"

    rows = get_db_connection().execute(sql, params).fetchall()
    pedidos = OrderedDict()
    for row in rows:
        pid = row["pedido_id"]
        if pid not in pedidos:
            pedidos[pid] = {
                "id": pid,
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
        if row["produto_id"] is not None:
            pedidos[pid]["itens"].append(
                {
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"] or "Desconhecido",
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"],
                }
            )
    return list(pedidos.values())


def stats():
    row = (
        get_db_connection()
        .execute(
            """
        SELECT
            COUNT(*) AS total,
            COALESCE(SUM(total), 0) AS faturamento,
            SUM(CASE WHEN status = 'pendente'  THEN 1 ELSE 0 END) AS pendentes,
            SUM(CASE WHEN status = 'aprovado'  THEN 1 ELSE 0 END) AS aprovados,
            SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END) AS cancelados
        FROM pedidos
        """
        )
        .fetchone()
    )
    return {
        "total": row["total"] or 0,
        "faturamento": row["faturamento"] or 0,
        "pendentes": row["pendentes"] or 0,
        "aprovados": row["aprovados"] or 0,
        "cancelados": row["cancelados"] or 0,
    }
