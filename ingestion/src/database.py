"""Motor de conexión de PostgreSQL utilizado por la ingesta de OpenBridge."""

from sqlalchemy import create_engine, text

from config import DATABASE_URL

# Crear el motor no abre una conexión hasta que se utiliza.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_timeout=10,
    connect_args={"connect_timeout": 10},
)


def test_connection() -> str:
    """Verifica la conexión con una consulta de lectura y devuelve el nombre de BD."""
    with engine.connect() as connection:
        database_name = connection.execute(text("SELECT current_database();")).scalar_one()

    print("Conexión exitosa ✅")
    print("Base de datos:", database_name)
    return database_name


if __name__ == "__main__":
    test_connection()
