from flask import Flask, render_template, request, jsonify
import pusher
import mysql.connector
from mysql.connector import pooling
import datetime
import pytz
import os

# Configuración de la conexión a la base de datos (usando un pool de conexiones)
dbconfig = {
    "host": os.getenv("DB_HOST", "185.232.14.52"),
    "database": os.getenv("DB_NAME", "u760464709_tst_sep"),
    "user": os.getenv("DB_USER", "u760464709_tst_sep_usr"),
    "password": os.getenv("DB_PASSWORD", "dJ0CIAFF=")
}
connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **dbconfig)

app = Flask(__name__)

# Configuración de Pusher
pusher_client = pusher.Pusher(
    app_id=os.getenv("PUSHER_APP_ID", "1766039"),
    key=os.getenv("PUSHER_KEY", "91998889612f4dcea6e7"),
    secret=os.getenv("PUSHER_SECRET", "b0b6a2508a63ef44c370"),
    cluster=os.getenv("PUSHER_CLUSTER", "us2"),
    ssl=True
)

@app.route("/")
def index():
    return render_template("app.html")

@app.route("/app")
def alumnos():
    return render_template("app.html")

# Ruta POST para guardar la información
@app.route("/app/guardar", methods=["POST"])
def alumnos_guardar():
    matricula = request.form.get("txtMatriculaFA")
    nombre_apellido = request.form.get("txtNombreApellidoFA")

    if not matricula or not nombre_apellido:
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    return f"Matrícula {matricula} Nombre y Apellido {nombre_apellido}"

# Ruta GET para buscar registros
@app.route("/buscar")
def buscar():
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tst0_reservas ORDER BY Id_Reserva DESC")
        registros = cursor.fetchall()
        return jsonify(registros)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        connection.close()

# Ruta GET para registrar datos
@app.route("/registrar", methods=["GET"])
def registrar():
    name = request.args.get("name")
    tel = request.args.get("tel")

    if not name or not tel:
        return jsonify({"error": "Nombre y teléfono son requeridos"}), 400

    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        sql = "INSERT INTO tst0_reservas (Nombre_Apellido, Telefono, Fecha) VALUES (%s, %s, %s)"
        val = (name, tel, datetime.datetime.now(pytz.timezone("America/Matamoros")))
        cursor.execute(sql, val)
        connection.commit()

        # Disparar evento Pusher
        pusher_client.trigger("canalRegistrosHabitacion", "eventoRegistrosHabitacion", {"name": name, "tel": tel})

        return jsonify({"name": name, "tel": tel}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    app.run(debug=True)
