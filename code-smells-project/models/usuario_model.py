from config.database import get_db_connection


def _row_to_public(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def get_all():
    rows = get_db_connection().execute("SELECT * FROM usuarios").fetchall()
    return [_row_to_public(r) for r in rows]


def get_by_id(usuario_id):
    row = (
        get_db_connection()
        .execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        .fetchone()
    )
    return _row_to_public(row) if row else None


def get_by_email_with_credentials(email):
    row = (
        get_db_connection()
        .execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        .fetchone()
    )
    if row is None:
        return None
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "senha_hash": row["senha"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def create(nome, email, senha_hash, tipo="cliente"):
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    conn.commit()
    return cursor.lastrowid
