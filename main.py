from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from typing import Callable
import random

app = Flask(__name__)


#Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class MySQLAlchemy(SQLAlchemy):
    Column: Callable
    String: Callable
    Integer: Callable
    Float: Callable
    Model: Callable
    Boolean: Callable


db = MySQLAlchemy(app)



#Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        #Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            #Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

    # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
    # return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def __repr__(self):
        return f'<Cafe {self.name}'


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random", methods=["GET"])
def random_cafe():
    all_cafes = db.session.query(Cafe).all()
    cafe_random = random.choice(all_cafes)
    return jsonify(id=cafe_random.id,
                   name=cafe_random.name,
                   map_url=cafe_random.map_url,
                   img_url=cafe_random.img_url,
                   location=cafe_random.location,
                   has_sockets=cafe_random.has_sockets,
                   has_toilet=cafe_random.has_toilet,
                   has_wifi=cafe_random.has_wifi,
                   can_take_calls=cafe_random.can_take_calls,
                   seats=cafe_random.seats,
                   coffee_price=cafe_random.coffee_price)


@app.route("/all", methods=["GET"])
def all_cafes():
    all_cafes = db.session.query(Cafe).all()
    cafe_list = []
    for cafe in all_cafes:
        cafe_list.append(cafe.to_dict())
    cafe_dict = {"cafes": cafe_list}
    cafe_json = jsonify(cafe_dict)
    return cafe_json


@app.route("/search", methods=["GET"])
def search():
    location_search = request.args.get("loc")
    if location_search:
        location_search = location_search.title()
        result = [cafe.to_dict() for cafe in Cafe.query.filter_by(location=location_search).all()]
        if result:
            return jsonify(cafe=result)
        else:
            return jsonify(error={"not found": "Sorry we don't have a cafe at that location"})
    else:
        return jsonify(error={"not found": "Sorry we don't have a cafe at that location"})


@app.route("/add", methods=["POST"])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=int(request.form.get("sockets")),
        has_toilet=int(request.form.get("toilet")),
        has_wifi=int(request.form.get("wifi")),
        can_take_calls=int(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price")
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response = {"success": "successfully added new cafe" })


@app.route("/update-price/<cafe_id>", methods=["POST"])
def update_price(cafe_id):
    cafe_to_update = Cafe.query.filter_by(id=cafe_id).first()
    new_price = request.args.get("new_price")
    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "successfully updated coffee price"}), 200
    else:
        return jsonify(error={"Not Found": "Cafe with that ID does not exist"}), 404


@app.route("/report-closed/<cafe_id>", methods=["POST"])
def delete_cafe(cafe_id):
    user_api = request.args.get("api-key")
    if user_api == "TopSecretAPIKey":
        cafe_to_delete = Cafe.query.get(cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            return jsonify(response={"success": "You reported the cafe closed"}), 200
        else:
            return jsonify(error={"Not Found": "Cafe with that ID does not exist"}), 404
    else:
        return jsonify(error={"Failed": "You do not have permission. Make sure you have the correct API key"}), 403

## HTTP GET - Read Record

## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
