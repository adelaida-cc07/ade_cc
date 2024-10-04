@app.route("/registrar", methods=["GET"])
def registrar():
    args = request.args

    nombre_apellido = args.get("name")
    telefono = args.get("tel")

    if not nombre_apellido or not telefono:
        return jsonify({"error": "Nombre y teléfono son requeridos"}), 400

    # Imprimir los valores para depurar
    print(f"Nombre: {nombre_apellido}, Teléfono: {telefono}")

    try:
        if not con.is_connected():
            con.reconnect()

        cursor = con.cursor()
        sql = "INSERT INTO tst0_reservas (Nombre_Apellido, Telefono, Fecha) VALUES (%s, %s, %s)"
        val = (nombre_apellido, telefono, datetime.datetime.now(pytz.timezone("America/Matamoros")))
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
