from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client.resume_db

collection_resume = db["resume_collection"]