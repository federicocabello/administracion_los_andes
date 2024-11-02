from flask import Flask, render_template, request, redirect, url_for, Response, send_file, json, jsonify
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_required, logout_user, login_user, current_user, UserMixin
from config import config
from io import BytesIO
import datetime as dt
import base64
import io
import os
import time
import smtplib, ssl

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Image as RLImage, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.fonts import addMapping
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

from reportlab.platypus import Frame, PageTemplate, BaseDocTemplate

from PIL import Image

from collections import defaultdict

app = Flask(__name__)

db = MySQL(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    cursor = db.connection.cursor()
    cursor.execute(f"insert into movimientos (mov, date_mov, agente) VALUES ('Cerró sesión.', now(), '{current_user.fullname}')")
    db.connection.commit()
    cursor.close()
    logout_user()
    return redirect(url_for('login'))

@app.route('/get_motivos', methods=['GET'])
def get_motivos():
    cursor = db.connection.cursor()
    cursor.execute("SELECT * FROM motivos ORDER BY razon ASC;")
    motivos = cursor.fetchall()
    result = [{'razon': motivo[0]} for motivo in motivos]
    return jsonify(result)

@app.route('/seguimiento/<telefono>/<nombre>')
@login_required
def seguimiento(telefono, nombre):
    cursor = db.connection.cursor()
    cursor.execute(f'select empresa, nombre, telefono, email, motivo, cotizacion, cotizaciontotal, fecha, tareas.tarea, fecha_tarea, hora_tarea, registros.tarea, nota_rechazo, agente, direccion, tareas.color, DATE_FORMAT(fecha_tarea, "%d %M %Y") from registros join tareas on tareas.idtarea = registros.tarea where telefono = "{telefono}" and estado = "registro" and nombre = "{nombre}" order by fecha desc;')
    registros = cursor.fetchall()
    cursor.execute(f'SELECT mov, DATE_FORMAT(date_mov, "%d %M %Y • %T"), agente, nombre, telefono, datonuevo FROM movimientos WHERE nombre = "{nombre}" or telefono = "{telefono}" ORDER BY date_mov DESC;')
    movimientos = cursor.fetchall()
    #cursor.execute(f"SELECT pregunta, respuesta, fecha from registros where telefono = '{telefono}' and estado = 'pregunta';")
    #preguntas = cursor.fetchall()
    preguntas = None
    cursor.execute("SELECT idtarea, tarea from tareas")
    tareas = cursor.fetchall()
    cursor.execute("SELECT empresa from clientes;")
    empresas = cursor.fetchall()
    cursor.execute("SELECT fullname from auth;")
    agentes = cursor.fetchall()
    return render_template('seguimiento.html', registros=registros, movimientos=movimientos, preguntas=preguntas, tareas=tareas, empresas=empresas, agentes=agentes)

@app.route('/usuarios/nuevousuario', methods=['GET', 'POST'])
@login_required
def altaUsuario():
    if request.method == 'POST':
        usuario = request.form['usuario'].lower().strip().replace(' ','')
        password = request.form['contrasena']
        fullname = request.form['nombre'].upper()
        rol = request.form['rol']
        cursor = db.connection.cursor()
        sql = f"INSERT INTO auth VALUES ('{usuario}', '{password}', '{fullname}', '{rol}')"
        cursor.execute(sql)
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} agregó al usuario {usuario.upper()} | {fullname}', now())")
        db.connection.commit()
        cursor.close()
        return redirect(url_for('dashboard'))
    return render_template('altauser.html')

@app.route('/usuarios/editarusuario', methods=['GET', 'POST'])
@login_required
def editarUsuario():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['contrasena']
        fullname = request.form['nombre'].upper()
        rol = request.form['rol']
        cursor = db.connection.cursor()
        cursor.execute(f"select fullname from auth where user = '{usuario}'")
        nombreviejo = cursor.fetchall()
        cursor.execute(f"update registros set agente = '{fullname}' where agente = '{nombreviejo[0][0]}'")
        cursor.execute(f"update pagos set agente = '{fullname}' where agente = '{nombreviejo[0][0]}'")
        cursor.execute(f"update movimientos set agente = '{fullname}' where agente = '{nombreviejo[0][0]}'")
        sql = f"DELETE FROM auth WHERE user = '{usuario}'"
        cursor.execute(sql)
        db.connection.commit()
        sql = f"INSERT INTO auth VALUES ('{usuario}', '{password}', '{fullname}', '{rol}')"
        cursor.execute(sql)
        cursor.execute(f"insert into movimientos (mov, date_mov, agente, datonuevo) values ('Modificó un usuario.', now(), '{current_user.fullname}', '{usuario.upper()}')")
        db.connection.commit()
        cursor.close()
    return redirect(url_for('dashboard'))

@app.route('/usuarios/gestionusuario', methods=['GET', 'POST'])
@login_required
def gestionUsuario():
    if request.method == 'POST':
        usuario = request.form['eliminar']
        cursor = db.connection.cursor()
        sql = f"SELECT * FROM auth where user='{usuario}'"
        cursor.execute(sql)
        tablas =  cursor.fetchall()
        return render_template('moduser.html', tablas=tablas)
    return redirect(url_for('usuarios'))

@app.route('/usuarios/eliminarusuario', methods=['GET', 'POST'])
@login_required
def eliminarUsuario():
    if request.method == 'POST':
        eliminar = request.form['eliminar']
        cursor = db.connection.cursor()
        sql = f"DELETE FROM auth where user = '{eliminar}'"
        cursor.execute(sql)
        cursor.execute(f"INSERT INTO movimientos (mov, date_mov, agente, datonuevo) VALUES ('Eliminó un usuario.', now(), '{current_user.fullname}', '{eliminar.upper()}');")
        db.connection.commit()
        cursor.close()
    return redirect(url_for('usuarios'))

@app.route('/empresas/logo/<empresa>', methods=['GET'])
def get_image(empresa):
    cursor = db.connection.cursor()
    cursor.execute("SELECT logo FROM clientes WHERE empresa = %s;", (empresa,))
    row = cursor.fetchone()
    cursor.close()

    if row and row[0]:
        image_data = row[0]
        return send_file(io.BytesIO(image_data), mimetype='image/png')
    else:
        return 'No image found', 404

@app.route('/empresas/imagenes/<empresa>/<articulo>/<precio>', methods=['GET'])
def get_image_art(empresa, articulo, precio):
    cursor = db.connection.cursor()
    cursor.execute(f"SELECT imagen FROM clientes_articulos WHERE empresa = '{empresa}' and precio = {precio} and articulo = '{articulo}';")
    imagen = cursor.fetchone()[0]
    cursor.close()
    if imagen:
        return send_file(io.BytesIO(imagen), mimetype='image/png')
    else:
        return 'No Image', 404

@app.route('/empresas/<empresa>', methods=['GET', 'POST'])
@login_required
def moduloEmpresa(empresa):
    cursor = db.connection.cursor()
    cursor.execute(f"SELECT * FROM clientes WHERE empresa = '{empresa}';")
    new = cursor.fetchone()
    cursor.execute(f"SELECT articulo, precio, descripcion, imagen, vendido FROM clientes_articulos WHERE empresa = '{empresa}' ORDER BY LENGTH(descripcion) ASC;")
    articulos = cursor.fetchall()
    cursor.execute("SELECT idtarea, tarea FROM tareas;")
    tareas = cursor.fetchall()
    cursor.close()
    return render_template('empresa.html', new=new, articulos=articulos, tareas=tareas)

@app.route('/empresas/nueva', methods=['GET', 'POST'])
@login_required
def nuevaEmpresa():
    nuevo = request.form.get('nuevo').strip().upper()
    cursor = db.connection.cursor()
    cursor.execute(f"INSERT INTO clientes (fecha_creacion, empresa, visible) VALUES (current_date(), '{nuevo}', 1);")
    cursor.execute(f"INSERT INTO movimientos (mov, date_mov, agente, datonuevo) VALUES ('Agregó una nueva empresa.',  now(), '{current_user.fullname}', '{nuevo}')")
    db.connection.commit()
    cursor.close()
    return jsonify({'status': 'success', 'redireccion': nuevo})

@app.route('/empresas/modificar', methods=['GET', 'POST'])
@login_required
def modificarEmpresa():
    accion = request.form.get('accion')
    empresa = request.form.get('empresa')
    cursor = db.connection.cursor()
    if accion == 'editar':
        datonuevo = request.form.get('datonuevo').upper().strip()
        if datonuevo:
            cursor.execute(f"UPDATE clientes SET empresa = '{datonuevo}' WHERE empresa = '{empresa}';")
            cursor.execute(f"UPDATE clientes_articulos SET empresa = '{datonuevo}' WHERE empresa = '{empresa}';")
            cursor.execute(f"UPDATE hojas SET empresa = '{datonuevo}' WHERE empresa = '{empresa}';")
            cursor.execute(f"UPDATE pagos SET empresa = '{datonuevo}' WHERE empresa = '{empresa}';")
            cursor.execute(f"UPDATE registros SET empresa = '{datonuevo}' WHERE empresa = '{empresa}';")
            cursor.execute(f"INSERT INTO movimientos (mov, date_mov, agente, datonuevo) VALUES ('Modificó la empresa {empresa}.',  now(), '{current_user.fullname}', '{datonuevo}')")
    elif accion == 'visible':
        datonuevo = request.form.get('datonuevo')
        cursor.execute(f"UPDATE clientes SET visible = {datonuevo} WHERE empresa = '{empresa}';")
        cursor.execute(f"INSERT INTO movimientos (mov, date_mov, agente, datonuevo) VALUES ('Cambió la visibilidad de una empresa.',  now(), '{current_user.fullname}', '{empresa}')")
    else:
        cursor.execute(f"DELETE FROM clientes WHERE empresa = '{empresa}';")
        cursor.execute(f"DELETE FROM clientes_articulos WHERE empresa = '{empresa}';")
        cursor.execute(f"INSERT INTO movimientos (mov, date_mov, agente, datonuevo) VALUES ('Eliminó una empresa.',  now(), '{current_user.fullname}', '{empresa}')")
    db.connection.commit()
    cursor.close()
    return jsonify({'status': 'success'})

@app.route('/empresas/articulos/vendido', methods=['POST'])
def empresArticuloVendido():
    empresa = request.form.get('empresa')
    articulo = request.form.get('articulo')
    vendido = request.form.get('vendido')
    cursor = db.connection.cursor()
    cursor.execute(f'UPDATE clientes_articulos SET vendido = {vendido} WHERE empresa = "{empresa}" and articulo = "{articulo}";')
    if vendido == '1':
        cursor.execute(f"INSERT INTO movimientos (mov, date_mov, agente, datonuevo) VALUES ('Marcó como VENDIDO a un artículo de la empresa {empresa}.',  now(), '{current_user.fullname}', '{articulo}')")
    else:
        cursor.execute(f"INSERT INTO movimientos (mov, date_mov, agente, datonuevo) VALUES ('Desmarcó como VENDIDO a un artículo de la empresa {empresa}.',  now(), '{current_user.fullname}', '{articulo}')")
    db.connection.commit()
    cursor.close()
    return jsonify({'status': 'success'})

@app.route('/empresas/actualizar', methods=['POST'])
def actualizar_empresa():
    empresa = request.form.get('empresa')
    datos = request.form.get('datos')
    que_vende = request.form.get('que_vende')
    clasificacion = request.form.get('clasificacion').strip().upper()
    introduccion = request.form.get('introduccion')
    tener_en_cuenta = request.form.get('tener_en_cuenta')
    estructura = request.form.get('estructura')
    c_no_interesado = request.form.get('c_no_interesado')
    c_potencial = request.form.get('c_potencial')
    c_interesado = request.form.get('c_interesado')
    speech_entrada = request.form.get('speech_entrada')
    speech_salida = request.form.get('speech_salida')
    reglas = request.form.get('reglas')
    formas_pago = request.form.get('formas_pago')
    preguntas_frecuentes = request.form.get('preguntas_frecuentes')
    terminologias = request.form.get('terminologias')
    archivo = request.files.get('logo')
    
    cursor = db.connection.cursor()
    if archivo:
        logo_data = archivo.read()
        cursor.execute("UPDATE clientes SET datos=%s, que_vende=%s, clasificacion=%s, introduccion=%s, tener_en_cuenta=%s, estructura=%s, c_no_interesado=%s, c_potencial=%s, c_interesado=%s, speech_entrada=%s, speech_salida=%s, reglas=%s, formas_pago=%s, preguntas_frecuentes=%s, terminologias=%s, logo=%s WHERE empresa=%s", (datos, que_vende, clasificacion, introduccion, tener_en_cuenta, estructura, c_no_interesado, c_potencial, c_interesado, speech_entrada, speech_salida, reglas, formas_pago, preguntas_frecuentes, terminologias, logo_data, empresa))
    else:
        cursor.execute("UPDATE clientes SET datos=%s, que_vende=%s, clasificacion=%s, introduccion=%s, tener_en_cuenta=%s, estructura=%s, c_no_interesado=%s, c_potencial=%s, c_interesado=%s, speech_entrada=%s, speech_salida=%s, reglas=%s, formas_pago=%s, preguntas_frecuentes=%s, terminologias=%s WHERE empresa=%s", (datos, que_vende, clasificacion, introduccion, tener_en_cuenta, estructura, c_no_interesado, c_potencial, c_interesado, speech_entrada, speech_salida, reglas, formas_pago, preguntas_frecuentes, terminologias, empresa))
        
    articulos = json.loads(request.form.get('articulos'))
    if articulos:
        for index, art in enumerate(articulos):
            archivo_key = f'archivo_{index}'
            articulo_nombre = art[0].strip().upper()
            precio = art[1].strip()
            descripcion = art[2]
            imagen_existente = art[3].strip()
            partes = imagen_existente.split('æ')
            if partes[0].strip() == 'delete':
                cursor.execute(f"DELETE FROM clientes_articulos WHERE empresa = '{empresa}' AND articulo = '{partes[1].strip()}' AND precio = {partes[2].strip()};")
            elif partes[0].strip() == 'update':
                if archivo_key in request.files:
                    imagen = request.files[archivo_key].read()
                    if imagen:
                        cursor.execute("UPDATE clientes_articulos SET articulo = %s, precio = %s, descripcion = %s, imagen = %s WHERE empresa = %s AND articulo = %s AND precio = %s", (articulo_nombre, precio, descripcion, imagen, empresa, partes[1].strip(), partes[2].strip()))
                else:
                    cursor.execute(f"UPDATE clientes_articulos SET articulo = '{articulo_nombre}', precio = {precio}, descripcion = '{descripcion}' WHERE empresa = '{empresa}' AND articulo = '{partes[1].strip()}' AND precio = {partes[2].strip()};")
            elif partes[0].strip() == 'insert':
                if archivo_key in request.files:
                    imagen = request.files[archivo_key].read()
                    if imagen:
                        cursor.execute("INSERT INTO clientes_articulos VALUES (%s, %s, %s, %s, %s, %s)", (empresa, articulo_nombre, precio, descripcion, imagen, 0))
                else:
                    cursor.execute(f"INSERT INTO clientes_articulos VALUES ('{empresa}', '{articulo_nombre}', {precio}, '{descripcion}', 0);")
    db.connection.commit()
    cursor.close()
    return jsonify({'status': 'success'})

@app.route('/descargar/contrato', methods=['GET', 'POST'])
@login_required
def descargarContrato():
    empresa = request.form['bajar_contrato']
    cursor = db.connection.cursor()
    cursor.execute(f"SELECT contrato from clientes where empresa = '{empresa}'")
    archivo = cursor.fetchone()
    archivo_new = archivo[0]
    contenido_pdf = base64.b64decode(archivo_new)
    
    pdf_buffer = io.BytesIO(contenido_pdf)
    pdf_buffer.seek(0)
    
    nombre = f"Contrato de {empresa.upper().strip()}.pdf"
    
    # CORRECTO --> with open(nombre, 'wb') as f:
        #CORRECTO --> f.write(contenido_pdf)
    
    #return send_from_directory('.', 'archivo.pdf', as_attachment=True)
    
    # CORRECTO --> return send_file(os.path.abspath(nombre), as_attachment=True)
    
    #return send_file(pdf_buffer, as_attachment=True, attachment_filename = 'archivo.pdf', mimetype='application/pdf')
    
    ruta_archivo = os.path.join("contratos", nombre)
    
    with open(ruta_archivo, 'wb') as f:
        f.write(contenido_pdf)
    
    return send_file(os.path.abspath(ruta_archivo), as_attachment=True)

class User(UserMixin):
            def __init__ (self, username, password, fullname, rol):
                self.id = username
                self.password = password
                self.fullname = fullname
                self.rol = rol
        
@login_manager.user_loader
def load_user(user_id):
    cur = db.connection.cursor()
    cur.execute("SELECT * FROM auth WHERE user = %s", (user_id,))
    user_data = cur.fetchone()
    cur.close()
    if user_data:
        return User(user_data[0], user_data[1], user_data[2], user_data[3])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'login_usuario' in request.form and 'login_contra' in request.form:
        usuario = request.form['login_usuario'].lower()
        contra = request.form['login_contra']
        
        cur = db.connection.cursor()
        cur.execute("USE administracion_los_andes")
        cur.execute("SELECT * FROM auth WHERE user = %s", (usuario,))
        user_data = cur.fetchone()

        if user_data and user_data[1] == contra:
            user = User(user_data[0], user_data[1], user_data[2], user_data[3])
            login_user(user)
            cur.execute(f"insert into movimientos (mov, date_mov, agente) VALUES ('Inició sesión.', now(), '{current_user.fullname}')")
            db.connection.commit()
            cur.close()
            return redirect(url_for('dashboard'))
    return render_template('auth/login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    cursor = db.connection.cursor()
    cursor.execute("SELECT empresa, clasificacion, visible from clientes order by empresa asc;")
    empresas = cursor.fetchall()
    #cursor.execute(f"SELECT DATE_FORMAT(fecha, '%d %M'), empresa, nombre, telefono, motivo, tareas.tarea, email, direccion, registros.tarea, fecha, hora_tarea, cast(hora_tarea as unsigned) AS hora FROM registros JOIN tareas ON tareas.idtarea = registros.tarea WHERE fecha_tarea = current_date AND pregunta is null AND estado = 'registro' AND agente = '{current_user.fullname}' AND registros.tarea in (select tarea from registros where tarea = 0 or tarea = 3 or tarea = 4 or tarea = 5 or tarea = 6 or tarea = 8 or tarea = 9 or tarea = 10 or tarea = 11 or tarea = 12 or tarea = 13 or tarea = 14 or tarea = 15 or tarea = 16 or tarea = 17 or tarea = 18 or tarea = 20 or tarea = 25 or tarea = 26) ORDER BY hora;")
    cursor.execute(f"""
                   SELECT 
    DATE_FORMAT(idtarea, '%d %M') AS fecha_formateada, 
    NULL AS empresa, 
    NULL AS nombre, 
    NULL AS telefono, 
    titulo AS motivo, 
    descripcion AS tarea, 
    NULL AS email, 
    NULL AS direccion, 
    NULL AS tarea_id, 
    idtarea AS fecha, 
    hora_rec AS hora, 
    CAST(hora_rec AS unsigned) AS hora_entero, 
    prioridades.prioridad, 
    tipo,
    'RECORDATORIO' AS origen,
    preaviso AS preaviso,
    CONCAT(fecha_rec, ' ', hora_rec) AS fechahoy
FROM 
    recordatorios 
JOIN 
    prioridades ON prioridades.idprioridades = recordatorios.prioridad 
WHERE 
    fecha_rec = current_date 
    AND realizada = 0 
    AND agente = '{current_user.fullname}'

UNION ALL

SELECT 
    DATE_FORMAT(fecha, '%d %M'), 
    empresa, 
    nombre, 
    telefono, 
    motivo, 
    tareas.tarea, 
    email, 
    direccion, 
    registros.tarea AS tarea_id, 
    fecha, 
    hora_tarea AS hora, 
    CAST(hora_tarea AS unsigned) AS hora_entero, 
    NULL AS prioridad, 
    NULL AS tipo,
    'REGISTRO' as origen,
    NULL as preaviso,
    NULL as fechahoy
FROM 
    registros 
JOIN 
    tareas ON tareas.idtarea = registros.tarea 
WHERE 
    fecha_tarea = current_date 
    AND pregunta IS NULL 
    AND estado = 'registro' 
    AND agente = '{current_user.fullname}' 
    AND registros.tarea IN (
        0, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 25, 26
    )
ORDER BY 
    hora_entero ASC,
    prioridad DESC;
                   """)
    pendiente = cursor.fetchall()
    cursor.execute("SELECT fullname from auth order by fullname")
    agentes = cursor.fetchall()
    cursor.execute("SELECT * from tareas")
    tareas = cursor.fetchall()
    cursor.execute("select CASE WHEN fecha_1 = current_date() THEN 'CUOTA 1' WHEN fecha_2 = current_date() THEN 'CUOTA 2' WHEN fecha_3 = current_date() THEN 'CUOTA 3' WHEN fecha_4 = current_date() THEN 'CUOTA 4' END AS cuota, CASE WHEN fecha_1 = current_date() THEN acuerdo_1 WHEN fecha_2 = current_date() THEN acuerdo_2 WHEN fecha_3 = current_date() THEN acuerdo_3 WHEN fecha_4 = current_date() THEN acuerdo_4 END AS pago, LPAD( idhoja, 8, '0'), nombre, telefono, servicio, objeto, notapago, idfecha, empresa FROM hojas WHERE fecha_1 = CURRENT_DATE() OR fecha_2 = current_date() or fecha_3 = current_date or fecha_4 = current_date();")
    vencehoy = cursor.fetchall()
    cursor.execute("SELECT 'CUOTA 1' AS cuota, fecha_1 AS vencimiento, acuerdo_1 AS pago, LPAD( idhoja, 8, '0'), nombre, telefono, servicio, objeto, notapago, datediff(current_date(), fecha_1) as diferencia, idfecha, empresa, DATE_FORMAT(fecha_1, '%d %M %Y') FROM hojas where fecha_1 < CURRENT_DATE() UNION ALL SELECT 'CUOTA 2' AS cuota, fecha_2 AS vencimiento, acuerdo_2 AS pago, LPAD( idhoja, 8, '0'), nombre, telefono, servicio, objeto, notapago, datediff(current_date(), fecha_2) as diferencia, idfecha, empresa, DATE_FORMAT(fecha_2, '%d %M %Y') FROM hojas where fecha_2 < CURRENT_DATE() UNION ALL SELECT 'CUOTA 3' AS cuota, fecha_3 AS vencimiento, acuerdo_3 AS pago, LPAD( idhoja, 8, '0'), nombre, telefono, servicio, objeto, notapago, datediff(current_date(), fecha_3) as diferencia, idfecha, empresa, DATE_FORMAT(fecha_3, '%d %M %Y') FROM hojas where fecha_3 < CURRENT_DATE() UNION ALL SELECT 'CUOTA 4' AS cuota, fecha_4 AS vencimiento, acuerdo_4 AS pago, LPAD( idhoja, 8, '0'), nombre, telefono, servicio, objeto, notapago, datediff(current_date(), fecha_4) as diferencia, idfecha, empresa, DATE_FORMAT(fecha_4, '%d %M %Y') FROM hojas where fecha_4 < CURRENT_DATE() order by diferencia;")
    vencidos = cursor.fetchall()
    cursor.execute("SELECT 'CUOTA 1' AS cuota, fecha_1 AS vencimiento, acuerdo_1 AS pago, LPAD( idhoja, 8, '0'), nombre, telefono, servicio, objeto, notapago, datediff(fecha_1, current_date()) as diferencia, idfecha, empresa, DATE_FORMAT(fecha_1, '%d %M %Y') FROM hojas where datediff(fecha_1, current_date()) > 0 and datediff(fecha_1, current_date()) < 6 UNION ALL SELECT 'CUOTA 2' AS cuota, fecha_2 AS vencimiento, acuerdo_2 AS pago, LPAD( idhoja, 8, '0'), nombre, telefono, servicio, objeto, notapago, datediff(fecha_2, current_date()) as diferencia, idfecha, empresa, DATE_FORMAT(fecha_2, '%d %M %Y') FROM hojas where datediff(fecha_2, current_date()) > 0 and datediff(fecha_2, current_date()) < 6 UNION ALL SELECT 'CUOTA 3' AS cuota, fecha_3 AS vencimiento, acuerdo_3 AS pago, LPAD( idhoja, 8, '0'), nombre, telefono, servicio, objeto, notapago, datediff(fecha_3, current_date()) as diferencia, idfecha, empresa, DATE_FORMAT(fecha_3, '%d %M %Y') FROM hojas where datediff(fecha_3, current_date()) > 0 and datediff(fecha_3, current_date()) < 6 UNION ALL SELECT 'CUOTA 4' AS cuota, fecha_4 AS vencimiento, acuerdo_4 AS pago, LPAD( idhoja, 8, '0'), nombre, telefono, servicio, objeto, notapago, datediff(fecha_4, current_date()) as diferencia, idfecha, empresa, DATE_FORMAT(fecha_4, '%d %M %Y') FROM hojas where datediff(fecha_4, current_date()) > 0 and  datediff(fecha_4, current_date()) < 6 order by diferencia;")
    porvencer = cursor.fetchall()
    cursor.execute(f"select DATE_FORMAT(fecha, '%d %M'), empresa, nombre, telefono, motivo, tareas.tarea, email, direccion, registros.tarea, fecha, hora_tarea, cast(hora_tarea as unsigned) as hora, DATE_FORMAT(fecha_tarea, '%d %M %Y'), datediff(current_date(), fecha_tarea) as dias, fecha_tarea from registros JOIN tareas ON registros.tarea = tareas.idtarea where (fecha_tarea < current_date() or fecha_tarea is null) and agente = '{current_user.fullname}' and estado = 'registro' and registros.tarea in (select tarea from registros where tarea = 0 or tarea = 3 or tarea = 4 or tarea = 5 or tarea = 6 or tarea = 8 or tarea = 9 or tarea = 10 or tarea = 11 or tarea = 12 or tarea = 13 or tarea = 14 or tarea = 15 or tarea = 16 or tarea = 17 or tarea = 18 or tarea = 20 or tarea = 25 or tarea = 26) ORDER BY dias, hora, fecha asc;")
    atrasados = cursor.fetchall()
    dias = ("Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado")
    nombre_dia_hoy = f'{dias[int(dt.date.today().strftime("%w"))]} {dt.date.today().strftime("%d")}'
    return render_template('dashboard.html', tareas=tareas, agentes=agentes, pendiente=pendiente, empresas=empresas, vencehoy=vencehoy, vencidos=vencidos, porvencer=porvencer, dia_hoy = dt.date.today(), nombre_dia_hoy=nombre_dia_hoy, atrasados=atrasados)

@app.route('/pagos/eliminarpago', methods=['GET', 'POST'])
@login_required
def eliminarPago():
    idpago = request.form.get('idpago')
    nombre = request.form.get('nombre')
    telefono = request.form.get('telefono')
    total = request.form.get('total')
    cursor = db.connection.cursor()
    cursor.execute(f"DELETE from pagos WHERE idpagos = {idpago};")
    cursor.execute(f"INSERT INTO movimientos (mov, date_mov, agente, nombre, telefono, datonuevo) VALUES ('Eliminó un pago del sistema.', now(), '{current_user.fullname}', '{nombre}', '{telefono}', '$ {total}')")
    db.connection.commit()
    cursor.close()
    return jsonify({'status': 'success'})

@app.route('/pagos/registrarpago', methods=['GET', 'POST'])
@login_required
def registrarPago():
    pago_condicional = request.form.get('pago_condicional')
    empresa = request.form.get('empresa')
    motivo = request.form.get('motivo')
    nombre = request.form.get('nombre')
    fecha_pago = request.form.get('fecha_pago')
    forma_pago = request.form.get('forma_pago')
    pago = request.form.get('pago')
    agente = current_user.fullname
    cursor = db.connection.cursor()
    if pago_condicional == 'hoja':
        fecha_vencimiento = request.form.get('fecha_vencimiento')
        idhoja = request.form.get('idhoja')
        telefono = request.form.get('telefono')
        cursor.execute('INSERT INTO pagos (empresa, motivo, idhoja, cliente, telefono, fecha_vencimiento, fecha_pago, forma_pago, pago, agente) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (empresa, motivo, idhoja, nombre, telefono, fecha_vencimiento, fecha_pago, forma_pago, pago, agente))
        cursor.execute(f'UPDATE hojas SET acuerdo_{motivo[6]} = null, interes_{motivo[6]} = null, fecha_{motivo[6]} = null WHERE idhoja = {idhoja}')
        cursor.execute(f"UPDATE hojas SET total = total-{pago} WHERE idhoja = {idhoja} and cantidad is null")
    if pago_condicional == 'recordatorio':
        fecha_vencimiento = request.form.get('fecha_vencimiento')
        idrecordatorio = request.form.get('idrecordatorio')
        telefono_sn = request.form.get('telefono')
        telefono = ''
        for n in telefono_sn:
            if n.isdigit():
                telefono = telefono+n
        cursor.execute('INSERT INTO pagos (empresa, motivo, cliente, telefono, fecha_vencimiento, fecha_pago, forma_pago, pago, agente, idrecordatorio) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (empresa, motivo, nombre, telefono, fecha_vencimiento, fecha_pago, forma_pago, pago, agente, idrecordatorio))
        cursor.execute(f"DELETE FROM recordatorios WHERE idrecordatorio = {idrecordatorio}")
    if pago_condicional == 'nuevo':
        telefono_sn = request.form.get('telefono')
        telefono = ''
        for n in telefono_sn:
            if n.isdigit():
                telefono = telefono+n
        nombre = nombre.strip().upper()
        motivo = motivo.strip().upper()
        empresa = empresa.strip().upper()
        cursor.execute('INSERT INTO pagos (empresa, motivo, cliente, telefono, fecha_pago, forma_pago, pago, agente) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (empresa, motivo, nombre, telefono, fecha_pago, forma_pago, pago, agente))
    cursor.execute(f"INSERT INTO movimientos (mov, date_mov, agente, nombre, telefono, datonuevo) VALUES ('Registró un pago.', now(), '{agente}', '{nombre}', '{telefono}', '{motivo}. $ {pago}')")
    db.connection.commit()
    cursor.close()
    return jsonify({'status': 'success'})

@app.route('/pagos', methods=['GET', 'POST'])
@login_required
def pagos():
    cursor = db.connection.cursor()
    fecha_inicial = None
    fecha_final = None
    if request.method == 'POST':
        mes = request.form['cambiar_mes']
        if mes == 'entrefechas':
            meses = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
            fecha_inicial = request.form['fecha_inicial']
            fecha_final = request.form['fecha_final']
            cursor.execute(f"SELECT LPAD(idhoja, 8, '0'), empresa, nombre, telefono, servicio, objeto, CASE WHEN fecha_1 BETWEEN '{fecha_inicial}' and '{fecha_final}' THEN acuerdo_1 ELSE null END as '1', CASE WHEN fecha_2 BETWEEN '{fecha_inicial}' and '{fecha_final}' THEN acuerdo_2 ELSE null END as '2', CASE WHEN fecha_3 BETWEEN '{fecha_inicial}' and '{fecha_final}' THEN acuerdo_3 ELSE null END as '3', CASE WHEN fecha_4 BETWEEN '{fecha_inicial}' and '{fecha_final}' THEN acuerdo_4 ELSE null END as '4', COALESCE(CASE WHEN fecha_1 BETWEEN '{fecha_inicial}' and '{fecha_final}' THEN acuerdo_1 ELSE 0 END,0)+COALESCE(CASE WHEN fecha_2 BETWEEN '{fecha_inicial}' and '{fecha_final}' THEN acuerdo_2 ELSE 0 END,0)+COALESCE(CASE WHEN fecha_3 BETWEEN '{fecha_inicial}' and '{fecha_final}' THEN acuerdo_3 ELSE 0 END,0)+COALESCE(CASE WHEN fecha_4 BETWEEN '{fecha_inicial}' and '{fecha_final}' THEN acuerdo_4 ELSE 0 END,0) as total, TRIM(CONCAT(CASE WHEN fecha_1 BETWEEN '{fecha_inicial}' and '{fecha_final}' THEN 'CUOTA 1' ELSE '' END,' ', CASE WHEN fecha_2 BETWEEN '{fecha_inicial}' and '{fecha_final}' THEN 'CUOTA 2' ELSE '' END, ' ',CASE WHEN fecha_3 BETWEEN '{fecha_inicial}' and '{fecha_final}' THEN 'CUOTA 3' ELSE '' END, ' ',CASE WHEN fecha_4 BETWEEN '{fecha_inicial}' and '{fecha_final}' THEN 'CUOTA 4' ELSE '' END)) as formateado from hojas where (COALESCE(acuerdo_1, 0)+COALESCE(acuerdo_2, 0)+COALESCE(acuerdo_3, 0)+COALESCE(acuerdo_4, 0) != 0) and (fecha_1 BETWEEN '{fecha_inicial}' and '{fecha_final}' or fecha_2 BETWEEN '{fecha_inicial}' and '{fecha_final}' or fecha_3 BETWEEN '{fecha_inicial}' and '{fecha_final}' or fecha_4 BETWEEN '{fecha_inicial}' and '{fecha_final}');")
            impagos = cursor.fetchall()
            cursor.execute(f"select idpagos, empresa, motivo, LPAD( idhoja, 8, '0'), cliente, telefono, date_format(fecha_vencimiento, '%d %M %Y'), date_format(fecha_pago, '%d %M %Y'), LOWER(forma_pago), pago, agente from pagos where fecha_pago BETWEEN '{fecha_inicial}' and '{fecha_final}' order by fecha_pago desc, idpagos desc;")
            fecha_inicial = f"{int(fecha_inicial[8]+fecha_inicial[9])} de {meses[int(fecha_inicial[5]+fecha_inicial[6])-1]} de {fecha_inicial[0]+fecha_inicial[1]+fecha_inicial[2]+fecha_inicial[3]}"
            fecha_final = f"{int(fecha_final[8]+fecha_final[9])} de {meses[int(fecha_final[5]+fecha_final[6])-1]} de {fecha_final[0]+fecha_final[1]+fecha_final[2]+fecha_final[3]}"
        else:
            cursor.execute(f"SELECT LPAD(idhoja, 8, '0'), empresa, nombre, telefono, servicio, objeto, CASE WHEN month(fecha_1) = {mes[5]+mes[6]} and year(fecha_1) = {mes[0]+mes[1]+mes[2]+mes[3]} THEN acuerdo_1 ELSE null END as '1', CASE WHEN month(fecha_2) = {mes[5]+mes[6]} and year(fecha_2) = {mes[0]+mes[1]+mes[2]+mes[3]} THEN acuerdo_2 ELSE null END as '2', CASE WHEN month(fecha_3) = {mes[5]+mes[6]} and year(fecha_3) = {mes[0]+mes[1]+mes[2]+mes[3]} THEN acuerdo_3 ELSE null END as '3', CASE WHEN month(fecha_4) = {mes[5]+mes[6]} and year(fecha_4) = {mes[0]+mes[1]+mes[2]+mes[3]} THEN acuerdo_4 ELSE null END as '4', COALESCE(CASE WHEN month(fecha_1) = {mes[5]+mes[6]} and year(fecha_1) = {mes[0]+mes[1]+mes[2]+mes[3]} THEN acuerdo_1 ELSE 0 END,0)+COALESCE(CASE WHEN month(fecha_2) = {mes[5]+mes[6]} and year(fecha_2) = {mes[0]+mes[1]+mes[2]+mes[3]} THEN acuerdo_2 ELSE 0 END,0)+COALESCE(CASE WHEN month(fecha_3) = {mes[5]+mes[6]} and year(fecha_3) = {mes[0]+mes[1]+mes[2]+mes[3]} THEN acuerdo_3 ELSE 0 END,0)+COALESCE(CASE WHEN month(fecha_4) = {mes[5]+mes[6]} and year(fecha_4) = {mes[0]+mes[1]+mes[2]+mes[3]} THEN acuerdo_4 ELSE 0 END,0) as total, TRIM(CONCAT(CASE WHEN month(fecha_1) = {mes[5]+mes[6]} and year(fecha_1) = {mes[0]+mes[1]+mes[2]+mes[3]} THEN 'CUOTA 1' ELSE '' END,' ', CASE WHEN month(fecha_2) = {mes[5]+mes[6]} and year(fecha_2) = {mes[0]+mes[1]+mes[2]+mes[3]} THEN 'CUOTA 2' ELSE '' END, ' ',CASE WHEN month(fecha_3) = {mes[5]+mes[6]} and year(fecha_3) = {mes[0]+mes[1]+mes[2]+mes[3]} THEN 'CUOTA 3' ELSE '' END, ' ',CASE WHEN month(fecha_4) = {mes[5]+mes[6]} and year(fecha_4) = {mes[0]+mes[1]+mes[2]+mes[3]} THEN 'CUOTA 4' ELSE '' END)) as formateado from hojas where (COALESCE(acuerdo_1, 0)+COALESCE(acuerdo_2, 0)+COALESCE(acuerdo_3, 0)+COALESCE(acuerdo_4, 0) != 0) and ((month(fecha_1) = {mes[5]+mes[6]} and year(fecha_1) = {mes[0]+mes[1]+mes[2]+mes[3]}) or (month(fecha_2) = {mes[5]+mes[6]} and year(fecha_2) = {mes[0]+mes[1]+mes[2]+mes[3]}) or (month(fecha_3) = {mes[5]+mes[6]} and year(fecha_3) = {mes[0]+mes[1]+mes[2]+mes[3]}) or (month(fecha_4) = {mes[5]+mes[6]} and year(fecha_4) = {mes[0]+mes[1]+mes[2]+mes[3]}));")
            impagos = cursor.fetchall()
            cursor.execute(f"select idpagos, empresa, motivo, LPAD( idhoja, 8, '0'), cliente, telefono, date_format(fecha_vencimiento, '%d %M %Y'), date_format(fecha_pago, '%d %M %Y'), LOWER(forma_pago), pago, agente from pagos where month(fecha_pago) = {mes[5]+mes[6]} and year(fecha_pago) = {mes[0]+mes[1]+mes[2]+mes[3]} order by fecha_pago desc, idpagos desc;")
    else:
        cursor.execute(f"SELECT LPAD(idhoja, 8, '0'), empresa, nombre, telefono, servicio, objeto, CASE WHEN month(fecha_1) = {dt.date.today().strftime('%m')} THEN acuerdo_1 ELSE null END as '1', CASE WHEN month(fecha_2) = {dt.date.today().strftime('%m')} THEN acuerdo_2 ELSE null END as '2', CASE WHEN month(fecha_3) = {dt.date.today().strftime('%m')} THEN acuerdo_3 ELSE null END as '3', CASE WHEN month(fecha_4) = {dt.date.today().strftime('%m')} THEN acuerdo_4 ELSE null END as '4', COALESCE(CASE WHEN month(fecha_1) = {dt.date.today().strftime('%m')} THEN acuerdo_1 ELSE 0 END,0)+COALESCE(CASE WHEN month(fecha_2) = {dt.date.today().strftime('%m')} THEN acuerdo_2 ELSE 0 END,0)+COALESCE(CASE WHEN month(fecha_3) = {dt.date.today().strftime('%m')} THEN acuerdo_3 ELSE 0 END,0)+COALESCE(CASE WHEN month(fecha_4) = {dt.date.today().strftime('%m')} THEN acuerdo_4 ELSE 0 END,0) as total, TRIM(CONCAT(CASE WHEN month(fecha_1) = {dt.date.today().strftime('%m')} THEN 'CUOTA 1' ELSE '' END,' ', CASE WHEN month(fecha_2) = {dt.date.today().strftime('%m')} THEN 'CUOTA 2' ELSE '' END, ' ',CASE WHEN month(fecha_3) = {dt.date.today().strftime('%m')} THEN 'CUOTA 3' ELSE '' END, ' ',CASE WHEN month(fecha_4) = {dt.date.today().strftime('%m')} THEN 'CUOTA 4' ELSE '' END)) as formateado from hojas where (COALESCE(acuerdo_1, 0)+COALESCE(acuerdo_2, 0)+COALESCE(acuerdo_3, 0)+COALESCE(acuerdo_4, 0) != 0) and (month(fecha_1) = {dt.date.today().strftime('%m')} or month(fecha_2) = {dt.date.today().strftime('%m')} or month(fecha_3) = {dt.date.today().strftime('%m')} or month(fecha_4) = {dt.date.today().strftime('%m')});")
        impagos = cursor.fetchall()
        cursor.execute(f"select idpagos, empresa, motivo, LPAD(idhoja, 8, '0'), cliente, telefono, date_format(fecha_vencimiento, '%d %M %Y'), date_format(fecha_pago, '%d %M %Y'), LOWER(forma_pago), pago, agente from pagos where month(fecha_pago) = {dt.date.today().strftime('%m')} and year(fecha_pago) = {dt.date.today().strftime('%Y')} order by fecha_pago desc, idpagos desc;")
        mes = f"{dt.date.today().strftime('%Y')}-{dt.date.today().strftime('%m')}"
    pagos = cursor.fetchall()
    suma = 0
    sumaimpagos = 0
    for i in range(0,len(pagos)):
        suma = suma+float(pagos[i][9])
    for p in range(0,len(impagos)):
        sumaimpagos = sumaimpagos+float(impagos[p][10])
    cursor.execute("SELECT empresa from clientes order by empresa asc;")
    empresas = cursor.fetchall()
    return render_template('pagos.html', pagos=pagos, empresas=empresas, hoy=dt.date.today(), mes=mes, suma=suma,fecha_inicial=fecha_inicial, fecha_final   =fecha_final, impagos=impagos, sumaimpagos = sumaimpagos)
    
@app.route('/usuarios')
@login_required
def usuarios():
    cursor = db.connection.cursor()
    sql = "SELECT * FROM auth;"
    cursor.execute(sql)
    tablas = cursor.fetchall()
    return render_template('usuarios.html', tablas=tablas)

@app.route('/movimientos', methods=['GET', 'POST'])
@login_required
def movimientos():
    cursor = db.connection.cursor()
    fecha = None
    if request.method == 'POST':
        accion = request.form['accion']
        if accion == 'cantidad':
            cant_mov = request.form['cantidad_mov']
            cursor.execute(f"SELECT mov, DATE_FORMAT(date_mov, '%d %M %Y • %T'), agente, nombre, datonuevo FROM movimientos order by date_mov desc limit {cant_mov};")
            mostrados = cant_mov
        if accion == 'filtro_fecha':
            fecha = request.form['fecha_unica']
            cursor.execute(f"SELECT count(*) from movimientos where date(date_mov) = '{fecha}'")
            contados_filtrados = cursor.fetchone()
            cursor.execute(f"SELECT mov, DATE_FORMAT(date_mov, '%d %M %Y • %T'), agente, nombre, datonuevo, date(date_mov) from movimientos where date(date_mov) = '{fecha}' order by date_mov desc")
            mostrados = contados_filtrados[0]
    else:
        cursor.execute("SELECT  mov, DATE_FORMAT(date_mov, '%d %M %Y • %T'), agente, nombre, datonuevo FROM movimientos ORDER BY date_mov DESC LIMIT 25;")
        mostrados = 25
    tablas = cursor.fetchall()
    cursor.execute("SELECT agente from movimientos where agente is not null group by agente;")
    agentes = cursor.fetchall()
    return render_template('movimientos.html', tablas=tablas, mostrados=mostrados, fecha=fecha, agentes=agentes)
    
@app.route('/registros', methods=['GET', 'POST'])
@login_required
def registros():
    cursor = db.connection.cursor()
    consulta = ("""SELECT 
    COUNT(DISTINCT registros.telefono, registros.nombre) AS total_registros
FROM 
    registros 
JOIN 
    tareas ON tareas.idtarea = registros.tarea 
LEFT JOIN 
    hojas ON registros.fecha = hojas.idfecha 
WHERE 
    registros.estado = 'registro' 
    AND registros.telefono != ''  -- Condición para omitir registros con teléfono vacío
    AND registros.telefono IN (
        SELECT telefono 
        FROM registros 
        WHERE telefono != ''  -- Asegura que solo se consideren teléfonos no vacíos
        GROUP BY telefono 
        HAVING COUNT(DISTINCT nombre) > 1
    );
    """)
    #repetidos = cursor.fetchone()
    repetidos = None
    start_time = time.time()
    cursor.execute("SELECT COUNT(*) from registros where estado = 'registro';")
    n_registros = cursor.fetchone()
    cursor.execute("select COUNT(*) from registros join tareas on registros.tarea = tareas.idtarea where (tareas.tarea = 'INSTALACIÓN PROGRAMADA' or tareas.tarea = 'INSPECCIÓN PROGRAMADA' or  tareas.tarea = 'YA INSTALÓ' or tareas.tarea = 'INSPECCIÓN REALIZADA') and (nombre NOT LIKE '% %' or direccion = '')")
    faltantes = cursor.fetchone()
    fechaunica = ''
    fecha_inicial = ''
    fecha_final = ''
    fecha_final = ''
    editar_telefono = 'SI'
    categoria = 'fecha'
    cursor.execute("select tareas.tarea from registros join tareas on registros.tarea = tareas.idtarea where registros.estado = 'registro' group by tareas.tarea order by tareas.tarea")
    tareas_empresa = cursor.fetchall()
    empresa = None

    
    if request.method == 'POST':
        filtro = request.form['filtro']
        if filtro == 'fecha_unica':
            fechaunica = request.form['fecha_inicial']
            cursor.execute(f"SELECT count(*) from registros join tareas on registros.tarea = tareas.idtarea where estado = 'registro' and fecha_tarea = '{fechaunica}' and tareas.tarea != 'NO LE INTERESA' and tareas.tarea != '';")
            one = cursor.fetchone()
            mostrados = one[0]
            cursor.execute(f"SELECT tareas.tarea FROM registros join tareas on registros.tarea = tareas.idtarea where estado = 'registro' and fecha_tarea = '{fechaunica}' and tareas.tarea != 'NO LE INTERESA' and tareas.tarea != '' group by registros.tarea order by registros.tarea")
            tareas_empresa = cursor.fetchall()
            cursor.execute(f"SELECT DISTINCT registros.empresa, registros.agente, registros.nombre, registros.telefono, registros.email, registros.motivo, registros.tarea, DATE_FORMAT(registros.fecha, '%d %M %Y • %T'), CAST(registros.fecha AS char), tareas.tarea, registros.fecha_tarea, registros.hora_tarea, registros.nota_rechazo, registros.direccion, tareas.color, CASE WHEN hojas.idfecha IS NOT NULL THEN 1 ELSE 0 END AS existe, DATE_FORMAT(fecha_tarea, '%d %M %Y'), perfil FROM registros join tareas on tareas.idtarea = registros.tarea LEFT JOIN hojas ON registros.fecha = hojas.idfecha WHERE estado = 'registro' and fecha_tarea = '{fechaunica}' and tareas.tarea != 'NO LE INTERESA' and tareas.tarea != '' order by registros.fecha desc")
        if filtro == 'fechas':
            fecha_inicial = request.form['fecha_inicial']
            fecha_final = request.form['fecha_final']
            categoria = request.form['limite']
            if categoria == 'fecha':
                cursor.execute(f"SELECT count(*) from registros where estado = 'registro' and fecha BETWEEN '{fecha_inicial}' and '{fecha_final}';")
                one = cursor.fetchone()
                mostrados = one[0]
                cursor.execute(f"SELECT tareas.tarea FROM registros join tareas on registros.tarea = tareas.idtarea where estado = 'registro' and fecha BETWEEN '{fecha_inicial}' and '{fecha_final}' group by registros.tarea order by registros.tarea")
                tareas_empresa = cursor.fetchall()
                cursor.execute(f"SELECT DISTINCT registros.empresa, registros.agente, registros.nombre, registros.telefono, registros.email, registros.motivo,  registros.tarea, DATE_FORMAT(registros.fecha, '%d %M %Y • %T'), CAST(registros.fecha AS char), tareas.tarea, registros.fecha_tarea, registros.hora_tarea, registros.nota_rechazo, registros.direccion, tareas.color, CASE WHEN hojas.idfecha IS NOT NULL THEN 1 ELSE 0 END AS existe, DATE_FORMAT(fecha_tarea, '%d %M %Y'), perfil FROM registros JOIN tareas ON tareas.idtarea = registros.tarea LEFT JOIN hojas ON registros.fecha = hojas.idfecha WHERE registros.estado = 'registro' and registros.fecha BETWEEN '{fecha_inicial}' and '{fecha_final} 23:59:59' order by registros.fecha desc;")
            else:
                cursor.execute(f"SELECT count(*) from registros where estado = 'registro' and tarea != 1 and tarea != 0 and tarea != 2 and fecha_tarea BETWEEN '{fecha_inicial}' and '{fecha_final}';")
                one = cursor.fetchone()
                mostrados = one[0]
                cursor.execute(f"SELECT tareas.tarea FROM registros join tareas on registros.tarea = tareas.idtarea where registros.tarea != 1 and registros.tarea != 0 and registros.tarea != 2 and estado = 'registro' and fecha_tarea BETWEEN '{fecha_inicial}' and '{fecha_final}' group by registros.tarea order by registros.tarea")
                tareas_empresa = cursor.fetchall()
                cursor.execute(f"SELECT DISTINCT registros.empresa, registros.agente, registros.nombre, registros.telefono, registros.email, registros.motivo,  registros.tarea, DATE_FORMAT(registros.fecha, '%d %M %Y • %T'), CAST(registros.fecha AS char), tareas.tarea, registros.fecha_tarea, registros.hora_tarea, registros.estado, registros.nota_rechazo, registros.direccion, tareas.color, CASE WHEN hojas.idfecha IS NOT NULL THEN 1 ELSE 0 END AS existe, DATE_FORMAT(fecha_tarea, '%d %M %Y'), perfil FROM registros JOIN tareas ON tareas.idtarea = registros.tarea LEFT JOIN hojas ON registros.fecha = hojas.idfecha WHERE registros.estado = 'registro' and registros.fecha_tarea BETWEEN '{fecha_inicial}' and '{fecha_final}' and registros.tarea != 1 and registros.tarea != 0 and registros.tarea != 2 order by registros.fecha_tarea desc;")
        if filtro == 'limite':
            limite = request.form['limite']
            if limite != 'all':
                cursor.execute(f"SELECT DISTINCT registros.empresa, registros.agente, registros.nombre, registros.telefono, registros.email, registros.motivo,  registros.tarea, DATE_FORMAT(registros.fecha, '%d %M %Y • %T'), CAST(registros.fecha AS char), tareas.tarea, registros.fecha_tarea, registros.hora_tarea, registros.nota_rechazo, registros.direccion, tareas.color, CASE WHEN hojas.idfecha IS NOT NULL THEN 1 ELSE 0 END AS existe, DATE_FORMAT(fecha_tarea, '%d %M %Y'), perfil FROM registros JOIN tareas ON tareas.idtarea = registros.tarea LEFT JOIN hojas ON registros.fecha = hojas.idfecha WHERE estado = 'registro' order by registros.fecha desc LIMIT {limite};")
                mostrados = limite
            else:
                cursor.execute(f"SELECT DISTINCT registros.empresa, registros.agente, registros.nombre, registros.telefono, registros.email, registros.motivo,  registros.tarea, DATE_FORMAT(registros.fecha, '%d %M %Y • %T'), CAST(registros.fecha AS char), tareas.tarea, registros.fecha_tarea, registros.hora_tarea, registros.nota_rechazo, registros.direccion, tareas.color, CASE WHEN hojas.idfecha IS NOT NULL THEN 1 ELSE 0 END AS existe, DATE_FORMAT(fecha_tarea, '%d %M %Y'), perfil FROM registros JOIN tareas ON tareas.idtarea = registros.tarea LEFT JOIN hojas ON registros.fecha = hojas.idfecha WHERE registros.estado = 'registro' order by registros.fecha desc LIMIT {n_registros[0]};")
                mostrados = n_registros[0]
        if filtro == 'duplicados':
            cursor.execute("""SELECT DISTINCT
    registros.empresa, 
    registros.agente, 
    registros.nombre, 
    registros.telefono, 
    registros.email, 
    registros.motivo,  
    registros.tarea, 
    DATE_FORMAT(registros.fecha, '%d %M %Y • %T') AS fecha_formateada, 
    CAST(registros.fecha AS char) AS fecha_char, 
    tareas.tarea, 
    registros.fecha_tarea, 
    registros.hora_tarea, 
    registros.nota_rechazo, 
    registros.direccion, 
    tareas.color, 
    CASE WHEN hojas.idfecha IS NOT NULL THEN 1 ELSE 0 END AS existe, 
    DATE_FORMAT(fecha_tarea, '%d %M %Y') AS fecha_tarea_formateada, 
    perfil 
FROM 
    registros 
JOIN 
    tareas ON tareas.idtarea = registros.tarea 
LEFT JOIN 
    hojas ON registros.fecha = hojas.idfecha 
WHERE 
    registros.estado = 'registro' 
    AND registros.telefono != ''  -- Condición para omitir registros con teléfono vacío
    AND registros.telefono IN (
        SELECT telefono 
        FROM registros 
        WHERE telefono != ''  -- Asegura que solo se consideren teléfonos no vacíos
        GROUP BY telefono 
        HAVING COUNT(DISTINCT nombre) > 1
    );""")
            mostrados = repetidos[0]
            editar_telefono = 'NO'
        if filtro == 'faltantes':
            cursor.execute("SELECT registros.empresa, registros.agente, registros.nombre, registros.telefono, registros.email, registros.motivo, registros.tarea, DATE_FORMAT(registros.fecha, '%d %M %Y • %T'), CAST(registros.fecha AS char), tareas.tarea, registros.fecha_tarea, registros.hora_tarea, registros.nota_rechazo, registros.direccion, tareas.color, CASE WHEN hojas.idfecha IS NOT NULL THEN 1 ELSE 0 END AS existe, DATE_FORMAT(fecha_tarea, '%d %M %Y'), perfil FROM registros JOIN tareas ON registros.tarea = tareas.idtarea LEFT JOIN hojas ON registros.fecha = hojas.idfecha WHERE (tareas.tarea = 'INSTALACIÓN PROGRAMADA' or tareas.tarea = 'INSPECCIÓN PROGRAMADA' or  tareas.tarea = 'YA INSTALÓ' or tareas.tarea = 'INSPECCIÓN REALIZADA') and (registros.nombre NOT LIKE '% %' or registros.direccion = '');")
            mostrados = faltantes[0]
        if filtro == 'empresa':
            empresa = request.form['limite']
            cursor.execute(f"SELECT COUNT(*) from registros where estado = 'registro' and empresa = '{empresa}';")
            one = cursor.fetchone()
            mostrados = one[0]
            cursor.execute(f"SELECT tareas.tarea FROM registros join tareas on registros.tarea = tareas.idtarea where estado = 'registro' and empresa = '{empresa}' group by registros.tarea order by registros.tarea")
            tareas_empresa = cursor.fetchall()
            cursor.execute(f"SELECT DISTINCT registros.empresa, registros.agente, registros.nombre, registros.telefono, registros.email, registros.motivo, registros.tarea, DATE_FORMAT(registros.fecha, '%d %M %Y • %T'), CAST(registros.fecha AS char), tareas.tarea, registros.fecha_tarea, registros.hora_tarea, registros.nota_rechazo, registros.direccion, tareas.color, CASE WHEN hojas.idfecha IS NOT NULL THEN 1 ELSE 0 END AS existe, DATE_FORMAT(fecha_tarea, '%d %M %Y'), perfil FROM registros JOIN tareas ON registros.tarea = tareas.idtarea LEFT JOIN hojas ON registros.fecha = hojas.idfecha WHERE registros.estado = 'registro' and registros.empresa = '{empresa}' order by registros.fecha desc;")
    else:
        
        cursor.execute("SELECT DISTINCT registros.empresa, registros.agente, registros.nombre, registros.telefono, registros.email, registros.motivo, registros.tarea, DATE_FORMAT(registros.fecha, '%d %M %Y • %T'), CAST(registros.fecha AS char), tareas.tarea, registros.fecha_tarea, registros.hora_tarea, registros.nota_rechazo, registros.direccion, tareas.color, CASE WHEN hojas.idfecha IS NOT NULL THEN 1 ELSE 0 END AS existe, DATE_FORMAT(fecha_tarea, '%d %M %Y'), perfil FROM registros JOIN tareas ON tareas.idtarea = registros.tarea LEFT JOIN hojas ON registros.fecha = hojas.idfecha WHERE registros.estado = 'registro' ORDER BY registros.fecha DESC LIMIT 25;")
        mostrados = 25
    tablas = cursor.fetchall()
    cursor.execute("SELECT agente from registros where agente is not null group by agente;")
    agentes_purgados = cursor.fetchall()
    cursor.execute("SELECT fullname from auth order by fullname asc")
    agentes = cursor.fetchall()
    cursor.execute("select * from tareas")
    tareas = cursor.fetchall()
    cursor.execute("SELECT empresa from clientes order by empresa asc;")
    empresas = cursor.fetchall()
    cursor.execute("SELECT LPAD( idhoja, 8, '0'), CAST(idfecha AS char), replace(nombre, ' ','_'), replace(idfecha, ':', '') from hojas where idfecha is not null group by idfecha;")
    pdfs = cursor.fetchall()
    db.connection.commit()
    cursor.execute("select LPAD( idhoja+1, 8, '0') from hojas where cantidad is null order by idhoja desc limit 1;")
    ultimahoja = cursor.fetchone()
    cursor.close()
    #end_time = time.time()
    #print(f"tiempo ejecucion: {end_time - start_time}")
    return render_template('registros.html', tablas=tablas, agentes=agentes, tareas=tareas, empresas=empresas, n_registros=n_registros, mostrados=mostrados, fecha_inicial=fecha_inicial, fecha_final=fecha_final, fechaunica=fechaunica, repetidos=repetidos, editar_telefono=editar_telefono, faltantes=faltantes, categoria=categoria, tareas_empresa=tareas_empresa, empresa=empresa, pdfs=pdfs, ultimahoja=ultimahoja, agentes_purgados=agentes_purgados)

@app.route('/hoja_de_inspeccion/generarpdf', methods=['GET', 'POST'])
@login_required
def generarPdf():
    addMapping("Helvetica-Bold", 1, 0, "Helvetica-Bold")
    idregistro = request.form
    existe = idregistro['existe']
    idfecha = idregistro['idfecha']
    cursor = db.connection.cursor()
    if existe == 'si':
        cursor.execute(f"select DAY(fecha_emision), DATE_FORMAT(fecha_emision, '%M'), YEAR(fecha_emision), LPAD( idhoja, 8, '0'), nombre, direccion, telefono, servicio, objeto, notas, total, enganche, tipopago, acuerdo_1, interes_1, DATE_FORMAT(fecha_1, '%d %M %Y'), acuerdo_2, interes_2, DATE_FORMAT(fecha_2, '%d %M %Y'), acuerdo_3, interes_3, DATE_FORMAT(fecha_3, '%d %M %Y'), acuerdo_4, interes_4, DATE_FORMAT(fecha_4, '%d %M %Y'), notapago, mapa from hojas where idfecha = '{idfecha}' and cantidad is null;")
        tabla = cursor.fetchall()
        if not tabla[0][13] and not tabla[0][16] and not tabla[0][19] and not tabla[0][22]:
            cursor.execute(f'UPDATE hojas SET tipopago = "" WHERE idfecha = "{idfecha}" and cantidad is null;')
            db.connection.commit()
            cursor.execute(f"select DAY(fecha_emision), DATE_FORMAT(fecha_emision, '%M'), YEAR(fecha_emision), LPAD( idhoja, 8, '0'), nombre, direccion, telefono, servicio, objeto, notas, total, enganche, tipopago, acuerdo_1, interes_1, DATE_FORMAT(fecha_1, '%d %M %Y'), acuerdo_2, interes_2, DATE_FORMAT(fecha_2, '%d %M %Y'), acuerdo_3, interes_3, DATE_FORMAT(fecha_3, '%d %M %Y'), acuerdo_4, interes_4, DATE_FORMAT(fecha_4, '%d %M %Y'), notapago, mapa from hojas where idfecha = '{idfecha}' and cantidad is null;")
            tabla = cursor.fetchall()
    else:
        datos = json.loads(idregistro['datos'])
        archivo = request.files['mapa']
        contenido = archivo.read()
        cursor.execute("select LPAD( idhoja+1, 8, '0') from hojas where cantidad is null order by idhoja desc limit 1;")
        ultimahoja = cursor.fetchone()
        cursor.execute("INSERT INTO hojas (idhoja, idfecha, fecha_emision, nombre, direccion, telefono, empresa, mapa, servicio, objeto, notas, total, enganche, notapago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ultimahoja[0], idfecha, dt.date.today(), datos[0].strip().upper(), datos[1].upper().strip(), datos[2].strip(), datos[3].upper().strip(), contenido, '', '', '', 0, 0,''))
        db.connection.commit()
        cursor.execute(f"select DAY(current_date()), DATE_FORMAT(current_date(), '%M'), YEAR(current_date()), LPAD( idhoja, 8, '0'), nombre, direccion, telefono, servicio, objeto, notas, total, enganche, tipopago, '_______________', '', '', '_______________', '', '', '_______________', '', '', '_______________', '', '', notapago, mapa from hojas where idfecha = '{idfecha}' and cantidad is null;")
        tabla = cursor.fetchall()
        
    saldo_restante = float(tabla[0][10]-tabla[0][11])
    pdf_filename = f"static/hojas/HOJA_{tabla[0][3].strip()}_{tabla[0][4].upper().strip().replace(' ','_')}_{idfecha.replace(':','')}.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize = A4, leftMargin=15, rightMargin=15, topMargin=15, bottomMargin=15, title=f"HOJA DE INSPECCIÓN N°{tabla[0][3]} - {tabla[0][4].strip()}")
    
    estilo_normal = ParagraphStyle(name='Normal', fontName='Helvetica', leading=14, textColor=colors.black, alignment=TA_LEFT)
    estilo_bold_italic = ParagraphStyle(name='BoldItalic', parent=estilo_normal, fontName='Helvetica-BoldOblique', fontSize=10, textColor=colors.black, alignment=TA_CENTER, spaceBefpte=10, spaceAfter=10, leading=14, wordWrap='LTR', leftIndent=0, rightIndent=0, firstLineIndent=0, underlineWidth=0, underlineColor=None, bulletFontName='Helvetica-BoldOblique', bulletFontSize=12, bulletIndent=0, textColorSpace=None)
    estilo_bold = ParagraphStyle(name='Bold', fontName='Helvetica-Bold', parent=estilo_normal, leading=14, textColor=colors.black, alignment=TA_LEFT)
    estilo_grande = ParagraphStyle(name="Grande", fontName="Helvetica-Bold", fontSize=18, alignment=TA_CENTER, leading=10)
    
    estilo_tabla1 = TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('SPAN', (0, 0), (2, 0)),
                                ('BACKGROUND', (0,0), (2,0), colors.lightblue),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('VALIGN', (0,0), (-1, -1), 'MIDDLE')])
    
    estilo_tabla2 = TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('VALIGN', (0,0), (-1, -1), 'MIDDLE'),
                                ('SPAN', (0, 1), (1, 1))])
    
    estilo_tabla3 = TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT')])
    
    estilo_tabla4 = TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')])
    
    estilo_tabla_materiales = TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black),
                                          ('VALIGN', (0,0), (-1,-1), "MIDDLE"),
                                          ('BACKGROUND', (0,0), (2,0), colors.lemonchiffon)])
    
    estilo_tabla_acuerdos = TableStyle([
        ('SPAN', (0,0), (1,0)),
        ('SPAN', (0,2), (1,2)),
        ('VALIGN', (0,1), (1,1), "TOP")
    ])
    
    estilo_tabla_firmas = TableStyle([
        ('SPAN', (0, 2), (1, 2)),
        ('SPAN', (0, 3), (1, 3)),
        ('SPAN', (0, 4), (1, 4))
    ])

    contenido = []

    datos_tabla1 = [
        [Paragraph("<para align=center><b>FECHA DE EMISIÓN</b></para>", estilo_bold)],
        [Paragraph("<para align=center><b>DÍA</b></para>", estilo_bold), Paragraph("<para align=center><b>MES</b></para>", estilo_bold), Paragraph("<para align=center><b>AÑO</b></para>", estilo_bold)],
        [tabla[0][0], tabla[0][1], tabla[0][2]]
    ]
    
    datos_tabla_principal = [
        [RLImage("static/img/portada_hoja_inspeccion.png", width=200, height=80), Table(datos_tabla1, style=estilo_tabla1)]
    ]
    
    contenido.append(Table(datos_tabla_principal))#, colWidths=[250, 250]))
    contenido.append(Spacer(1, 5))
    contenido.append(Paragraph(f"ORDEN DE SERVICIOS N° - {tabla[0][3]}", estilo_grande))
    datos_tabla2 = [
        [Paragraph(f"<b>Nombre:</b> {tabla[0][4]}",  estilo_normal), Paragraph(f"<b>Teléfono:</b> {tabla[0][6]}", estilo_normal)],
        [Paragraph(f"<b>Dirección:</b> {tabla[0][5]}", estilo_normal)]
    ]
    contenido.append(Spacer(1, 20))
    contenido.append(Table(datos_tabla2, style=estilo_tabla2))
    contenido.append(Spacer(1, 5))
    
    if existe == 'si':
        if tabla[0][8] != "CCTV" and tabla[0][8] != "INTERNET":
            contenido.append(Paragraph(f"Otro: {tabla[0][8]}", estilo_bold))
            contenido.append(Spacer(1, 5))
    servicio = [
        [Paragraph("MANTENIMIENTO PREVENTIVO", estilo_bold), ""],
        [Paragraph("INSTALACIÓN", estilo_bold), ""],
        [Paragraph("MANTENIMIENTO CORRECTIVO", estilo_bold), ""],
        [Paragraph("INSPECCIÓN", estilo_bold), ""]
    ]
    objeto = [
        [Paragraph("CCTV", estilo_bold), ""],
        [Paragraph("INTERNET", estilo_bold), ""],
        [Paragraph("Otro", estilo_bold), ""]
    ]
    
    if tabla[0][7] == "MANTENIMIENTO PREVENTIVO":
        servicio[0][1] = RLImage("static/img/seleccionador-check.png", width=15, height=15)
    elif tabla[0][7] == "INSTALACIÓN":
        servicio[1][1] = RLImage("static/img/seleccionador-check.png", width=15, height=15)
    elif tabla[0][7] == "MANTENIMIENTO CORRECTIVO":
        servicio[2][1] = RLImage("static/img/seleccionador-check.png", width=15, height=15)
    elif tabla[0][7] == "INSPECCIÓN":
        servicio[3][1] = RLImage("static/img/seleccionador-check.png", width=15, height=15)
    
    if existe == 'si':
        if tabla[0][8] == "CCTV":
            objeto[0][1] = RLImage("static/img/seleccionador-check.png", width=15, height=15)
        elif tabla[0][8] == "INTERNET":
            objeto[1][1] = RLImage("static/img/seleccionador-check.png", width=15, height=15)
        else:
            objeto[2][1] = RLImage("static/img/seleccionador-check.png", width=15, height=15)
    
    if existe != 'si':
        servicio[3][1] = RLImage("static/img/seleccionador-check.png", width=15, height=15)
        
    datos_tabla_servicios = [
        [Table(servicio, style=estilo_tabla3, colWidths=[235, 30]), Table(objeto, style=estilo_tabla3, colWidths=[235, 30])]
    ]
    contenido.append(Table(datos_tabla_servicios, style=estilo_tabla4))
    contenido.append(Spacer(1, 7))
    
    estilo_tabla_notas = TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black),
                                    ('VALIGN', (0,0), (-1,-1), "MIDDLE"),
                                    ('BACKGROUND', (0,0), (0,0), colors.lemonchiffon)])
    
    cursor.execute(f"SELECT cantidad, material from hojas where material is not null and idfecha = '{idfecha}';")
    materiales = cursor.fetchall()
    if materiales:
            datos_tabla_materiales = [
                [Paragraph("<para align=center><b>Cantidad</b></para>", estilo_bold), Paragraph("<para align=center><b>Materiales</b></para>", estilo_bold)]
            ]
            for material in materiales:
                fila = [
                    Paragraph(str(material[0]), estilo_bold),
                    Paragraph(material[1], estilo_bold)
                ]
                datos_tabla_materiales.append(fila)
            contenido.append(Table(datos_tabla_materiales, style=estilo_tabla_materiales, colWidths=[60, 495]))
            contenido.append(Spacer(1, 10))
            if tabla[0][9]:
                datos_tabla_notas = [
                [Paragraph("<para align=center><b>Notas técnicas</b></para>", estilo_bold)],
                [Paragraph(f"{tabla[0][9]}", estilo_bold)]
            ]    
                contenido.append(Table(datos_tabla_notas, style=estilo_tabla_notas))
                contenido.append(Spacer(1, 10))
    else:
            datos_tabla_materiales = [
                [Paragraph("<para align=center><b>Cantidad</b></para>", estilo_bold), Paragraph("<para align=center><b>Materiales</b></para>", estilo_bold)],
                [],[],[],[],[],[],[]
            ]
            datos_tabla_notas = [
                [Paragraph("<para align=center><b>Notas técnicas</b></para>", estilo_bold)],
                [],[],[],[]
            ]
            contenido.append(Table(datos_tabla_materiales, style=estilo_tabla_materiales, colWidths=[60, 495]))
            contenido.append(Spacer(1, 10))
            contenido.append(Table(datos_tabla_notas, style=estilo_tabla_notas))
            contenido.append(Spacer(1, 10))

    datos_tabla_pagos = [
        [f"PRECIO TOTAL: ${str(tabla[0][10])}"],
        [f"ENGANCHE: ${str(tabla[0][11])}"],
        [f"SALDO RESTANTE: ${str(saldo_restante)}"]
    ]
    datos_tabla_fechas = []
    
    if tabla[0][12]:
        if tabla[0][12] == 'totalidad':
            datos_tabla_fechas.append([Paragraph("ABONÓ EN SU TOTALIDAD")])
        else:
            if tabla[0][13] or tabla[0][15]:
                if tabla[0][15]:
                    datos_tabla_fechas.append([Paragraph(f"PAGO #1: ${tabla[0][13]}. Vencimiento: {tabla[0][15]}")])
                else:
                    datos_tabla_fechas.append([Paragraph(f"PAGO #1: ${tabla[0][13]}. No tiene asignada una fecha de vencimiento.")])
            if tabla[0][16] or tabla[0][18]:
                if tabla[0][18]:
                    datos_tabla_fechas.append([Paragraph(f"PAGO #2: ${tabla[0][16]}. Vencimiento: {tabla[0][18]}")])
                else:
                    datos_tabla_fechas.append([Paragraph(f"PAGO #2: ${tabla[0][16]}. No tiene asignada una fecha de vencimiento.")])
            if tabla[0][19] or tabla[0][21]:
                if tabla[0][21]:
                    datos_tabla_fechas.append([Paragraph(f"PAGO #3: ${tabla[0][19]}. Vencimiento: {tabla[0][21]}")])
                else:
                    datos_tabla_fechas.append([Paragraph(f"PAGO #3: ${tabla[0][19]}. No tiene asignada una fecha de vencimiento.")])
            if tabla[0][22] or tabla[0][24]:
                if tabla[0][24]:
                    datos_tabla_fechas.append([Paragraph(f"PAGO #4: ${tabla[0][22]}. Vencimiento: {tabla[0][24]}")])
                else:
                    datos_tabla_fechas.append([Paragraph(f"PAGO #4: ${tabla[0][22]}. No tiene asignada una fecha de vencimiento.")])
    else:
        datos_tabla_fechas.append([Paragraph("NO SE HA CONFIRMADO NINGUNA FORMA DE PAGO")])
        
    tabla_acuerdos_pagos = [
        [Paragraph("<para align=center><b>Acuerdo de pago</b></para>", estilo_bold)],
        [Table(datos_tabla_pagos), Table(datos_tabla_fechas)],
        [Paragraph("En caso de que el cliente no cumpla con los pagos tenemos derecho a retirar los equipos instalados.", estilo_bold_italic)]
    ]
    contenido.append(Table(tabla_acuerdos_pagos, style=estilo_tabla_acuerdos))
    contenido.append(Spacer(1, 50))
    datos_tabla_firmas = [
        [Paragraph("<para align=center>_________________________</para>", estilo_bold), Paragraph("<para align=center>_________________________</para>", estilo_bold)],
        [Paragraph("<para align=center>Firma Técnico Responsable</para>"), Paragraph("<para align=center>Firma y Sello Cliente</para>")],
        [""],
        [Paragraph("<para align=center>TS NETWORK al lado del hotel Texas Inn Brownsville.</para>")],
        [Paragraph("<para align=center>845 N Expressway 77, Brownsville, TX 78520. (956) 640 6784.</para>")]
    ]
    contenido.append(Table(datos_tabla_firmas, style=estilo_tabla_firmas))
    #MÓDULO DE CARGA DE IMAGEN
    # Add the image from the database at the end
    if tabla[0][26]:  # Verificar si los datos de la imagen no están vacíos
        image_data = tabla[0][26]
        image = Image.open(io.BytesIO(image_data))
        # Tamaño máximo disponible en la página del PDF (considerando márgenes)
        page_width, page_height = A4
        margin = 15  # Márgenes de 15 unidades
        usable_width = page_width - 2 * margin
        usable_height = page_height - 2 * margin

        # Crear un frame personalizado para manejar el contenido
        frame = Frame(margin, margin, usable_width, usable_height, id='normal')

        # Crear el template de la página
        template = PageTemplate(id='Later', frames=[frame])

        # Crear el documento PDF con el template personalizado
        doc = BaseDocTemplate(pdf_filename, pagesize=A4, leftMargin=margin, rightMargin=margin, topMargin=margin, bottomMargin=margin, title=f"HOJA DE INSPECCIÓN N°{tabla[0][3]} - {tabla[0][4].strip()}")
        doc.addPageTemplates([template])

        # Añadir contenido antes de la imagen (si lo hay)
        contenido.append(Spacer(1, 70))  # Ejemplo de contenido

        # Redimensionar la imagen como antes, asegurándote de que encaje
        max_width, max_height = usable_width, usable_height
        width_ratio = max_width / image.width
        height_ratio = max_height / image.height
        resize_ratio = min(width_ratio, height_ratio)

        new_width = int(image.width * resize_ratio)
        new_height = int(image.height * resize_ratio)

        # Asegurarte de que la imagen no exceda el tamaño permitido
        if new_width > max_width or new_height > max_height:
            new_width = max_width
            new_height = max_height

        # Redimensionar la imagen
        image = image.resize((new_width, new_height), Image.LANCZOS)

        # Convertir la imagen PIL a un formato compatible con ReportLab
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # Crear la imagen para el PDF
        rl_image = RLImage(img_byte_arr, width=new_width, height=new_height)

        # Añadir la imagen al contenido del PDF
        contenido.append(rl_image)

    else:
        pass
    doc.build(contenido)
    cursor.close()
    return Response(status=200)
    
@app.route('/pdf')
def pdf():
    return render_template('pdf.html', pdf_filename="datos.pdf")

@app.route('/empresas/registrarllamada', methods=['GET', 'POST'])
@login_required
def registrarLlamada():
    if request.method == 'POST':
        empresa = request.form.get('empresa')
        nombre = request.form.get('nombre').strip().upper()
        telefono_sn = request.form.get('telefono')
        direccion = request.form.get('direccion').strip().upper().replace("'", '')
        email = request.form.get('email').replace(' ','').lower()
        nota = request.form.get('nota')
        if nota:
            nota = nota.replace('\n','.')
            nota = nota.strip().upper().replace("'", '´')
        else:
            nota = ''
        tarea = request.form.get('tarea')
        fechatarea = request.form.get('fechatarea')
        fecha_tarea = fechatarea[:10]
        hora_tarea = fechatarea[11:]
        telefono = ''
        for n in telefono_sn:
            if n.isdigit():
                telefono = telefono+n
        perfil = request.form.get('perfil')
        cursor = db.connection.cursor()
        cursor.execute(f"INSERT INTO registros (empresa, agente, nombre, telefono, direccion, email, motivo, fecha, tarea, fecha_tarea, hora_tarea, estado, perfil, nota_rechazo) VALUES ('{empresa}', '{current_user.fullname}', '{nombre}', '{telefono}', '{direccion}', '{email}', '{nota}', now(), {tarea}, '{fecha_tarea}', '{hora_tarea}', 'registro', '{perfil}', '');")
        #cursor.execute("INSERT INTO registros (empresa, agente, nombre, telefono, direccion, email, motivo, fecha, tarea, fecha_tarea, hora_tarea, estado) VALUES (%s, %s, %s, %s, %s, %s, %s, 'now()', %s, %s, %s, 'registro')", (empresa, current_user.fullname, nombre, telefono, direccion, email, nota, tarea, fecha_tarea, hora_tarea))
        
        if tarea == 0:
            cursor.execute(f"INSERT INTO movimientos (mov, date_mov, agente, nombre, telefono, datonuevo) VALUES ('Registró una llamada sin ninguna tarea asignada.', now(), '{current_user.fullname}', '{nombre}', '{telefono}', '{nota}')")
            #cursor.execute("INSERT INTO movimientos (mov, date_mov, agente, nombre, telefono, datonuevo) VALUES ('Registró una llamada sin ninguna tarea asignada.', 'now()', %s, %s, %s, %s)", (current_user.fullname, nombre, telefono, nota))
        else:
            cursor.execute(f"INSERT INTO movimientos (mov, date_mov, agente, nombre, telefono, datonuevo) VALUES ('Registró una llamada.', now(), '{current_user.fullname}', '{nombre}', '{telefono}', '{nota}')")
            #cursor.execute("INSERT INTO movimientos (mov, date_mov, agente, nombre, telefono, datonuevo) VALUES ('Registró una llamada.', 'now()', %s, %s, %s, %s)", (current_user.fullname, nombre, telefono, nota))
            
        #if num_preguntas != 0:
        #    for i in range(1, int(num_preguntas)+1):
        #        respuesta = request.form[f'respuesta{i}.0'].strip().upper()
        #        if respuesta != '':
        #            pregunta = request.form[f'pregunta{i}.0']
        #            cursor.execute(f"insert into registros (fecha, estado, pregunta, respuesta, telefono, cotizaciontotal) VALUES (now(), 'pregunta', '{pregunta}', '{respuesta}', '{telefono}', null)")
        if not fechatarea:
            cursor.execute(f"UPDATE registros SET fecha_tarea = null, hora_tarea = null WHERE fecha_tarea = '0000-00-00' AND hora_tarea = '';")
        db.connection.commit()
        cursor.close()
        return jsonify({'status': 'success', 'redireccion': None})
    
@app.route('/motivos/nuevo', methods=['GET', 'POST'])
@login_required
def agregarMotivo():  
    nuevom = request.form.get('nuevom') 
    cursor = db.connection.cursor()
    cursor.execute(f"INSERT INTO motivos VALUES ('{nuevom}')")
    db.connection.commit()
    cursor.close()
    return jsonify({'status': 'success'})

@app.route('/recordatorios/modificar/agente', methods=['GET', 'POST'])
@login_required
def cambiarAgenteRecordatorio():
    accion = request.form.get('accion')
    idfecha = request.form.get('idfecha')
    cursor = db.connection.cursor()
    if accion == 'agente':
        nuevo = request.form.get('nuevo')
        cursor.execute(f"UPDATE recordatorios SET agente = '{nuevo}' WHERE idtarea = '{idfecha}';")
    elif accion == 'realizado':
        cursor.execute(f"UPDATE recordatorios SET realizada = 1 WHERE idtarea = '{idfecha}';")
    db.connection.commit()
    cursor.close()
    return jsonify({'status': 'success', 'accion': accion})

@app.route('/recordatorios/nuevo', methods=['GET', 'POST'])
@login_required
def nuevoRecordatorio():
    #FORMDATA IMPRIMIR
    data = request.form
    for key, value in data.items():
        print(f"{key}: {value}")
    recordatorioid = request.form.get('recordatorioid')
    titulo = request.form.get('titulo').upper().strip()
    descripcion = request.form.get('descripcion').upper().strip()
    date = request.form.get('fecha').strip()
    if date:
        fecha = date[:10]
        hora = date[11:]
    else:
        fecha = None
        hora = None
    prioridad = request.form.get('prioridad')
    tipo = request.form.get('tipo')
    preaviso = request.form.get('preaviso')
    cursor = db.connection.cursor()
    if recordatorioid:
        #cursor.execute("UPDATE recordatorios SET titulo = %s, descripcion = %s, fecha_rec = %s, hora_rec = %s, prioridad =%s, tipo = %s, preaviso = %s WHERE idtarea = %s)", (titulo, descripcion, fecha, hora, prioridad, tipo, preaviso, recordatorioid))
        cursor.execute(f"UPDATE recordatorios SET titulo = '{titulo}', descripcion = '{descripcion}', fecha_rec = '{fecha}', hora_rec = '{hora}', prioridad = {int(prioridad)}, tipo = '{tipo}', preaviso = {int(preaviso)} WHERE idtarea = '{recordatorioid}';")
    else:
        cursor.execute("INSERT INTO recordatorios VALUES (now(), %s, %s, %s, %s, %s, %s, 0, %s, %s)", (titulo, descripcion, fecha, hora, prioridad, tipo, current_user.fullname, preaviso))
    db.connection.commit()
    cursor.close()
    return jsonify({'status': 'success', 'recordatorioid': recordatorioid})

@app.route('/motivos/eliminar', methods=['GET', 'POST'])
@login_required
def eliminarMotivo(): 
    eliminarm = request.form.get('eliminarm')  
    cursor = db.connection.cursor()
    cursor.execute(f"DELETE FROM motivos WHERE razon = '{eliminarm}';")
    db.connection.commit()
    cursor.close()
    return jsonify({'status': 'success'})

@app.route('/registros/editarregistro/actualizar', methods=['GET', 'POST'])
@login_required
def actualizarRegistro():
    if request.method == 'POST':
        cursor = db.connection.cursor()
        datonuevo = request.form.get('datonuevo').strip().upper()
        idfecha = request.form.get('idfecha')
        accion = request.form.get('accion')
        redireccion = request.form.get('redireccion')
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        #datoanterior = request.form.get('datoanterior')
        if accion == 'empresa':
            cursor.execute(f"UPDATE registros SET empresa = '{datonuevo}' WHERE fecha = '{idfecha}' and estado = 'registro';")
            cursor.execute(f"insert into movimientos (mov, date_mov, agente, nombre, telefono, datonuevo) values ('Cambió la empresa.', now(), '{current_user.fullname}', '{nombre}', '{telefono}', '{datonuevo}')")
        elif accion == 'agente':
            cursor.execute(f"UPDATE registros SET agente ='{datonuevo}' WHERE fecha = '{idfecha}' AND estado = 'registro';")
            cursor.execute(f"insert into movimientos (mov, date_mov, agente, nombre, telefono, datonuevo) values ('Cambió de agente.', now(), '{current_user.fullname}', '{nombre}', '{telefono}', '{datonuevo}')")
        elif accion == 'nombre':
            cursor.execute(f"UPDATE registros SET nombre = '{datonuevo}' WHERE estado = 'registro' AND fecha = '{idfecha}';")
            cursor.execute(f"insert into movimientos (mov, date_mov, agente, nombre, telefono, datonuevo) values ('Cambió el nombre.', now(), '{current_user.fullname}', '{nombre}', '{telefono}', '{datonuevo}')")
        elif accion == 'telefono':
            telefono = ''
            for n in datonuevo:
                if n.isdigit():
                    telefono = telefono+n
            cursor.execute(f"UPDATE registros SET telefono = '{telefono}' WHERE telefono = '{idfecha}';")
            cursor.execute(f"UPDATE movimientos SET telefono = '{telefono}' WHERE telefono = '{idfecha}';")
            cursor.execute(f"insert into movimientos (mov, date_mov, agente, nombre, telefono, datonuevo) values ('Cambió el  teléfono.', now(), '{current_user.fullname}', '{nombre}', '{telefono}', '{telefono}')")
        elif accion == 'direccion':
            cursor.execute(f"UPDATE registros SET direccion = '{datonuevo}' WHERE estado = 'registro' and FECHA = '{idfecha}';")
            cursor.execute(f"insert into movimientos (mov, date_mov, agente, nombre, telefono, datonuevo) values ('Cambió la dirección.', now(), '{current_user.fullname}', '{nombre}', '{telefono}', '{datonuevo}')")
        elif accion == 'email':
            cursor.execute(f"UPDATE registros SET email = '{datonuevo.lower().strip()}' WHERE estado = 'registro' AND fecha = '{idfecha}';")
            cursor.execute(f"insert into movimientos (mov, date_mov, agente, nombre, telefono, datonuevo) values ('Cambió el email.', now(), '{current_user.fullname}', '{nombre}', '{telefono}', '{datonuevo}')")
        elif accion == 'nota':
            cursor.execute(f"UPDATE registros SET motivo = '{datonuevo}' WHERE fecha = '{idfecha}' AND estado = 'registro';")
            cursor.execute(f"insert into movimientos (mov, date_mov, agente, nombre, telefono, datonuevo) values ('Cambió la nota de la llamada.', now(), '{current_user.fullname}', '{nombre}', '{telefono}', '{datonuevo}')")
        elif accion == 'razon de desinteres':
            cursor.execute(f"UPDATE registros SET tarea = 2, nota_rechazo = '{datonuevo}' WHERE fecha = '{idfecha}' AND estado = 'registro';")
            cursor.execute(f"insert into movimientos (mov, date_mov, agente, nombre, telefono, datonuevo) values ('Cambió la tarea del registro. NO LE INTERESÓ.', now(), '{current_user.fullname}', '{nombre}', '{telefono}', '{datonuevo}')")
        elif accion == 'telefono sin registrar':
            telefono = ''
            for n in datonuevo:
                if n.isdigit():
                    telefono = telefono+n
            cursor.execute(f"UPDATE registros SET telefono = '{telefono}' WHERE fecha = '{idfecha}';")
            cursor.execute(f"insert into movimientos (mov, date_mov, agente, nombre, telefono, datonuevo) values ('Agregó el número de teléfono.', now(), '{current_user.fullname}', '{nombre}', '{telefono}', '{telefono}')")
        else:
            if datonuevo:
                datonuevo = datonuevo.upper().strip().replace('\n', ' ')
            else:
                datonuevo = ''
            cursor.execute(f"UPDATE registros SET motivo = '{datonuevo}', tarea = {redireccion}, fecha_tarea = '{accion[:10]}', hora_tarea = '{accion[11:]}' WHERE fecha = '{idfecha}' AND estado = 'registro';")
            cursor.execute(f"insert into movimientos (mov, date_mov, agente, nombre, telefono, datonuevo) values ('Realizó cambios en la tarea y su fecha.', now(), '{current_user.fullname}', '{nombre}', '{telefono}', '{datonuevo}')")
            redireccion = None
        db.connection.commit()
        cursor.close()
    return jsonify({'status': 'success', 'redireccion': redireccion})

@app.route('/cotizacion', methods=['GET', 'POST'])
@login_required
def enviarCotizacion():
    if request.method == 'POST':
        nombre = request.form['nombre'].upper()
        email = request.form['email'].lower()
        fecha = request.form['fecha']
        cotizacion = request.form['cotizacion'].upper()
        totalcotizacion = request.form['cotizaciontotal']
        #TODO CONFIGURAR PARA ENVIAR CORREO
        port = 587
        smtp_server = "smtp.gmail.com"
        sender_email = ""
        receiver_email = email
        password = ""
        message = f"""
        Subject: Cotización - Los Andes

        {nombre} desde el equipo de ventas de Los Andes le agradecemos por comunicarse y estar interesado por nuestros servicios.
        A continuación le enviamos una cotización solicitada y especialmente adaptada por un agente para que usted pueda tener la experiencia deseada y que sumamente satisfecho contratando nuestros servicios.
        
        {cotizacion}
        El precio final de esta cotización sería de ${totalcotizacion}
        
        No dude en aprovechar este precio especial ya que es por tiempo limitado.
        Estamos a su servicio. Un coordial saludo.
        
        Los Andes.
        """
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
        
        cursor = db.connection.cursor()
        cursor.execute(f"SELECT idtarea from tareas where tarea = 'COTIZACIÓN ENVIADA'")
        cotizacion_enviada = cursor.fetchone()
        cursor.execute('select cast(substring(date_add(current_time(), interval -5 hour), 1, 2) as unsigned);')
        hora_actual = cursor.fetchone()
        cursor.execute(f"UPDATE registros SET nombre = '{nombre}', email = '{email}', cotizacion = '{cotizacion}', cotizaciontotal = {totalcotizacion}, fecha_tarea = current_date(), tarea = {cotizacion_enviada[0]}, hora_tarea =  '{hora_actual[0]}:00 h' where fecha = '{fecha}' and estado = 'registro';")
        #cursor.execute(f"insert into movimientos (mov, date_mov) VALUES ('{current_user.fullname} envío una cotización de ${totalcotizacion} a {email} del cliente {nombre}', now())")
        db.connection.commit()
        cursor.close()
    return Response(status=204)

@app.route('/tareas', methods=['GET', 'POST'])
@login_required
def tareas():
    cursor = db.connection.cursor()
    cursor.execute("SELECT * from tareas where idtarea!= 0 order by idtarea asc")
    tareas = cursor.fetchall()
    return render_template('tareas.html', tareas=tareas)

@app.route('/tareas/altatarea', methods=['GET', 'POST'])
@login_required
def altaTarea():
    if request.method == 'POST':
        tarea  = request.form['tarea'].upper().replace('\n','').strip()
        cursor = db.connection.cursor()
        cursor.execute(f"insert into tareas (tarea) values ('{tarea}');")
        cursor.execute(f"insert into movimientos (mov, date_mov, agente, datonuevo) values ('Agregó una nueva tarea al sistema.', now(), '{current_user.fullname}', '{tarea}');")
        db.connection.commit()
        cursor.close()
        return redirect(url_for('tareas'))
    return Response(status=204)

@app.route('/tareas/eliminartarea', methods=['GET', 'POST'])
@login_required
def bajaTarea():
    if request.method == 'POST':
        idtarea  = request.form['eliminar']
        tarea = request.form['desc_tarea'].strip()
        cursor = db.connection.cursor()
        cursor.execute(f"update registros set tarea = 0 where tarea = {idtarea} and estado = 'registro';")
        cursor.execute(f"delete from tareas where idtarea = {idtarea};")
        cursor.execute(f"insert into movimientos (mov, date_mov, agente, datonuevo) values ('Eliminó una tarea del sistema.', now(), '{current_user.fullname}', '{tarea}');")
        db.connection.commit()
        cursor.close()
        return redirect(url_for('tareas'))
    return Response(status=204)

@app.route('/tareas/editartarea', methods=['GET', 'POST'])
@login_required
def modTarea():
    if request.method == 'POST':
        idtarea = request.form['idtarea']
        tareanueva = request.form['tareanueva'].replace('\n','').strip().upper()
        cursor = db.connection.cursor()
        cursor.execute(f"update tareas set tarea = '{tareanueva}' where idtarea = {idtarea};")
        cursor.execute(f"insert into movimientos (mov, date_mov, agente, datonuevo) VALUES ('Cambió una tarea del sistema.', now(), '{current_user.fullname}','{tareanueva}');")
        db.connection.commit()
        cursor.close()
        return redirect(url_for('tareas'))
    return Response(status=204)

@app.route('/hojas/imagenes/<string:idhoja>')
@login_required
def mostrar_mapa(idhoja):
    cursor = db.connection.cursor()
    cursor.execute(f"SELECT mapa FROM hojas WHERE idhoja = {idhoja} and cantidad is null;")
    imagen_data = cursor.fetchone()[0]
    if imagen_data:
        return send_file(BytesIO(imagen_data), mimetype='image/jpeg')

@app.route('/hoja_de_inspeccion', methods=['GET', 'POST'])
@login_required
def hoja():
    if request.method == 'POST':
        fecha = request.form['eliminar']
        cursor = db.connection.cursor()
        cursor.execute(f"SELECT count(*) from hojas where idfecha = '{fecha}' and cantidad is null and material is null group by idfecha;")
        condicional = cursor.fetchone()
        if condicional == None:
            condicional = 0
        else:
            condicional = int(condicional[0])
        if condicional != 0:
            cursor.execute(f"SELECT LPAD( idhoja, 8, '0') from hojas where idfecha = '{fecha}' and cantidad is null and material is null;")
            n_hoja = cursor.fetchone()
            cursor.execute(f"SELECT fecha_emision, nombre, direccion, telefono, servicio, objeto, notas, total, enganche, total-enganche, idfecha, tipopago, acuerdo_1, interes_1, fecha_1, acuerdo_2, interes_2, fecha_2, acuerdo_3, interes_3, fecha_3, acuerdo_4, interes_4, fecha_4, notapago, COALESCE(acuerdo_1, 0)+COALESCE(acuerdo_2, 0)+COALESCE(acuerdo_3, 0)+COALESCE(acuerdo_4, 0), empresa, mapa from hojas where idfecha = '{fecha}' and cantidad is null and material is null;")
            hoja = cursor.fetchone()
            cursor.execute(f"SELECT count(*) from hojas where idfecha = '{fecha}' and cantidad is not null and material is not null")
            n_materiales = cursor.fetchone()
            n_materiales = n_materiales[0]
            cursor.execute(f"SELECT cantidad, material from hojas where idfecha = '{fecha}' and cantidad is not null and material is not null")
            materiales = cursor.fetchall()
            cursor.execute(f"select count(acuerdo_1)+count(acuerdo_2)+count(acuerdo_3)+count(acuerdo_4) from hojas where idfecha = '{fecha}' and cantidad is null and material is null;")
            n_cuotas = cursor.fetchone()
            n_cuotas = n_cuotas[0]
        else:
            empresa = request.form['empresa']
            cursor.execute("SELECT LPAD( idhoja+1, 8, '0') from hojas where cantidad is null and material is null order by idhoja desc limit 1;")
            n_hoja = cursor.fetchone()
            n_materiales = 0
            cursor.execute(f"SELECT current_date(), nombre, direccion, telefono, '', '', '', 0, 0, '', fecha, '', '', '', '','','','','','','','','','','','', '{empresa}', null from registros where fecha = '{fecha}' and estado = 'registro';")
            hoja = cursor.fetchone()
            materiales = None
            n_cuotas = 0
        cursor.close()
        return render_template('hojainspeccion.html', condicional=condicional, hoja=hoja, materiales=materiales, n_hoja=n_hoja, n_materiales=n_materiales, n_cuotas=n_cuotas)
    return Response(status=204)

@app.route('/hoja_de_inspeccion/guardar', methods=['POST'])
@login_required
def guardar_en_mysql():
    data = request.form
    #tabla_data = data['materiales']
    #datos_data = data['datos']
    tabla_data = json.loads(data['materiales'])
    datos_data = json.loads(data['datos'])
    #accion_data = data['accion']
    accion_data = json.loads(data['accion'])
    telefono_sn = datos_data[5]
    telefono = ''
    for n in telefono_sn:
        if n.isdigit():
            telefono = telefono+n
    cursor = db.connection.cursor()
    for r in range (12, 24):
        if datos_data[r] == '':
            datos_data[r] = 'null'
    movimiento = "creó una nueva"
    
    condicional_mapa = data['condicional_mapa']
    if condicional_mapa == 'nada':
        cursor.execute("UPDATE hojas SET fecha_emision = %s, nombre = %s, direccion = %s, telefono = %s, servicio = %s, objeto = %s, notas = %s, total = %s, enganche = %s, tipopago = %s, acuerdo_1 = %s, interes_1 = %s, fecha_1 = %s, acuerdo_2 = %s, interes_2 = %s, fecha_2 = %s, acuerdo_3 = %s, interes_3 = %s, fecha_3 = %s, acuerdo_4 = %s, interes_4 = %s, fecha_4 = %s, notapago = %s, empresa = %s WHERE idhoja = %s and idfecha = %s and cantidad is null", (datos_data[2],datos_data[3].upper().strip(), datos_data[4].upper().strip(), telefono, datos_data[6], datos_data[7].upper().strip(), datos_data[8].upper().strip(), datos_data[9], datos_data[10], datos_data[11], datos_data[12], datos_data[13], datos_data[14], datos_data[15], datos_data[16], datos_data[17], datos_data[18], datos_data[19], datos_data[20], datos_data[21], datos_data[22], datos_data[23], datos_data[24].strip().upper(), datos_data[25].strip().upper(), datos_data[0], datos_data[1]))
        cursor.execute(f"DELETE from hojas where idhoja = '{datos_data[0]}' and idfecha = '{datos_data[1]}' and cantidad is not null")
    elif condicional_mapa == 'eliminar':
        if accion_data == 'actualizar':
            cursor.execute(f"DELETE from hojas where idhoja = '{datos_data[0]}' and idfecha = '{datos_data[1]}'")
            movimiento = "actualizó la"
        cursor.execute("INSERT INTO hojas (idhoja, idfecha, fecha_emision, nombre, direccion, telefono, servicio, objeto, notas, total, enganche, tipopago, acuerdo_1, interes_1, fecha_1, acuerdo_2, interes_2, fecha_2, acuerdo_3, interes_3, fecha_3, acuerdo_4, interes_4, fecha_4, notapago, empresa) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (datos_data[0], datos_data[1], datos_data[2], datos_data[3].upper().strip(), datos_data[4].upper().strip(), telefono, datos_data[6], datos_data[7].upper().strip(), datos_data[8].upper().strip(), datos_data[9], datos_data[10], datos_data[11], datos_data[12], datos_data[13], datos_data[14], datos_data[15], datos_data[16], datos_data[17], datos_data[18], datos_data[19], datos_data[20], datos_data[21], datos_data[22], datos_data[23], datos_data[24].strip().upper(), datos_data[25].strip().upper()))
    else:
        if accion_data == 'actualizar':
            cursor.execute(f"DELETE from hojas where idhoja = '{datos_data[0]}' and idfecha = '{datos_data[1]}'")
            movimiento = "actualizó la"
        archivo = request.files['mapa']
        contenido = archivo.read()
        cursor.execute("INSERT INTO hojas (idhoja, idfecha, fecha_emision, nombre, direccion, telefono, servicio, objeto, notas, total, enganche, tipopago, acuerdo_1, interes_1, fecha_1, acuerdo_2, interes_2, fecha_2, acuerdo_3, interes_3, fecha_3, acuerdo_4, interes_4, fecha_4, notapago, empresa, mapa) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (datos_data[0], datos_data[1], datos_data[2], datos_data[3].upper().strip(), datos_data[4].upper().strip(), telefono, datos_data[6], datos_data[7].upper().strip(), datos_data[8].upper().strip(), datos_data[9], datos_data[10], datos_data[11], datos_data[12], datos_data[13], datos_data[14], datos_data[15], datos_data[16], datos_data[17], datos_data[18], datos_data[19], datos_data[20], datos_data[21], datos_data[22], datos_data[23], datos_data[24].strip().upper(), datos_data[25].strip().upper(), contenido))
    #cursor.execute(f"INSERT INTO hojas (idhoja, idfecha, fecha_emision, nombre, direccion, telefono, servicio, objeto, notas, total, enganche, tipopago, acuerdo_1, interes_1, fecha_1, acuerdo_2, interes_2, fecha_2, acuerdo_3, interes_3, fecha_3, acuerdo_4, interes_4, fecha_4, notapago, empresa, mapa) VALUES ({datos_data[0]}, '{datos_data[1]}', '{datos_data[2]}', '{datos_data[3].upper().strip()}', '{datos_data[4].upper().strip()}', '{telefono}', '{datos_data[6]}', '{datos_data[7].upper().strip()}', '{datos_data[8].upper().strip()}', {datos_data[9]}, {datos_data[10]}, '{datos_data[11]}', {datos_data[12]}, {datos_data[13]}, '{datos_data[14]}', {datos_data[15]}, {datos_data[16]}, '{datos_data[17]}', {datos_data[18]}, {datos_data[19]}, '{datos_data[20]}', {datos_data[21]}, {datos_data[22]}, '{datos_data[23]}', '{datos_data[24].strip().upper()}', '{datos_data[25].strip().upper()}', {datos_data[26]}, '{contenido}')")
    cursor.execute("UPDATE hojas SET fecha_1 = null, acuerdo_1 = null, interes_1 = null, fecha_2 = null, acuerdo_2 = null, interes_2 = null, fecha_3 = null, acuerdo_3 = null, interes_3 = null, fecha_4 = null, acuerdo_4 = null, interes_4 = null where tipopago = 'totalidad' or tipopago = '';")
    for f in range (1,5):
        cursor.execute(f"UPDATE hojas SET fecha_{f} = null, acuerdo_{f} = null, interes_{f} = null where fecha_{f} = '0000-00-00' or fecha_{f} is null;")
    for row in tabla_data:
            if row != [] and row != ['', '']:
                cursor.execute(f"INSERT INTO hojas (idhoja, idfecha, cantidad, material) VALUES ({datos_data[0]}, '{datos_data[1]}', {row[0]}, '{row[1].upper().strip()}')")
    if datos_data[11] == 'totalidad': #and accion_data != 'actualizar':
        cursor.execute(f"INSERT INTO pagos (empresa, motivo, idhoja, cliente, telefono, fecha_vencimiento, fecha_pago, forma_pago, pago, agente) VALUES ('{datos_data[25].strip().upper()}', 'ABONÓ TODO', {datos_data[0]}, '{datos_data[3].upper(). strip()}', '{telefono}', '{datos_data[2]}', '{datos_data[2]}', '{datos_data[26].upper().strip()}', {datos_data[9]}, '{current_user.fullname}');")
        cursor.execute(f"UPDATE hojas SET total = 0 WHERE idhoja = '{datos_data[0]}' and idfecha = '{datos_data[1]}' and cantidad is not null")
        cursor.execute(f"insert into movimientos (mov, date_mov, agente, datonuevo) VALUES ('{movimiento.capitalize()} hoja de inspección que abonó en su totalidad. Dicho pago fue registrado en la sección ´Pagos´.', now(), '{current_user.fullname}', 'N°{datos_data[0]}');")
    cursor.execute(f"insert into movimientos (mov, date_mov, agente, datonuevo) VALUES ('{movimiento.capitalize()} hoja de inspección.', now(), '{current_user.fullname}', 'N°{datos_data[0]}');")
    db.connection.commit()
    cursor.close()
    return redirect(url_for('registros'))

@app.route('/impulsos')
@login_required
def impulsos():
    cursor = db.connection.cursor()
    cursor.execute("SELECT * from impulsos order by fecha_registro")
    impulsos = cursor.fetchall()
    cursor.execute("select empresa from clientes order by empresa")
    empresas = cursor.fetchall()
    cursor.close()
    return render_template('impulsos.html', impulsos=impulsos, empresas=empresas)

def pagina_no_encontrada(error):
    return render_template('error404.html'), 404

def pagina_no_autorizada(error):
    return render_template('error401.html'), 401

app.config.from_object(config['development'])
app.register_error_handler(401, pagina_no_autorizada)
app.register_error_handler(404, pagina_no_encontrada)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
    #
    #app.config.from_object(config['development'])
    #app.register_error_handler(401, pagina_no_autorizada)
    #app.register_error_handler(404, pagina_no_encontrada)
    #app.run(debug=False)
    #app.run(debug=False, port=30358, host='admin.losandestx.com')
    #app.run(host='0.0.0.0', port=80, debug=True)