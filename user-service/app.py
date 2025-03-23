from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import random
import string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(10), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

@app.route('/api/usuarios/registro', methods=['POST'])
def registro():
    data = request.get_json()
    if User.query.filter_by(dni=data['dni']).first() or User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Usuario ya existe'}), 400

    password = generate_password()
    new_user = User(
        nombre=data['nombre'],
        dni=data['dni'],
        email=data['email']
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'mensaje': 'Usuario registrado', 'contraseña': password}), 201

@app.route('/api/usuarios/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(dni=data['dni']).first()
    if user and user.check_password(data['contraseña']):
        return jsonify({'mensaje': 'Login exitoso', 'user_id': user.id}), 200
    return jsonify({'error': 'Credenciales inválidas'}), 401

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000)
