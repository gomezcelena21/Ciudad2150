from flask import Flask, render_template, request, redirect, session, abort
import json
import os
import uuid
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_key")

ARCHIVO = "ciudadanos_2150.json"

# Usuario
USUARIO = "admin"
PASSWORD_HASH = generate_password_hash("1234")  # FIXED

# ------------------------
# UTILIDADES
# ------------------------

def cargar():
    try:
        with open(ARCHIVO, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def guardar(data):
    with open(ARCHIVO, "w") as f:
        json.dump(data, f, indent=4)

def generar_id():
    return f"C-{uuid.uuid4().hex[:8]}"

def login_requerido():
    return session.get("login", False)

# ------------------------
# RUTAS
# ------------------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("user", "")
        password = request.form.get("password", "")

        if user == USUARIO and check_password_hash(PASSWORD_HASH, password):
            session["login"] = True
            return redirect("/panel")

        return render_template("login.html", error="Credenciales inválidas")

    return render_template("login.html")

@app.route("/panel")
def panel():
    if not login_requerido():
        return redirect("/")

    return render_template("index.html", ciudadanos=cargar())

@app.route("/agregar", methods=["POST"])
def agregar():
    if not login_requerido():
        return redirect("/")

    data = cargar()
    nombre = request.form.get("nombre", "").strip()
    edad = request.form.get("edad", "").strip()

    if not nombre or not edad.isdigit():
        return redirect("/panel")

    edad = int(edad)

    if edad < 0 or edad > 120:
        return redirect("/panel")

    data.append({
        "id": generar_id(),
        "nombre": nombre,
        "edad": edad
    })

    guardar(data)
    return redirect("/panel")

@app.route("/buscar", methods=["POST"])
def buscar():
    if not login_requerido():
        return redirect("/")

    data = cargar()
    query = request.form.get("nombre", "").lower()

    resultados = [c for c in data if query in c["nombre"].lower()]

    return render_template("index.html", ciudadanos=resultados)

@app.route("/eliminar/<id>", methods=["POST"])
def eliminar(id):
    if not login_requerido():
        return redirect("/")

    data = cargar()
    nuevo = [c for c in data if c["id"] != id]

    if len(nuevo) == len(data):
        abort(404)

    guardar(nuevo)
    return redirect("/panel")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ------------------------

if __name__ == "__main__":
    app.run(debug=True)