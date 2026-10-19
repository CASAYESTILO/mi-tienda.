import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')
app = Flask(__name__, template_folder=template_dir)

# Configuraciones de seguridad para Render
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tienda_secreta_123')

# Conexión con PostgreSQL para Render o SQLite para pruebas locales
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///catalogo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# MODELOS DE BASE DE DATOS
class UsuarioAdmin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Float, nullable=False)
    imagen_url = db.Column(db.String(500), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return UsuarioAdmin.query.get(int(user_id))

# RUTAS PÚBLICAS
@app.route('/')
def catalogo():
    lista_productos = Producto.query.all()
    return render_template('catalogo.html', productos=lista_productos)

# RUTAS DE ADMINISTRACIÓN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('username')
        clave = request.form.get('password')
        user = UsuarioAdmin.query.filter_by(username=usuario).first()
        if user and user.password == clave:
            login_user(user)
            flash('¡Bienvenido al panel!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('catalogo'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if request.method == 'POST':
        nuevo_producto = Producto(
            nombre=request.form.get('nombre'),
            descripcion=request.form.get('descripcion'),
            precio=float(request.form.get('precio')),
            imagen_url=request.form.get('imagen_url')
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        flash('Producto agregado con éxito', 'success')
        return redirect(url_for('admin_panel'))
    lista_productos = Producto.query.all()
    return render_template('admin.html', productos=lista_productos)

@app.route('/admin/eliminar/<int:id>')
@login_required
def eliminar_producto(id):
    prod = Producto.query.get_or_404(id)
    db.session.delete(prod)
    db.session.commit()
    flash('Producto eliminado', 'warning')
    return redirect(url_for('admin_panel'))

# CREACIÓN AUTOMÁTICA DE BASE DE DATOS Y USUARIO POR DEFECTO
with app.app_context():
    db.create_all()
    if not UsuarioAdmin.query.filter_by(username='admin').first():
        admin_defecto = UsuarioAdmin(username='admin', password='AdminPassword123')
        db.session.add(admin_defecto)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
