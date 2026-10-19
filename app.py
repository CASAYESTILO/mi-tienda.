
import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Rutas absolutas a prueba de fallos para Render
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

# Configuraciones de seguridad obligatorias
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tienda_secreta_123')

# Conexión directa con PostgreSQL de Render o SQLite local
Mostrar texto citado
# RUTAS DE LA APLICACIÓN
# ==========================================

@app.route('/')
def catalogo():
    try:
        lista_productos = Producto.query.all()
    except Exception:
        lista_productos = []
