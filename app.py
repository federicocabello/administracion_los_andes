from flask import Flask, render_template, request, redirect, url_for, flash, Response, send_file
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_required, logout_user, login_user, current_user, UserMixin
from config import config
from io import BytesIO
import datetime as dt
import base64
import io
import os
import zipfile
import smtplib, ssl
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
    cursor.execute(f"insert into movimientos (mov, date_mov) VALUES ('{current_user.fullname} cerró sesión', now())")
    db.connection.commit()
    cursor.close()
    logout_user()
    return redirect(url_for('login'))

@app.route('/menu', methods=['GET', 'POST'])
@login_required
def abrirMenu():
    if request.method == 'POST':
        empresa = request.form['menuempresa'].replace(' ','_')
        cursor = db.connection.cursor()
        sql = f"SELECT articulo, precio, art_descripcion, imagen FROM {empresa} where articulo is not null"
        cursor.execute(sql)
        articulos = cursor.fetchall()
        cursor.execute(f"SELECT imagen from {empresa} where articulo is not null")
        registros = cursor.fetchall()      
        for registro in registros:
                archivo_zip = registro[0]
                images = []
                if archivo_zip != None:
                    zip_buffer = io.BytesIO(archivo_zip)
                    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
                        for name in zip_file.namelist():
                            with zip_file.open(name) as file:
                                images.append(base64.b64encode(file.read()).decode('utf-8'))
        sql = f"SELECT speech,descripcion FROM {empresa} WHERE speech is not null"
        cursor.execute(sql)
        speech = cursor.fetchall()
        sql = f"select nombre, telefono, motivo, tareas.tarea, fecha_tarea, fecha, agente from registros JOIN tareas ON tareas.idtarea=registros.tarea WHERE estado = 'pendiente' AND empresa = '{empresa.replace('_',' ')}' and agente = '{current_user.fullname}' order by fecha asc limit 10;"
        cursor.execute(sql)
        pendientes = cursor.fetchall()
        cursor.execute("select * from tareas where idtarea != 0")
        tareas = cursor.fetchall()
        cursor.execute("select * from calendario order by date asc")
        calendario = cursor.fetchall()
        #print(calendario[0][0])
        #print(dt.date.today())
        if dt.date.today() == calendario[0][0]:
            cursor.execute("delete from calendario;")
            for i in range (1,18):
                cursor.execute(f"insert into calendario values (date_add(current_date(), interval {i} day), DATE_FORMAT(date_add(current_date(), interval {i} day), '%W %e'))")
                cursor.execute("delete from calendario where date_format like 'Sunday%'")
        cursor.execute("SELECT fullname from auth order by fullname asc")
        agentes = cursor.fetchall()
        db.connection.commit()
        return render_template('menu.html', empresa=empresa.replace('_', ' '), articulos=articulos, speech=speech, pendientes=pendientes, tareas=tareas, calendario=calendario, registros=registros, agentes=agentes)
    return Response(status=204)

@app.route('/menu/preguntasfrecuentes', methods=['GET', 'POST'])
@login_required
def abrirPreguntasFrecuentes():
    if request.method == 'POST':
        empresa = request.form['menuempresa'].replace(' ','_')
        cursor = db.connection.cursor()
        sql = f"SELECT speech,descripcion FROM {empresa} WHERE speech is not null"
        cursor.execute(sql)
        speech = cursor.fetchall()
        sql = f"select nombre, telefono, motivo, tareas.tarea, fecha_tarea, fecha, agente from registros JOIN tareas ON tareas.idtarea=registros.tarea WHERE estado = 'pendiente' AND empresa = '{empresa.replace('_',' ')}' and agente = '{current_user.fullname}' order by fecha asc limit 10;"
        cursor.execute(sql)
        pendientes = cursor.fetchall()
        cursor.execute("select * from tareas where idtarea != 0")
        tareas = cursor.fetchall()
        cursor.execute("select * from calendario order by date asc")
        calendario = cursor.fetchall()
        #print(calendario[0][0])
        #print(dt.date.today())
        if dt.date.today() == calendario[0][0]:
            cursor.execute("delete from calendario;")
            for i in range (1,18):
                cursor.execute(f"insert into calendario values (date_add(current_date(), interval {i} day), DATE_FORMAT(date_add(current_date(), interval {i} day), '%W %e'))")
                cursor.execute("delete from calendario where date_format like 'Sunday%'")
        db.connection.commit()
        cursor.execute(f"select pregunta, (@row := @row + 1) as contador from {empresa}, (SELECT @row := 0) r where pregunta is not null")
        preguntas = cursor.fetchall()
        cursor.execute("SELECT fullname from auth order by fullname")
        agentes = cursor.fetchall()
        return render_template('preguntasfrecuentes.html', empresa=empresa.replace('_', ' '), speech=speech, pendientes=pendientes, tareas=tareas, calendario=calendario, preguntas=preguntas, agentes=agentes)
    return Response(status=204)

@app.route('/imagenes/<string:cliente>')
@login_required
def mostrar_logo(cliente):
    cursor = db.connection.cursor()
    cursor.execute(f"SELECT logo FROM clientes where empresa = '{cliente}'")
    #cursor.execute("SELECT imagen FROM clientenuevo WHERE articulo = %s", (articulo,))
    imagen_data = cursor.fetchone()[0]
    if imagen_data:
        return send_file(BytesIO(imagen_data), mimetype='image/jpeg')

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
        sql = f"DELETE FROM auth WHERE user = '{usuario}'"
        cursor.execute(sql)
        db.connection.commit()
        sql = f"INSERT INTO auth VALUES ('{usuario}', '{password}', '{fullname}', '{rol}')"
        cursor.execute(sql)
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} modificó al usuario {usuario.upper()}',now())")
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

@app.route('/clientes/gestioncliente', methods=['GET', 'POST'])
@login_required
def gestionCliente():
    if request.method == 'POST':
        usuario = request.form['eliminar']
        cursor = db.connection.cursor()
        sql = f"SELECT * FROM clientes WHERE empresa = '{usuario}';"
        cursor.execute(sql)
        cliente = cursor.fetchall()
        sql = f"select articulo, precio, art_descripcion, imagen from {usuario.replace(' ','_')} where articulo is not null;"
        cursor.execute(sql)
        articulos = cursor.fetchall()
        sql = f"SELECT speech, descripcion from {usuario.replace(' ','_')} where speech is not null;"
        cursor.execute(sql)
        speech = cursor.fetchall()
        sql = f"SELECT idplan, plan from planes where idplan != 0;"
        cursor.execute(sql)
        planes = cursor.fetchall()
        #cursor.execute(f"SELECT imagen from {usuario.replace(' ', '_')} where articulo is not null")
        cursor.execute(f"SELECT pregunta from {usuario.replace(' ','_')} where pregunta is not null")
        preguntas = cursor.fetchall()
        return render_template('modcliente.html', cliente=cliente, articulos=articulos, speech=speech, planes=planes, preguntas=preguntas)
    return redirect(url_for('clientes'))

@app.route('/imagenes/articulo/<string:articulo>/<string:empresa>')
@login_required
def mostrar_imagen_art(articulo, empresa):
    cursor = db.connection.cursor()
    cursor.execute(f"SELECT imagen FROM {empresa.replace(' ','_')} where articulo = '{articulo}'")
    archivo_zip = cursor.fetchone()[0]
    zip_buffer = io.BytesIO(archivo_zip)
    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        images = []
        for name in zip_file.namelist():
            with zip_file.open(name) as file:
                #images.append(base64.b64encode(file.read()).decode('utf-8'))
                return send_file(io.BytesIO(file.read()), mimetype='image/jpeg')
                #return send_file(images, mimetype="image/jpeg")

@app.route('/usuarios/eliminarusuario', methods=['GET', 'POST'])
@login_required
def eliminarUsuario():
    if request.method == 'POST':
        eliminar = request.form['eliminar']
        cursor = db.connection.cursor()
        sql = f"DELETE FROM auth where user = '{eliminar}'"
        cursor.execute(sql)
        cursor.execute(f"INSERT INTO movimientos (mov, date_mov) VALUES ('{current_user.fullname} eliminó al usuario {eliminar.upper()}', now());")
        db.connection.commit()
        cursor.close()
    return redirect(url_for('usuarios'))

@app.route('/clientes/gestioncliente/eliminararticulo', methods=['GET', 'POST'])
@login_required
def eliminarArticulo():
    if request.method == 'POST':
        empresa = request.form['empresanueva']
        articuloeliminado = request.form['articuloeliminado']
        cursor = db.connection.cursor()
        sql = f"DELETE FROM {empresa.replace(' ','_')} where articulo = '{articuloeliminado}';"
        cursor.execute(sql)
        db.connection.commit()
        cursor.close()
    return Response(status=204)
        
@app.route('/clientes/gestioncliente/eliminarspeech', methods=['GET', 'POST'])
@login_required
def eliminarSpeech():
    if request.method == 'POST':
        empresa = request.form['empresanueva']
        speecheliminado = request.form['speecheliminado']
        cursor = db.connection.cursor()
        sql = f"DELETE FROM {empresa.replace(' ','_')} where speech = '{speecheliminado}';"
        cursor.execute(sql)
        db.connection.commit()
        cursor.close()
    return Response(status=204)

@app.route('/clientes/gestioncliente/eliminarpregunta', methods=['GET', 'POST'])
@login_required
def eliminarPregunta():
    if request.method == 'POST':
        empresa = request.form['empresanueva']
        preguntaeliminada = request.form['preguntaeliminada']
        cursor = db.connection.cursor()
        sql = f"DELETE FROM {empresa.replace(' ','_')} where pregunta = '{preguntaeliminada}';"
        cursor.execute(sql)
        db.connection.commit()
        cursor.close()
    return Response(status=204)

@app.route('/clientes/gestioncliente/editarcliente', methods=['GET', 'POST'])
@login_required
def editarCliente():
    if request.method == 'POST':
        empresa = request.form['empresa'].upper().strip()
        nombre = request.form['persona'].upper()
        direccion = request.form['direccion'].upper()
        telefono = request.form['telefono']
        email = request.form['email'].lower()
        vende = request.form['vende'].upper()
        plan = request.form['plan']
        nombreviejo = request.form['empresanueva']
        logos_file = request.files.getlist('logo[]')
        logos_data = [logo_file.read() if logo_file else None for logo_file in logos_file]
        fichainterna = request.form['fichainterna'].upper().strip()
        pdf = request.files['pdf']
        c_base64 = base64.b64encode(pdf.read()).decode('utf-8')
        cursor = db.connection.cursor()
        sql = f"ALTER TABLE {nombreviejo.replace(' ','_')} RENAME TO {empresa.replace(' ','_')};"
        cursor.execute(sql)
        db.connection.commit()
        if logos_data and c_base64:
            sql = f"UPDATE clientes SET empresa = %s, logo = %s, nombre = %s, direccion = %s, telefono = %s, email = %s, vende = %s, plan = %s, plan_fichainterna = %s, contrato = %s WHERE empresa = '{nombreviejo}';"
            valores = [(empresa, logo_data, nombre, direccion, telefono, email, vende, plan, fichainterna, c_base64) for logo_data in logos_data]
        if logos_data and c_base64 == '':
            sql = f"UPDATE clientes SET empresa = %s, logo = %s, nombre = %s, direccion = %s, telefono = %s, email = %s, vende = %s, plan = %s, plan_fichainterna = %s WHERE empresa = '{nombreviejo}';"
            valores = [(empresa, logo_data, nombre, direccion, telefono, email, vende, plan, fichainterna) for logo_data in logos_data]
        if logos_data == '' and c_base64:
            sql = f"UPDATE clientes SET empresa = %s, nombre = %s, direccion = %s, telefono = %s, email = %s, vende = %s, plan = %s, plan_fichainterna = %s, contrato = %s WHERE empresa = '{nombreviejo}';"
            valores = [(empresa, nombre, direccion, telefono, email, vende, plan, fichainterna, c_base64)]
        if logos_data == '' and c_base64 == '':
            sql = f"UPDATE clientes SET empresa = %s, nombre = %s, direccion = %s, telefono = %s, email = %s, vende = %s, plan = %s, plan_fichainterna = %s WHERE empresa = '{nombreviejo}';"
            valores = [(empresa, nombre, direccion, telefono, email, vende, plan, fichainterna)]
        cursor.executemany(sql, valores)
        db.connection.commit()
        if empresa != nombreviejo:
            cursor.execute(f"insert into movimientos (mov, date_mov) VALUES ('{current_user.fullname} modificó al cliente {nombreviejo.replace('_', ' ')}. Ahora es {empresa.replace('_',' ')}', now())")
        num_art = int(request.form['n_articulos'])
        num_esp = int(request.form['n_espacios'])
        num_preg = int(request.form['n_preguntas'])
        
        if num_art != 0:
            cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} agregó {num_art} artículos al cliente {empresa.replace('_', ' ')}', now())")
            for i in range(1, num_art+1):
                articulo = request.form[f'art{i}'].upper()
                precio = request.form[f'precio{i}']
                art_descripcion = request.form[f'art_descripcion{i}']
                files = request.files.getlist(f'imagenes{i}[]')
                if str(files) == "[<FileStorage: '' ('application/octet-stream')>]":
                    sql = f"INSERT INTO {empresa.replace(' ','_')} VALUES ('{articulo}', {precio}, '{art_descripcion}', null, null, null, null)"
                    cursor.execute(sql)
                else:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                        for file in files:
                            zip_file.writestr(file.filename, file.read())
                    cursor.execute(f"INSERT INTO {empresa.replace(' ','_')} VALUES ('{articulo}', {precio}, '{art_descripcion}', %s, null, null, null)", (zip_buffer.getvalue(),))
                
        if num_esp != 0:
            cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} agregó {num_esp} espacios de trabajo al cliente {empresa}', now())")
            for i in range(1, num_esp+1):
                speech = request.form[f'speech{i}'].upper()
                desc = request.form[f'desc{i}']
                sql = f"INSERT INTO {empresa.replace(' ','_')} VALUES (null, null, null, null, '{speech}', '{desc}', null)"
                cursor.execute(sql)
                
        if num_preg != 0:
            cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} agregó {num_preg} preguntas al cliente {empresa}', now())")
            for i in range(1, num_preg+1):
                pregunta = request.form[f"pregunta{i}"].upper().strip().replace('?', '').replace('¿','')
                cursor.execute(f"INSERT INTO {empresa.replace(' ','_')} VALUES (null, null, null, null, null, null, '¿{pregunta}?')")
        
        cursor.execute(f"UPDATE registros SET empresa = '{empresa}' where empresa = '{nombreviejo}'") 
        db.connection.commit()
        cursor.close()
    return redirect(url_for('dashboard'))  

@app.route('/clientes/eliminarcliente', methods=['GET', 'POST'])
@login_required
def eliminarCliente():
    if request.method == 'POST':
        eliminar = request.form['eliminar']
        cursor = db.connection.cursor()
        sql = f"DELETE FROM clientes where empresa = '{eliminar}';"
        cursor.execute(sql)
        db.connection.commit()
        sql = f"DROP TABLE {eliminar.replace(' ','_')};"
        cursor.execute(sql)
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} eliminó al cliente {eliminar.replace('_',' ')}',now())")
        db.connection.commit()
        cursor.close()
    return redirect(url_for('clientes'))

@app.route('/clientes/nuevocliente', methods=['GET', 'POST'])
@login_required
def altaCliente():
    if request.method == 'POST':
        empresa = request.form['empresa'].upper().strip().replace(' ','_')
        logos_file = request.files.getlist('logo[]')
        logos_data = [logo_file.read() if logo_file else None for logo_file in logos_file]
        persona = request.form['persona'].upper()
        direccion = request.form['direccion'].upper()
        telefono = request.form['telefono']
        email = request.form['email'].lower()
        vende = request.form['vende'].upper()
        plan = request.form['plan']
        fichainterna = request.form['fichainterna'].upper().strip()
        pdf = request.files['pdf']
        c_base64 = base64.b64encode(pdf.read()).decode('utf-8')
        cursor = db.connection.cursor()
        sql = f"CREATE TABLE `{empresa}` (`articulo` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL, `precio` decimal(12,2) DEFAULT NULL, `art_descripcion` text COLLATE utf8_unicode_ci, `imagen` longblob, `speech` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL, `descripcion` text COLLATE utf8_unicode_ci, `pregunta` text COLLATE utf8_unicode_ci, UNIQUE KEY `articulo` (`articulo`), UNIQUE KEY `speech` (`speech`)) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;"
        cursor.execute(sql)
        if logos_data and c_base64:
            sql = f"INSERT INTO clientes VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, current_date(), %s) ON DUPLICATE KEY UPDATE empresa=VALUES(empresa), logo=VALUES(logo), nombre=VALUES(nombre), direccion=VALUES(direccion), telefono=VALUES(telefono), email=VALUES(email), vende=VALUES(vende), plan=VALUES(plan), plan_fichainterna=VALUES(plan_fichainterna), fecha=VALUES(fecha), contrato=VALUES(contrato)"
            valores = [(empresa.replace('_', ' '), logo_data, persona, direccion, telefono, email, vende, plan, fichainterna, c_base64) for logo_data in logos_data]
        if logos_data and c_base64 == '':
            sql = f"INSERT INTO clientes VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, current_date(), null) ON DUPLICATE KEY UPDATE empresa=VALUES(empresa), logo=VALUES(logo), nombre=VALUES(nombre), direccion=VALUES(direccion), telefono=VALUES(telefono), email=VALUES(email), vende=VALUES(vende), plan=VALUES(plan), plan_fichainterna=VALUES(plan_fichainterna), fecha=VALUES(fecha), contrato=VALUES(contrato)"
            valores = [(empresa.replace('_', ' '), logo_data, persona, direccion, telefono, email, vende, plan, fichainterna) for logo_data in logos_data]
        if logos_data == '' and c_base64:
            sql = f"INSERT INTO clientes VALUES (%s, null, %s, %s, %s, %s, %s, %s, %s, current_date(), %s) ON DUPLICATE KEY UPDATE empresa=VALUES(empresa), logo=VALUES(logo), nombre=VALUES(nombre), direccion=VALUES(direccion), telefono=VALUES(telefono), email=VALUES(email), vende=VALUES(vende), plan=VALUES(plan), plan_fichainterna=VALUES(plan_fichainterna), fecha=VALUES(fecha), contrato=VALUES(contrato)"
            valores = [(empresa.replace('_', ' '), persona, direccion, telefono, email, vende, plan, fichainterna, c_base64)]
        if logos_data =='' and c_base64 == '':
            sql = f"INSERT INTO clientes VALUES (%s, null, %s, %s, %s, %s, %s, %s, %s, current_date(), null) ON DUPLICATE KEY UPDATE empresa=VALUES(empresa), logo=VALUES(logo), nombre=VALUES(nombre), direccion=VALUES(direccion), telefono=VALUES(telefono), email=VALUES(email), vende=VALUES(vende), plan=VALUES(plan), plan_fichainterna=VALUES(plan_fichainterna), fecha=VALUES(fecha), contrato=VALUES(contrato)"
            valores = [(empresa.replace('_', ' '), persona, direccion, telefono, email, vende, plan, fichainterna)]
        cursor.executemany(sql, valores)
        num_art = int(request.form['n_articulos'])
        num_esp = int(request.form['n_espacios'])
        num_preg = int(request.form['n_preguntas'])
        
        if num_art != 0:
            for i in range(1, num_art+1):
                articulo = request.form[f'art{i}'].upper()
                precio = request.form[f'precio{i}']
                art_descripcion = request.form[f'art_descripcion{i}']
                files = request.files.getlist(f'imagenes{i}[]')
                if str(files) == "[<FileStorage: '' ('application/octet-stream')>]":
                    sql = f"INSERT INTO {empresa} VALUES ('{articulo}', {precio}, '{art_descripcion}', null, null, null, null)"
                    cursor.execute(sql)
                else:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                        for file in files:
                            zip_file.writestr(file.filename, file.read())
                    cursor.execute(f"INSERT INTO {empresa} VALUES ('{articulo}', {precio}, '{art_descripcion}', %s, null, null, null)", (zip_buffer.getvalue(),))
                                
        if num_esp != 0:
            for i in range(1, num_esp+1):
                speech = request.form[f'speech{i}'].upper()
                desc = request.form[f'desc{i}']
                sql = f"INSERT INTO {empresa} VALUES (null, null, null, null, '{speech}', '{desc}', null)"
                cursor.execute(sql)
        
        if num_preg != 0:
            for i in range(1, num_preg+1):
                pregunta = request.form[f"pregunta{i}"].upper().strip().replace('?', '').replace('¿','')
                cursor.execute(f"INSERT INTO {empresa} VALUES (null, null, null, null, null, null, '¿{pregunta}?')")
        
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} agregó al cliente {empresa.replace('_', ' ')} con {num_art} artículos, {num_esp} espacios de trabajo y {num_preg} preguntas frecuentes', now())")
        db.connection.commit()
        cursor.close()
        return redirect(url_for('dashboard'))
    cursor = db.connection.cursor()
    cursor.execute("SELECT idplan, plan from planes where idplan != 0 order by idplan")
    planes = cursor.fetchall()
    return render_template('altacliente.html', planes=planes)

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
        cur.execute("SELECT * FROM auth WHERE user = %s", (usuario,))
        user_data = cur.fetchone()

        if user_data and user_data[1] == contra:
            user = User(user_data[0], user_data[1], user_data[2], user_data[3])
            login_user(user)
            cur.execute(f"insert into movimientos (mov, date_mov) VALUES ('{current_user.fullname} inció sesión', now())")
            db.connection.commit()
            cur.close()
            return redirect(url_for('dashboard'))
    return render_template('auth/login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    cursor = db.connection.cursor()
    #sql = "show TABLES where tables_in_administracion_los_andes <> 'auth' and tables_in_administracion_los_andes <> 'clientes' and tables_in_administracion_los_andes <> 'registros' and tables_in_administracion_los_andes <> 'movimientos' and tables_in_administracion_los_andes <> 'planes';"
    sql = "SELECT empresa,logo from clientes order by empresa;"
    cursor.execute(sql)
    tablas =  cursor.fetchall()
    #tablas = [elemento[0].upper().replace('_',' ') for elemento in tablas]
    cursor.execute(f"SELECT current_date, empresa, nombre, telefono, motivo, tareas.tarea, email, cotizacion, cotizaciontotal, fecha from registros join tareas on tareas.idtarea = registros.tarea WHERE agente = '{current_user.fullname}' and fecha_tarea = current_date() and estado='pendiente';")
    tareas = cursor.fetchall()
    return render_template('dashboard.html', tablas=tablas, tareas=tareas)

@app.route('/usuarios')
@login_required
def usuarios():
    cursor = db.connection.cursor()
    sql = "SELECT * FROM auth;"
    cursor.execute(sql)
    tablas = cursor.fetchall()
    return render_template('usuarios.html', tablas=tablas)

@app.route('/movimientos')
@login_required
def movimientos():
    cursor = db.connection.cursor()
    sql = "SELECT * FROM movimientos order by date_mov desc;"
    cursor.execute(sql)
    tablas = cursor.fetchall()
    return render_template('movimientos.html', tablas=tablas)

@app.route('/registros')
@login_required
def registros():
    cursor = db.connection.cursor()
    sql = "SELECT empresa, agente, nombre, telefono, email, motivo, cotizacion, cotizaciontotal, fecha, tareas.tarea, fecha_tarea, estado, nota_rechazo from registros join tareas on tareas.idtarea = registros.tarea order by registros.fecha desc;"
    cursor.execute(sql)
    tablas = cursor.fetchall()
    cursor.execute("SELECT fullname from auth order by fullname asc")
    agentes = cursor.fetchall()
    return render_template('registros.html', tablas=tablas, agentes=agentes)

@app.route('/preguntas')
@login_required
def preguntas():
    cursor = db.connection.cursor()
    cursor.execute("select empresa, agente, nombre, telefono, email, tareas.tarea, fecha from registros join tareas on registros.tarea = tareas.idtarea where pregunta is not null and estado = 'cotizar' group by fecha order by fecha desc;")
    clientes = cursor.fetchall()
    cursor.execute("select fecha,pregunta, respuesta from registros where pregunta is not null and estado = 'cotizar';")
    preguntas = cursor.fetchall()
    return render_template('preguntas.html', clientes=clientes, preguntas=preguntas)

@app.route('/clientes')
@login_required
def clientes():
    cursor = db.connection.cursor()
    sql = "select empresa, logo, nombre, direccion, telefono, email, vende, planes.plan, plan_fichainterna, fecha, contrato from clientes JOIN planes ON planes.idplan = clientes.plan ORDER BY empresa asc;"
    cursor.execute(sql)
    tablas = cursor.fetchall()
    return render_template('clientes.html', tablas=tablas)

@app.route('/menu/registrarllamada', methods=['GET', 'POST'])
@login_required
def registrarLlamada():
    if request.method == 'POST':
        empresa = request.form['empresa'].upper()
        nombre = request.form['nombre'].upper()
        telefono = request.form['telefono']
        motivo = request.form['motivo']
        email = request.form['email'].lower()
        cotizacion = request.form['cotizacion'].upper().replace(' | $','')
        cotizaciontotal = request.form['cotizaciontotal']
        tarea = request.form['tarea']
        fecha_tarea = request.form['fecha_tarea']
        cursor = db.connection.cursor()
        if fecha_tarea != 'null':
            sql = f"INSERT INTO registros VALUES ('{empresa}', '{current_user.fullname}','{nombre}', '{telefono}', '{email}', '{motivo}', '{cotizacion}', {cotizaciontotal}, now(), {tarea}, '{fecha_tarea}', 'pendiente', null, null, null);"
        else:
            sql = f"INSERT INTO registros VALUES ('{empresa}', '{current_user.fullname}','{nombre}', '{telefono}', '{email}', '{motivo}', '{cotizacion}', {cotizaciontotal}, now(), {tarea}, null, 'pendiente', null, null, null);"
        cursor.execute(sql)
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} registró una llamada de {nombre} por {motivo.upper()} del cliente {empresa.replace('_', ' ')}', now() )")
        db.connection.commit()
        cursor.close()
        return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))

@app.route('/menu/registrarpreguntas', methods=['GET', 'POST'])
@login_required
def registrarPreguntas():
    if request.method == 'POST':
        empresa = request.form['empresa'].upper()
        nombre = request.form['nombre'].upper()
        telefono = request.form['telefono']
        email = request.form['email'].lower()
        tarea = request.form['tarea']
        fecha_tarea = request.form['fecha_tarea']
        cursor = db.connection.cursor()
        cursor.execute(f"SELECT count(pregunta) from {empresa.replace(' ','_')} where pregunta is not null")
        num_preg = cursor.fetchone()
        for i in range(1,int(num_preg[0])+1):
            pregunta = request.form[f'pregunta{i}.0']
            respuesta = request.form[f'respuesta{i}.0'].strip().upper()
            if fecha_tarea != 'null':
                cursor.execute(f"INSERT INTO registros VALUES ('{empresa}', '{current_user.fullname}','{nombre}', '{telefono}', '{email}', null, null, null, now(), {tarea}, '{fecha_tarea}', 'cotizar', null, '{pregunta}', '{respuesta}');")
            else:
                cursor.execute(f"INSERT INTO registros VALUES ('{empresa}', '{current_user.fullname}','{nombre}', '{telefono}', '{email}', null, null, null, now(), {tarea}, null, 'cotizar', null, '{pregunta}', '{respuesta}');")
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} registró preguntas a {nombre} de {empresa.replace('_', ' ')}', now() )")
        db.connection.commit()
        cursor.close()
        return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))

@app.route('/registros/editarregistro', methods=['GET', 'POST'])
@login_required
def editarRegistro():
    if request.method == 'POST':
        cursor = db.connection.cursor()
        agentenuevo = request.form['agentenuevo']
        registro = request.form['eliminar']
        if agentenuevo == 'null':
            accion = request.form['accion']
            nota = request.form['nota'].upper().strip()
            if accion == "eliminar":
                sql = f"UPDATE registros SET estado = 'rechazado', nota_rechazo = '{nota}' where fecha = '{registro}';"
            if accion == "a_listo":
                sql = f"UPDATE registros SET estado='listo' where fecha = '{registro}'"
            if accion == "a_pendiente":
                sql = f"UPDATE registros SET estado='pendiente' WHERE fecha = '{registro}'"
            cursor.execute(sql)
        else:
            cursor.execute(f"UPDATE registros SET agente = '{agentenuevo}' where fecha = '{registro}'")
            cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} envió el registro N° ´{registro}´ a {agentenuevo}', now())")
        db.connection.commit()
        cursor.close()
        if request.form['redireccion'] == 'menu':
            return Response(status=204)
    return redirect(url_for('registros'))

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
        cursor.execute(f"UPDATE registros SET nombre = '{nombre}', email = '{email}', cotizacion = '{cotizacion}', cotizaciontotal = {totalcotizacion}, estado = 'enviado', fecha = now(), tarea = 0, fecha_tarea = null where fecha = '{fecha}';")
        cursor.execute(f"insert into movimientos (mov, date_mov) VALUES ('{current_user.fullname} envío una cotización de ${totalcotizacion} a {email} del cliente {nombre}', now())")
        db.connection.commit()
        cursor.close()
    return Response(status=204)

@app.route('/cotizacion/listo', methods=['GET', 'POST'])
@login_required
def cotizacionListo():
    if request.method == 'POST':
        fecha = request.form['cotizacion_listo']
        cursor = db.connection.cursor()
        cursor.execute(f"UPDATE registros SET estado = 'listo' WHERE fecha = '{fecha}';")
        db.connection.commit()
        cursor.close()
        return redirect(url_for('dashboard'))
    return Response(status=204)

@app.route('/tareas', methods=['GET', 'POST'])
@login_required
def tareas():
    cursor = db.connection.cursor()
    cursor.execute("SELECT * from tareas where idtarea!= 0 order by idtarea asc")
    tareas = cursor.fetchall()
    return render_template('tareas.html', tareas=tareas)

@app.route('/enviadas', methods=['GET', 'POST'])
@login_required
def enviadas():
    cursor = db.connection.cursor()
    cursor.execute("select empresa, agente, nombre, telefono, email, motivo, cotizacion, cotizaciontotal, fecha from registros where estado = 'enviado' order by fecha desc;")
    tablas = cursor.fetchall()
    return render_template('enviadas.html', tablas=tablas)

@app.route('/tareas/altatarea', methods=['GET', 'POST'])
@login_required
def altaTarea():
    if request.method == 'POST':
        tarea  = request.form['tarea'].upper().replace('\n','').strip()
        cursor = db.connection.cursor()
        cursor.execute(f"insert into tareas (tarea) values ('{tarea}');")
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} agregó una nueva tarea al sistema: {tarea}', now());")
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
        cursor.execute(f"update registros set tarea = 0 where tarea = {idtarea}")
        cursor.execute(f"delete from tareas where idtarea = {idtarea};")
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} eliminó del sistema la tarea {tarea}', now());")
        db.connection.commit()
        cursor.close()
        return redirect(url_for('tareas'))
    return Response(status=204)

@app.route('/tareas/editartarea', methods=['GET', 'POST'])
@login_required
def modTarea():
    if request.method == 'POST':
        idtarea = request.form['idtarea']
        tareavieja = request.form['tareavieja'].strip()
        tareanueva = request.form['tareanueva'].replace('\n','').strip().upper()
        cursor = db.connection.cursor()
        cursor.execute(f"update tareas set tarea = '{tareanueva}' where idtarea = {idtarea};")
        cursor.execute(f"insert into movimientos (mov, date_mov) VALUES ('{current_user.fullname} editó la tarea {tareavieja}. Ahora es {tareanueva}', now());")
        db.connection.commit()
        cursor.close()
        return redirect(url_for('tareas'))
    return Response(status=204)

@app.route('/planes', methods=['GET', 'POST'])
@login_required
def planes():
    cursor = db.connection.cursor()
    cursor.execute("SELECT * from planes where idplan != 0 order by idplan asc")
    planes = cursor.fetchall()
    return render_template('planes.html', planes=planes)

@app.route('/planes/nuevoplan', methods=['GET', 'POST'])
@login_required
def altaPlan():
    if request.method == 'POST':
        plan  = request.form['plan'].upper().strip()
        descripcion = request.form['desc_plan'].replace('\n','').upper().strip()
        precioplan = request.form['precioplan']
        cursor = db.connection.cursor()
        cursor.execute(f"insert into planes (plan, descripcion, precio) VALUES ('{plan}', '{descripcion}', {precioplan})")
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} agregó un nuevo plan al sistema: {plan}', now());")
        db.connection.commit()
        cursor.close()
        return redirect(url_for('planes'))
    return Response(status=204)

@app.route('/planes/eliminarplan', methods=['GET', 'POST'])
@login_required
def bajaPlan():
    if request.method == 'POST':
        id  = request.form['eliminar']
        plan = request.form['desc_plan'].strip()
        cursor = db.connection.cursor()
        cursor.execute(f"UPDATE clientes set plan = 0 where plan = {id}")
        cursor.execute(f"delete from planes where idplan = {id};")
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} eliminó del sistema el plan {plan}', now());")
        db.connection.commit()
        cursor.close()
        return redirect(url_for('planes'))
    return Response(status=204)

@app.route('/planes/editarplan', methods=['GET', 'POST'])
@login_required
def modPlan():
    if request.method == 'POST':
        id = request.form['idplan']
        plan = request.form['plan'].upper().strip()
        desc_plan = request.form['desc_plan'].replace('\n','').strip().upper()
        precio = request.form['precioplan']
        cursor = db.connection.cursor()
        cursor.execute(f"update planes set plan = '{plan}', descripcion = '{desc_plan}', precio = {precio} where idplan = {id}")
        cursor.execute(f"insert into movimientos (mov, date_mov) VALUES ('{current_user.fullname} editó un plan, se actualizó a {plan}', now());")
        db.connection.commit()
        cursor.close()
        return redirect(url_for('planes'))
    return Response(status=204)

def pagina_no_encontrada(error):
    return render_template('error404.html'), 404

def pagina_no_autorizada(error):
    return render_template('error401.html'), 401

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(401, pagina_no_autorizada)
    app.register_error_handler(404, pagina_no_encontrada)
    #app.run(debug=True, port=5001)
    app.run(debug=False, port=30358, host='admin.losandestx.com')