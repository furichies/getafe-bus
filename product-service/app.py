from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
client = MongoClient('mongodb://localhost:27017/')
db = client['productos_db']

@app.route('/api/productos', methods=['GET'])
def get_productos():
    categoria = request.args.get('categoria')
    productos = list(db.productos.find({'categoria': categoria}, {'_id': 0}))
    return jsonify(productos), 200

@app.route('/api/productos/<string:product_id>', methods=['GET'])
def get_producto(product_id):
    producto = db.productos.find_one({'id': product_id}, {'_id': 0})
    if producto:
        return jsonify(producto), 200
    return jsonify({'error': 'Producto no encontrado'}), 404

if __name__ == '__main__':
    app.run(port=5001)
