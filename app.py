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
    try:
        walks = list(walksCollection.find({}))
        for walk in walks:
            walk['_id'] = str(walk['_id'])
        return jsonify(walks), 200
    except Exception as e:
            return jsonify({"error": str(e)}), 500

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

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = usersCollection.find_one({"username": username})

    if user and user.get("password") == password:
        # Convert user ID to string for frontend use
        user['_id'] = str(user['_id'])

        # Fetch completed walk IDs and resolve full walk documents
        completed_walk_ids = user.get("completed_walks", [])
        object_ids = [
            ObjectId(wid) if not isinstance(wid, ObjectId) else wid
            for wid in completed_walk_ids
        ]

        # Lookup completed walk documents
        walks = list(walksCollection.find({'_id': {'$in': object_ids}}))
        for walk in walks:
            walk['_id'] = str(walk['_id'])

        # Replace completed_walks field with full documents
        user['completed_walks'] = walks

        # Remove password before sending to frontend
        user.pop('password', None)

        return jsonify(user), 200

    return jsonify({"error": "Invalid credentials"}), 401



@app.route('/users/<user_id>/completed_walks', methods=['POST'])
def add_completed_walk(user_id):
    walk_id = request.json.get('walk_id')

    if not walk_id:
        return jsonify({"error": "No walk data provided"}), 400

    try:
        result = usersCollection.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"completed_walks": ObjectId(walk_id)}}
        )
        
        if result.modified_count == 1:
            return jsonify({"message": "Walk added successfully"}), 200
        else:
            return jsonify({"error": "User not found or no changes made"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
