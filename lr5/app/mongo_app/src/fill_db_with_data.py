import random

import loguru
from faker import Faker
from loguru import logger

from .config import get_config, logger_set_up
from .models.settings_model import Settings


class Filler:
    def __init__(self, settings: Settings):
        self.logger: loguru.Logger = loguru.logger.bind(object_id='Filler')
        self.logger.debug(f'Filler here')
        self.settings = settings

    def generate_data(self) -> dict:
        MAX_ADMINS = 5
        MAX_USERS = 10
        MAX_MSGS = 30
        fake = Faker()
        chat = dict()
        chat['is_P2P'] = random.choice([True, False])  # choose p2p or not
        admins = list()
        members = list()

        max_admins = random.randint(3, MAX_ADMINS)
        # print(f'max_admins: {max_admins}')
        while len(admins) < max_admins:
            admins.append(fake.unique.pyint(min_value=100, max_value=99999))
        admins = list(set(admins))

        if chat['is_P2P']:
            # if P2P then all members are admins
            members = admins.copy()

        else:
            members = admins.copy()
            max_users = random.randint(len(members), MAX_USERS)
            # print(f'max_users: {max_users}')
            while len(members) < max_users:
                members.append(random.randint(1, 10000))
            members = list(set(members))

            if len(members) == len(admins):
                members.append(random.randint(1, 10000))

        chat['admins'] = admins
        chat['members'] = members
        chat['chat_name'] = 'Chat_' + fake.company()
        chat['messages'] = []
        for _ in range(random.randint(10, MAX_MSGS)):
            message = dict()
            message['message_text'] = fake.text()
            # message['send_date'] = Initializer.random_date(
            #     datetime(2022, 1, 1), datetime.now())
            # message['send_date'] = fake.date_this_month()
            message['send_date'] = fake.date_time_this_month()
            message['member'] = random.choice(chat['members'])
            chat['messages'].append(message)

        return chat

    def generate_chats(self, num_chats: int = 4) -> list[dict]:
        return [self.generate_data() for _ in range(num_chats)]


def print_chat(chat: dict, output_more: bool = False) -> None:
    # logger.trace(f'chat keys: {chat.keys()}')
    logger.debug(f'chat isP2P: {chat.get("is_P2P")}')

    logger.debug(f'Number of admins: {len(chat.get("admins"))}')
    if output_more:
        for admin in chat['admins']:
            logger.trace(f'admin: {admin}')

    logger.debug(f'Number of members: {len(chat.get("members"))}')
    if output_more:
        for user in chat['members']:
            logger.trace(f'user: {user}')

    logger.debug(f'Number of messages: {len(chat.get("messages"))}')
    if output_more:
        for msg in chat['messages']:
            logger.trace(f'msg: {msg}')


if __name__ == '__main__':
    num_of_chats = 5
    s = get_config()
    logger_set_up(s)
    f = Filler(s)
    # chat1 = f.generate_data()
    chats = f.generate_chats(num_of_chats)
    list(map(print_chat, chats))
    # logger.info(f'chat1: {chat1}')
