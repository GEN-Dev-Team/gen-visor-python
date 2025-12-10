# server.py
import os
import requests
from flask import Flask, jsonify, abort
from flask_cors import CORS  # pip install flask-cors

# Lee credenciales desde variables de entorno
APS_CLIENT_ID = os.environ.get("APS_CLIENT_ID")
APS_CLIENT_SECRET = os.environ.get("APS_CLIENT_SECRET")
# URN del modelo (sin el prefijo "urn:")
APS_MODEL_URN = os.environ.get("APS_MODEL_URN")

if not APS_CLIENT_ID or not APS_CLIENT_SECRET:
    raise RuntimeError(
        "Debes definir las variables de entorno APS_CLIENT_ID y APS_CLIENT_SECRET "
        "antes de ejecutar este servidor."
    )

if not APS_MODEL_URN:
    raise RuntimeError(
        "Debes definir la variable de entorno APS_MODEL_URN "
        "con la URN de tu modelo (sin el prefijo 'urn:')."
    )

app = Flask(__name__)

# CORS para todas las rutas /api/*
# En producción conviene cambiar origins="*" por tu dominio real.
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route("/api/aps/token")
def get_aps_token():
    """
    Endpoint que devuelve un token 2-legged para el Viewer.
    """
    url = "https://developer.api.autodesk.com/authentication/v2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": APS_CLIENT_ID,
        "client_secret": APS_CLIENT_SECRET,
        "scope": "data:read"
    }

    resp = requests.post(url, data=data)
    if resp.status_code != 200:
        print("Error al pedir token APS:", resp.status_code, resp.text)
        abort(500, description="No se pudo obtener token de APS")

    payload = resp.json()
    return jsonify(
        access_token=payload["access_token"],
        expires_in=payload["expires_in"]
    )

@app.route("/api/aps/model-urn")
def get_model_urn():
    """
    Devuelve la URN del modelo sin el prefijo 'urn:'.
    El frontend la pedirá vía fetch, así no queda hardcodeada en el HTML/JS.
    """
    if not APS_MODEL_URN:
        abort(500, description="APS_MODEL_URN no está configurada")
    return jsonify(urn=APS_MODEL_URN)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
