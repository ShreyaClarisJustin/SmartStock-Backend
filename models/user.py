# // const mongoose = require("mongoose");

# // const UserSchema = new mongoose.Schema({
# //     firstname: { type: String, required: true },
# //     email: { type: String, required: true, unique: true },
# //     password: { type: String, required: true },
# //     role: { type: String, enum: ["admin", "employee"], required: true }
# // });

# // module.exports = mongoose.model("User", UserSchema);


# const mongoose = require("mongoose");

# const userSchema = new mongoose.Schema({
#   firstname: { type: String, required: true },
#   email: { type: String, required: true, unique: true },
#   password: { type: String, required: true },
#   role: { type: String, enum: ["admin", "employee"], required: true }
# });

# module.exports = mongoose.models.User || mongoose.model("User", userSchema);


from bson.objectid import ObjectId


class User:
    ALLOWED_ROLES = ["admin", "employee"]

    def __init__(
        self,
        mongo,
        firstname,
        email,
        password,
        role,
        _id=None
    ):
        if role not in self.ALLOWED_ROLES:
            raise ValueError("Invalid user role")

        self.mongo = mongo
        self.collection = mongo.db.users

        self._id = _id
        self.firstname = firstname
        self.email = email
        self.password = password
        self.role = role

    # --------------------------
    # Save user
    # --------------------------
    def save(self):
        data = {
            "firstname": self.firstname,
            "email": self.email,
            "password": self.password,
            "role": self.role
        }

        if self._id:
            self.collection.update_one(
                {"_id": ObjectId(self._id)},
                {"$set": data}
            )
        else:
            # enforce unique email
            if self.collection.find_one({"email": self.email}):
                raise ValueError("Email already exists")

            result = self.collection.insert_one(data)
            self._id = result.inserted_id

        return self

    # --------------------------
    # Convert to dict (safe)
    # --------------------------
    def to_dict(self, include_password=False):
        user = {
            "_id": str(self._id),
            "firstname": self.firstname,
            "email": self.email,
            "role": self.role
        }

        if include_password:
            user["password"] = self.password

        return user

    # --------------------------
    # STATIC METHODS (Mongoose-like)
    # --------------------------
    @staticmethod
    def find_by_email(mongo, email):
        doc = mongo.db.users.find_one({"email": email})
        if not doc:
            return None
        return User.from_mongo(mongo, doc)

    @staticmethod
    def find_by_id(mongo, user_id):
        doc = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not doc:
            return None
        return User.from_mongo(mongo, doc)

    @staticmethod
    def find_all(mongo):
        users = []
        for doc in mongo.db.users.find({}, {"password": 0}):
            users.append(User.from_mongo(mongo, doc))
        return users

    @staticmethod
    def delete_by_id(mongo, user_id):
        return mongo.db.users.find_one_and_delete(
            {"_id": ObjectId(user_id)}
        )

    @staticmethod
    def from_mongo(mongo, doc):
        return User(
            mongo=mongo,
            _id=doc["_id"],
            firstname=doc["firstname"],
            email=doc["email"],
            password=doc["password"],
            role=doc["role"]
        )
