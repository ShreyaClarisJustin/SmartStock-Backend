from flask import Blueprint, request, jsonify, current_app
import bcrypt, jwt, datetime
from flask_pymongo import PyMongo

auth_bp = Blueprint("auth", __name__)
mongo = None

def init_auth_routes(mongo_instance, app):
    global mongo
    mongo = mongo_instance

@auth_bp.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.json
        users = mongo.db.users
        
        # Validate required fields
        if not data.get("email") or not data.get("password") or not data.get("firstname") or not data.get("role"):
            return jsonify({"error": "Missing required fields"}), 400
        
        if users.find_one({"email": data["email"]}):
            return jsonify({"error": "Email already registered"}), 400

        hashed = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())
        users.insert_one({
            "firstname": data["firstname"],
            "email": data["email"],
            "password": hashed,
            "role": data["role"]
        })

        return jsonify({"message": "Signup successful"})
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        
        # Validate required fields
        if not data.get("email") or not data.get("password"):
            return jsonify({"error": "Email and password required"}), 400
        
        users = mongo.db.users
        user = users.find_one({"email": data["email"]})
        
        if not user:
            return jsonify({"error": "User not found"}), 400

        # Check password
        if not bcrypt.checkpw(data["password"].encode(), user["password"]):
            return jsonify({"error": "Wrong password"}), 400

        # Create JWT token
        token = jwt.encode({
            "id": str(user["_id"]),
            "role": user["role"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, current_app.config["SECRET_KEY"], algorithm="HS256")

        return jsonify({
            "message": "Login successful",
            "token": token,
            "role": user["role"],
            "user": {
                "firstname": user.get("firstname", ""),
                "email": user["email"],
                "role": user["role"]
            }
        })
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"error": str(e)}), 500

