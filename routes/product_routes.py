from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from middleware.auth_middleware import authenticate_token, verify_admin

product_bp = Blueprint("products", __name__, url_prefix="/products")

# Global mongo instance
mongo = None

def init_product_routes(mongo_instance, app=None):
    """Initialize product routes with mongo instance"""
    global mongo
    mongo = mongo_instance


# -------------------------
# GET ALL PRODUCTS
# -------------------------
@product_bp.route("", methods=["GET"])
@product_bp.route("/", methods=["GET"])
@authenticate_token
def get_products():
    try:
        if mongo is None:
            print("ERROR: mongo is None")
            return jsonify({"error": "Database not initialized"}), 500
            
        products_collection = mongo.db.products
        products = []
        
        print(f"Fetching products for user: {request.user}")
        
        for product in products_collection.find():
            product["_id"] = str(product["_id"])
            products.append(product)
        
        print(f"Found {len(products)} products")
        return jsonify(products), 200
    except Exception as e:
        print(f"Error fetching products: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# -------------------------
# ADD A NEW PRODUCT
# -------------------------
@product_bp.route("", methods=["POST"])
@product_bp.route("/", methods=["POST"])
@authenticate_token
@verify_admin
def add_product():
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ["name", "category", "supplier", "sku", "price", "stock", "lowStockLimit"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        products_collection = mongo.db.products
        
        product = {
            "name": data["name"],
            "category": data["category"],
            "supplier": data["supplier"],
            "sku": data["sku"],
            "price": float(data["price"]),
            "stock": int(data["stock"]),
            "lowStockLimit": int(data["lowStockLimit"]),
            "createdAt": __import__("datetime").datetime.utcnow()
        }
        
        result = products_collection.insert_one(product)
        product["_id"] = str(result.inserted_id)
        
        return jsonify({
            "message": "Product added successfully",
            "product": product
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# UPDATE PRODUCT STOCK
# -------------------------
@product_bp.route("/<product_id>/stock", methods=["PUT"])
@authenticate_token
def update_stock(product_id):
    try:
        data = request.json
        
        if "stock" not in data:
            return jsonify({"error": "Missing 'stock' field"}), 400
        
        products_collection = mongo.db.products
        transactions_collection = mongo.db.transactions
        
        # Convert string ID to ObjectId
        try:
            product_obj_id = ObjectId(product_id)
        except:
            return jsonify({"error": "Invalid product ID"}), 400
        
        product = products_collection.find_one({"_id": product_obj_id})
        
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        old_stock = product["stock"]
        new_stock = int(data["stock"])
        quantity_changed = new_stock - old_stock
        
        # Update product stock
        products_collection.update_one(
            {"_id": product_obj_id},
            {"$set": {"stock": new_stock}}
        )
        
        # Record transaction - use 'id' from JWT token (not '_id')
        transaction = {
            "productId": product_obj_id,
            "userId": request.user.get("id"),
            "type": "stock_update",
            "quantity_changed": quantity_changed,
            "old_stock": old_stock,
            "new_stock": new_stock,
            "timestamp": __import__("datetime").datetime.utcnow()
        }
        transactions_collection.insert_one(transaction)
        
        return jsonify({
            "message": "Stock updated successfully",
            "product": {
                "_id": str(product["_id"]),
                "name": product["name"],
                "old_stock": old_stock,
                "new_stock": new_stock
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# DELETE PRODUCT
# -------------------------
@product_bp.route("/<product_id>", methods=["DELETE"])
@authenticate_token
@verify_admin
def delete_product(product_id):
    try:
        products_collection = mongo.db.products
        
        # Convert string ID to ObjectId
        try:
            product_obj_id = ObjectId(product_id)
        except:
            return jsonify({"error": "Invalid product ID"}), 400
        
        result = products_collection.delete_one({"_id": product_obj_id})
        
        if result.deleted_count == 0:
            return jsonify({"error": "Product not found"}), 404
        
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
