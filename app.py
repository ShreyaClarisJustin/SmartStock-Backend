from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify, send_from_directory
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.objectid import ObjectId
from functools import wraps
import jwt
import bcrypt
import datetime
import os

# Import blueprints
from routes.auth_routes import auth_bp, init_auth_routes
from routes.product_routes import product_bp, init_product_routes
from routes.transaction_routes import transaction_bp, init_transaction_routes
from middleware.auth_middleware import authenticate_token

# --------------------------
# APP SETUP
# --------------------------
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")

# app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
app = Flask(__name__)

# Configure CORS to allow preflight requests
CORS(app, 
     resources={r"/*": {"origins": "*"}},
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# app.config["MONGO_URI"] = "mongodb+srv://<smartstock>:<smartstock123>@cluster0.58zie8k.mongodb.net/authDB?appName=Cluster0"
# app.config["SECRET_KEY"] = "MY_SECRET_KEY"

app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

mongo = PyMongo(app)

# --------------------------
# INITIALIZE BLUEPRINTS (API ROUTES)
# --------------------------
init_auth_routes(mongo, app)
init_product_routes(mongo, app)
init_transaction_routes(mongo, app)

app.register_blueprint(auth_bp)
app.register_blueprint(product_bp)
app.register_blueprint(transaction_bp)

# Handle OPTIONS requests for CORS preflight
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response, 200

# --------------------------
# FRONTEND STATIC ROUTES
# --------------------------
@app.route("/")
def index():
    return jsonify({"message": "SmartStock Backend Running"})



# --------------------------
# DB COLLECTIONS
# --------------------------
users = mongo.db.users
products = mongo.db.products
transactions = mongo.db.transactions

# --------------------------
# USER MANAGEMENT (ADMIN)
# --------------------------
@app.route("/users", methods=["GET"])
@authenticate_token
def get_users():
    if request.user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    result = []
    for u in users.find({}, {"password": 0}):
        u["_id"] = str(u["_id"])
        result.append(u)

    return jsonify(result)

@app.route("/users", methods=["POST"])
@authenticate_token
def create_user():
    if request.user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    try:
        data = request.json
        
        # Check if email exists
        if users.find_one({"email": data["email"]}):
            return jsonify({"error": "Email already exists"}), 400
        
        hashed = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())

        users.insert_one({
            "firstname": data["firstname"],
            "email": data["email"],
            "password": hashed,
            "role": data["role"]
        })

        return jsonify({"message": "User created successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<id>", methods=["PUT"])
@authenticate_token
def update_user(id):
    if request.user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    try:
        data = request.json
        result = users.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": data},
            return_document=True
        )
        if not result:
            return jsonify({"error": "User not found"}), 404
        
        result["_id"] = str(result["_id"])
        return jsonify({"message": "User updated successfully", "user": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<id>", methods=["DELETE"])
@authenticate_token
def delete_user(id):
    if request.user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    try:
        result = users.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({"message": "User deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------
# START SERVER
# --------------------------
if __name__ == "__main__":
    app.run(port=3000, debug=True)

