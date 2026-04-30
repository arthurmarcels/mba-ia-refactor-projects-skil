from config.database import get_db_connection


def _row_to_produto(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def get_all():
    rows = get_db_connection().execute("SELECT * FROM produtos").fetchall()
    return [_row_to_produto(r) for r in rows]


def get_by_id(produto_id):
    row = (
        get_db_connection()
        .execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        .fetchone()
    )
    return _row_to_produto(row) if row else None


def get_many_by_ids(ids):
    if not ids:
        return {}
    placeholders = ",".join("?" for _ in ids)
    rows = (
        get_db_connection()
        .execute(
            f"SELECT * FROM produtos WHERE id IN ({placeholders})",
            tuple(ids),
        )
        .fetchall()
    )
    return {r["id"]: _row_to_produto(r) for r in rows}


def create(nome, descricao, preco, estoque, categoria):
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    conn.commit()
    return cursor.lastrowid


def update(produto_id, nome, descricao, preco, estoque, categoria):
    conn = get_db_connection()
    conn.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    conn.commit()


def delete(produto_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    conn.commit()


def search(termo, categoria, preco_min, preco_max):
    sql = "SELECT * FROM produtos WHERE 1=1"
    params = []
    if termo:
        sql += " AND (nome LIKE ? OR descricao LIKE ?)"
        like = f"%{termo}%"
        params.extend([like, like])
    if categoria:
        sql += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        sql += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        sql += " AND preco <= ?"
        params.append(preco_max)
    rows = get_db_connection().execute(sql, params).fetchall()
    return [_row_to_produto(r) for r in rows]


def adjust_estoque(produto_id, delta):
    conn = get_db_connection()
    conn.execute(
        "UPDATE produtos SET estoque = estoque + ? WHERE id = ?",
        (delta, produto_id),
    )
    conn.commit()
