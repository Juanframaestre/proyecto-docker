import os
import time

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

# El host es el NOMBRE DEL SERVICIO definido en docker-compose.yml ("db"),
# NO localhost ni una IP fija. Docker resuelve el nombre por DNS interno.
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "db"),
    "port": int(os.environ.get("DB_PORT", "5432")),
    "dbname": os.environ["POSTGRES_DB"],
    "user": os.environ["POSTGRES_USER"],
    "password": os.environ["POSTGRES_PASSWORD"],
}


def get_conn(retries=10, delay=2):
    for intento in range(retries):
        try:
            return psycopg2.connect(**DB_CONFIG)
        except psycopg2.OperationalError:
            print(f"Esperando a la base de datos... ({intento + 1}/{retries})", flush=True)
            time.sleep(delay)
    raise RuntimeError("No fue posible conectar con la base de datos")


def init_db():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS notas (
                id SERIAL PRIMARY KEY,
                texto TEXT NOT NULL,
                creada TIMESTAMP DEFAULT NOW()
            )
            """
        )


@app.get("/")
def index():
    return jsonify(
        mensaje="App en contenedor 1 comunicada con la BD en contenedor 2",
        db_host=DB_CONFIG["host"],
    )


@app.get("/health")
def health():
    with get_conn(retries=1) as conn, conn.cursor() as cur:
        cur.execute("SELECT 1")
    return jsonify(estado="ok")


@app.post("/notas")
def crear_nota():
    texto = (request.get_json(silent=True) or {}).get("texto")
    if not texto:
        return jsonify(error="Falta el campo 'texto'"), 400
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO notas (texto) VALUES (%s) RETURNING id", (texto,))
        nota_id = cur.fetchone()[0]
    return jsonify(id=nota_id, texto=texto), 201


@app.get("/notas")
def listar_notas():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, texto, creada FROM notas ORDER BY id")
        filas = cur.fetchall()
    return jsonify([{"id": f[0], "texto": f[1], "creada": f[2].isoformat()} for f in filas])


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
