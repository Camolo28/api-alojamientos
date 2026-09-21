import sys
from pathlib import Path

raiz_proyecto = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(raiz_proyecto))

from app import create_app
from app.dominios.usuarios import servicios
from app.errores import ErrorAPI


def main():
    if len(sys.argv) != 2:
        print("Uso: python scripts/promover_admin.py correo@ejemplo.com")
        raise SystemExit(1)

    correo = sys.argv[1]
    app = create_app()

    with app.app_context():
        try:
            usuario = servicios.promover_admin(correo)
        except ErrorAPI as error:
            print(error.mensaje)
            raise SystemExit(1)

        print(f"Usuario promovido a admin: {usuario['correo']}")


if __name__ == "__main__":
    main()
