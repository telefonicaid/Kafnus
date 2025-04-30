from sqlalchemy import create_engine, text
import requests
import time

POSTGRES_URL = "postgresql://test:test@localhost:5432/testdb"
CONNECT_URL = "http://localhost:8083"

def before_scenario(context, scenario):
    # Verifica que la DB esté lista
    engine = create_engine(POSTGRES_URL)
    retries = 5
    for _ in range(retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            break
        except Exception:
            time.sleep(2)
    context.db_engine = engine

def after_scenario(context, scenario):
    # Limpia la tabla si fue creada
    with context.db_engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS clientes"))

    # Elimina el conector si existe
    try:
        r = requests.delete(f"{CONNECT_URL}/connectors/jdbc-sink")
        if r.status_code not in (200, 404):
            print(f"Error eliminando conector: {r.text}")
    except Exception as e:
        print(f"Error al conectar con Kafka Connect: {e}")
