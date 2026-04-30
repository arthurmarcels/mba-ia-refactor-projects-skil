import sqlite3

from flask import g

from config.settings import Config


def get_db_connection():
    if "db" not in g:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


def close_db_connection(_exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def register_db(app):
    app.teardown_appcontext(close_db_connection)
