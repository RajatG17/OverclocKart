import requests

from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

## Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# # In-memory storage for orders
# orders = []

## Creating an Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="created")

    def as_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'status': self.status
        }

## create database if it dosen;t exist
with app.app_context():
    db.create_all()

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

    # # Add the orrder to the in-memory storage
    # new_order = {
    #     'id': len(orders) +1,
    #     "priduct_id": request.json['product_id'],
    #     "quantity": request.json['quantity'],
    #     "status": "created"
    # }

    # orders.append(new_order)

    ## Create and add ordert to the database
    new_order = Order(product_id=product_id, quantity=request.json['quantity'], status="created")
    db.session.add(new_order)
    db.session.commit()

    return jsonify(new_order.as_dict()), 201

# GET an order by id
@app.route('/order/<int:order_idx>', methods=['GET'])
def get_order(order_idx: int):
    order = Order.query.get(order_idx)
    if order is None:
        abort(404, description="Order not found")
    return jsonify(order.as_dict())

if __name__=="__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)
