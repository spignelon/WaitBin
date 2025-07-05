#!/usr/bin/env python3

from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB setup
client = MongoClient(os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/'))
db = client.waitbin
pastebin_codes_collection = db.pastebin_codes

# Sample codes to add
sample_codes = [
    'hello',
    'world',
    'test123',
    'admin',
    'secret'
]

print("Adding sample pastebin codes...")

for code in sample_codes:
    # Check if code already exists
    if not pastebin_codes_collection.find_one({'code': code}):
        pastebin_codes_collection.insert_one({'code': code})
        print(f"Added code: {code}")
    else:
        print(f"Code already exists: {code}")

print(f"\nTotal codes in database: {pastebin_codes_collection.count_documents({})}")
