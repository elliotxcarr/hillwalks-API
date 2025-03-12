from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)


client = MongoClient("mongodb://localhost:27017/")
db = client["walking_db"]
collection = db["hillwalks"]

@app.route("/walks", methods=["GET"])
def get_walks():
    walks = list(collection.find({}, {"_id": 0})) 
    return jsonify(walks)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
