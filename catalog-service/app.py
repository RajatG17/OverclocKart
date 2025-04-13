from flask import Flask, jsonify, abort, request

app = Flask(__name__)

@app.route('/')
def _hello_world():
    return "<h1>Hello, World!</h1>"

##  "database" for the sake of example
products = [
    {'id': 1, 'name': 'Product 1', 'price': 10.0},
    {'id': 2, 'name': 'Product 2', 'price': 20.0},
    {'id': 3, 'name': 'Product 3', 'price': 30.0},
]

## GET all products
@app.route('/catalog', methods=['GET'])
def get_products():
    return jsonify(products)

## GET product by id
@app.route('/catalog/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product is None:
        abort(404, description='Product not found')
    return jsonify(product)

## POST new product
@app.route('/catalog', methods=['POST'])
def add_product():
    if not request.json or 'name' not in request.json or 'price' not in request.json:
        abort(400, description='Missing Data')
    new_id = max(p['id'] for p in products) +1 if products else 1
    new_product = {
        'id': new_id,
        'name': request.json['name'],
        'price': request.json['price']
    }

    products.append(new_product)
    return jsonify(new_product), 201

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
