
import logging
import os

from flask import Flask, jsonify, abort, request, Response
from flask_sqlalchemy import SQLAlchemy
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

REQUEST_COUNT = Counter("catalog_requests_total", "Total requests to catalog", ["method", "endpoint", "http_status"])

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

@app.before_request
def log_request():
    app.logger.info(f"-> {request.method} {request.path} {request.get_json(silent=True)}")

@app.after_request
def log_response(response):
    app.logger.info(f"<- {request.method} {request.path} {response.status_code}")
    return response

@app.after_request
def after_request(response):
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    return response

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.get('/health')
def health():
    return {"status": "ok"}

@app.route('/')
def _hello_world():
    return "<h1>Hello, World!</h1>"

# ##  "database" for the sake of example
# products = [
#     {'id': 1, 'name': 'Product 1', 'price': 10.0},
#     {'id': 2, 'name': 'Product 2', 'price': 20.0},
#     {'id': 3, 'name': 'Product 3', 'price': 30.0},
# ]

## Congiguring the SQLite database
db_path = os.getenv("DB_PATH", "catalog.db")  # still works outside Docker
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
db = SQLAlchemy(app)

## Defining the Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price
        }

# create database and table => runs during startup if the database does not exist
with app.app_context():
    db.create_all()

## GET all products
@app.route('/catalog', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([p.as_dict() for p in products])


## GET product by id
@app.route('/catalog/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        abort(404, description='Product not found')
    return jsonify(product.as_dict())

## POST new product
@app.route('/catalog', methods=['POST'])
def add_product():
    if not request.json or 'name' not in request.json or 'price' not in request.json:
        abort(400, description='Missing Data')
    # new_id = max(p['id'] for p in products) +1 if products else 1
    # new_product = {
    #     'id': new_id,
    #     'name': request.json['name'],
    #     'price': request.json['price']
    # }
    # products.append(new_product)

    new_product = Product(
        name=request.json['name'],
        price=request.json['price']
    )

    db.session.add(new_product)
    db.session.commit()
    
    return jsonify(new_product.as_dict()), 201

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
