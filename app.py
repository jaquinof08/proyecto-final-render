import os
from flask import Flask, request, render_template_string, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import smtplib # Importamos la librería para correos

app = Flask(__name__)

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
db_url = os.environ.get("DATABASE_URL", "sqlite:///test.db")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELO DE LA BASE DE DATOS (LA TABLA) ---
class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    dni = db.Column(db.String(8), unique=True, nullable=False)

with app.app_context():
    db.create_all()

# --- CÓDIGO DEL FORMULARIO HTML ---
HTML_FORMULARIO = """
<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><title>Registro - Proyecto con DB</title>
<style>body{font-family:sans-serif;max-width:500px;margin:40px auto;padding:25px;border:1px solid #e1e1e1;border-radius:12px}h2,h3{text-align:center}label{display:block;margin-top:20px}input{width:100%;padding:10px;margin-top:5px;box-sizing:border-box;border-radius:6px;border:1px solid #ccc}button{display:block;width:100%;background-color:#007bff;color:white;padding:12px;border:none;border-radius:6px;cursor:pointer;margin-top:25px;font-size:16px}a{display:block;text-align:center;margin-top:20px}</style>
</head><body><h2>Formulario de Registro</h2><form action="/registrar" method="POST"><label for="nombre">Nombre:</label><input type="text" id="nombre" name="nombre" required><label for="apellido">Apellido:</label><input type="text" id="apellido" name="apellido" required><label for="dni">DNI:</label><input type="text" id="dni" name="dni" required maxlength="8" pattern="[0-9]{8}"><button type="submit">Guardar y Enviar</button></form><a href="/registros">Ver todos los registros</a></body></html>
"""

# --- RUTA PRINCIPAL QUE MUESTRA EL FORMULARIO ---
@app.route('/')
def index():
    return render_template_string(HTML_FORMULARIO)

# --- RUTA QUE GUARDA EN DB Y ENVÍA CORREO ---
@app.route('/registrar', methods=['POST'])
def registrar():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    dni = request.form['dni']
    
    # Guardar en la base de datos
    nuevo_registro = Registro(nombre=nombre, apellido=apellido, dni=dni)
    db.session.add(nuevo_registro)
    db.session.commit()
    
    # Enviar el correo electrónico
    try:
        remitente = "tu_correo@gmail.com"  # <<< TU CORREO DE GMAIL
        password = "tu_contraseña_de_aplicacion" # <<< TU CONTRASEÑA DE APLICACIÓN DE GOOGLE
        destinatario = ["jaquinof@autonoma.edu.pe"
                        josephzx12@gmail.com]
        asunto = f"Nuevo Registro: {nombre} {apellido}"
        mensaje = f"Se ha registrado un nuevo usuario:\n\nNombre: {nombre}\nApellido: {apellido}\nDNI: {dni}"
        email_body = f"Subject: {asunto}\n\n{mensaje}"

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(remitente, password)
            smtp.sendmail(remitente, destinatario, email_body.encode('utf-8'))
    except Exception as e:
        print(f"Error al enviar correo: {e}") # Esto mostrará el error en los logs de Render

    return redirect(url_for('ver_registros'))

# --- RUTA PARA VER TODOS LOS REGISTROS ---
@app.route('/registros')
def ver_registros():
    todos_los_registros = Registro.query.all()
    html_respuesta = "<h2>Registros Guardados</h2><table border='1' style='width:100%;text-align:center;'><tr><th>ID</th><th>Nombre</th><th>Apellido</th><th>DNI</th></tr>"
    for registro in todos_los_registros:
        html_respuesta += f"<tr><td>{registro.id}</td><td>{registro.nombre}</td><td>{registro.apellido}</td><td>{registro.dni}</td></tr>"
    html_respuesta += "</table><br><a href='/'>Volver al formulario</a>"
    return html_respuesta
