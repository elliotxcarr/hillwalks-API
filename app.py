from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)


client = MongoClient("mongodb://localhost:27017/")
db = client["walking_db"]
walksCollection = db["hillwalks"]
usersCollection = db["users"]

@app.route("/walks", methods=["GET"])
def get_walks():
    walks = list(walksCollection.find({}, {"_id": 0})) 
    return jsonify(walks)

@app.route("/users", methods=["GET"])
def get_users():
    users = list(usersCollection.find({}, {"_id":0}))
    return jsonify(users)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
