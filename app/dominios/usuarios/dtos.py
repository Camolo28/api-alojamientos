from marshmallow import Schema, fields, pre_load, validate


class DatosUsuarioDTO(Schema):
    @pre_load
    def normalizar(self, datos, **kwargs):
        if not isinstance(datos, dict):
            return datos

        datos = datos.copy()
        for campo in ("nombre", "correo"):
            if isinstance(datos.get(campo), str):
                datos[campo] = datos[campo].strip()

        if isinstance(datos.get("correo"), str):
            datos["correo"] = datos["correo"].lower()

        return datos


class RegistroUsuarioDTO(DatosUsuarioDTO):
    nombre = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
    )
    correo = fields.Email(
        required=True,
        validate=validate.Length(max=254),
    )
    contrasena = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=6, max=128),
    )


class LoginUsuarioDTO(DatosUsuarioDTO):
    correo = fields.Email(
        required=True,
        validate=validate.Length(max=254),
    )
    contrasena = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=1, max=128),
    )
