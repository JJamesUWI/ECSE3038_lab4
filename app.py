from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from datetime import datetime
import linecache

# Username in line 1 and password in line 2 of text file (store.txt)
filename = "store.txt"
uname = linecache.getline(filename, 1).strip()
upass = linecache.getline(filename, 2).strip()

# Updating postgres URI with extracted credentials
uri_update1 = "postgres://{}:{}@ziggy.db.elephantsql.com:5432/{}".format(
    uname, upass, uname)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = uri_update1
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

profile_obj = {}


class Tank(db.Model):
    __tablename__ = "Tanks"

    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(50), unique=True, nullable=False)
    lat = db.Column(db.String(50), nullable=False)
    long = db.Column(db.String(50), nullable=False)
    percentage_full = db.Column(db.Integer, nullable=False)


class TankSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Tank
        fields = ("id", "location", "lat", "long", "percentage_full")


db.init_app(app)
migrate = Migrate(app, db)

# GET /profile


@app.route("/profile", methods=["GET"])
def get_profile():
    return profile_obj

# POST /profile


@app.route("/profile", methods=["POST"])
def post_profile():
    profile_obj["username"] = request.json["username"]
    profile_obj["role"] = request.json["role"]
    profile_obj["color"] = request.json["color"]
    profile_obj["last_updated"] = datetime.now()

    return {
        "success": True,
        "data": profile_obj
    }

# PATCH /profile


@app.route("/profile", methods=["PATCH"])
def patch_profile():
    if "username" in request.json:
        profile_obj["username"] = request.json["username"]

    if "role" in request.json:
        profile_obj["role"] = request.json["role"]

    if "color" in request.json:
        profile_obj["color"] = request.json["color"]

    profile_obj["last_updated"] = datetime.now()

    return {
        "success": True,
        "data": profile_obj
    }

# GET /data


@app.route("/data", methods=["GET"])
def get_data():
    Tanks = Tank.query.all()
    tanks_view = TankSchema(many=True).dump(Tanks)
    return jsonify(tanks_view)

# POST /data


@app.route("/data", methods=["POST"])
def post_data():
    addTank = Tank(
        location=request.json["location"],
        lat=request.json["lat"],
        long=request.json["long"],
        percentage_full=request.json["percentage_full"]
    )
    db.session.add(addTank)
    db.session.commit()
    return TankSchema().dump(addTank)

# PATCH /data/:id


@app.route("/data/<int:id>", methods=["PATCH"])
def patch_data(id):
    patchTank = Tank.query.get(id)
    patch = request.json
    if "location" in patch:
        patchTank.location = patch["location"]
    if "lat" in patch:
        patchTank.lat = patch["lat"]
    if "long" in patch:
        patchTank.long = patch["long"]
    if "percentage_full" in patch:
        patchTank.percentage_full = patch["percentage_full"]

    db.session.commit()
    return TankSchema().dump(patchTank)

# DELETE /data/:id


@app.route("/data/<int:id>", methods=["DELETE"])
def delete_data(id):
    delTank = Tank.query.get(id)
    db.session.delete(delTank)
    db.session.commit()

    return {
        "success": True
    }


if __name__ == "__main__":
    app.run(debug=True)
