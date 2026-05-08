#!/usr/bin/env python3
"""
Quick test to verify MongoDB connection and Flask app setup
"""

from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/authDB"

try:
    mongo = PyMongo(app)
    print("✓ Flask and PyMongo imports working")
    
    with app.app_context():
        # Test MongoDB connection
        test_db = mongo.db.test_collection
        print("✓ MongoDB connection successful")
        
        # List databases
        try:
            client = mongo.cx
            dbs = client.list_database_names()
            print(f"✓ Available databases: {dbs}")
        except Exception as e:
            print(f"✗ Error listing databases: {e}")
            
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nNow try running: python app.py")
