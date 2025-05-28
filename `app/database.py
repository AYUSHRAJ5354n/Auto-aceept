from pymongo import MongoClient
from typing import Dict, List

class MongoDB:
    def __init__(self, uri: str):
        self.client = MongoClient(uri)
        self.db = self.client.telegram_bot
    
    def init_db(self):
        # Create collections if not exists
        self.db.groups.create_index("chat_id", unique=True)
        self.db.users.create_index("user_id", unique=True)
    
    def broadcast_message(self, bot, message: str) -> int:
        """Send message to all groups/users. Returns success count."""
        success = 0
        for chat in self.db.groups.find():
            try:
                bot.send_message(chat_id=chat["chat_id"], text=message)
                success += 1
            except:
                pass
        return success
    
    def get_stats(self) -> Dict:
        return {
            "groups": self.db.groups.count_documents({}),
            "users": self.db.users.count_documents({})
        }
