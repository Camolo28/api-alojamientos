from app import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(254), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="usuario")

    perfil = db.relationship(
        "PerfilUsuario",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
    )


class PerfilUsuario(db.Model):
    __tablename__ = "perfiles"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        unique=True,
        nullable=False,
    )

    usuario = db.relationship("Usuario", back_populates="perfil")
