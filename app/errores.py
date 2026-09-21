from marshmallow import ValidationError


class ErrorAPI(Exception):
    def __init__(self, mensaje, codigo=400):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo


def registrar_errores(app):
    @app.errorhandler(ValidationError)
    def manejar_validacion(error):
        return {
            "error": "Datos invalidos",
            "detalles": error.messages,
        }, 400

    @app.errorhandler(ErrorAPI)
    def manejar_error_api(error):
        return {"error": error.mensaje}, error.codigo
