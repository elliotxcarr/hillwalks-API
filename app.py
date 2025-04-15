from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId

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
    users = list(usersCollection.find({}))
    
    for user in users:
        user["_id"] = str(user["_id"])
    return jsonify(users)

@app.route('/login', methods=['POST'])
def login():
    
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')

    user = usersCollection.find_one({"username": username})
    
    if user and user.get("password") == password:
        user['_id'] = str(user['_id'])
        return jsonify(user),200
    
    return jsonify({"error": "Invalid credentials"}),401


@app.route('/users/<user_id>/completed_walks', methods=['GET'])
def get_completed_walks(user_id):
    user = usersCollection.find_one({"_id": ObjectId(user_id)})

    if user:
        completed_walks =  user.get("completed_walks", [])
        return jsonify(completed_walks), 200
    elif not user:
        return jsonify({"error": "User not found"}, 404)
    elif completed_walks == []:
        return jsonify([]), 200
    

@app.route('/users/<user_id>/completed_walks', methods=['POST'])
def add_completed_walk(user_id):
    walk = request.json.get('walk')

    if not walk:
        return jsonify({"error": "No walk data provided"}), 400

    try:
        result = usersCollection.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"completed_walks": walk}}
        )
        
        if result.modified_count == 1:
            return jsonify({"message": "Walk added successfully"}), 200
        else:
            return jsonify({"error": "User not found or no changes made"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
