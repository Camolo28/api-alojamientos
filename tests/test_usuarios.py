from sqlalchemy import select
from werkzeug.security import check_password_hash

from app import db


def datos_registro():
    return {
        "nombre": "Ana",
        "correo": "ana@example.com",
        "contrasena": "123456",
    }


def test_registro_exitoso(client, app):
    datos = datos_registro()
    respuesta = client.post(
        "/api/v1/usuarios/registro",
        json=datos,
    )

    assert respuesta.status_code == 201
    contenido = respuesta.get_json()
    assert contenido["correo"] == datos["correo"]
    assert contenido["rol"] == "usuario"
    assert contenido["perfil"]["nombre"] == datos["nombre"]
    assert "contrasena" not in contenido
    assert "contrasena" not in contenido["perfil"]

    from app.dominios.usuarios.modelos import Usuario

    with app.app_context():
        usuario = db.session.execute(
            select(Usuario).where(Usuario.correo == datos["correo"])
        ).scalar_one()

        assert usuario.contrasena != datos["contrasena"]
        assert check_password_hash(
            usuario.contrasena, datos["contrasena"]
        )
        assert usuario.perfil.nombre == datos["nombre"]
        assert usuario.contrasena not in respuesta.get_data(as_text=True)


def test_registro_correo_invalido(client):
    datos = datos_registro()
    datos["correo"] = "correo-invalido"

    respuesta = client.post(
        "/api/v1/usuarios/registro",
        json=datos,
    )

    assert respuesta.status_code == 400


def test_registro_correo_duplicado(client):
    datos = datos_registro()
    primera = client.post("/api/v1/usuarios/registro", json=datos)
    segunda = client.post("/api/v1/usuarios/registro", json=datos)

    assert primera.status_code == 201
    assert segunda.status_code == 409


def test_login_exitoso(client):
    datos = datos_registro()
    registro = client.post("/api/v1/usuarios/registro", json=datos)
    assert registro.status_code == 201

    respuesta = client.post(
        "/api/v1/usuarios/login",
        json={
            "correo": datos["correo"],
            "contrasena": datos["contrasena"],
        },
    )

    assert respuesta.status_code == 200
    contenido = respuesta.get_json()
    assert isinstance(contenido["access_token"], str)
    assert contenido["access_token"]
    assert "contrasena" not in contenido


def test_login_incorrecto(client):
    datos = datos_registro()
    registro = client.post("/api/v1/usuarios/registro", json=datos)
    assert registro.status_code == 201

    respuesta = client.post(
        "/api/v1/usuarios/login",
        json={
            "correo": datos["correo"],
            "contrasena": "clave-incorrecta",
        },
    )

    assert respuesta.status_code == 401
    assert "access_token" not in respuesta.get_json()


def test_perfil_sin_token(client):
    respuesta = client.get("/api/v1/usuarios/perfil")

    assert respuesta.status_code == 401


def test_perfil_con_token(client, headers_autenticados, usuario_autenticado):
    respuesta = client.get(
        "/api/v1/usuarios/perfil",
        headers=headers_autenticados,
    )

    assert respuesta.status_code == 200
    contenido = respuesta.get_json()
    usuario = usuario_autenticado["usuario"]

    assert contenido["id"] == usuario["id"]
    assert contenido["correo"] == usuario["correo"]
    assert contenido["perfil"]["nombre"] == "Laura"
    assert "contrasena" not in contenido
    assert "contrasena" not in contenido["perfil"]


def test_perfil_sin_token(client):
    respuesta = client.get("/api/v1/usuarios/perfil")

    assert respuesta.status_code == 401


def test_perfil_con_token(client, headers_autenticados, usuario_autenticado):
    respuesta = client.get(
        "/api/v1/usuarios/perfil",
        headers=headers_autenticados,
    )

    assert respuesta.status_code == 200
    contenido = respuesta.get_json()
    usuario = usuario_autenticado["usuario"]

    assert contenido["id"] == usuario["id"]
    assert contenido["correo"] == usuario["correo"]
    assert contenido["perfil"]["nombre"] == "Laura"
    assert "contrasena" not in contenido


def test_usuario_normal_no_accede_a_admin(client, headers_autenticados):
    respuesta = client.get(
        "/api/v1/admin/usuarios",
        headers=headers_autenticados,
    )

    assert respuesta.status_code == 403


def test_administrador_lista_usuarios(
    client,
    headers_admin,
    administrador_autenticado,
):
    respuesta = client.get(
        "/api/v1/admin/usuarios",
        headers=headers_admin,
    )

    assert respuesta.status_code == 200
    contenido = respuesta.get_json()

    assert isinstance(contenido["usuarios"], list)
    assert any(
        usuario["correo"] == administrador_autenticado["correo"]
        and usuario["rol"] == "admin"
        for usuario in contenido["usuarios"]
    )

    for usuario in contenido["usuarios"]:
        assert "contrasena" not in usuario
