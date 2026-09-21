from sqlalchemy import select

from app import db
from app.dominios.usuarios.modelos import Usuario


def buscar_por_correo(correo):
    consulta = select(Usuario).where(Usuario.correo == correo)
    return db.session.execute(consulta).scalar_one_or_none()


def buscar_por_id(usuario_id):
    return db.session.get(Usuario, usuario_id)


def listar_todos():
    consulta = select(Usuario).order_by(Usuario.id)
    return db.session.execute(consulta).scalars().all()


def guardar(usuario):
    try:
        db.session.add(usuario)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return usuario
