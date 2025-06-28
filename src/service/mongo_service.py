# src/services/mongo_service.py

from pymongo import MongoClient
from src.utils.settings import settings
from typing import Union
from pydantic import BaseModel

mongo_client = None
mongo_db = None

def init_mongo():
    global mongo_client, mongo_db
    mongo_client = MongoClient(settings.mongo_uri)
    mongo_db = mongo_client[settings.mongo_db_name]

def get_collection(collection_name: str):
    if mongo_db is None:
        raise RuntimeError("MongoDB not initialized.")
    return mongo_db[collection_name]

def insert_one(doc: Union[dict, BaseModel], collection_name: str):
    collection = get_collection(collection_name)
    doc_dict = doc.dict() if isinstance(doc, BaseModel) else doc
    if not collection.find_one({"slug": doc_dict["slug"]}):
        collection.insert_one(doc_dict)

def find_one(query: Union[dict, BaseModel], collection_name: str) -> dict | None:
    collection = get_collection(collection_name)
    query_dict = query.dict() if isinstance(query, BaseModel) else query
    return collection.find_one(query_dict)

def update_one(query: Union[dict, BaseModel], updates: Union[dict, BaseModel], collection_name: str):
    collection = get_collection(collection_name)
    query_dict = query.dict() if isinstance(query, BaseModel) else query
    updates_dict = updates.dict() if isinstance(updates, BaseModel) else updates
    collection.update_one(query_dict, {"$set": updates_dict})

def delete_one(query: Union[dict, BaseModel], collection_name: str):
    collection = get_collection(collection_name)
    query_dict = query.dict() if isinstance(query, BaseModel) else query
    collection.delete_one(query_dict)
