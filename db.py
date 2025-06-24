from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["avscript"]
chats_collection = db["chats"]

def save_chat(session_id, role, content):
    chats_collection.insert_one({
        "session": session_id,
        "role": role,
        "content": content
    })

def get_chat_history(session_id):
    return list(chats_collection.find({"session": session_id}))
