import os
from flask import Flask, request, render_template_string, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Inicialización de la aplicación Flask
app = Flask(__name__)

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
# Lee la URL de la base de datos desde el entorno de Render
db_url = os.environ.get("DATABASE_URL", "sqlite:///test.db")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELO DE LA BASE DE DATOS ---
# Define la estructura de la tabla 'Registro'
class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    dni = db.Column(db.String(8), unique=True, nullable=False)

# Crea la tabla en la base de datos si no existe al iniciar la app
with app.app_context():
    db.create_all()

# --- CÓDIGO DEL FORMULARIO HTML ---
HTML_FORMULARIO = """
<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Registro</title><style>body{font-family:sans-serif;max-width:500px;margin:40px auto;padding:25px;border:1px solid #e1e1e1;border-radius:12px}h2{text-align:center}label{display:block;margin-top:20px;font-weight:bold}input{width:100%;padding:10px;margin-top:5px;box-sizing:border-box;border-radius:6px;border:1px solid #ccc}button{display:block;width:100%;background-color:#007bff;color:white;padding:12px;border:none;border-radius:6px;cursor:pointer;margin-top:25px;font-size:16px}a{display:block;text-align:center;margin-top:20px}</style></head><body><h2>Formulario de Registro del Proyecto</h2><form action="/registrar" method="POST"><label for="nombre">Nombre:</label><input type="text" id="nombre" name="nombre" required><label for="apellido">Apellido:</label><input type="text" id="apellido" name="apellido" required><label for="dni">DNI:</label><input type="text" id="dni" name="dni" required maxlength="8" pattern="[0-9]{8}"><button type="submit">Guardar y Enviar</button></form><a href="/registros">Ver todos los registros</a></body></html>
"""

# --- RUTA PRINCIPAL QUE MUESTRA EL FORMULARIO ---
@app.route('/')
def index():
    return render_template_string(HTML_FORMULARIO)

# --- RUTA QUE GUARDA EN DB Y ENVÍA CORREO ---
@app.route('/registrar', methods=['POST'])
def registrar():
    # Guardar en la base de datos
    nuevo_registro = Registro(nombre=request.form['nombre'], apellido=request.form['apellido'], dni=request.form['dni'])
    db.session.add(nuevo_registro)
    db.session.commit()
    
    # Bloque para intentar enviar el correo
    try:
        # --- CONFIGURACIÓN DEL CORREO ---
        remitente = "josephzx12@gmail.com"      # <<< ¡IMPORTANTE! TU CORREO DE GMAIL
        password = "ghinbxjeafewpggy"     # <<< ¡IMPORTANTE! TU CONTRASEÑA DE APP DE 16 LETRAS
        
        # Lista de correos a los que se enviará la notificación
        destinatarios = ["josephzx12@gmail.com", "jaquinof@autonoma.edu.pe"]
        
        # Crear el objeto del mensaje
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = ", ".join(destinatarios)
        msg['Subject'] = f"Nuevo Registro en el Proyecto: {request.form['nombre']} {request.form['apellido']}"
        
        # Cuerpo del mensaje
        cuerpo_del_correo = f"Se ha registrado un nuevo usuario en la plataforma:\n\nNombre: {request.form['nombre']}\nApellido: {request.form['apellido']}\nDNI: {request.form['dni']}"
        
        # Adjuntar el cuerpo del mensaje con la codificación correcta (UTF-8)
        msg.attach(MIMEText(cuerpo_del_correo, 'plain', 'utf-8'))
        
        # Enviar el correo
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(remitente, password)
            smtp.sendmail(remitente, destinatarios, msg.as_string())
            
    except Exception as e:
        # Si algo falla al enviar el correo, se imprimirá el error en los logs de Render
        print(f"Error al enviar correo: {e}")

    # Redirigir a la página que muestra todos los registros
    return redirect(url_for('ver_registros'))

# --- RUTA PARA VER TODOS LOS REGISTROS ---
@app.route('/registros')
def ver_registros():
    registros = Registro.query.all()
    html = "<h2>Registros Guardados</h2><table border='1' style='width:100%;text-align:center;'><tr><th>ID</th><th>Nombre</th><th>Apellido</th><th>DNI</th></tr>"
    for r in registros:
        html += f"<tr><td>{r.id}</td><td>{r.nombre}</td><td>{r.apellido}</td><td>{r.dni}</td></tr>"
    html += "</table><br><a href='/'>Volver al formulario</a>"
    return html
