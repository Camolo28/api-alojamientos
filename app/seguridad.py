from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, request

from app.errores import ErrorAPI


def generar_token(usuario_id):
    ahora = datetime.now(timezone.utc)

    contenido = {
        "sub": str(usuario_id),
        "iat": ahora,
        "exp": ahora + timedelta(
            minutes=current_app.config["JWT_EXP_MINUTES"]
        ),
    }

    return jwt.encode(
        contenido,
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )


def obtener_usuario_del_token():
    autorizacion = request.headers.get("Authorization", "")
    partes = autorizacion.split()

    if len(partes) != 2 or partes[0].lower() != "bearer":
        raise ErrorAPI("Token de autenticacion requerido", 401)

    try:
        contenido = jwt.decode(
            partes[1],
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )
        usuario_id = int(contenido["sub"])
    except (
        jwt.ExpiredSignatureError,
        jwt.InvalidTokenError,
        KeyError,
        TypeError,
        ValueError,
    ):
        raise ErrorAPI("Token invalido o expirado", 401)

    from app.dominios.usuarios import repositorios

    usuario = repositorios.buscar_por_id(usuario_id)
    if usuario is None:
        raise ErrorAPI("Usuario no encontrado", 401)

    return usuario


def requiere_token(funcion):
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        usuario = obtener_usuario_del_token()
        g.usuario_id = usuario.id
        return funcion(*args, **kwargs)

    return envoltura


def requiere_admin(funcion):
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        usuario = obtener_usuario_del_token()

        if usuario.rol != "admin":
            raise ErrorAPI("No tiene permisos para acceder", 403)

        g.usuario_id = usuario.id
        return funcion(*args, **kwargs)

    return envoltura
