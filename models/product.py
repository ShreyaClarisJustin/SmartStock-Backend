# // const mongoose = require("mongoose");

# // const ProductSchema = new mongoose.Schema({
# //     name: { type: String, required: true },
# //     description: { type: String },
# //     price: { type: Number, required: true },
# //     stock: { type: Number, required: true },
# //     category: { type: String },
# //     createdAt: { type: Date, default: Date.now }
# // });

# // module.exports = mongoose.model("Product", ProductSchema);



# const mongoose = require("mongoose");

# const productSchema = new mongoose.Schema({
#   name: { type: String, required: true },
#   description: { type: String },
#   price: { type: Number, required: true },
#   stock: { type: Number, required: true },
#   lowStockLimit : { type: Number, required: true },
#   lowStockAlertSent: {
#     type: Boolean,
#     default: false // 🔴 prevents repeated emails
#   },
#   category: { type: String },
#   createdAt: { type: Date, default: Date.now }
# });

# // module.exports = mongoose.models.Product || mongoose.model("Product", productSchema);

# module.exports = mongoose.model("Product", productSchema);




from datetime import datetime
from bson.objectid import ObjectId


class Product:
    def __init__(
        self,
        mongo,
        name,
        price,
        stock,
        lowStockLimit,
        description=None,
        category=None,
        lowStockAlertSent=False,
        createdAt=None,
        _id=None
    ):
        self.mongo = mongo
        self.collection = mongo.db.products

        self._id = _id
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.lowStockLimit = lowStockLimit
        self.lowStockAlertSent = lowStockAlertSent
        self.category = category
        self.createdAt = createdAt or datetime.utcnow()

    # --------------------------
    # Save (create or update)
    # --------------------------
    def save(self):
        data = {
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "stock": self.stock,
            "lowStockLimit": self.lowStockLimit,
            "lowStockAlertSent": self.lowStockAlertSent,
            "category": self.category,
            "createdAt": self.createdAt
        }

        if self._id:
            self.collection.update_one(
                {"_id": ObjectId(self._id)},
                {"$set": data}
            )
        else:
            result = self.collection.insert_one(data)
            self._id = result.inserted_id

        return self

    # --------------------------
    # Convert to dict (JSON)
    # --------------------------
    def to_dict(self):
        return {
            "_id": str(self._id),
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "stock": self.stock,
            "lowStockLimit": self.lowStockLimit,
            "lowStockAlertSent": self.lowStockAlertSent,
            "category": self.category,
            "createdAt": self.createdAt
        }

    # --------------------------
    # STATIC METHODS (like Mongoose)
    # --------------------------
    @staticmethod
    def find_by_id(mongo, product_id):
        doc = mongo.db.products.find_one({"_id": ObjectId(product_id)})
        if not doc:
            return None
        return Product.from_mongo(mongo, doc)

    @staticmethod
    def find_all(mongo):
        products = []
        for doc in mongo.db.products.find():
            products.append(Product.from_mongo(mongo, doc))
        return products

    @staticmethod
    def delete_by_id(mongo, product_id):
        return mongo.db.products.find_one_and_delete(
            {"_id": ObjectId(product_id)}
        )

    @staticmethod
    def from_mongo(mongo, doc):
        return Product(
            mongo=mongo,
            _id=doc["_id"],
            name=doc["name"],
            description=doc.get("description"),
            price=doc["price"],
            stock=doc["stock"],
            lowStockLimit=doc["lowStockLimit"],
            lowStockAlertSent=doc.get("lowStockAlertSent", False),
            category=doc.get("category"),
            createdAt=doc.get("createdAt")
        )
