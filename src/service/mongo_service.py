# src/services/mongo_service.py

from pymongo import MongoClient
from src.utils.settings import settings

mongo_client = None
mongo_db = None
problems_collection = None

def init_mongo():
    global mongo_client, mongo_db, problems_collection
    mongo_client = MongoClient(settings.mongo_uri)
    mongo_db = mongo_client[settings.mongo_db_name]
    problems_collection = mongo_db["problems"]

def insert_problem(problem_doc: dict):
    if problems_collection is None:
        raise RuntimeError("MongoDB not initialized.")
    if not problems_collection.find_one({"slug": problem_doc["slug"]}):
        problems_collection.insert_one(problem_doc)

def get_problem_by_slug(slug: str):
    if problems_collection is None:
        raise RuntimeError("MongoDB not initialized.")
    return problems_collection.find_one({"slug": slug})

def update_problem(slug: str, updates: dict):
    if problems_collection is None:
        raise RuntimeError("MongoDB not initialized.")
    problems_collection.update_one({"slug": slug}, {"$set": updates})
