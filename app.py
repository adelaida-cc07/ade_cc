 from flask import Flask

from flask import render_template
from flask import request

import pusher

import mysql.connector
import datetime
import pytz

con = mysql.connector.connect(
    host="185.232.14.52",
    database="u760464709_tst_sep",
    user="u760464709_tst_sep_usr",
    password="dJ0CIAFF="
)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("app.html")

# Ejemplo de ruta GET usando templates para mostrar una vista
@app.route("/app")
def alumnos():
    con.close()

    return render_template("app.html")

# Ejemplo de ruta POST para ver cómo se envia la informacion
@app.route("/app/guardar", methods=["POST"])
def alumnosGuardar():
    con.close()
    matricula      = request.form["txtMatriculaFA"]
    nombreapellido = request.form["txtNombreApellidoFA"]

    return f"Matrícula {matricula} Nombre y Apellido {nombreapellido}"

# Código usado en las prácticas
@app.route("/buscar")
def buscar():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor()
    cursor.execute("SELECT * FROM tst0_reservas ORDER BY Id_Reserva DESC")
    registros = cursor.fetchall()

    con.close()

    return registros

@app.route("/registrar", methods=["GET"])
def registrar():
    args = request.args

    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor()

    sql = "INSERT INTO tst0_reservas (Nombre_Apellido, Telefono, Fecha) VALUES (%s, %s, %s)"
 
    val = (args.get("name"), args.get("tel"), datetime.datetime.now(pytz.timezone("America/Matamoros")))
 
    cursor.execute(sql, val)
    con.commit()
 
    cursor.close()
    con.close()

    pusher_client = pusher.Pusher(
        app_id = "1766039"
        key = "91998889612f4dcea6e7"
        secret = "b0b6a2508a63ef44c370"
        cluster = "us2",
        ssl=True
    )

    pusher_client.trigger("canalRegistrosHabitacion", "eventoRegistrosHabitacion", args)

    return args
