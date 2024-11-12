from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pusher
import mysql.connector

# Conexión a la base de datos
con = mysql.connector.connect(
    host="185.232.14.52",
    database="u760464709_tst_sep",
    user="u760464709_tst_sep_usr",
    password="dJ0CIAFF="
)

# Inicialización de Flask
app = Flask(__name__)
CORS(app)

# Ruta principal
@app.route("/")
def index():
    return render_template("app.html")

# Ruta para guardar tareas
@app.route("/guardar", methods=["POST"])
def alumnosGuardar():
    Titulo = request.form["titulo"]
    Descripcion = request.form["descripcion"]

    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor()
    sql = "INSERT INTO tst0_tareas (Titulo, Descripcion) VALUES (%s, %s)"
    val = (Titulo, Descripcion)
    cursor.execute(sql, val)
    con.commit()

    cursor.close()

    # Enviar evento de Pusher
    pusher_client = pusher.Pusher(
        app_id="1766039",
        key="91998889612f4dcea6e7",
        secret="b0b6a2508a63ef44c370",
        cluster="us2",
        ssl=True
    )
    pusher_client.trigger("canalRegistroTarea", "registroEventoTareas", {"titulo": Titulo, "descripcion": Descripcion})

    return jsonify({"Titulo": Titulo, "Descripcion": Descripcion})

# Ruta para buscar tareas
@app.route("/buscar")
def buscar():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor()
    cursor.execute("SELECT * FROM tst0_tareas ORDER BY Id_Tarea DESC")
    registros = cursor.fetchall()
    cursor.close()

    return jsonify(registros)

# Ruta para actualizar tareas
@app.route("/actualizar", methods=["POST"])
def actualizar():
    id_tarea = request.form["id_tarea"]
    titulo = request.form["titulo"]
    descripcion = request.form["descripcion"]

    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor()
    sql = "UPDATE tst0_tareas SET Titulo = %s, Descripcion = %s WHERE Id_Tarea = %s"
    val = (titulo, descripcion, id_tarea)
    cursor.execute(sql, val)
    con.commit()

    cursor.close()
    return jsonify({"mensaje": "Tarea actualizada"})

# Ruta para eliminar tareas
@app.route("/eliminar", methods=["POST"])
def eliminar():
    id_tarea = request.form["id_tarea"]

    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor()
    sql = "DELETE FROM tst0_tareas WHERE Id_Tarea = %s"
    cursor.execute(sql, (id_tarea,))
    con.commit()

    cursor.close()
    return jsonify({"mensaje": "Tarea eliminada"})

if __name__ == "__main__":
    app.run(debug=True)
