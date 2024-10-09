from flask import Flask, render_template, request
import pusher
import mysql.connector
import pytz

con = mysql.connector.connect(
  host="185.232.14.52",
  database="u760464709_tst_sep",
  user="u760464709_tst_sep_usr",
  password="dJ0CIAFF="
)

app = Flask(__name__)

# Ruta principal que sirve una página de inicio
@app.route("/")
def index():
    return render_template("app.html")

# Ruta que sirve la página de alumnos
@app.route("/app")
def alumnos():
    return render_template("app.html")

# Ruta para guardar los datos de los alumnos enviados desde el formulario
@app.route("/app/guardar", methods=["POST"])
def alumnosGuardar():
    Titulo = request.form["titulo"]
    Descripcion = request.form["descripcion"]
  

    # Devolviendo una respuesta con los datos recibidos
    return f"Titulo: {titulo}, Descripcion: {descripcion}"
#buscar
@app.route("/buscar")
def buscar():
    if not con.is_connected():
    con.reconnect()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM tst0_tareas ORDER BY Id_Tarea DESC")

    registros = cursor.fetchall()
    con.close()

    return registros

@app.route("/registrar", methods=["GET"])
def registrar():
    args = request.args  # Obtener los parámetros desde la URL

    if not con.is_connected():
    con.reconnect()

    cursor = con.cursor()

    # SQL para insertar los datos en la tabla 'tst0_tareas'
    sql = "INSERT INTO tst0_tareas (Titulo, Descripcion) VALUES (%s, %s, %s)"
    
    # Valores obtenidos de los parámetros en la URL (por ejemplo: ?name=Juan&comment=Buen+trabajo&rating=5)
    val = (args.get("titulo"), args.get("descrpicion"))
    
    cursor.execute(sql, val)
    con.commit()
    
    cursor.close()
    con.close()


    # Conexión con Pusher utilizando las credenciales correctas
    pusher_client = pusher.Pusher(
    app_id = "1766039"
    key = "91998889612f4dcea6e7"
    secret = "b0b6a2508a63ef44c370"
    cluster = "us2"
    ssl=True
    )

    # Disparando un evento a través de Pusher
    pusher_client.trigger("canalRegistroTarea", "registroEventoTareas", args)
  #    pusher_client.trigger("my-channel", "my-event", args)

    
    return args
