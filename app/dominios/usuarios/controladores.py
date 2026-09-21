from flask import Blueprint, g, request

from app.dominios.usuarios import servicios
from app.dominios.usuarios.dtos import LoginUsuarioDTO, RegistroUsuarioDTO
from app.errores import ErrorAPI
from app.seguridad import requiere_admin, requiere_token


usuarios_bp = Blueprint("usuarios", __name__)
admin_bp = Blueprint("admin", __name__)


def leer_json():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        raise ErrorAPI("El cuerpo debe ser un objeto JSON valido", 400)

    return datos


@usuarios_bp.post("/registro")
def registro():
    datos = RegistroUsuarioDTO().load(leer_json())
    return servicios.registrar_usuario(datos), 201


@usuarios_bp.post("/login")
def login():
    datos = LoginUsuarioDTO().load(leer_json())
    return servicios.iniciar_sesion(datos), 200


@usuarios_bp.get("/perfil")
@requiere_token
def perfil():
    return servicios.obtener_perfil(g.usuario_id), 200


@admin_bp.get("/usuarios")
@requiere_admin
def usuarios_administracion():
    return {"usuarios": servicios.listar_usuarios()}, 200
