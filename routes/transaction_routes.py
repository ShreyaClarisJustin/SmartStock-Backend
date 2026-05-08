from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from middleware.auth_middleware import authenticate_token, verify_admin
from datetime import datetime

transaction_bp = Blueprint("transactions", __name__, url_prefix="/transactions")

# Global mongo instance
mongo = None

def init_transaction_routes(mongo_instance, app=None):
    """Initialize transaction routes with mongo instance"""
    global mongo
    mongo = mongo_instance


# -------------------------
# GET ALL TRANSACTIONS
# -------------------------
@transaction_bp.route("", methods=["GET"])
@transaction_bp.route("/", methods=["GET"])
@authenticate_token
def get_transactions():
    try:
        if mongo is None:
            return jsonify({"error": "Database not initialized"}), 500
            
        transactions_collection = mongo.db.transactions
        result = []
        
        for t in transactions_collection.find():
            t["_id"] = str(t["_id"])
            if isinstance(t.get("productId"), ObjectId):
                t["productId"] = str(t["productId"])
            if isinstance(t.get("userId"), ObjectId):
                t["userId"] = str(t["userId"])
            result.append(t)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# CREATE TRANSACTION (General)
# -------------------------
@transaction_bp.route("", methods=["POST"])
@authenticate_token
def create_transaction():
    try:
        if mongo is None:
            return jsonify({"error": "Database not initialized"}), 500
            
        data = request.json
        transactions_collection = mongo.db.transactions
        
        # Add userId from token and timestamp if not provided
        data["userId"] = ObjectId(request.user["id"])
        if "createdAt" not in data:
            data["createdAt"] = datetime.utcnow()
        
        result = transactions_collection.insert_one(data)
        
        return jsonify({
            "message": "Transaction recorded successfully",
            "id": str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# GET TRANSACTION BY ID
# -------------------------
@transaction_bp.route("/<id>", methods=["GET"])
@authenticate_token
def get_transaction(id):
    try:
        if mongo is None:
            return jsonify({"error": "Database not initialized"}), 500
            
        transactions_collection = mongo.db.transactions
        transaction = transactions_collection.find_one({"_id": ObjectId(id)})
        
        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404
        
        transaction["_id"] = str(transaction["_id"])
        if isinstance(transaction.get("productId"), ObjectId):
            transaction["productId"] = str(transaction["productId"])
        if isinstance(transaction.get("userId"), ObjectId):
            transaction["userId"] = str(transaction["userId"])
        
        return jsonify(transaction)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# UPDATE TRANSACTION
# -------------------------
@transaction_bp.route("/<id>", methods=["PUT"])
@authenticate_token
@verify_admin
def update_transaction(id):
    try:
        if mongo is None:
            return jsonify({"error": "Database not initialized"}), 500
            
        data = request.json
        transactions_collection = mongo.db.transactions
        
        result = transactions_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": data},
            return_document=True
        )
        
        if not result:
            return jsonify({"error": "Transaction not found"}), 404
        
        result["_id"] = str(result["_id"])
        if isinstance(result.get("productId"), ObjectId):
            result["productId"] = str(result["productId"])
        if isinstance(result.get("userId"), ObjectId):
            result["userId"] = str(result["userId"])
        
        return jsonify({"message": "Transaction updated successfully", "transaction": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# DELETE TRANSACTION
# -------------------------
@transaction_bp.route("/<id>", methods=["DELETE"])
@authenticate_token
@verify_admin
def delete_transaction(id):
    try:
        if mongo is None:
            return jsonify({"error": "Database not initialized"}), 500
            
        transactions_collection = mongo.db.transactions
        result = transactions_collection.delete_one({"_id": ObjectId(id)})
        
        if result.deleted_count == 0:
            return jsonify({"error": "Transaction not found"}), 404
        
        return jsonify({"message": "Transaction deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# SALE (Stock reduction)
# -------------------------
@transaction_bp.route("/sale", methods=["POST"])
@authenticate_token
def sale():
    try:
        if mongo is None:
            return jsonify({"error": "Database not initialized"}), 500
            
        data = request.json
        product_id = data.get("productId")
        quantity = data.get("quantity")
        
        if not product_id or not quantity:
            return jsonify({"error": "Missing productId or quantity"}), 400
        
        products_collection = mongo.db.products
        transactions_collection = mongo.db.transactions
        
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        if product.get("stock", 0) < quantity:
            return jsonify({"error": "Insufficient stock"}), 400
        
        # Update stock
        products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"stock": -quantity}}
        )
        
        # Record transaction
        transactions_collection.insert_one({
            "productId": ObjectId(product_id),
            "quantity": -quantity,
            "type": "sale",
            "userId": ObjectId(request.user["id"]),
            "createdAt": datetime.utcnow()
        })
        
        return jsonify({"message": "Sale recorded successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# RESTOCK (Stock increase)
# -------------------------
@transaction_bp.route("/restock", methods=["POST"])
@authenticate_token
def restock():
    try:
        if mongo is None:
            return jsonify({"error": "Database not initialized"}), 500
            
        data = request.json
        product_id = data.get("productId")
        quantity = data.get("quantity")
        
        if not product_id or not quantity:
            return jsonify({"error": "Missing productId or quantity"}), 400
        
        products_collection = mongo.db.products
        transactions_collection = mongo.db.transactions
        
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        # Update stock
        products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"stock": quantity}}
        )
        
        # Record transaction
        transactions_collection.insert_one({
            "productId": ObjectId(product_id),
            "quantity": quantity,
            "type": "restock",
            "userId": ObjectId(request.user["id"]),
            "createdAt": datetime.utcnow()
        })
        
        return jsonify({"message": "Restock successful"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
