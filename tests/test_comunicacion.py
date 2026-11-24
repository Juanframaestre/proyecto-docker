"""Prueba de comunicación entre contenedores.

Se ejecuta dentro del contenedor "app":
    docker compose exec -T app python - < tests/test_comunicacion.py

Verifica que la app: 1) usa el nombre del servicio "db" como host, 2) guarda una nota
en PostgreSQL y 3) la lee de vuelta. Cualquier fallo termina con código 1 y hace
fallar el build de Jenkins.
"""
import json
import os
import sys
import time
import urllib.request

BASE = "http://localhost:5000"


def pedir(ruta, datos=None):
    peticion = urllib.request.Request(
        BASE + ruta,
        data=json.dumps(datos).encode() if datos is not None else None,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(peticion, timeout=5) as r:
        return r.status, json.loads(r.read())


def fallar(mensaje):
    print(f"FALLO: {mensaje}")
    sys.exit(1)


# 1) La app debe apuntar a la base de datos por el NOMBRE DEL SERVICIO
host = os.environ.get("DB_HOST")
if host != "db":
    fallar(f"DB_HOST debe ser 'db' (nombre del servicio), pero es '{host}'")
print(f"OK 1/3: la app usa el host '{host}' (nombre del servicio)")

# 2) Esperar a que la app responda y alcance la base de datos
listo = False
for _ in range(30):
    try:
        if pedir("/health")[1].get("estado") == "ok":
            listo = True
            break
    except Exception:
        pass
    time.sleep(2)
if not listo:
    fallar("la app no logró comunicarse con la base de datos (/health)")

# 3) Ida y vuelta: guardar y leer
texto = f"hola desde Jenkins {int(time.time())}"
estado, creada = pedir("/notas", {"texto": texto})
if estado != 201:
    fallar(f"POST /notas devolvió {estado}")
print(f"OK 2/3: nota guardada en la BD (id {creada['id']})")

_, notas = pedir("/notas")
if texto not in [n["texto"] for n in notas]:
    fallar("la nota guardada no aparece al leer /notas")
print(f"OK 3/3: nota leída de la BD ({len(notas)} nota(s) en total)")
print("PRUEBA DE COMUNICACION APROBADA")
