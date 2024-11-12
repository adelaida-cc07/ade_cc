# Ruta para actualizar una tarea existente
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

# Ruta para eliminar una tarea
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
