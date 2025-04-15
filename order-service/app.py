from flask import Flask, jsonify, abort, request
import requests


app = Flask(__name__)


# In-memory storage for orders
orders = []

# POST a new order
@app.route('/order', methods=['POST'])
def create_order():
    if not request.json or 'product_id' not in request.json or 'quantity' not in request.json:
        abort(400, description="Missing order data")

    
    product_id = request.json['product_id']
    
    # calling catalog service to check if the product exists
    catalog_url = f'http://127.0.0.1:5001/catalog/{product_id}'
    response = requests.get(catalog_url)
    if response.status_code != 200:
        abort(404, description="Product not found in catalog")
    else:
        print(f"{product_id} found in catalog service")

    # Add the orrder to the in-memory storage
    new_order = {
        'id': len(orders) +1,
        "priduct_id": request.json['product_id'],
        "quantity": request.json['quantity'],
        "status": "created"
    }

    orders.append(new_order)
    return jsonify(new_order), 201

# GET an order by id
@app.route('/order/<int:order_idx>', methods=['GET'])
def get_order(order_idx: int):
    order = next((o for o in orders if o['id'] == order_idx), None)
    if order is None:
        abort(404, description="Order not found")
    return jsonify(order)

if __name__=="__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)
