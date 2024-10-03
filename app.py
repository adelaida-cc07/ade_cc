from flask 
import Flask, render_template, request, jsonify
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
    app_id=os.getenv("PUSHER_APP_ID", "1714541"),
    key=os.getenv("PUSHER_KEY", "2df86616075904231311"),
    secret=os.getenv("PUSHER_SECRET", "2f91d936fd43d8e85a1a"),
    cluster=os.getenv("PUSHER_CLUSTER", "us2"),
    ssl=True
)

@app.route("/")
def index():
    return render_template("app.html")

# Ejemplo de ruta GET usando templates para mostrar una vista
@app.route("/alumnos")
def alumnos():
    return render_template("alumnos.html")

# Ejemplo de ruta POST para guardar la información
@app.route("/alumnos/guardar", methods=["POST"])
def alumnos_guardar():
    matricula = request.form.get("txtMatriculaFA")
    nombre_apellido = request.form.get("txtNombreApellidoFA")

    if not matricula or not nombre_apellido:
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    return f"Matrícula {matricula} Nombre y Apellido {nombre_apellido}"

# Código usado en las prácticas para obtener registros
@app.route("/buscar")
def buscar():
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sensor_log ORDER BY Id_Log DESC")
        registros = cursor.fetchall()
        return jsonify(registros)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        connection.close()

# Ruta GET para registrar datos de temperatura y humedad
@app.route("/registrar", methods=["GET"])
def registrar():
    temperatura = request.args.get("temperatura")
    humedad = request.args.get("humedad")

    if not temperatura or not humedad:
        return jsonify({"error": "Temperatura y humedad son requeridos"}), 400

    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        sql = "INSERT INTO sensor_log (Temperatura, Humedad, Fecha_Hora) VALUES (%s, %s, %s)"
        val = (temperatura, humedad, datetime.datetime.now(pytz.timezone("America/Matamoros")))
        cursor.execute(sql, val)
        connection.commit()

        # Disparar evento Pusher
        pusher_client.trigger("canalRegistrosTemperaturaHumedad", "registroTemperaturaHumedad", {"temperatura": temperatura, "humedad": humedad})

        return jsonify({"temperatura": temperatura, "humedad": humedad}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    app.run(debug=True)
