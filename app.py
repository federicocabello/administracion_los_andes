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
    cursor.execute(f"insert into movimientos (mov, date_mov) VALUES ('{current_user.fullname} cerró sesión', date_add(now(), interval -5 hour))")
    db.connection.commit()
    cursor.close()
    logout_user()
    return redirect(url_for('login'))

@app.route('/seguimiento/<telefono>')
@login_required
def seguimiento(telefono):
    cursor = db.connection.cursor()
    cursor.execute(f'select empresa, nombre, telefono, email, motivo, cotizacion, cotizaciontotal, fecha, tareas.tarea, fecha_tarea, hora_tarea, estado, nota_rechazo, agente, direccion, tareas.color from registros join tareas on tareas.idtarea = registros.tarea where telefono = "{telefono}" and estado = "registro" order by fecha desc;')
    registros = cursor.fetchall()
    cursor.execute(f'select mov, date_mov from movimientos where mov like "%{registros[0][1]}%" order by date_mov desc;')
    movimientos = cursor.fetchall()
    cursor.execute(f"SELECT pregunta, respuesta, fecha from registros where telefono = '{telefono}' and estado = 'pregunta';")
    preguntas = cursor.fetchall()
    cursor.execute("SELECT idtarea, tarea from tareas")
    tareas = cursor.fetchall()
    cursor.execute("select * from calendario")
    calendario = cursor.fetchall()
    return render_template('seguimiento.html', registros=registros, movimientos=movimientos, preguntas=preguntas, tareas=tareas, calendario=calendario)
    return Response(status=204)

@app.route('/seguimiento', methods=['GET', 'POST'])
@login_required
def pre_seguimiento():
    if request.method == 'POST':
        telefono = request.form['telefono_seg']
        return seguimiento(telefono)

@app.route('/menu/<empresa>', methods=['GET', 'POST'])
@login_required
def refrescarMenu(empresa):
        empresa.replace(' ','_').upper()
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
        sql = f"select nombre, telefono, motivo, tareas.tarea, fecha_tarea, fecha, agente, hora_tarea, direccion, email, tareas.color from registros JOIN tareas ON tareas.idtarea=registros.tarea WHERE tareas.tarea != '' AND tareas.tarea != 'NO ATENDIÓ' AND tareas.tarea != 'NO LE INTERESA' AND tareas.tarea != 'SI ASISTIÓ' AND tareas.tarea != 'RENTÓ' AND tareas.tarea != 'ESPERAR LLAMADA' AND tareas.tarea != 'INFORMACIÓN ENVIADA' AND tareas.tarea != 'INSPECCIÓN REALIZADA' AND tareas.tarea != 'YA INSTALÓ' AND empresa = '{empresa.replace('_',' ')}' and agente = '{current_user.fullname}' and estado = 'registro' order by fecha asc limit 7;"
        cursor.execute(sql)
        pendientes = cursor.fetchall()
        cursor.execute("select * from tareas")
        tareas = cursor.fetchall()
        cursor.execute("select * from calendario order by date asc")
        calendario = cursor.fetchall()
        #print(calendario[0][0])
        #print(dt.date.today())
        if dt.date.today() != calendario[0][0]:
            cursor.execute("delete from calendario;")
            cursor.execute("insert into calendario values (current_date(), DATE_FORMAT(current_date(), '%W %e'))")
            for i in range (1,18):
                cursor.execute(f"insert into calendario values (date_add(current_date(), interval {i} day), DATE_FORMAT(date_add(current_date(), interval {i} day), '%W %e'))")
                cursor.execute("delete from calendario where date_format like 'Sunday%'")
        db.connection.commit()
        cursor.execute("select * from calendario order by date asc")
        calendario = cursor.fetchall()
        cursor.execute("SELECT fullname from auth order by fullname asc")
        agentes = cursor.fetchall()
        cursor.execute(f"select pregunta, (@row := @row + 1) as contador from {empresa}, (SELECT @row := 0) r where pregunta is not null;")
        preguntas = cursor.fetchall()
        cursor.execute(f"select count(*) from {empresa} where pregunta is not null")
        num_preguntas = cursor.fetchall()
        cursor.execute("SELECT telefono from registros where estado = 'registro' group by telefono")
        telefonos = cursor.fetchall()
        return render_template('menu.html', empresa=empresa.replace('_', ' ').upper(), articulos=articulos, speech=speech, pendientes=pendientes, tareas=tareas, calendario=calendario, registros=registros, agentes=agentes, preguntas=preguntas, num_preguntas=num_preguntas, telefonos=telefonos)

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
        sql = f"select nombre, telefono, motivo, tareas.tarea, fecha_tarea, fecha, agente, hora_tarea, direccion, email, tareas.color from registros JOIN tareas ON tareas.idtarea=registros.tarea WHERE tareas.tarea != '' AND tareas.tarea != 'NO ATENDIÓ' AND tareas.tarea != 'NO LE INTERESA' AND tareas.tarea != 'SI ASISTIÓ' AND tareas.tarea != 'RENTÓ' AND tareas.tarea != 'ESPERAR LLAMADA' AND tareas.tarea != 'INFORMACIÓN ENVIADA' AND tareas.tarea != 'INSPECCIÓN REALIZADA' AND tareas.tarea != 'YA INSTALÓ' AND empresa = '{empresa.replace('_',' ')}' and agente = '{current_user.fullname}' and estado = 'registro' order by fecha asc limit 7;"
        cursor.execute(sql)
        pendientes = cursor.fetchall()
        cursor.execute("select * from tareas")
        tareas = cursor.fetchall()
        cursor.execute("select * from calendario order by date asc")
        calendario = cursor.fetchall()
        #print(calendario[0][0])
        #print(dt.date.today())
        if dt.date.today() != calendario[0][0]:
            cursor.execute("delete from calendario;")
            cursor.execute("insert into calendario values (current_date(), DATE_FORMAT(current_date(), '%W %e'))")
            for i in range (1,18):
                cursor.execute(f"insert into calendario values (date_add(current_date(), interval {i} day), DATE_FORMAT(date_add(current_date(), interval {i} day), '%W %e'))")
                cursor.execute("delete from calendario where date_format like 'Sunday%'")
        db.connection.commit()
        cursor.execute("select * from calendario order by date asc")
        calendario = cursor.fetchall()
        cursor.execute("SELECT fullname from auth order by fullname asc")
        agentes = cursor.fetchall()
        cursor.execute(f"select pregunta, (@row := @row + 1) as contador from {empresa}, (SELECT @row := 0) r where pregunta is not null;")
        preguntas = cursor.fetchall()
        cursor.execute(f"select count(*) from {empresa} where pregunta is not null")
        num_preguntas = cursor.fetchall()
        cursor.execute("SELECT telefono from registros where estado = 'registro' group by telefono")
        telefonos = cursor.fetchall()
        return render_template('menu.html', empresa=empresa.replace('_', ' '), articulos=articulos, speech=speech, pendientes=pendientes, tareas=tareas, calendario=calendario, registros=registros, agentes=agentes, preguntas=preguntas, num_preguntas=num_preguntas, telefonos=telefonos)
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
        if dt.date.today() != calendario[0][0]:
            cursor.execute("delete from calendario;")
            cursor.execute("insert into calendario values (current_date(), DATE_FORMAT(current_date(), '%W %e'))")
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
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} agregó al usuario {usuario.upper()} | {fullname}', date_add(now(), interval -5 hour))")
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
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} modificó al usuario {usuario.upper()}', date_add(now(), interval -5 hour))")
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
        cursor.execute(f"INSERT INTO movimientos (mov, date_mov) VALUES ('{current_user.fullname} eliminó al usuario {eliminar.upper()}', date_add(now(), interval -5 hour));")
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
        telefono_sn = request.form['telefono']
        telefono = ''
        for n in telefono_sn:
            if n.isdigit():
                telefono = telefono+n
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
            cursor.execute(f"insert into movimientos (mov, date_mov) VALUES ('{current_user.fullname} modificó al cliente {nombreviejo.replace('_', ' ')}. Ahora es {empresa.replace('_',' ')}', date_add(now(), interval -5 hour))")
        num_art = int(request.form['n_articulos'])
        num_esp = int(request.form['n_espacios'])
        num_preg = int(request.form['n_preguntas'])
        
        if num_art != 0:
            cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} agregó {num_art} artículos al cliente {empresa.replace('_', ' ')}', date_add(now(), interval -5 hour))")
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
            cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} agregó {num_esp} espacios de trabajo al cliente {empresa}', date_add(now(), interval -5 hour))")
            for i in range(1, num_esp+1):
                speech = request.form[f'speech{i}'].upper()
                desc = request.form[f'desc{i}']
                sql = f"INSERT INTO {empresa.replace(' ','_')} VALUES (null, null, null, null, '{speech}', '{desc}', null)"
                cursor.execute(sql)
                
        if num_preg != 0:
            cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} agregó {num_preg} preguntas a {empresa}', date_add(now(), interval -5 hour))")
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
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} eliminó al cliente {eliminar.replace('_',' ')}',date_add(now(), interval -5 hour))")
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
        telefono_sn = request.form['telefono']
        telefono = ''
        for n in telefono_sn:
            if n.isdigit():
                telefono = telefono+n
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
        
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} agregó al cliente {empresa.replace('_', ' ')} con {num_art} artículos, {num_esp} espacios de trabajo y {num_preg} preguntas frecuentes', date_add(now(), interval -5 hour))")
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
            cur.execute(f"insert into movimientos (mov, date_mov) VALUES ('{current_user.fullname} inció sesión', date_add(now(), interval -5 hour))")
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
    cursor.execute(f"SELECT DATE_FORMAT(fecha, '%d %M'), empresa, nombre, telefono, motivo, tareas.tarea, email, cotizacion, cotizaciontotal, fecha, hora_tarea, cast(hora_tarea as unsigned) as hora, direccion from registros join tareas on tareas.idtarea = registros.tarea WHERE agente = '{current_user.fullname}' and fecha_tarea = current_date() and tareas.tarea != 'NO LE INTERESA' and tareas.tarea != '' and pregunta is null and estado = 'registro' order by hora;")
    pendiente = cursor.fetchall()
    cursor.execute("SELECT fullname from auth order by fullname")
    agentes = cursor.fetchall()
    cursor.execute("SELECT * from tareas")
    tareas = cursor.fetchall()
    cursor.execute("select * from calendario")
    calendario = cursor.fetchall()
    cursor.execute("select CASE WHEN fecha_1 = current_date() THEN 'CUOTA 1' WHEN fecha_2 = current_date() THEN 'CUOTA 2' WHEN fecha_3 = current_date() THEN 'CUOTA 3' WHEN fecha_4 = current_date() THEN 'CUOTA 4' END AS cuota, CASE WHEN fecha_1 = current_date() THEN acuerdo_1 WHEN fecha_2 = current_date() THEN acuerdo_2 WHEN fecha_3 = current_date() THEN acuerdo_3 WHEN fecha_4 = current_date() THEN acuerdo_4 END AS pago, LPAD( idhoja, 8, '0'), nombre, telefono, servicio, objeto, notapago, idfecha, empresa FROM hojas WHERE fecha_1 = CURRENT_DATE() OR fecha_2 = current_date() or fecha_3 = current_date or fecha_4 = current_date();")
    vencehoy = cursor.fetchall()
    cursor.execute("SELECT 'CUOTA 1' AS cuota, fecha_1 AS vencimiento, acuerdo_1 AS pago, LPAD( idhoja, 8, '0'), nombre, telefono, servicio, objeto, notapago, datediff(current_date(), fecha_1) as diferencia, idfecha, empresa FROM hojas where fecha_1 < CURRENT_DATE() UNION ALL SELECT 'CUOTA 2' AS cuota, fecha_2 AS vencimiento, acuerdo_2 AS pago, LPAD( idhoja, 8, '0'), nombre, telefono, servicio, objeto, notapago, datediff(current_date(), fecha_2) as diferencia, idfecha, empresa FROM hojas where fecha_2 < CURRENT_DATE() UNION ALL SELECT 'CUOTA 3' AS cuota, fecha_3 AS vencimiento, acuerdo_3 AS pago, LPAD( idhoja, 8, '0'), nombre, telefono, servicio, objeto, notapago, datediff(current_date(), fecha_3) as diferencia, idfecha, empresa FROM hojas where fecha_3 < CURRENT_DATE() UNION ALL SELECT 'CUOTA 4' AS cuota, fecha_4 AS vencimiento, acuerdo_4 AS pago, LPAD( idhoja, 8, '0'), nombre, telefono, servicio, objeto, notapago, datediff(current_date(), fecha_4) as diferencia, idfecha, empresa FROM hojas where fecha_4 < CURRENT_DATE() order by diferencia;")
    vencidos = cursor.fetchall()
    cursor.execute("SELECT 'CUOTA 1' AS cuota, fecha_1 AS vencimiento, acuerdo_1 AS pago, LPAD( idhoja, 8, '0'), nombre, telefono, servicio, objeto, notapago, datediff(fecha_1, current_date()) as diferencia, idfecha, empresa FROM hojas where datediff(fecha_1, current_date()) > 0 and datediff(fecha_1, current_date()) < 6 UNION ALL SELECT 'CUOTA 2' AS cuota, fecha_2 AS vencimiento, acuerdo_2 AS pago, LPAD( idhoja, 8, '0'), nombre, telefono, servicio, objeto, notapago, datediff(fecha_2, current_date()) as diferencia, idfecha, empresa FROM hojas where datediff(fecha_2, current_date()) > 0 and datediff(fecha_2, current_date()) < 6 UNION ALL SELECT 'CUOTA 3' AS cuota, fecha_3 AS vencimiento, acuerdo_3 AS pago, LPAD( idhoja, 8, '0'), nombre, telefono, servicio, objeto, notapago, datediff(fecha_3, current_date()) as diferencia, idfecha, empresa FROM hojas where datediff(fecha_3, current_date()) > 0 and datediff(fecha_3, current_date()) < 6 UNION ALL SELECT 'CUOTA 4' AS cuota, fecha_4 AS vencimiento, acuerdo_4 AS pago, LPAD( idhoja, 8, '0'), nombre, telefono, servicio, objeto, notapago, datediff(fecha_4, current_date()) as diferencia, idfecha, empresa FROM hojas where datediff(fecha_4, current_date()) > 0 and  datediff(fecha_4, current_date()) < 6 order by diferencia;")
    porvencer = cursor.fetchall()
    cursor.execute(f"select DATE_FORMAT(fecha, '%d %M'), empresa, nombre, telefono, motivo, tareas.tarea, email, cotizacion, cotizaciontotal, fecha, hora_tarea, cast(hora_tarea as unsigned) as hora, direccion, DATE_FORMAT(fecha_tarea, '%d %M'), datediff(current_date(), fecha_tarea) as dias from registros JOIN tareas ON registros.tarea = tareas.idtarea where (fecha_tarea < current_date() or fecha_tarea is null) and agente = '{current_user.fullname}' and estado = 'registro' and registros.tarea in (select tarea from registros where tarea = 0 or tarea = 3 or tarea = 4 or tarea = 5 or tarea = 6 or tarea = 8 or tarea = 9 or tarea = 10 or tarea = 11 or tarea = 14 or tarea = 15 or tarea = 16 or tarea = 18) order by dias, hora, fecha asc;")
    atrasados = cursor.fetchall()
    nombre_dia_hoy = f'{dt.date.today().strftime("%A")} {dt.date.today().strftime("%d")}'
    return render_template('dashboard.html', tablas=tablas, tareas=tareas, agentes=agentes, pendiente=pendiente, calendario=calendario, vencehoy=vencehoy, vencidos=vencidos, porvencer=porvencer, dia_hoy = dt.date.today(), nombre_dia_hoy=nombre_dia_hoy, atrasados=atrasados)

@app.route('/pagos/registrar_pago', methods=['GET', 'POST'])
@login_required
def registrarPago():
    data = request.json
    pago = data['pago']
    cursor = db.connection.cursor()
    if pago[2] == None:
        pago[2] = 'null'
    telefono_sn = pago[4]
    telefono = ''
    for n in telefono_sn:
        if n.isdigit():
            telefono = telefono+n
    cursor.execute(f"INSERT INTO pagos (empresa, motivo, idhoja, cliente, telefono, fecha_vencimiento, fecha_pago, forma_pago, pago, agente) VALUES ('{pago[0]}', '{pago[1].upper().strip()}', {pago[2]}, '{pago[3].upper().strip()}', '{telefono}', '{pago[5]}', '{pago[6]}', '{pago[7]}', {pago[8]}, '{current_user.fullname}')")
    if pago[5] == '0000-00-00':
        cursor.execute("UPDATE pagos SET fecha_vencimiento = null where fecha_vencimiento = '0000-00-00';")
    if pago[1] == 'CUOTA 1' or pago[1] == 'CUOTA 2' or pago[1] == 'CUOTA 3' or pago[1] == 'CUOTA 4':
        if pago[2] != None: 
            cursor.execute(f"UPDATE hojas SET acuerdo_{pago[1][6]} = null, fecha_{pago[1][6]} = null, interes_{pago[1][6]} = null WHERE idhoja = {pago[2]};")
    cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} registró un pago de $ {pago[8]} de {pago[0]} del cliente {pago[3].upper().strip()}', date_add(now(), interval -5 hour))")
    db.connection.commit()
    cursor.close()
    return redirect(url_for('dashboard'))

@app.route('/pagos')
@login_required
def pagos():
    cursor = db.connection.cursor()
    cursor.execute("select idpagos, empresa, motivo, LPAD( idhoja, 8, '0'), cliente, telefono, date_format(fecha_vencimiento, '%d %M %Y'), date_format(fecha_pago, '%d %M %Y'), forma_pago, pago, agente from pagos order by fecha_pago desc, idpagos desc;")
    pagos = cursor.fetchall()
    cursor.execute("SELECT empresa from clientes order by empresa;")
    empresas = cursor.fetchall()
    return render_template('pagos.html', pagos=pagos, empresas=empresas, hoy=dt.date.today())

@app.route('/pagos/eliminar_pago', methods=['GET', 'POST'])
@login_required
def eliminarPago():
    data = request.json
    pago = data['pagosid']
    cursor = db.connection.cursor()
    cursor.execute(f"DELETE from pagos where idpagos = {pago[0]}")
    cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} eliminó el pago N°{pago[0]} del cliente {pago[1]}', date_add(now(), interval -5 hour))")
    db.connection.commit()
    cursor.close()
    return redirect(url_for('pagos'))
    
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
    cursor.execute("SELECT count(*) from movimientos")
    n_mov = cursor.fetchone()
    fecha = ''
    if request.method == 'POST':
        accion = request.form['accion']
        if accion == 'cantidad':
            cant_mov = request.form['cantidad_mov']
            cursor.execute(f"SELECT * FROM movimientos order by date_mov desc limit {cant_mov};")
            mostrados = cant_mov
        if accion == 'filtro_fecha':
            fecha = request.form['fecha_unica']
            cursor.execute(f"SELECT count(*) from movimientos where date(date_mov) = '{fecha}'")
            contados_filtrados = cursor.fetchone()
            cursor.execute(f"SELECT *, date(date_mov) from movimientos where date(date_mov) = '{fecha}' order by date_mov desc")
            mostrados = contados_filtrados[0]
    else:
        cursor.execute("SELECT * FROM movimientos order by date_mov desc limit 25;")
        mostrados = 25
    tablas = cursor.fetchall()
    return render_template('movimientos.html', tablas=tablas, n_mov=n_mov, mostrados=mostrados, fecha=fecha)
    

@app.route('/registros', methods=['GET', 'POST'])
@login_required
def registros():
    cursor = db.connection.cursor()
    cursor.execute("SELECT count(*) from registros where estado ='registro' and telefono in (select telefono from registros group by telefono having count(DISTINCT nombre) >1)")
    repetidos = cursor.fetchone()
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
    habilitar_tareas = 'no'
    tareas_empresa = ()
    empresa = None
    if request.method == 'POST':
        filtro = request.form['filtro']
        if filtro == 'fecha_unica':
            fechaunica = request.form['fecha_inicial']
            cursor.execute(f"SELECT count(*) from registros join tareas on registros.tarea = tareas.idtarea where estado = 'registro' and fecha_tarea = '{fechaunica}' and tareas.tarea != 'NO LE INTERESA' and tareas.tarea != '';")
            one = cursor.fetchone()
            mostrados = one[0]
            cursor.execute(f"SELECT empresa, agente, nombre, telefono, email, motivo, cotizacion, cotizaciontotal, fecha, tareas.tarea, fecha_tarea, hora_tarea, estado, nota_rechazo, direccion, tareas.color from registros join tareas on tareas.idtarea = registros.tarea where estado = 'registro' and fecha_tarea = '{fechaunica}' and tareas.tarea != 'NO LE INTERESA' and tareas.tarea != '' order by registros.fecha desc;")
        if filtro == 'fechas':
            fecha_inicial = request.form['fecha_inicial']
            fecha_final = request.form['fecha_final']
            categoria = request.form['limite']
            habilitar_tareas = 'si'
            if categoria == 'fecha':
                cursor.execute(f"SELECT count(*) from registros where estado = 'registro' and fecha BETWEEN '{fecha_inicial}' and '{fecha_final}';")
                one = cursor.fetchone()
                mostrados = one[0]
                cursor.execute(f"SELECT tareas.tarea FROM registros join tareas on registros.tarea = tareas.idtarea where estado = 'registro' and fecha BETWEEN '{fecha_inicial}' and '{fecha_final}' group by registros.tarea order by registros.tarea")
                tareas_empresa = cursor.fetchall()
                cursor.execute(f"SELECT empresa, agente, nombre, telefono, email, motivo, cotizacion, cotizaciontotal, fecha, tareas.tarea, fecha_tarea, hora_tarea, estado, nota_rechazo, direccion, tareas.color from registros join tareas on tareas.idtarea = registros.tarea where registros.estado = 'registro' and registros.fecha BETWEEN '{fecha_inicial}' and '{fecha_final}' order by registros.fecha desc;")
            else:
                cursor.execute(f"SELECT count(*) from registros where estado = 'registro' and tarea != 1 and tarea != 0 and tarea != 2 and fecha_tarea BETWEEN '{fecha_inicial}' and '{fecha_final}';")
                one = cursor.fetchone()
                mostrados = one[0]
                cursor.execute(f"SELECT tareas.tarea FROM registros join tareas on registros.tarea = tareas.idtarea where registros.tarea != 1 and registros.tarea != 0 and registros.tarea != 2 and estado = 'registro' and fecha_tarea BETWEEN '{fecha_inicial}' and '{fecha_final}' group by registros.tarea order by registros.tarea")
                tareas_empresa = cursor.fetchall()
                cursor.execute(f"SELECT empresa, agente, nombre, telefono, email, motivo, cotizacion, cotizaciontotal, fecha, tareas.tarea, fecha_tarea, hora_tarea, estado, nota_rechazo, direccion, tareas.color from registros join tareas on tareas.idtarea = registros.tarea where registros.estado = 'registro' and registros.fecha_tarea BETWEEN '{fecha_inicial}' and '{fecha_final}' and registros.tarea != 1 and registros.tarea != 0 and registros.tarea != 2 order by registros.fecha_tarea desc;")
        if filtro == 'limite':
            limite = request.form['limite']
            if limite != 'all':
                cursor.execute(f"SELECT empresa, agente, nombre, telefono, email, motivo, cotizacion, cotizaciontotal, fecha, tareas.tarea, fecha_tarea, hora_tarea, estado, nota_rechazo, direccion, tareas.color, (@row := @row + 1) from registros join tareas on tareas.idtarea = registros.tarea,   (SELECT @row := 0) r where estado = 'registro' order by registros.fecha desc limit {limite};")
                mostrados = limite
            else:
                cursor.execute(f"SELECT empresa, agente, nombre, telefono, email, motivo, cotizacion, cotizaciontotal, fecha, tareas.tarea, fecha_tarea, hora_tarea, estado, nota_rechazo, direccion, tareas.color, (@row := @row + 1) from registros join tareas on tareas.idtarea = registros.tarea, (SELECT @row := 0) r where estado = 'registro' order by registros.fecha desc limit {n_registros[0]};")
                mostrados = n_registros[0]
        if filtro == 'duplicados':
            cursor.execute("SELECT empresa, agente, nombre, telefono, email, motivo, cotizacion, cotizaciontotal, fecha, tareas.tarea, fecha_tarea, hora_tarea, estado, nota_rechazo, direccion, tareas.color from registros join tareas on tareas.idtarea = registros.tarea where estado ='registro' and telefono in (select telefono from registros group by telefono having count(DISTINCT nombre) >1)")
            mostrados = repetidos[0]
            editar_telefono = 'NO'
        if filtro == 'faltantes':
            cursor.execute("SELECT empresa, agente, nombre, telefono, email, motivo, cotizacion, cotizaciontotal, fecha, tareas.tarea, fecha_tarea, hora_tarea, estado, nota_rechazo, direccion, tareas.color from registros join tareas on registros.tarea = tareas.idtarea where (tareas.tarea = 'INSTALACIÓN PROGRAMADA' or tareas.tarea = 'INSPECCIÓN PROGRAMADA' or  tareas.tarea = 'YA INSTALÓ' or tareas.tarea = 'INSPECCIÓN REALIZADA') and (nombre NOT LIKE '% %' or direccion = '')")
            mostrados = faltantes[0]
        if filtro == 'empresa':
            empresa = request.form['limite']
            cursor.execute(f"SELECT COUNT(*) from registros where estado = 'registro' and empresa = '{empresa}';")
            one = cursor.fetchone()
            mostrados = one[0]
            habilitar_tareas = 'si'
            cursor.execute(f"SELECT tareas.tarea FROM registros join tareas on registros.tarea = tareas.idtarea where estado = 'registro' and empresa = '{empresa}' group by registros.tarea order by registros.tarea")
            tareas_empresa = cursor.fetchall()
            cursor.execute(f"SELECT empresa, agente, nombre, telefono, email, motivo, cotizacion, cotizaciontotal, fecha, tareas.tarea, fecha_tarea, hora_tarea, estado, nota_rechazo, direccion, tareas.color from registros join tareas on registros.tarea = tareas.idtarea where estado = 'registro' and empresa = '{empresa}' order by registros.fecha desc;")
    else:
        cursor.execute("SELECT empresa, agente, nombre, telefono, email, motivo, cotizacion, cotizaciontotal, fecha, tareas.tarea, fecha_tarea, hora_tarea, estado, nota_rechazo, direccion, tareas.color, (@row := @row + 1) from registros join tareas on tareas.idtarea = registros.tarea, (SELECT @row := 0) r where estado = 'registro' order by registros.fecha desc limit 25;")
        mostrados = 25
    tablas = cursor.fetchall()
    cursor.execute("SELECT fullname from auth order by fullname asc")
    agentes = cursor.fetchall()
    cursor.execute("select * from tareas")
    tareas = cursor.fetchall()
    cursor.execute("SELECT empresa from clientes order by empresa asc;")
    empresas = cursor.fetchall()
    return render_template('registros.html', tablas=tablas, agentes=agentes, tareas=tareas, empresas=empresas, n_registros=n_registros, mostrados=mostrados, fecha_inicial=fecha_inicial, fecha_final=fecha_final, fechaunica=fechaunica, repetidos=repetidos, editar_telefono=editar_telefono, faltantes=faltantes, categoria=categoria, habilitar_tareas=habilitar_tareas, tareas_empresa=tareas_empresa, empresa=empresa)

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
        nombre = request.form['nombre'].upper().strip()
        telefono_sn = request.form['telefono']
        telefono = ''
        for n in telefono_sn:
            if n.isdigit():
                telefono = telefono+n
        motivo = request.form['motivo'].upper().strip()
        email = request.form['email'].lower()
        cotizacion = request.form['cotizacion'].upper()#.replace(' | $','')
        cotizaciontotal = request.form['cotizaciontotal']
        tarea = request.form['tarea']
        calendario = request.form['calendario']
        hora = request.form['hora']
        direccion = request.form['direccion'].upper()
        cursor = db.connection.cursor()
        cursor.execute(f"SELECT tarea from tareas where idtarea = {tarea}")
        tarea_desc = cursor.fetchone()
        num_preguntas = request.form['comprobarSiHayPreguntas']
        if tarea != 0:
            if calendario != '':
                cursor.execute(f"INSERT INTO registros (empresa, agente, nombre, telefono, direccion, email, motivo, cotizacion, cotizaciontotal, fecha, tarea, fecha_tarea, hora_tarea, estado) VALUES ('{empresa}', '{current_user.fullname}','{nombre}', '{telefono}', '{direccion}', '{email}', '{motivo}', '{cotizacion}', {cotizaciontotal}, date_add(now(), interval -5 hour), {tarea}, '{calendario}', '{hora}', 'registro');")
            else:
                cursor.execute(f"INSERT INTO registros (empresa, agente, nombre, telefono, direccion, email, motivo, cotizacion, cotizaciontotal, fecha, tarea, hora_tarea, estado) VALUES ('{empresa}', '{current_user.fullname}','{nombre}', '{telefono}', '{direccion}', '{email}', '{motivo}', '{cotizacion}', {cotizaciontotal}, date_add(now(), interval -5 hour), {tarea}, '', 'registro');")
            cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} registró una llamada de {nombre} con notas: {motivo} de la empresa {empresa.replace('_', ' ')}. Se le asignó la tarea {tarea_desc[0]}', date_add(now(), interval -5 hour))")
        else:
            cursor.execute(f"INSERT INTO registros (empresa, agente, nombre, telefono, direccion, email, motivo, cotizacion, cotizaciontotal, fecha, tarea,hora_tarea, estado) VALUES ('{empresa}', '{current_user.fullname}','{nombre}', '{telefono}', '{direccion}', '{email}', '{motivo}', '{cotizacion}', {cotizaciontotal}, date_add(now(), interval -5 hour), 0, '{hora}', 'registro');")
            cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} registró una llamada de {nombre} con notas: {motivo} de la empresa {empresa.replace('_', ' ')}. No se le asignó ninguna tarea', date_add(now(), interval -5 hour))")
            
        if num_preguntas != 0:
            for i in range(1, int(num_preguntas)+1):
                respuesta = request.form[f'respuesta{i}.0'].strip().upper()
                if respuesta != '':
                    pregunta = request.form[f'pregunta{i}.0']
                    cursor.execute(f"insert into registros (fecha, estado, pregunta, respuesta, telefono, cotizaciontotal) VALUES (date_add(now(), interval -5 hour), 'pregunta', '{pregunta}', '{respuesta}', '{telefono}', null)")
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
                cursor.execute(f"INSERT INTO registros VALUES ('{empresa}', '{current_user.fullname}','{nombre}', '{telefono}', '{email}', null, null, null, date_add(now(), interval -5 hour), {tarea}, '{fecha_tarea}', 'cotizar', null, '{pregunta}', '{respuesta}');")
            else:
                cursor.execute(f"INSERT INTO registros VALUES ('{empresa}', '{current_user.fullname}','{nombre}', '{telefono}', '{email}', null, null, null, date_add(now(), interval -5 hour), {tarea}, null, 'cotizar', null, '{pregunta}', '{respuesta}');")
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} registró preguntas a {nombre} de {empresa.replace('_', ' ')}', date_add(now(), interval -5 hour))")
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
        cursor.execute(f"SELECT nombre, tareas.tarea from registros join tareas on tareas.idtarea=registros.tarea where fecha = '{registro}' and pregunta is null")
        estadoanterior = cursor.fetchone()
        if agentenuevo == 'null':
            accion = request.form['accion']
            nota = request.form['nota'].upper().strip()
            if accion == "eliminar":
                cursor.execute(f"UPDATE registros SET tarea = 2, nota_rechazo = '{nota}' where fecha = '{registro}' and estado = 'registro';")
                cursor.execute(f"insert into movimientos (mov, date_mov) VALUES ('{current_user.fullname} cambió el registro N°´{registro}´ de {estadoanterior[0]}, se modificó de {estadoanterior[1].upper()} a NO LE INTERESA: {nota}', date_add(now(), interval -5 hour))")
        else:
            cursor.execute(f"UPDATE registros SET agente = '{agentenuevo}' where fecha = '{registro}' and estado = 'registro';")
            cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} envió el registro N° ´{registro}´ de {estadoanterior[0]} a {agentenuevo}', date_add(now(), interval -5 hour))")
        db.connection.commit()
        cursor.close()
        if request.form['redireccion'] == 'menu':
            return Response(status=204)
    return redirect(url_for('registros'))

@app.route('/registros/editarregistro/actualizar', methods=['GET', 'POST'])
@login_required
def actualizarRegistro():
    if request.method == 'POST':
        cursor = db.connection.cursor()
        accion = request.form['accion']
        reg_act = request.form['agentenuevo'].strip().upper()
        idfecha = request.form['eliminar']
        redireccion = request.form['redireccion']
        cursor.execute(f"SELECT nombre, estado, tareas.tarea, fecha_tarea, hora_tarea, motivo, nota_rechazo from registros join tareas on registros.tarea = tareas.idtarea where fecha = '{idfecha}' and estado = 'registro' order by fecha desc;")
        estadoanterior = cursor.fetchone()
        if accion == 'agente':
            cursor.execute(f"UPDATE registros SET agente ='{reg_act}' where fecha = '{idfecha}' and estado = 'registro';")
            cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} envió el registro N° ´{idfecha}´ de {estadoanterior[0]} a {reg_act}', date_add(now(), interval -5 hour))")
        if accion == 'tarea':
            cursor.execute(f"UPDATE registros SET tarea = {reg_act} WHERE fecha = '{idfecha}' and estado = 'registro';")
            cursor.execute(f"select tarea from tareas where idtarea = {reg_act}")
            tareavieja = cursor.fetchone()
            no = 'NO SE LE ASIGNÓ NINGUNA TAREA'
            if tareavieja[0] == '':
                tareaold = no
            else:
                tareaold = tareavieja[0]
            if estadoanterior[2] == '':
                estadoold = no
            else:
                estadoold = estadoanterior[2]
            cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} cambió la tarea del registro N° ´{idfecha}´ de {estadoanterior[0]}, pasó de {estadoold.upper()} a {tareaold.upper()}', date_add(now(), interval -5 hour))")
        if accion == 'fecha':
            cursor.execute(f"UPDATE registros SET fecha_tarea = '{reg_act}' WHERE fecha = '{idfecha}' and estado = 'registro';")
            cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} actualizó la fecha de la tarea del registro N° ´{idfecha}´ de {estadoanterior[0]}, pasó del {estadoanterior[3]} para el {reg_act}', date_add(now(), interval -5 hour))")
        if accion == 'hora':
            cursor.execute(f"UPDATE registros SET hora_tarea = '{reg_act.lower()}' WHERE fecha = '{idfecha}' and estado = 'registro';")
            cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} actualizó la hora de la tarea del registro N° ´{idfecha}´ de {estadoanterior[0]}, pasó de las {estadoanterior[4]} para las {reg_act}', date_add(now(), interval -5 hour))")
        if accion == 'motivo':
            cursor.execute(f"UPDATE registros SET motivo = '{reg_act}' where fecha = '{idfecha}' and estado = 'registro';")
            cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} cambió la nota del registro N° ´{idfecha}´ de {estadoanterior[0]}, pasó de {estadoanterior[5]} a {reg_act}', date_add(now(), interval -5 hour))")
        if accion == 'rechazo':
            cursor.execute(f"UPDATE registros SET tarea = 2, nota_rechazo = '{reg_act}' where fecha = '{idfecha}' and estado = 'registro';")
            cursor.execute(f"insert into movimientos (mov, date_mov) VALUES ('{current_user.fullname} cambió el registro N°´{idfecha}´ de {estadoanterior[0]}, se modificó de {estadoanterior[2].upper()} a NO LE INTERESA: {reg_act}', date_add(now(), interval -5 hour))")
        if accion == 'nombre':
            cursor.execute(f"UPDATE registros SET nombre = '{reg_act}' where estado = 'registro' and telefono = '{idfecha}';")
            reg_viejo = request.form['cliente'].upper().strip()
            cursor.execute(f"INSERT INTO movimientos (mov, date_mov) values ('{current_user.fullname} modificó el nombre del cliente {reg_viejo} a {reg_act}', date_add(now(), interval -5 hour));")
        if accion == 'telefono':
            telefono_sn = request.form['agentenuevo']
            telefono = ''
            for n in telefono_sn:
                if n.isdigit():
                    telefono = telefono+n
            cursor.execute(f"UPDATE registros SET telefono = '{telefono}' where telefono = '{idfecha}';")
            reg_viejo = request.form['cliente'].upper().strip()
            cursor.execute(f"INSERT INTO movimientos (mov, date_mov) values ('{current_user.fullname} modificó el telefono del cliente {reg_viejo} a {telefono}', date_add(now(), interval -5 hour));")
        if accion == 'ubicacion':
            cursor.execute(f"UPDATE registros SET direccion = '{reg_act}' where estado = 'registro' and fecha = '{idfecha}';")
            reg_viejo = request.form['cliente'].upper().strip()
            cursor.execute(f"INSERT INTO movimientos (mov, date_mov) values ('{current_user.fullname} modificó la dirección del cliente {reg_viejo} a {reg_act}', date_add(now(), interval -5 hour));")
        if accion == 'email':
            cursor.execute(f"UPDATE registros SET email = '{reg_act.lower().strip()}' where estado = 'registro' and telefono = '{idfecha}';")
            reg_viejo = request.form['cliente'].upper().strip()
            cursor.execute(f"INSERT INTO movimientos (mov, date_mov) values ('{current_user.fullname} modificó el email del cliente {reg_viejo} a {reg_act}', date_add(now(), interval -5 hour));")
        if redireccion == 'seguimiento':
            nombre = request.form['cliente'].strip().upper()
            viejo = request.form['nota']
            if accion == 'tarea_seg':
                cursor.execute(f"select tarea from tareas where idtarea = {reg_act}")
                nuevo = cursor.fetchone()
                nuevo = nuevo[0]
                if nuevo == '':
                    nuevo = 'NO SE LE ASIGNÓ NINGUNA TAREA'
                cursor.execute(f"update registros set tarea = {reg_act} where fecha = '{idfecha}' and estado = 'registro';")
                cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} cambió la tarea del registro N° ´{idfecha}´ de {nombre}, pasó de {viejo} a {nuevo}', date_add(now(), interval -5 hour))")
            if accion == 'fecha_seg':
                cursor.execute(f"UPDATE registros SET fecha_tarea = '{reg_act}' where fecha = '{idfecha}' and estado = 'registro';")
                if viejo == 'None':
                    viejo = 'NO TIENE ASIGNADA NINGUNA FECHA'
                cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} actualizó la fecha de la tarea del registro N° ´{idfecha}´ de {nombre}, pasó del {viejo} para el {reg_act}', date_add(now(), interval -5 hour))")
            if accion == 'hora_seg':
                cursor.execute(f"UPDATE registros set hora_tarea = '{reg_act.lower()}' where fecha = '{idfecha}' and estado = 'registro';")
                if reg_act == '':
                    reg_act = 'SIN HORA'
                if viejo == '':
                    viejo = 'SIN HORA'
                cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} actualizó la hora de la tarea del registro N° ´{idfecha}´ de {nombre}, pasó de las {viejo} para las {reg_act.lower()}', date_add(now(), interval -5 hour))")
            if accion == 'razon':
                cursor.execute(f"UPDATE registros SET nota_rechazo = '{reg_act}' where fecha = '{idfecha}' and estado = 'registro';")
                if viejo == '':
                    viejo = 'NO TIENE UNA RAZÓN CARGADA'
                if reg_act == '':
                    reg_act = 'NO TIENE UNA RAZÓN CARGADA'
                cursor.execute(f"insert into movimientos (mov, date_mov) VALUES ('{current_user.fullname} actualizó la razón de NO LE INTERESA, pasó de {viejo} a {reg_act}, del registro N° ´{idfecha}´ de {nombre}',date_add(now(), interval -5 hour));")
            if accion == 'notas':
                cursor.execute(f"UPDATE registros SET motivo = '{reg_act}' where fecha = '{idfecha}' and estado = 'registro';")
                if reg_act == '':
                    reg_act = 'NO TIENE NOTAS DE LLAMADA CARGADAS'
                if viejo == '':
                    viejo = 'NO TIENE NOTAS DE LLAMADA CARGADAS'
                cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} cambió la nota del registro N° ´{idfecha}´ de {nombre}, pasó de {viejo} a {reg_act}',date_add(now(), interval -5 hour));")
            if accion == 'numero':
                telefono_seg = ''
                for n in reg_act:
                    if n.isdigit():
                        telefono_seg = telefono_seg+n
                cursor.execute(f"UPDATE registros SET telefono = '{telefono_seg}' where telefono = '{viejo}';")
                cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} modificó el telefono del cliente {nombre}, de {viejo} a {telefono_seg}', date_add(now(), interval -5 hour));")
                db.connection.commit()
                cursor.close()
                return seguimiento(telefono_seg)
            if accion == 'direccion':
                cursor.execute(f"UPDATE registros SET direccion = '{reg_act}' where fecha = '{idfecha}' and estado = 'registro';")
                if reg_act == '':
                    reg_act = 'NO TIENE NINGUNA DIRECCIÓN CARGADA'
                cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} modificó la dirección del cliente {nombre} a {reg_act}', date_add(now(), interval -5 hour));")
            if accion == 'correo electronico':
                cursor.execute(f"UPDATE registros SET email = '{reg_act.lower()}' where fecha = '{idfecha}' and estado = 'registro';")
                if reg_act == '':
                    reg_act = 'NO TIENE NINGÚN EMAIL CARGADO'
                cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} modificó el email del cliente {nombre} a {reg_act}', date_add(now(), interval -5 hour));")
            if accion == 'cotizacion':
                cotizacion = request.form['cotizacion'].upper().strip()
                if cotizacion == '':
                    reg_act = 0
                if reg_act == '':
                    reg_act = 0
                if viejo == '':
                    viejo = 0
                cursor.execute(f"UPDATE registros SET cotizacion = '{cotizacion}', cotizaciontotal = {reg_act} where fecha = '{idfecha}' and estado = 'registro';")
                cursor.execute(f"insert into movimientos (mov, date_mov) VALUES ('{current_user.fullname} modificó la cotización del registro N° ´{idfecha}´ del cliente {nombre}, el total pasó de ${viejo} a ${reg_act}', date_add(now(), interval -5 hour))")
            db.connection.commit()
            cursor.close()
            t_seguimiento = request.form['tel_seg']
            return seguimiento(t_seguimiento)
        db.connection.commit()
        cursor.close()
        if redireccion == 'menu':
            menu_empresa = request.form['menu_empresa'].upper().replace(' ','_')
            return refrescarMenu(menu_empresa)
        if redireccion == 'dashboard':
            return redirect(url_for('dashboard'))
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
        cursor.execute(f"SELECT idtarea from tareas where tarea = 'COTIZACIÓN ENVIADA'")
        cotizacion_enviada = cursor.fetchone()
        cursor.execute('select cast(substring(date_add(current_time(), interval -5 hour), 1, 2) as unsigned);')
        hora_actual = cursor.fetchone()
        cursor.execute(f"UPDATE registros SET nombre = '{nombre}', email = '{email}', cotizacion = '{cotizacion}', cotizaciontotal = {totalcotizacion}, fecha_tarea = current_date(), tarea = {cotizacion_enviada[0]}, hora_tarea =  '{hora_actual[0]}:00 h' where fecha = '{fecha}' and estado = 'registro';")
        cursor.execute(f"insert into movimientos (mov, date_mov) VALUES ('{current_user.fullname} envío una cotización de ${totalcotizacion} a {email} del cliente {nombre}', date_add(now(), interval -5 hour))")
        db.connection.commit()
        cursor.close()
    return Response(status=204)

@app.route('/cotizacion/listo', methods=['GET', 'POST'])
@login_required
def cotizacionListo():
    if request.method == 'POST':
        fecha = request.form['cotizacion_listo']
        cursor = db.connection.cursor()
        cursor.execute(f"UPDATE registros SET estado = 'listo' WHERE fecha = '{fecha}' and estado = 'registro';")
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
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} agregó una nueva tarea al sistema: {tarea}', date_add(now(), interval -5 hour));")
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
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} eliminó del sistema la tarea {tarea}', date_add(now(), interval -5 hour));")
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
        cursor.execute(f"insert into movimientos (mov, date_mov) VALUES ('{current_user.fullname} editó la tarea {tareavieja}. Ahora es {tareanueva}', date_add(now(), interval -5 hour));")
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
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} agregó un nuevo plan al sistema: {plan}', date_add(now(), interval -5 hour));")
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
        cursor.execute(f"insert into movimientos (mov, date_mov) values ('{current_user.fullname} eliminó del sistema el plan {plan}', date_add(now(), interval -5 hour));")
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
        cursor.execute(f"insert into movimientos (mov, date_mov) VALUES ('{current_user.fullname} editó un plan, se actualizó a {plan}', date_add(now(), interval -5 hour));")
        db.connection.commit()
        cursor.close()
        return redirect(url_for('planes'))
    return Response(status=204)

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
            cursor.execute(f"SELECT fecha_emision, nombre, direccion, telefono, servicio, objeto, notas, total, enganche, total-enganche, idfecha, tipopago, acuerdo_1, interes_1, fecha_1, acuerdo_2, interes_2, fecha_2, acuerdo_3, interes_3, fecha_3, acuerdo_4, interes_4, fecha_4, notapago, COALESCE(acuerdo_1, 0)+COALESCE(acuerdo_2, 0)+COALESCE(acuerdo_3, 0)+COALESCE(acuerdo_4, 0), empresa from hojas where idfecha = '{fecha}' and cantidad is null and material is null;")
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
            cursor.execute(f"SELECT current_date(), nombre, direccion, telefono, '', '', '', 0, 0, '', fecha, '', '', '', '','','','','','','','','','','','', '{empresa}' from registros where fecha = '{fecha}' and estado = 'registro';")
            hoja = cursor.fetchone()
            materiales = None
            n_cuotas = 0
        cursor.close()
        return render_template('hojainspeccion.html', condicional=condicional, hoja=hoja, materiales=materiales, n_hoja=n_hoja, n_materiales=n_materiales, n_cuotas=n_cuotas)
    return Response(status=204)

@app.route('/hoja_de_inspeccion/guardar', methods=['POST'])
@login_required
def guardar_en_mysql():
    data = request.json
    tabla_data = data['materiales']
    datos_data = data['datos']
    accion_data = data['accion']
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
    if accion_data == 'actualizar':
        cursor.execute(f"DELETE from hojas where idhoja = '{datos_data[0]}' and idfecha = '{datos_data[1]}'")
        movimiento = "actualizó la"
    cursor.execute(f"INSERT INTO hojas (idhoja, idfecha, fecha_emision, nombre, direccion, telefono, servicio, objeto, notas, total, enganche, tipopago, acuerdo_1, interes_1, fecha_1, acuerdo_2, interes_2, fecha_2, acuerdo_3, interes_3, fecha_3, acuerdo_4, interes_4, fecha_4, notapago, empresa) VALUES ({datos_data[0]}, '{datos_data[1]}', '{datos_data[2]}', '{datos_data[3].upper().strip()}', '{datos_data[4].upper().strip()}', '{telefono}', '{datos_data[6]}', '{datos_data[7].upper().strip()}', '{datos_data[8].upper().strip()}', {datos_data[9]}, {datos_data[10]}, '{datos_data[11]}', {datos_data[12]}, {datos_data[13]}, '{datos_data[14]}', {datos_data[15]}, {datos_data[16]}, '{datos_data[17]}', {datos_data[18]}, {datos_data[19]}, '{datos_data[20]}', {datos_data[21]}, {datos_data[22]}, '{datos_data[23]}', '{datos_data[24].strip().upper()}', '{datos_data[25].strip().upper()}')")
    cursor.execute("UPDATE hojas SET fecha_1 = null, fecha_2 = null, fecha_3 = null, fecha_4 = null where tipopago = 'totalidad' or tipopago = '';")
    for f in range (1,5):
        cursor.execute(f"UPDATE hojas SET fecha_{f} = null where fecha_{f} = '0000-00-00';")
    for row in tabla_data:
            if row != [] and row != ['', '']:
                cursor.execute(f"INSERT INTO hojas (idhoja, idfecha, cantidad, material) VALUES ({datos_data[0]}, '{datos_data[1]}', {row[0]}, '{row[1].upper().strip()}')")
    if datos_data[11] == 'totalidad':
        cursor.execute(f"INSERT INTO pagos (empresa, motivo, idhoja, cliente, telefono, fecha_vencimiento, fecha_pago, forma_pago, pago, agente) VALUES ('{datos_data[25].strip().upper()}', 'ABONÓ TODO', {datos_data[0]}, '{datos_data[3].upper(). strip()}', '{telefono}', '{datos_data[2]}', '{datos_data[2]}', '{datos_data[26].upper().strip()}', {datos_data[9]}, '{current_user.fullname}');")
    #print(datos_data)
    cursor.execute(f"insert into movimientos (mov, date_mov) VALUES ('{current_user.fullname} {movimiento} hoja de inspección N°´{datos_data[0]}´ del cliente {datos_data[3].upper().strip()}', date_add(now(), interval -5 hour));")
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

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(401, pagina_no_autorizada)
    app.register_error_handler(404, pagina_no_encontrada)
    #app.run(debug=True, port=5001)
    app.run(debug=False, port=30358, host='admin.losandestx.com')