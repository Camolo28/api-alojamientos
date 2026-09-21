import pytest

from app import create_app, db


@pytest.fixture
def app():
    aplicacion = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "clave-exclusiva-para-pruebas-automatizadas",
        "JWT_EXP_MINUTES": 15,
        "CORS_ALLOWED_ORIGINS": ["http://localhost:5173"],
    })

    with aplicacion.app_context():
        db.create_all()

    yield aplicacion

    with aplicacion.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def usuario_autenticado(client):
    datos = {
        "nombre": "Laura",
        "correo": "laura@example.com",
        "contrasena": "123456",
    }

    registro = client.post("/api/v1/usuarios/registro", json=datos)
    assert registro.status_code == 201

    login = client.post(
        "/api/v1/usuarios/login",
        json={
            "correo": datos["correo"],
            "contrasena": datos["contrasena"],
        },
    )
    assert login.status_code == 200

    return {
        "usuario": registro.get_json(),
        "token": login.get_json()["access_token"],
    }


@pytest.fixture
def headers_autenticados(usuario_autenticado):
    return {
        "Authorization": f"Bearer {usuario_autenticado['token']}",
    }


@pytest.fixture
def administrador_autenticado(client, app):
    datos = {
        "nombre": "Administrador",
        "correo": "admin@example.com",
        "contrasena": "123456",
    }

    registro = client.post("/api/v1/usuarios/registro", json=datos)
    assert registro.status_code == 201

    from app.dominios.usuarios import repositorios

    with app.app_context():
        usuario = repositorios.buscar_por_correo(datos["correo"])
        usuario.rol = "admin"
        repositorios.guardar(usuario)

    login = client.post(
        "/api/v1/usuarios/login",
        json={
            "correo": datos["correo"],
            "contrasena": datos["contrasena"],
        },
    )
    assert login.status_code == 200

    return {
        "correo": datos["correo"],
        "token": login.get_json()["access_token"],
    }


@pytest.fixture
def headers_admin(administrador_autenticado):
    return {
        "Authorization": (
            f"Bearer {administrador_autenticado['token']}"
        ),
    }
