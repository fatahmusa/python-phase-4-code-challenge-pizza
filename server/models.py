from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin


metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)



class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    
    # Relationship mapping the restaurant to related restaurant_pizzas
    
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='restaurant', cascade='all, delete-orphan')
    
    # Association proxy to get pizzas for this restaurant through restaurant_pizzas
    pizzas = association_proxy('restaurant_pizzas', 'pizza',
                                 creator=lambda pizza_obj: RestaurantPizza(pizza=pizza_obj))
   
    # add serialization rules
    serialize_rules = ('-pizzas',)

    def __repr__(self):
        return f"<Restaurant {self.name}>"

    def to_dict(self, include_pizzas=False):
        data = {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "pizzas": [pizza.id for pizza in self.pizzas],
                  
        }

        if include_pizzas:
            data["restaurant_pizzas"] = [rp.to_dict() for rp in self.restaurant_pizzas]
        return data


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship

    # Relationship mapping the pizza to related restaurant_pizzas
    restaurant_pizzas = db.relationship(
        'RestaurantPizza', back_populates='pizza', cascade='all, delete-orphan')
    
    # Association proxy to get restaurants for this pizza through restaurant_pizzas
    restaurants = association_proxy('restaurant_pizzas', 'restaurant',
                                  creator=lambda restaurant_obj: RestaurantPizza(restaurant=restaurant_obj))

    # add serialization rules
    serialize_rules = ('-restaurants',)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "ingredients": self.ingredients,
            "restaurants": [restaurant.to_dict() for restaurant in self.restaurants] 
        }


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)


    # add relationships
   
    # Foreign key to store the restaurant id
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))

    # Foreign key to store the pizza id
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))
    
    # Relationship mapping the RestaurantPizza to related restaurant
    restaurant = db.relationship('Restaurant', back_populates='restaurant_pizzas')
    
    # Relationship mapping the RestaurantPizza to related pizza
    pizza = db.relationship('Pizza',back_populates='restaurant_pizzas')
    

    # add serialization rules
    serialize_rules = ('-restaurant', '-pizza')
    
    # add validation

    @validates('price')
    def validate_price(self, key, price):
        if not (1 <= price <= 30):
            raise ValueError("Price must be between 1 and 30")
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
    def to_dict(self):
        return {
            "id": self.id,
            "price": self.price,
            "restaurant_id": self.restaurant_id,
            "pizza_id": self.pizza_id
        }