from flask import Flask
from flask_cors import CORS

from config.database import register_db
from config.logging import configure_logging
from config.settings import Config
from middlewares.error_handler import register_error_handlers
from migrations.init_schema import init_schema
from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp
from routes.pedido_routes import pedido_bp
from routes.produto_routes import produto_bp
from routes.relatorio_routes import relatorio_bp
from routes.system_routes import system_bp
from routes.usuario_routes import usuario_bp
from seeds.initial_data import seed_if_empty


def create_app():
    configure_logging()
    init_schema()
    seed_if_empty()

    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/*": {"origins": Config.ALLOWED_ORIGINS}})

    register_db(app)
    register_error_handlers(app)

    app.register_blueprint(system_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(relatorio_bp)
    app.register_blueprint(admin_bp)

    return app


if __name__ == "__main__":
    application = create_app()
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://{Config.HOST}:{Config.PORT}")
    print("=" * 50)
    application.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
