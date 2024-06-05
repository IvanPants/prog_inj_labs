
import loguru
import pymongo
from bson import ObjectId
from pymongo import MongoClient

# from..models.chat_model import ChatModel
# from src.models.message import Message
# from src.models.settings_model import Settings

from .models.chat_model import ChatModel
from .models.message import Message
from .models.settings_model import Settings


class MongoApi:
    def __init__(self, settings: Settings):
        self.logger: loguru.Logger = loguru.logger.bind(object_id='MongoApi')
        self.logger.debug(f'MongoApi here')
        self.settings = settings
        self.client = MongoClient(host=self.settings.db_host, port=self.settings.db_port)
        self.db = self.get_or_create_db()
        self.logger.debug(f'Db info: {self.db}')

    def get_or_create_db(self):
        db = self.client[f"{self.settings.db_name}"]
        self.logger.trace(f'db: {db}')
        return db


class ChatWorker:
    def __init__(self, settings: Settings):
        self.logger: loguru.Logger = loguru.logger.bind(object_id='Run main')
        self.mongo_api: MongoApi = MongoApi(settings)
        self.chats: pymongo.collection = self.mongo_api.db.chats

    async def add_member(self, chat_id: str, member: int) -> tuple[bool, str]:
        self.logger.debug(f'Adding member {member} to chat {chat_id}...')
        filter_query = {"_id": ObjectId(chat_id)}
        update_query = {"$push": {"members": member}}
        res = self.chats.update_one(filter_query, update=update_query)
        self.logger.trace(f'res: {res}')
        if res.modified_count == 1:
            self.logger.debug('Member added successfully')
            return True, 'Member added successfully'
        else:
            self.logger.debug(f'Chat not found')
            return False, 'Chat not found'

    async def add_chat(self, chat: ChatModel):
        self.logger.trace(chat)
        self.logger.trace(ChatModel.model_dump(chat))
        result = self.chats.insert_one(ChatModel.model_dump(chat))
        inserted_id = str(result.inserted_id)
        self.logger.debug(f'Inserted id: {inserted_id}')
        return inserted_id

    async def view_chat_by_id(self, chat_id: str):
        chat = self.chats.find_one({"_id": ObjectId(chat_id)})
        self.logger.trace(chat)
        if chat:
            chat["_id"] = str(chat["_id"])
        return chat

    async def change_chat_name(self, chat_id: str, name):
        filter_query = {"_id": ObjectId(chat_id)}
        update_query = {"$set": {"chat_name": name}}
        chat = self.chats.update_one(filter_query, update=update_query)
        return chat

    #
    async def add_message(self, chat_id: str, message: Message):
        filter_query = {"_id": ObjectId(chat_id)}
        update_query = {"$push": {"messages": Message.model_dump(message)}}
        chat = self.chats.update_one(filter_query, update=update_query)
        return chat

    async def delete_chat(self, chat_id: str):
        self.logger.debug(f'Deleting chat {chat_id}...')
        filter_query = {"_id": ObjectId(chat_id)}
        res = self.chats.delete_one(filter_query)
        self.logger.trace(f'res: {res}')
        # self.logger.trace(f'res upserted: {res.upserted_id}')
        if res.deleted_count == 1:
            self.logger.debug('Chat deleted successfully')
            return True, 'Chat deleted successfully'
        else:
            self.logger.debug(f'Chat not found')
            return False, 'Chat not found'

