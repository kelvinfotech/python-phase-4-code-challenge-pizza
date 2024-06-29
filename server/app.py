#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
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

@app.route("/restaurants", methods=['GET'])
def get_restaurants():
    restaurant_list = [restaurant.to_dict(rules=("-restaurant_pizzas",)) for restaurant in Restaurant.query.all()]
    return make_response(restaurant_list, 200)

@app.route("/restaurants/<int:id>", methods=['GET'])
def get_restaurants_by_id(id):
    restaurant_by_id = Restaurant.query.filter_by(id=id).one_or_none()
    if restaurant_by_id is not None:
        return make_response(restaurant_by_id.to_dict(), 200)
    else:
        return make_response({"error":"Restaurant not found"}, 404)

@app.route("/restaurants/<int:id>", methods=['DELETE'])
def delete_restaurant_by_id(id):
    restaurant_by_id = Restaurant.query.filter_by(id=id).one_or_none()
    if restaurant_by_id:
        RestaurantPizza.query.filter_by(restaurant_id=id).delete()
        db.session.delete(restaurant_by_id)
        db.session.commit()
        return make_response('', 204)
    else:
        return make_response({"error": "Restaurant not found"}, 404)

@app.route("/pizzas", methods=['GET'])
def get_pizzas():
    all_pizzas = Pizza.query.all()
    pizzas_get = [{'id':pizza.id, 'name':pizza.name, 'ingredients': pizza.ingredients} for pizza in all_pizzas]
    return make_response(pizzas_get), 200

@app.route("/restaurant_pizzas", methods=['POST'])
def create_restaurant_pizza():
    try:
        data = request.get_json()
        new_restaurant_pizza = RestaurantPizza(price=data["price"], pizza_id=data["pizza_id"], restaurant_id=data["restaurant_id"])
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        return make_response(new_restaurant_pizza.to_dict(), 201)
    except ValueError:
        return make_response({"errors":["validation errors"]}, 400)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
