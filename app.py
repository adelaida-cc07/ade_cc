from flask import Flask, render_template, request
import pusher
import mysql.connector
import datetime
import pytz

# Configuración de la conexión a la base de datos
def get_db_connection():
    return mysql.connector.connect(
        host="185.232.14.52",
        database="u760464709_tst_sep",
        user="u760464709_tst_sep_usr",
        password="dJ0CIAFF="
    )

app = Flask(__name__)

# Configuración de Pusher
pusher_client = pusher.Pusher(
    app_id="1766039",
    key="91998889612f4dcea6e7",
    secret="b0b6a2508a63ef44c370",
    cluster="us2",
    ssl=True
)

@app.route("/")
def index():
    return render_template("app.html")

# Ejemplo de ruta GET usando templates para mostrar una vista
@app.route("/app")
def alumnos():
    return render_template("app.html")

# Ruta para buscar registros
@app.route("/buscar")
def buscar():
    con = get_db_connection()
    
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM tst0_reservas ORDER BY Id_Reserva DESC")
        registros = cursor.fetchall()
        return {"registros": registros}  # Retornando como JSON
        except Exception as e:
        return {"error": str(e)}
        finally:
        con.close()

# Ruta para registrar datos
@app.route("/registrar", methods=["GET"])
def registrar():
    args = request.args
    con = get_db_connection()

    try:
        cursor = con.cursor()

        sql = "INSERT INTO tst0_reservas (Nombre_Apellido, Telefono, Fecha) VALUES (%s, %s, %s)"
        val = (
            args.get("name"), 
            args.get("tel"), 
            datetime.datetime.now(pytz.timezone("America/Matamoros"))
        )
        cursor.execute(sql, val)
        
        con.commit()

        # Notificar con Pusher
        pusher_client.trigger("canalRegistrosHabitacion", "eventoRegistrosHabitacion", args)

        return args
        except Exception as e:
        return {"error": str(e)}
        finally:
        con.close()

if __name__ == "__main__":
    app.run(debug=True)
