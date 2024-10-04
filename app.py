from flask import Flask, render_template, request, jsonify
import pusher
import mysql.connector
import datetime
import pytz

# Conexión a la base de datos
con = mysql.connector.connect(
    host="185.232.14.52",
    database="u760464709_tst_sep",
    user="u760464709_tst_sep_usr",
    password="dJ0CIAFF="
)

app = Flask(__main__)

# Ruta de inicio
@app.route("/")
def index():
    con.close()
    return render_template("app.html")

# Ruta para mostrar la vista de 'alumnos'
@app.route("/app")
def alumnos():
    con.close()
    return render_template("app.html")

# Ruta POST para guardar información de alumnos (ejemplo)
@app.route("/app/guardar", methods=["POST"])
def alumnos_guardar():
    con.close()
    matricula = request.form.get("txtMatriculaFA")
    nombreapellido = request.form.get("txtNombreApellidoFA")
    return f"Matrícula {matricula} Nombre y Apellido {nombreapellido}"

# Ruta para buscar registros de la tabla `tst0_reservas`
@app.route("/buscar")
def buscar():
    try:
        if not con.is_connected():
            con.reconnect()

        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tst0_reservas ORDER BY Id_Reserva DESC")
        registros = cursor.fetchall()
        return jsonify(registros)
    finally:
        cursor.close()
        con.close()

# Ruta para registrar datos en la tabla `tst0_reservas`
@app.route("/registrar", methods=["GET"])
def registrar():
    args = request.args

    nombre_apellido = args.get("name")
    telefono = args.get("tel")

    if not nombre_apellido or not telefono:
        return jsonify({"error": "Nombre y teléfono son requeridos"}), 400

    try:
        if not con.is_connected():
            con.reconnect()

        cursor = con.cursor()
        sql = "INSERT INTO tst0_reservas (Nombre_Apellido, Telefono, Fecha) VALUES (%s, %s, %s)"
        val = (nombre_apellido, telefono, fecha.datetime.now(pytz.timezone("America/Matamoros")))
        cursor.execute(sql, val)
        con.commit()

        # Trigger para Pusher
        pusher_client = pusher.Pusher(
            app_id="1766039",
            key="91998889612f4dcea6e7",
            secret="b0b6a2508a63ef44c370",
            cluster="us2",
            ssl=True
        )
        pusher_client.trigger("canalRegistrosHabitacion", "eventoRegistrosHabitacion", {"name": nombre_apellido, "tel": telefono})

        return jsonify({"name": nombre_apellido, "tel": telefono}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        con.close()

if __name__ == "__main__":
    app.run(debug=True)
