from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app.dominios.usuarios import repositorios
from app.dominios.usuarios.modelos import PerfilUsuario, Usuario
from app.errores import ErrorAPI
from app.seguridad import generar_token


def representar_usuario(usuario):
    return {
        "id": usuario.id,
        "correo": usuario.correo,
        "rol": usuario.rol,
        "perfil": {
            "nombre": usuario.perfil.nombre,
        },
    }


def registrar_usuario(datos):
    if repositorios.buscar_por_correo(datos["correo"]) is not None:
        raise ErrorAPI("El correo ya esta registrado", 409)

    usuario = Usuario(
        correo=datos["correo"],
        contrasena=generate_password_hash(datos["contrasena"]),
        rol="usuario",
    )
    usuario.perfil = PerfilUsuario(nombre=datos["nombre"])

    try:
        repositorios.guardar(usuario)
    except IntegrityError:
        if repositorios.buscar_por_correo(datos["correo"]) is not None:
            raise ErrorAPI("El correo ya esta registrado", 409)
        raise

    return representar_usuario(usuario)


def iniciar_sesion(datos):
    usuario = repositorios.buscar_por_correo(datos["correo"])

    if usuario is None:
        raise ErrorAPI("Correo o contrasena incorrectos", 401)

    if not check_password_hash(usuario.contrasena, datos["contrasena"]):
        raise ErrorAPI("Correo o contrasena incorrectos", 401)

    return {"access_token": generar_token(usuario.id)}


def obtener_perfil(usuario_id):
    usuario = repositorios.buscar_por_id(usuario_id)

    if usuario is None:
        raise ErrorAPI("Usuario no encontrado", 404)

    return representar_usuario(usuario)


def listar_usuarios():
    usuarios = repositorios.listar_todos()
    return [representar_usuario(usuario) for usuario in usuarios]


def promover_admin(correo):
    usuario = repositorios.buscar_por_correo(correo.strip().lower())

    if usuario is None:
        raise ErrorAPI("Usuario no encontrado", 404)

    usuario.rol = "admin"
    repositorios.guardar(usuario)
    return representar_usuario(usuario)
