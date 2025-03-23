from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import redis
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
db = SQLAlchemy(app)
cache = redis.Redis(host='localhost', port=6379)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    productos = db.Column(db.JSON, nullable=False)
    total = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, server_default=db.func.now())

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    cart_key = f"cart:{data['user_id']}"
    item = {
        'product_id': data['product_id'],
        'proveedor': data['proveedor'],
        'cantidad': data['cantidad'],
        'precio': data['precio']
    }
    cache.rpush(cart_key, json.dumps(item))
    return jsonify({'mensaje': 'Producto añadido'}), 200

@app.route('/api/cart/<int:user_id>', methods=['GET'])
def view_cart(user_id):
    cart_key = f"cart:{user_id}"
    items = cache.lrange(cart_key, 0, -1)
    productos = [json.loads(item) for item in items]
    total = sum(p['precio'] * p['cantidad'] for p in productos)
    return jsonify({'productos': productos, 'total': total}), 200

@app.route('/api/ordenes', methods=['POST'])
def checkout():
    data = request.get_json()
    user_id = data['user_id']
    cart_key = f"cart:{user_id}"
    items = cache.lrange(cart_key, 0, -1)
    if not items:
        return jsonify({'error': 'Carrito vacío'}), 400

    productos = [json.loads(item) for item in items]
    total = sum(p['precio'] * p['cantidad'] for p in productos)
    
    new_order = Order(user_id=user_id, productos=productos, total=total)
    db.session.add(new_order)
    db.session.commit()
    cache.delete(cart_key)
    return jsonify({'mensaje': 'Compra realizada', 'total': total}), 201

@app.route('/api/ordenes/<int:user_id>', methods=['GET'])
def historial(user_id):
    orders = Order.query.filter_by(user_id=user_id).all()
    result = [{'id': o.id, 'productos': o.productos, 'total': o.total, 'fecha': o.fecha} for o in orders]
    return jsonify(result), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5002)
