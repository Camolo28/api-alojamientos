from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

API_VERSION = "v1"

db = SQLAlchemy()
migrate = Migrate()


def create_app(configuracion=None):
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)

    if configuracion is not None:
        app.config.update(configuracion)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Configura SECRET_KEY en el archivo .env")

    db.init_app(app)

    from app.dominios.usuarios.controladores import admin_bp, usuarios_bp
    from app.errores import registrar_errores

    migrate.init_app(app, db)
    CORS(app, origins=app.config["CORS_ALLOWED_ORIGINS"])

    app.register_blueprint(usuarios_bp, url_prefix="/api/v1/usuarios")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")
    registrar_errores(app)

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "service": "alojamientos-api",
            "version": API_VERSION,
        }, 200

    return app
