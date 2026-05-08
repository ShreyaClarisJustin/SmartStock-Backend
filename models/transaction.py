# const mongoose = require("mongoose");

# const transactionSchema = new mongoose.Schema({
#   type: {
#     type: String,
#     required: true,
#     enum: ['sale', 'restock', 'return', 'transfer', 'adjustment']
#   },
#   productId: {
#     type: mongoose.Schema.Types.ObjectId,
#     ref: 'Product',
#     required: true
#   },
#   quantity: {
#     type: Number,
#     required: true
#   },
#   userId: {
#     type: mongoose.Schema.Types.ObjectId,
#     ref: 'User',
#     required: true
#   },
#   store: {
#     type: String,
#     default: 'Main Store'
#   },
#   notes: {
#     type: String
#   },
#   date: {
#     type: Date,
#     default: Date.now
#   },
#   createdAt: {
#     type: Date,
#     default: Date.now
#   }
# });

# module.exports = mongoose.models.Transaction || mongoose.model("Transaction", transactionSchema);






from datetime import datetime
from bson.objectid import ObjectId


class Transaction:
    ALLOWED_TYPES = ["sale", "restock", "return", "transfer", "adjustment"]

    def __init__(
        self,
        mongo,
        type,
        productId,
        quantity,
        userId,
        store="Main Store",
        notes=None,
        date=None,
        createdAt=None,
        _id=None
    ):
        if type not in self.ALLOWED_TYPES:
            raise ValueError("Invalid transaction type")

        self.mongo = mongo
        self.collection = mongo.db.transactions

        self._id = _id
        self.type = type
        self.productId = ObjectId(productId)
        self.quantity = quantity
        self.userId = ObjectId(userId)
        self.store = store
        self.notes = notes
        self.date = date or datetime.utcnow()
        self.createdAt = createdAt or datetime.utcnow()

    # --------------------------
    # Save transaction
    # --------------------------
    def save(self):
        data = {
            "type": self.type,
            "productId": self.productId,
            "quantity": self.quantity,
            "userId": self.userId,
            "store": self.store,
            "notes": self.notes,
            "date": self.date,
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
    # Convert to dict
    # --------------------------
    def to_dict(self):
        return {
            "_id": str(self._id),
            "type": self.type,
            "productId": str(self.productId),
            "quantity": self.quantity,
            "userId": str(self.userId),
            "store": self.store,
            "notes": self.notes,
            "date": self.date,
            "createdAt": self.createdAt
        }

    # --------------------------
    # STATIC METHODS (Mongoose-like)
    # --------------------------
    @staticmethod
    def find_all(mongo):
        result = []
        for doc in mongo.db.transactions.find():
            result.append(Transaction.from_mongo(mongo, doc))
        return result

    @staticmethod
    def find_by_id(mongo, transaction_id):
        doc = mongo.db.transactions.find_one(
            {"_id": ObjectId(transaction_id)}
        )
        if not doc:
            return None
        return Transaction.from_mongo(mongo, doc)

    @staticmethod
    def delete_by_id(mongo, transaction_id):
        return mongo.db.transactions.find_one_and_delete(
            {"_id": ObjectId(transaction_id)}
        )

    @staticmethod
    def from_mongo(mongo, doc):
        return Transaction(
            mongo=mongo,
            _id=doc["_id"],
            type=doc["type"],
            productId=doc["productId"],
            quantity=doc["quantity"],
            userId=doc["userId"],
            store=doc.get("store", "Main Store"),
            notes=doc.get("notes"),
            date=doc.get("date"),
            createdAt=doc.get("createdAt")
        )
