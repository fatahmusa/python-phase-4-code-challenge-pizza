#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants')
def get_restaurants():
    restaurants= Restaurant.query.all()
    return jsonify([restaurant.to_dict(include_pizzas=False) for restaurant in restaurants]), 200

@app.route('/restaurants/<int:id>')
def get_restaurant(id):
    restaurant= db.session.get(Restaurant, id)
    if restaurant is None:
        return jsonify({
        'error': 'Restaurant not found'
    }), 404

    return jsonify(restaurant.to_dict(include_pizzas=True)), 200

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def deletes_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant is None:
        return jsonify({'error': 'Restaurant not found'}), 404

    db.session.delete(restaurant)
    db.session.commit()

    return '', 204

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas= Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas]), 200

@app.route('/restaurant_pizzas', methods=['POST'])
def creates_restaurant_pizzas():
    data = request.get_json()
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')
    price = data.get('price')

    if not pizza_id or not restaurant_id or price is None:
        return jsonify({'error': 'Missing data'}), 400

    if not (1<= price <=30):
        return jsonify({'errors': ["validation errors"]}), 400
    
    pizza = db.session.get(Pizza, pizza_id)
    restaurant = db.session.get(Restaurant, restaurant_id)

    if not pizza or not restaurant:
        return jsonify({'error': 'Pizza or Restaurant not found'}), 404

    restaurant_pizza = RestaurantPizza( pizza_id=pizza_id, restaurant_id=restaurant_id, price=price)
    db.session.add(restaurant_pizza)
    db.session.commit()

    return jsonify({
        "id": restaurant_pizza.id,
        "price": restaurant_pizza.price,
        "pizza_id": restaurant_pizza.pizza_id,
        "restaurant_id": restaurant_pizza.restaurant_id,
        "pizza": {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients
        },
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address
        }
        
    }), 201


    
    


if __name__ == "__main__":
    app.run(port=5555, debug=True)
